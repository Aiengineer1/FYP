import threading
import time
import cv2
import numpy as np
from queue import Queue, Empty
from tracking_core import tracking_yolo_model, PERSON_CLASS_ID, match_and_assign_ids_embedding_only, extract_embedding
from zone_utils import load_global_zone_from_json, transform_points, point_in_polygon
import torch
from PIL import Image
import json
import datetime
import sys

# Helper function for point-in-polygon if not present

def point_in_polygon(point, polygon):
    return cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), point, False) >= 0

# --- Helper for interaction proximity ---
def is_interacting(point, polygon, proximity_threshold=100):
    dist = cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), point, True)
    return dist >= 0 or (dist < 0 and abs(dist) <= proximity_threshold)

class CameraTracker(threading.Thread):
    def __init__(self, camera_name, rtsp_url, mapping_json, offset, global_registry, mall_map_img_path, overlap_zones, overlap_pairs, person_class_id=0):
        super().__init__()
        self.camera_name = camera_name
        self.rtsp_url = rtsp_url
        self.mapping_json = mapping_json
        self.offset = offset
        self.global_registry = global_registry
        self.mall_map_img_path = mall_map_img_path
        self.person_class_id = person_class_id
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
        # --- Face, Age, Gender Model Integration ---
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
        def load_models(yolo_face_path="./yolov11n-face.pt", resnet_path="ResNet-18 Age 0.60 + Gender 93.pt"):
            if not os.path.exists(yolo_face_path) or not os.path.exists(resnet_path):
                raise FileNotFoundError("Model files not found.")
            face_model = YOLO(yolo_face_path)
            face_model.fuse()
            age_gender_model = models.resnet18(weights=None)
            age_gender_model.fc = nn.Linear(512, CLASSES + 2)
            age_gender_model = nn.Sequential(age_gender_model, nn.Sigmoid())
            state_dict = torch.load(resnet_path, map_location=DEVICE)
            age_gender_model.load_state_dict(state_dict)
            age_gender_model.to(DEVICE)
            age_gender_model.eval()
            return face_model, age_gender_model
        transform = transforms.Compose([transforms.ToTensor()])
        def preprocess_face(face_roi):
            if face_roi is None or face_roi.size == 0:
                return None
            face_pil = Image.fromarray(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))
            return transform(face_pil).unsqueeze(0).to(DEVICE)
        def extract_info(model, tensor_img):
            if tensor_img is None:
                return "Unknown", "Unknown", [0.0, 0.0]
            with torch.no_grad():
                tensor_labels = model(tensor_img)[0]
            age_group = AGE_GROUPS[torch.argmax(tensor_labels[:CLASSES])]
            gender = "Male" if torch.argmax(tensor_labels[CLASSES:]) == 0 else "Female"
            return age_group, gender, [float(torch.max(tensor_labels[:CLASSES])), float(torch.max(tensor_labels[CLASSES:]))]
        def process_face_frame(frame, face_model, age_gender_model):
            faces = []  # To store face info for association
            results = face_model(frame, imgsz=(640, 640), verbose=False, conf=0.4, iou=0.5, show=False)[0]
            for result in results.boxes.data:
                try:
                    x1, y1, x2, y2, conf, _ = result.tolist()[:6]
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    face_roi = frame[y1:y2, x1:x2]
                    if face_roi.size == 0:
                        continue
                    face_tensor = preprocess_face(face_roi)
                    age_group, gender, _ = extract_info(age_gender_model, face_tensor)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"{age_group} {gender} ({conf:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    # Store face info for association
                    faces.append({
                        'bbox': (x1, y1, x2, y2),
                        'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                        'age_group': age_group,
                        'gender': gender
                    })
                except Exception as e:
                    print(f"Error processing detection: {e}")
            return frame, faces
        # Load models once
        face_model, age_gender_model = load_models()
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
        # --- Interaction time tracking structures ---
        interaction_times = {}  # legacy, will be replaced by new structure
        interactions = {}  # NEW: {person_id: {object_name: {start_time, duration_sec}}}
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
        # --- Main loop ---
        while not self.stop_event.is_set():
            # Always get the latest frame (drain the queue)
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
            # --- Detection ---
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
                        # Compute tracking point based on PERSON_MAP_POINT
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
                        # else: skip detection outside global zone
            # --- Tracking ---
            if person_boxes:
                use_half = torch.cuda.is_available()
                def fast_extract_embedding(frame, bbox):
                    from tracking_core import embedding_model, preprocess
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
                from tracking_core import match_and_assign_ids_embedding_only as orig_match
                orig_extract = orig_match.__globals__['extract_embedding']
                orig_match.__globals__['extract_embedding'] = fast_extract_embedding
                current_objects = orig_match(
                    person_boxes, prev_objects, camera_img, self.object_memory
                )
                orig_match.__globals__['extract_embedding'] = orig_extract
                prev_objects = current_objects
                for obj in current_objects:
                    embedding = obj.embedding
                    # SUPERVISOR CAMERA STRATEGY
                    global_id, supervisor_camera = self.global_registry.match_embedding(embedding, self.camera_name, timestamp=time.time())
                    if global_id is not None:
                        self.global_registry.update(global_id, embedding, self.camera_name, timestamp=time.time())
                        print(f"[CameraTracker] Camera {self.camera_name}: Matched to global_id={global_id} (supervisor={supervisor_camera}) for local id={obj.id}")
                    else:
                        # Only allow this camera to register if it is not already a supervisor for any person
                        if self.global_registry.can_register(self.camera_name):
                            global_id = self.global_registry.register_new(embedding, self.camera_name, timestamp=time.time())
                            print(f"[CameraTracker] Camera {self.camera_name}: Registered new global_id={global_id} for local id={obj.id}")
                        else:
                            print(f"[CameraTracker] Camera {self.camera_name}: Possible duplicate for local id={obj.id} (not supervisor, not registering new global id)")
                            global_id = None
                    x1, y1, x2, y2 = obj.bbox
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    pt = np.array([[[cx, cy]]], dtype=np.float32)
                    mapped_pt = cv2.perspectiveTransform(pt, self.H)[0][0]
                    # --- Route tracking logic ---
                    local_id = f"id_{obj.id}"
                    if local_id not in route_data:
                        route_data[local_id] = {
                            "route": [],
                            "age": None,
                            "gender": None,
                            "start_time": now_str,
                            "end_time": now_str
                        }
                    route_data[local_id]["route"].append([int(mapped_pt[0]), int(mapped_pt[1])])
                    route_data[local_id]["end_time"] = now_str
                    # Try to get age/gender from face overlays (if available)
                    # For now, just keep last seen overlay if present
                    # (You can improve this by associating face to person by proximity)
                    # --- End route tracking logic ---
                    overlay_text = f'Person ID: {obj.id} | Global ID: {global_id if global_id is not None else "?"}'
                    cv2.rectangle(camera_img, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.circle(camera_img, (cx, cy), 5, (0,0,255), -1)
                    cv2.putText(camera_img, overlay_text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                    cv2.circle(mall_map_img, (int(mapped_pt[0]), int(mapped_pt[1])), 10, (0,0,255), -1)
                    cv2.putText(mall_map_img, overlay_text, (int(mapped_pt[0])+10, int(mapped_pt[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
                    for other_cam, other_zone in self.overlap_zones.items():
                        if other_cam == self.camera_name:
                            continue
                        overlap = point_in_polygon(mapped_pt, other_zone)
                        if overlap:
                            cv2.putText(camera_img, f'IN OVERLAP: {other_cam}', (x1, y2+40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                            print(f'[LOG] Person {global_id} in overlap zone with {other_cam}')
            # --- After all person tracking and drawing, run face/age/gender detection ---
            camera_img, detected_faces = process_face_frame(camera_img, face_model, age_gender_model)
            # --- Associate faces to tracked persons and update age/gender ---
            for obj in current_objects if 'current_objects' in locals() else []:
                local_id = f"id_{obj.id}"
                x1, y1, x2, y2 = obj.bbox
                person_cx = int((x1 + x2) / 2)
                person_cy = int((y1 + y2) / 2)
                min_dist = float('inf')
                best_face = None
                for face in detected_faces:
                    fx, fy = face['center']
                    dist = ((person_cx - fx) ** 2 + (person_cy - fy) ** 2) ** 0.5
                    if dist < min_dist:
                        min_dist = dist
                        best_face = face
                if best_face is not None:
                    route_data[local_id]['age'] = best_face['age_group']
                    route_data[local_id]['gender'] = best_face['gender']
            # --- Draw full route for each person ---
            for person in route_data.values():
                if len(person['route']) > 1:
                    pts = np.array(person['route'], dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(mall_map_img, [pts], isClosed=False, color=(0,255,0), thickness=2)
            # --- Draw global zone on mall map ---
            overlay = mall_map_img.copy()
            polygon_np = np.array(dst_polygon, dtype=np.int32)
            cv2.fillPoly(overlay, [polygon_np], color=(0, 0, 255))  # Fill with red
            alpha = 0.3  # Transparency factor
            cv2.addWeighted(overlay, alpha, mall_map_img, 1 - alpha, 0, mall_map_img)
            cv2.polylines(mall_map_img, [polygon_np], isClosed=True, color=(0,0,255), thickness=3)  # Red boundary
            # Label the polygon
            label_pt = tuple(np.array(dst_polygon[0], dtype=int))
            cv2.putText(mall_map_img, 'GLOBAL ZONE', label_pt, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)
            # --- Draw object polygons and labels on mall map ---
            for obj_name, dst_poly in object_polygons_dst:
                poly_np = np.array(dst_poly, dtype=np.int32)
                cv2.polylines(mall_map_img, [poly_np], isClosed=True, color=(255, 165, 0), thickness=2)
                label_pt = tuple(np.array(dst_poly[0], dtype=int))
                cv2.putText(mall_map_img, obj_name, label_pt, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            # --- Draw object polygons and labels on camera frame ---
            for obj_name, src_poly in object_polygons_src:
                poly_np = np.array(src_poly, dtype=np.int32)
                cv2.polylines(camera_img, [poly_np], isClosed=True, color=(255, 165, 0), thickness=2)
                label_pt = tuple(np.array(src_poly[0], dtype=int))
                cv2.putText(camera_img, obj_name, label_pt, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            # --- Annotate current interactions ---
            for obj in current_objects if 'current_objects' in locals() else []:
                local_id = f"id_{obj.id}"
                x1, y1, x2, y2 = obj.bbox
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                pt = np.array([[[cx, cy]]], dtype=np.float32)
                mapped_pt = cv2.perspectiveTransform(pt, self.H)[0][0]
                # --- INTERACTION TRACKING LOGIC ---
                # Get mapped point (mall map)
                person_mapped_pt = (int(mapped_pt[0]), int(mapped_pt[1]))
                # Initialize person's interaction dict if not present
                if local_id not in interactions:
                    interactions[local_id] = {}
                # Track which objects this person is inside or near this frame
                interacting_objects = []
                for obj_name, dst_poly in object_polygons_dst:
                    if is_interacting(person_mapped_pt, dst_poly, proximity_threshold=100):
                        interacting_objects.append(obj_name)
                        # Start or continue timing
                        if obj_name not in interactions[local_id]:
                            interactions[local_id][obj_name] = {"start_time": time.time(), "duration_sec": 0.0}
                        elif interactions[local_id][obj_name]["start_time"] is None:
                            interactions[local_id][obj_name]["start_time"] = time.time()
                    else:
                        # If previously inside/near, accumulate duration
                        if obj_name in interactions[local_id] and interactions[local_id][obj_name]["start_time"] is not None:
                            start = interactions[local_id][obj_name]["start_time"]
                            interactions[local_id][obj_name]["duration_sec"] += time.time() - start
                            interactions[local_id][obj_name]["start_time"] = None
                # For objects not in interacting_objects but present in dict, check if timing needs to be stopped
                for obj_name in list(interactions[local_id].keys()):
                    if obj_name not in interacting_objects and interactions[local_id][obj_name]["start_time"] is not None:
                        start = interactions[local_id][obj_name]["start_time"]
                        interactions[local_id][obj_name]["duration_sec"] += time.time() - start
                        interactions[local_id][obj_name]["start_time"] = None
                # --- END INTERACTION TRACKING LOGIC ---
                if local_id in interactions:
                    for obj_name, data in interactions[local_id].items():
                        if data["start_time"] is not None:
                            # On mall map
                            cv2.putText(mall_map_img, f"Interacting: {obj_name}", (person_mapped_pt[0]+10, person_mapped_pt[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)
                            # On camera frame
                            cv2.putText(camera_img, f"Interacting: {obj_name}", (x1, y2+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)
            # --- END INTERACTION VISUALIZATION ---
            frame_count += 1
            if frame_count % self.age_gender_skip == 0:
                try:
                    from tracking_core import run_face_age_gender_detection
                    camera_img = run_face_age_gender_detection(camera_img, None, None)
                except ImportError:
                    pass
            cv2.imshow(f'Camera: {self.camera_name}', camera_img)
            cv2.imshow(f'Mall Map: {self.camera_name}', mall_map_img)
            self.frames_processed += 1
            if self.frames_processed % self.fps_log_interval == 0:
                now = time.time()
                fps = self.fps_log_interval / (now - self.last_fps_time)
                print(f'[INFO] {self.camera_name}: FPS={fps:.2f}, Frames Dropped={self.frames_dropped}')
                self.last_fps_time = now
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_event.set()
                break
        # --- Save person routes + interactions to JSON on exit ---
        # Finalize durations for any ongoing interactions
        for local_id in interactions:
            for obj_name, data in interactions[local_id].items():
                if data["start_time"] is not None:
                    data["duration_sec"] += time.time() - data["start_time"]
                    data["start_time"] = None
        # Merge interactions into route_data
        for local_id in route_data:
            if local_id in interactions:
                # Only keep duration_sec in output
                route_data[local_id]["interactions"] = {k: {"duration_sec": v["duration_sec"]} for k, v in interactions[local_id].items() if v["duration_sec"] > 0}
        json_path = f"person_routes_{self.camera_name}.json"
        print(f"Saving route+interaction data to {json_path}")
        with open(json_path, "w") as f:
            json.dump(route_data, f, indent=4)
        print("Route+interaction data saved and dictionary cleared.")
        route_data.clear()
        interactions.clear()
        cv2.destroyAllWindows()

    def stop(self):
        self.stop_event.set() 