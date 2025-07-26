import threading
import time
import cv2
import numpy as np
from queue import Queue, Empty
from core.tracking_core import tracking_yolo_model, PERSON_CLASS_ID, match_and_assign_ids_embedding_only, extract_embedding
from core.zone_utils import load_global_zone_from_json, transform_points, point_in_polygon
import torch
from PIL import Image
import json
import datetime
import sys
import os

# Helper function for point-in-polygon if not present
def point_in_polygon(point, polygon):
    return cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), point, False) >= 0

# --- Helper for interaction proximity ---
def is_interacting(point, polygon, proximity_threshold=100):
    dist = cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), point, True)
    return dist >= 0 or (dist < 0 and abs(dist) <= proximity_threshold)

class CameraTracker(threading.Thread):
    def __init__(self, camera_name, rtsp_url, mapping_json, offset, global_registry, mall_map_img_path, overlap_zones, overlap_pairs, person_class_id=0, mode=None):
        super().__init__()
        self.camera_name = camera_name
        self.rtsp_url = rtsp_url
        self.mapping_json = mapping_json
        self.offset = offset
        self.global_registry = global_registry
        self.mall_map_img_path = mall_map_img_path
        self.person_class_id = person_class_id
        self.mode = mode
        self.frame_queue = Queue(maxsize=1)  # Only keep latest frame
        self.stop_event = threading.Event()
        self.global_zone, self.H = load_global_zone_from_json(self.mapping_json)
        self.global_zone_mall = transform_points(self.global_zone['dst_points'], np.eye(3))
        self.overlap_zones = overlap_zones
        self.overlap_pairs = overlap_pairs
        self.object_memory = match_and_assign_ids_embedding_only.__globals__['ObjectMemory']()
        self.fps_log_interval = 30
        self.frames_processed = 0
        self.last_fps_time = time.time()
        self.frames_dropped = 0
        self.age_gender_skip = 5  # Only run age/gender overlay every N frames
        
        # Store person demographics data
        self.person_demographics = {}  # {person_id: {'age': age, 'gender': gender, 'confidence': conf}}

    def _frame_grabber(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            frame = cv2.resize(frame, (1280, 720))
            # Drop oldest frame if queue is full
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                    self.frames_dropped += 1
                except Empty:
                    pass
            self.frame_queue.put(frame)
        cap.release()

    def run(self):
        # --- Load AI Models for Synchronized Pipeline ---
        import torch
        import torchvision.models as models
        import torchvision.transforms as transforms
        from ultralytics import YOLO
        from PIL import Image
        import torch.nn as nn
        import os
        
        # Constants for face/age/gender
        DEVICE = torch.device("cpu")
        AGE_GROUPS = ['00-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        CLASSES = len(AGE_GROUPS)
        
        def load_models():
            """Load all AI models for the pipeline"""
            yolo_face_path = os.path.join(os.path.dirname(__file__), "..", "ml_models", "face_recognition", "yolov11n-face.pt")
            resnet_path = os.path.join(os.path.dirname(__file__), "..", "ml_models", "age_gender", "ResNet-18 Age 0.60 + Gender 93.pt")
            
            if not os.path.exists(yolo_face_path) or not os.path.exists(resnet_path):
                print(f"Warning: Model files not found. Face detection disabled.")
                return None, None
                
            print(f"Loading face detection model: {yolo_face_path}")
            face_model = YOLO(yolo_face_path)
            face_model.fuse()
            
            print(f"Loading age/gender model: {resnet_path}")
            age_gender_model = models.resnet18(weights=None)
            age_gender_model.fc = nn.Linear(512, CLASSES + 2)
            age_gender_model = nn.Sequential(age_gender_model, nn.Sigmoid())
            state_dict = torch.load(resnet_path, map_location=DEVICE)
            age_gender_model.load_state_dict(state_dict)
            age_gender_model.to(DEVICE)
            age_gender_model.eval()
            
            return face_model, age_gender_model
        
        def preprocess_face(face_roi):
            """Preprocess face ROI for age/gender detection"""
            if face_roi is None or face_roi.size == 0:
                return None
            try:
                face_pil = Image.fromarray(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))
                transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
                return transform(face_pil).unsqueeze(0).to(DEVICE)
            except Exception as e:
                print(f"Error preprocessing face: {e}")
                return None
        
        def extract_age_gender(model, tensor_img):
            """Extract age and gender from face tensor"""
            if tensor_img is None or model is None:
                return "Unknown", "Unknown", 0.0
            try:
                with torch.no_grad():
                    tensor_labels = model(tensor_img)[0]
                age_group = AGE_GROUPS[torch.argmax(tensor_labels[:CLASSES])]
                gender = "Male" if torch.argmax(tensor_labels[CLASSES:]) == 0 else "Female"
                confidence = float(torch.max(tensor_labels[:CLASSES]))
                return age_group, gender, confidence
            except Exception as e:
                print(f"Error extracting age/gender: {e}")
                return "Unknown", "Unknown", 0.0
        
        def detect_faces_in_person_region(frame, person_bbox, face_model):
            """Detect faces within a person's bounding box"""
            if face_model is None:
                return []
            
            x1, y1, x2, y2 = person_bbox
            # Expand person bbox slightly to catch faces at edges
            margin = 20
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(frame.shape[1], x2 + margin)
            y2 = min(frame.shape[0], y2 + margin)
            
            person_region = frame[y1:y2, x1:x2]
            if person_region.size == 0:
                return []
            
            try:
                # Detect faces in person region
                results = face_model(person_region, imgsz=(640, 640), verbose=False, conf=0.4, iou=0.5, show=False)[0]
                faces = []
                
                for result in results.boxes.data:
                    try:
                        fx1, fy1, fx2, fy2, conf, _ = result.tolist()[:6]
                        fx1, fy1, fx2, fy2 = map(int, [fx1, fy1, fx2, fy2])
                        
                        # Convert back to original frame coordinates
                        fx1 += x1
                        fy1 += y1
                        fx2 += x1
                        fy2 += y1
                        
                        # Extract face ROI
                        face_roi = frame[fy1:fy2, fx1:fx2]
                        if face_roi.size == 0:
                            continue
                            
                        faces.append({
                            'bbox': (fx1, fy1, fx2, fy2),
                            'roi': face_roi,
                            'confidence': conf
                        })
                    except Exception as e:
                        print(f"Error processing face detection: {e}")
                        continue
                        
                return faces
            except Exception as e:
                print(f"Error in face detection: {e}")
                return []
        
        def process_person_with_demographics(frame, person_bbox, person_id, face_model, age_gender_model):
            """Process a person: detect face, extract age/gender, and associate"""
            # Step 1: Detect faces within person bounding box
            faces = detect_faces_in_person_region(frame, person_bbox, face_model)
            
            if not faces:
                return None
            
            # Step 2: Process the best face (highest confidence)
            best_face = max(faces, key=lambda x: x['confidence'])
            face_roi = best_face['roi']
            
            # Step 3: Extract age and gender
            face_tensor = preprocess_face(face_roi)
            age_group, gender, confidence = extract_age_gender(age_gender_model, face_tensor)
            
            # Step 4: Store demographics for this person
            self.person_demographics[person_id] = {
                'age': age_group,
                'gender': gender,
                'confidence': confidence,
                'face_bbox': best_face['bbox'],
                'last_updated': time.time()
            }
            
            return {
                'age': age_group,
                'gender': gender,
                'confidence': confidence,
                'face_bbox': best_face['bbox']
            }
        
        # Load all models
        print(f"[{self.camera_name}] Loading AI models...")
        face_model, age_gender_model = load_models()
        if face_model is not None and age_gender_model is not None:
            print(f"[{self.camera_name}] AI models loaded successfully")
        else:
            print(f"[{self.camera_name}] Warning: Some AI models failed to load")
        
        # Start frame grabber
        grabber_thread = threading.Thread(target=self._frame_grabber, daemon=True)
        grabber_thread.start()
        
        prev_objects = []
        mall_map_img_orig = cv2.imread(self.mall_map_img_path)
        mall_map_img_orig = cv2.resize(mall_map_img_orig, (1280, 720))
        frame_count = 0
        
        # --- Load global zone polygon from homography JSON ---
        import json
        with open(self.mapping_json, 'r') as f:
            mapping_data = json.load(f)
        global_zone_obj = None
        if isinstance(mapping_data, dict) and 'global_zone' in mapping_data:
            global_zone_obj = mapping_data['global_zone']
        else:
            for obj in mapping_data:
                if obj.get('name') == 'global_zone':
                    global_zone_obj = obj
                    break
        if global_zone_obj is None:
            raise ValueError('No global_zone found in mapping JSON')
        dst_polygon = [tuple(pt) for pt in global_zone_obj['dst_points']]
        
        # --- Route tracking structures ---
        route_data = {}
        interactions = {}  # {person_id: {object_name: {start_time, duration_sec}}}
        
        # --- Load regular_objects from homography JSON ---
        regular_objects = []
        if isinstance(mapping_data, dict) and 'regular_objects' in mapping_data:
            regular_objects = mapping_data['regular_objects']
        else:
            for obj in mapping_data:
                if obj.get('name') != 'global_zone':
                    regular_objects.append(obj)
        
        # --- Precompute polygons for drawing ---
        object_polygons_dst = [(obj['name'], obj['dst_points']) for obj in regular_objects]
        object_polygons_src = [(obj['name'], obj['src_points']) for obj in regular_objects if 'src_points' in obj]
        
        print(f"[{self.camera_name}] Starting synchronized AI pipeline...")
        
        # --- Main processing loop ---
        while not self.stop_event.is_set():
            # Get latest frame
            frame = None
            while not self.frame_queue.empty():
                try:
                    frame = self.frame_queue.get_nowait()
                except Empty:
                    break
            if frame is None:
                time.sleep(0.01)
                continue
                
            camera_img = frame.copy()
            mall_map_img = mall_map_img_orig.copy()
            now_str = time.strftime('%H:%M:%S')
            
            # --- STEP 1: PERSON DETECTION ---
            print(f"[{self.camera_name}] Step 1: Person Detection")
            results = tracking_yolo_model(camera_img, conf=0.3, iou=0.5)
            if isinstance(results, list):
                results = results[0]
            person_boxes = []
            
            if results.boxes is not None:
                for result in results.boxes.data:
                    x1, y1, x2, y2 = map(int, result[:4])
                    conf = result[4].item()
                    class_id = int(result[5])
                    if class_id == PERSON_CLASS_ID and conf > 0.3:
                        # Compute tracking point
                        cx = int((x1 + x2) / 2)
                        if hasattr(self, 'PERSON_MAP_POINT'):
                            map_point = self.PERSON_MAP_POINT
                        else:
                            map_point = 'center'
                        if map_point == 'feet':
                            cy = int(y2)
                        elif map_point == 'head':
                            cy = int(y1)
                        else:
                            cy = int((y1 + y2) / 2)
                        pt = np.array([[[cx, cy]]], dtype=np.float32)
                        mapped_pt = cv2.perspectiveTransform(pt, self.H)[0][0]
                        
                        # Check if mapped point is inside dst_polygon (mall map global zone)
                        if point_in_polygon((int(mapped_pt[0]), int(mapped_pt[1])), dst_polygon):
                            person_boxes.append((x1, y1, x2, y2))
            
            # --- STEP 2: PERSON TRACKING ---
            if person_boxes:
                print(f"[{self.camera_name}] Step 2: Person Tracking - {len(person_boxes)} persons detected")
                use_half = torch.cuda.is_available()
                
                def fast_extract_embedding(frame, bbox):
                    from core.tracking_core import embedding_model, preprocess
                    try:
                        x1, y1, x2, y2 = map(int, bbox)
                        person_region = frame[y1:y2, x1:x2]
                        person_image = cv2.cvtColor(person_region, cv2.COLOR_BGR2RGB)
                        input_tensor = preprocess(Image.fromarray(person_image))
                        if use_half:
                            input_tensor = input_tensor.half()
                        input_batch = input_tensor.unsqueeze(0).to(embedding_model[0].weight.device)
                        with torch.no_grad():
                            if use_half:
                                embedding_model.half()
                            else:
                                embedding_model.float()
                            embedding = embedding_model(input_batch)
                            embedding = embedding.squeeze().cpu().numpy()
                        return embedding
                    except Exception as e:
                        print(f"Error extracting embedding: {e}")
                        return None
                
                from core.tracking_core import match_and_assign_ids_embedding_only as orig_match
                orig_extract = orig_match.__globals__['extract_embedding']
                orig_match.__globals__['extract_embedding'] = fast_extract_embedding
                current_objects = orig_match(person_boxes, prev_objects, camera_img, self.object_memory)
                orig_match.__globals__['extract_embedding'] = orig_extract
                prev_objects = current_objects
                
                # --- STEP 3: FACE DETECTION & AGE/GENDER FOR EACH PERSON ---
                print(f"[{self.camera_name}] Step 3: Face Detection & Age/Gender Analysis")
                for obj in current_objects:
                    person_id = obj.id
                    person_bbox = obj.bbox
                    
                    # Process demographics every few frames to avoid over-processing
                    if frame_count % self.age_gender_skip == 0:
                        demographics = process_person_with_demographics(
                            camera_img, person_bbox, person_id, face_model, age_gender_model
                        )
                        if demographics:
                            print(f"[{self.camera_name}] Person {person_id}: {demographics['age']} {demographics['gender']} (conf: {demographics['confidence']:.2f})")
                    
                    # Get stored demographics for this person
                    person_demo = self.person_demographics.get(person_id, {})
                    
                    # --- STEP 4: GLOBAL ID ASSIGNMENT ---
                    embedding = obj.embedding
                    global_id = None
                    if self.global_registry is not None:
                        global_id, supervisor_camera = self.global_registry.match_embedding(embedding, self.camera_name, timestamp=time.time())
                        if global_id is not None:
                            self.global_registry.update(global_id, embedding, self.camera_name, timestamp=time.time())
                            print(f"[{self.camera_name}] Camera {self.camera_name}: Matched to global_id={global_id} (supervisor={supervisor_camera}) for local id={obj.id}")
                        else:
                            global_id = self.global_registry.register_new_atomic(embedding, self.camera_name, timestamp=time.time())
                            if global_id is not None:
                                print(f"[{self.camera_name}] Camera {self.camera_name}: Registered new global_id={global_id} for local id={obj.id}")
                            else:
                                print(f"[{self.camera_name}] Camera {self.camera_name}: Could not register local id={obj.id}")
                                global_id = None
                    else:
                        global_id = obj.id
                    
                    # --- STEP 5: VISUALIZATION & DATA STORAGE ---
                    x1, y1, x2, y2 = obj.bbox
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    pt = np.array([[[cx, cy]]], dtype=np.float32)
                    mapped_pt = cv2.perspectiveTransform(pt, self.H)[0][0]
                    
                    # Route tracking
                    local_id = f"id_{obj.id}"
                    if local_id not in route_data:
                        route_data[local_id] = {
                            "route": [],
                            "age": person_demo.get('age', 'Unknown'),
                            "gender": person_demo.get('gender', 'Unknown'),
                            "start_time": now_str,
                            "end_time": now_str
                        }
                    route_data[local_id]["route"].append([int(mapped_pt[0]), int(mapped_pt[1])])
                    route_data[local_id]["end_time"] = now_str
                    
                    # Update demographics in route data
                    if person_demo:
                        route_data[local_id]["age"] = person_demo.get('age', 'Unknown')
                        route_data[local_id]["gender"] = person_demo.get('gender', 'Unknown')
                    
                    # Visualization
                    overlay_text = f'Person ID: {obj.id} | Global ID: {global_id if global_id is not None else "?"}'
                    if person_demo:
                        overlay_text += f' | {person_demo.get("age", "Unknown")} {person_demo.get("gender", "Unknown")}'
                    
                    # Draw person bounding box
                    cv2.rectangle(camera_img, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.circle(camera_img, (cx, cy), 5, (0,0,255), -1)
                    cv2.putText(camera_img, overlay_text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                    
                    # Draw face bounding box if available
                    if person_demo and 'face_bbox' in person_demo:
                        fx1, fy1, fx2, fy2 = person_demo['face_bbox']
                        cv2.rectangle(camera_img, (fx1, fy1), (fx2, fy2), (255,0,0), 2)
                        cv2.putText(camera_img, f"{person_demo['age']} {person_demo['gender']}", 
                                  (fx1, fy1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
                    
                    # Draw on mall map
                    cv2.circle(mall_map_img, (int(mapped_pt[0]), int(mapped_pt[1])), 10, (0,0,255), -1)
                    cv2.putText(mall_map_img, overlay_text, (int(mapped_pt[0])+10, int(mapped_pt[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
                    
                    # Check overlap zones
                    for other_cam, other_zone in self.overlap_zones.items():
                        if other_cam == self.camera_name:
                            continue
                        overlap = point_in_polygon(mapped_pt, other_zone)
                        if overlap:
                            cv2.putText(camera_img, f'IN OVERLAP: {other_cam}', (x1, y2+40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                            print(f'[LOG] Person {global_id} in overlap zone with {other_cam}')
            
            # --- PERFORMANCE MONITORING ---
            if self.frames_processed % 30 == 0 and self.global_registry is not None:
                # Performance monitoring code here
                pass
            
            # --- FPS CALCULATION ---
            self.frames_processed += 1
            if self.frames_processed % self.fps_log_interval == 0:
                current_time = time.time()
                fps = self.fps_log_interval / (current_time - self.last_fps_time)
                print(f"[{self.camera_name}] FPS: {fps:.2f}, Processed: {self.frames_processed}, Dropped: {self.frames_dropped}")
                self.last_fps_time = current_time
            
            frame_count += 1
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    def stop(self):
        """Stop the camera tracker"""
        self.stop_event.set()
        print(f"[{self.camera_name}] Camera tracker stopped") 