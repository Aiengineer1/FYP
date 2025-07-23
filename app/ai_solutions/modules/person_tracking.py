import os
import cv2
import numpy as np
import threading
from ultralytics import YOLO
from queue import Queue
import math
from concurrent.futures import ThreadPoolExecutor
import time
from collections import deque
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image

class PersonTracker:
    def __init__(self):
        # Set the environment variable to resolve OpenMP conflicts
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

        # Load YOLOv8 model
        try:
            self.model = YOLO("yolo11n-seg.pt")  # Load segmentation model
            self.model.fuse()  # Fuse model layers for faster inference
            print("YOLO segmentation model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

        # Load ResNet18 for embeddings
        try:
            embedding_model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            embedding_model = torch.nn.Sequential(*list(embedding_model.children())[:-1])
            embedding_model.eval()
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            embedding_model = embedding_model.to(device)
            print(f"ResNet18 embedding model loaded successfully on {device}.")
            self.embedding_model = embedding_model
            self.device = device
        except Exception as e:
            print(f"Error loading ResNet18 model: {e}")
            raise

        self.PERSON_CLASS_ID = 0
        self.EMBEDDING_SIMILARITY_THRESHOLD = 0.85
        self.MEMORY_DURATION = 70
        self.MEMORY_EMBEDDING_THRESHOLD = 0.75
        self.MIN_EMBEDDING_SIMILARITY = 0.75
        self.FRAME_HISTORY_SIZE = 30
        self.EXPECTED_FPS = 20
        self.SKIP_THRESHOLD = 0.5
        self.EVALUATION_INTERVAL = 100
        self.SAVE_EVALUATION_PLOTS = True
        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def extract_embedding(self, frame, bbox):
        try:
            x1, y1, x2, y2 = map(int, bbox)
            person_region = frame[y1:y2, x1:x2]
            person_image = Image.fromarray(cv2.cvtColor(person_region, cv2.COLOR_BGR2RGB))
            input_tensor = self.preprocess(person_image)
            input_batch = input_tensor.unsqueeze(0).to(self.device)
            with torch.no_grad():
                embedding = self.embedding_model(input_batch)
                embedding = embedding.squeeze().cpu().numpy()
            return embedding
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            return None

    def calculate_embedding_similarity(self, embedding1, embedding2):
        try:
            if embedding1 is None or embedding2 is None:
                return 0.0
            emb1_norm = embedding1 / np.linalg.norm(embedding1)
            emb2_norm = embedding2 / np.linalg.norm(embedding2)
            similarity = np.dot(emb1_norm, emb2_norm)
            return max(0.0, similarity)
        except Exception as e:
            print(f"Error calculating embedding similarity: {e}")
            return 0.0

    class FrameStats:
        def __init__(self, FRAME_HISTORY_SIZE, SKIP_THRESHOLD):
            self.frame_times = deque(maxlen=FRAME_HISTORY_SIZE)
            self.frame_count = 0
            self.skipped_frames = 0
            self.last_frame_time = time.time()
            self.processing_times = deque(maxlen=FRAME_HISTORY_SIZE)
            self.last_stats_print = time.time()
            self.stats_interval = 5.0
            self.SKIP_THRESHOLD = SKIP_THRESHOLD

        def update(self, frame_time):
            current_time = time.time()
            frame_interval = current_time - self.last_frame_time
            if frame_interval > self.SKIP_THRESHOLD:
                self.skipped_frames += 1
                print(f"\nWARNING: Frame skip detected! Interval: {frame_interval:.3f}s")
            self.frame_times.append(frame_interval)
            self.last_frame_time = current_time
            self.frame_count += 1

        def update_processing_time(self, processing_time):
            self.processing_times.append(processing_time)

        def get_stats(self):
            if not self.frame_times:
                return "No frames processed yet"
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
            return (f"FPS: {current_fps:.2f} | "
                    f"Avg Frame Time: {avg_frame_time*1000:.1f}ms | "
                    f"Avg Processing Time: {avg_processing_time*1000:.1f}ms | "
                    f"Skipped Frames: {self.skipped_frames} | "
                    f"Total Frames: {self.frame_count}")

        def should_print_stats(self):
            current_time = time.time()
            if current_time - self.last_stats_print >= self.stats_interval:
                self.last_stats_print = current_time
                return True
            return False

    class TrackedObject:
        def __init__(self, obj_id, bbox, frame_count=0, embedding=None):
            self.id = obj_id
            self.bbox = bbox
            self.centroid = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
            self.last_seen = frame_count
            self.disappeared = False
            self.disappeared_frames = 0
            self.track_history = [self.centroid]
            self.embedding = embedding
            self.embedding_history = [embedding] if embedding is not None else []

    class ObjectMemory:
        def __init__(self, max_age, calculate_embedding_similarity):
            self.objects = {}
            self.max_age = max_age
            self.frame_count = 0
            self.used_ids = set()
            self.id_counter = 0
            self.calculate_embedding_similarity = calculate_embedding_similarity

        def update(self, current_objects):
            self.frame_count += 1
            for obj in current_objects:
                if obj.id in self.objects:
                    del self.objects[obj.id]
                obj.last_seen = self.frame_count
                obj.disappeared = False
                obj.disappeared_frames = 0
                self.used_ids.add(obj.id)
                if obj.embedding is not None:
                    obj.embedding_history.append(obj.embedding)
                    if len(obj.embedding_history) > 5:
                        obj.embedding_history.pop(0)
            disappeared_ids = []
            for obj_id, obj in self.objects.items():
                obj.disappeared_frames += 1
                if obj.disappeared_frames > self.max_age:
                    disappeared_ids.append(obj_id)
            for obj_id in disappeared_ids:
                del self.objects[obj_id]

        def add_disappeared(self, obj):
            obj.disappeared = True
            obj.disappeared_frames = 0
            self.objects[obj.id] = obj
            self.used_ids.add(obj.id)

        def find_match(self, embedding, MEMORY_EMBEDDING_THRESHOLD):
            best_score = -1
            best_match = None
            for obj_id, obj in self.objects.items():
                if obj.disappeared_frames > self.max_age:
                    continue
                max_similarity = 0.0
                for hist_embedding in obj.embedding_history:
                    if hist_embedding is not None:
                        similarity = self.calculate_embedding_similarity(embedding, hist_embedding)
                        max_similarity = max(max_similarity, similarity)
                if max_similarity > best_score and max_similarity >= MEMORY_EMBEDDING_THRESHOLD:
                    best_score = max_similarity
                    best_match = obj
            return best_match, best_score

        def get_next_id(self):
            while self.id_counter in self.used_ids:
                self.id_counter += 1
            new_id = self.id_counter
            self.id_counter += 1
            return new_id

    class TrackingMetrics:
        def __init__(self):
            self.true_positives = 0
            self.false_positives = 0
            self.false_negatives = 0
            self.id_switches = 0
            self.prev_ids = set()
            self.current_ids = set()
            self.confusion_matrix = None
            self.accuracy = 0.0
            self.precision = 0.0
            self.recall = 0.0
            self.f1_score = 0.0
            self.id_switch_rate = 0.0
            self.evaluation_frames = 0
        def update(self, current_objects, ground_truth=None):
            self.evaluation_frames += 1
            self.prev_ids = self.current_ids.copy()
            self.current_ids = {obj.id for obj in current_objects}
            for obj_id in self.current_ids:
                if obj_id in self.prev_ids:
                    continue
                else:
                    for prev_id in self.prev_ids:
                        if prev_id not in self.current_ids:
                            self.id_switches += 1
                            break
            if ground_truth is not None:
                pass
        def calculate_metrics(self):
            if self.evaluation_frames == 0:
                return
            self.id_switch_rate = self.id_switches / self.evaluation_frames
            if self.true_positives + self.false_positives > 0:
                self.precision = self.true_positives / (self.true_positives + self.false_positives)
            else:
                self.precision = 0.0
            if self.true_positives + self.false_negatives > 0:
                self.recall = self.true_positives / (self.true_positives + self.false_negatives)
            else:
                self.recall = 0.0
            if self.precision + self.recall > 0:
                self.f1_score = 2 * (self.precision * self.recall) / (self.precision + self.recall)
            else:
                self.f1_score = 0.0
        def plot_confusion_matrix(self, save_path=None):
            if self.confusion_matrix is not None:
                plt.figure(figsize=(10, 8))
                sns.heatmap(self.confusion_matrix, annot=True, fmt='d', cmap='Blues')
                plt.title('Tracking Confusion Matrix')
                plt.xlabel('Predicted ID')
                plt.ylabel('True ID')
                if save_path and True:
                    plt.savefig(save_path)
                    print(f"Confusion matrix saved to {save_path}")
                else:
                    plt.show()
        def print_metrics(self):
            print("\n" + "="*50)
            print("TRACKING PERFORMANCE METRICS:")
            print("="*50)
            print(f"True Positives: {self.true_positives}")
            print(f"False Positives: {self.false_positives}")
            print(f"False Negatives: {self.false_negatives}")
            print(f"ID Switches: {self.id_switches}")
            print(f"ID Switch Rate: {self.id_switch_rate:.4f}")
            print(f"Precision: {self.precision:.4f}")
            print(f"Recall: {self.recall:.4f}")
            print(f"F1 Score: {self.f1_score:.4f}")
            print("="*50 + "\n")

    def match_and_assign_ids_embedding_only(self, current_boxes, prev_objects, frame, object_memory, tracking_metrics, frame_stats):
        assigned_ids = []
        matched_prev_ids = set()
        matched_current_indices = set()
        current_embeddings = []
        for box in current_boxes:
            if frame is not None:
                embedding = self.extract_embedding(frame, box)
                current_embeddings.append(embedding)
            else:
                current_embeddings.append(None)
        for prev_idx, prev_obj in enumerate(prev_objects):
            if prev_idx in matched_prev_ids:
                continue
            best_similarity = -1
            best_match_idx = -1
            for cur_idx, cur_embedding in enumerate(current_embeddings):
                if cur_idx in matched_current_indices:
                    continue
                embedding_sim = 0.0
                if cur_embedding is not None and prev_obj.embedding is not None:
                    embedding_sim = self.calculate_embedding_similarity(cur_embedding, prev_obj.embedding)
                if embedding_sim > best_similarity:
                    best_similarity = embedding_sim
                    best_match_idx = cur_idx
            if best_similarity >= self.EMBEDDING_SIMILARITY_THRESHOLD and best_match_idx != -1:
                if best_match_idx in matched_current_indices:
                    for i, (prev_id, _, _) in enumerate(assigned_ids):
                        if prev_id == prev_objects[best_match_idx].id:
                            if best_similarity > embedding_sim:
                                assigned_ids[i] = (prev_obj.id, current_boxes[best_match_idx], current_embeddings[best_match_idx] if frame is not None else None)
                                matched_prev_ids.add(prev_idx)
                            break
                else:
                    assigned_ids.append((prev_obj.id, current_boxes[best_match_idx], current_embeddings[best_match_idx] if frame is not None else None))
                    matched_prev_ids.add(prev_idx)
                    matched_current_indices.add(best_match_idx)
            else:
                object_memory.add_disappeared(prev_obj)
        for cur_idx, cur_embedding in enumerate(current_embeddings):
            if cur_idx in matched_current_indices:
                continue
            memory_match, memory_similarity = object_memory.find_match(cur_embedding, self.MEMORY_EMBEDDING_THRESHOLD)
            if memory_match is not None:
                assigned_ids.append((memory_match.id, current_boxes[cur_idx], current_embeddings[cur_idx] if frame is not None else None))
                matched_current_indices.add(cur_idx)
                del object_memory.objects[memory_match.id]
        for cur_idx, cur_embedding in enumerate(current_embeddings):
            if cur_idx not in matched_current_indices:
                new_id = object_memory.get_next_id()
                assigned_ids.append((new_id, current_boxes[cur_idx], current_embeddings[cur_idx] if frame is not None else None))
        current_objects = [self.TrackedObject(obj_id, bbox, object_memory.frame_count, embedding) for obj_id, bbox, embedding in assigned_ids]
        object_memory.update(current_objects)
        tracking_metrics.update(current_objects)
        if frame_stats.frame_count % self.EVALUATION_INTERVAL == 0:
            tracking_metrics.calculate_metrics()
            tracking_metrics.print_metrics()
            if self.SAVE_EVALUATION_PLOTS:
                tracking_metrics.plot_confusion_matrix(f"confusion_matrix_{frame_stats.frame_count}.png")
        return current_objects

    def run(self, rtsp_url):
        frame_queue = Queue(maxsize=2)
        frame_stats = self.FrameStats(self.FRAME_HISTORY_SIZE, self.SKIP_THRESHOLD)
        object_memory = self.ObjectMemory(self.MEMORY_DURATION, self.calculate_embedding_similarity)
        tracking_metrics = self.TrackingMetrics()
        def load_frames():
            try:
                cap = cv2.VideoCapture(rtsp_url)
                if not cap.isOpened():
                    raise ValueError("Could not open video stream. Check the RTSP URL or credentials.")
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                print("Video stream opened successfully.")
            except Exception as e:
                print(f"Error opening RTSP stream: {e}")
                return
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    if not frame_queue.full():
                        frame_queue.put((frame, time.time()))
                    else:
                        continue
                else:
                    print("Failed to read frame from stream.")
            cap.release()
        def process_frames():
            prev_objects = []
            cv2.namedWindow("Person Tracking (Embedding-Only)", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Person Tracking (Embedding-Only)", 1280, 720)
            print("Starting embedding-only frame processing...")
            while True:
                try:
                    if not frame_queue.empty():
                        frame, frame_time = frame_queue.get()
                        frame_stats.update(frame_time)
                        display_frame = frame.copy()
                        process_start = time.time()
                        results = self.model.predict(
                            source=frame,
                            verbose=False,
                            conf=0.5,
                            iou=0.5,
                            imgsz=(1280, 720)
                        )[0]
                        person_boxes = []
                        if results.boxes is not None:
                            for i, result in enumerate(results.boxes.data):
                                x1, y1, x2, y2 = map(int, result[:4])
                                conf = result[4].item()
                                class_id = int(result[5])
                                if class_id == self.PERSON_CLASS_ID and conf > 0.5:
                                    bbox = (x1, y1, x2, y2)
                                    person_boxes.append(bbox)
                        if person_boxes:
                            current_objects = self.match_and_assign_ids_embedding_only(person_boxes, prev_objects, frame, object_memory, tracking_metrics, frame_stats)
                            prev_objects = current_objects
                            for obj in current_objects:
                                x1, y1, x2, y2 = obj.bbox
                                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cx, cy = obj.centroid
                                cv2.circle(display_frame, (cx, cy), 5, (0, 0, 255), -1)
                                label = f"ID: {obj.id}"
                                cv2.putText(display_frame, label, (x1, y1 - 10),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                            process_time = time.time() - process_start
                            frame_stats.update_processing_time(process_time)
                            if frame_stats.should_print_stats():
                                print("\n" + "="*50)
                                print(frame_stats.get_stats())
                                print("="*50 + "\n")
                            cv2.imshow("Person Tracking (Embedding-Only)", display_frame)
                            key = cv2.waitKey(1) & 0xFF
                            if key == ord('q'):
                                print("\nQuitting program...")
                                cv2.destroyAllWindows()
                                tracking_metrics.calculate_metrics()
                                tracking_metrics.print_metrics()
                                return
                except Exception as e:
                    print(f"Error in processing frames: {e}")
                    continue
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_load = executor.submit(load_frames)
            future_process = executor.submit(process_frames)
            future_process.result()
            future_load.cancel()
        print("Program terminated successfully.") 