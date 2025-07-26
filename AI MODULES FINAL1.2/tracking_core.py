import cv2
import numpy as np
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image
from ultralytics import YOLO

# --- Tracking parameters ---
PERSON_CLASS_ID = 0
EMBEDDING_SIMILARITY_THRESHOLD = 0.88
MEMORY_DURATION = 250
MEMORY_EMBEDDING_THRESHOLD = 0.80
MIN_EMBEDDING_SIMILARITY = 0.75

# --- Model paths ---
DETECTION_MODEL_PATH = "person_detect_yolov11.pt"
TRACKING_MODEL_PATH = "yolo11n-seg.pt"

# --- Load YOLO models ---
detection_yolo_model = YOLO(DETECTION_MODEL_PATH, verbose=False)
tracking_yolo_model = YOLO(TRACKING_MODEL_PATH, verbose=False)

# --- Load ResNet18 for embeddings ---
embedding_model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
embedding_model = torch.nn.Sequential(*list(embedding_model.children())[:-1])
embedding_model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
embedding_model = embedding_model.to(device)

# Image preprocessing for embedding extraction
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_embedding(frame, bbox):
    try:
        x1, y1, x2, y2 = map(int, bbox)
        person_region = frame[y1:y2, x1:x2]
        person_image = Image.fromarray(cv2.cvtColor(person_region, cv2.COLOR_BGR2RGB))
        input_tensor = preprocess(person_image)
        input_batch = input_tensor.unsqueeze(0).to(device)
        with torch.no_grad():
            embedding = embedding_model(input_batch)
            embedding = embedding.squeeze().cpu().numpy()
        embedding = embedding / np.linalg.norm(embedding)  # Normalize embedding
        return embedding
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        return None

def calculate_embedding_similarity(embedding1, embedding2):
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
    def __init__(self, max_age=MEMORY_DURATION):
        self.objects = {}
        self.max_age = max_age
        self.frame_count = 0
        self.used_ids = set()
        self.id_counter = 0

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

    def find_match(self, embedding):
        if embedding is None:
            return None, -1
        embedding = embedding / np.linalg.norm(embedding)  # Normalize incoming embedding
        best_score = -1
        best_match = None
        for obj_id, obj in self.objects.items():
            if obj.disappeared_frames > self.max_age:
                continue
            if len(obj.embedding_history) < 2:
                continue
            if self.frame_count - obj.last_seen > 150:
                continue
            avg_embedding = np.mean(obj.embedding_history, axis=0)
            avg_embedding /= np.linalg.norm(avg_embedding)
            similarity = calculate_embedding_similarity(embedding, avg_embedding)
            print(f"[DEBUG] ID {obj.id} — Avg similarity: {similarity:.3f} — Last seen: {obj.last_seen}")
            if similarity > best_score and similarity >= MEMORY_EMBEDDING_THRESHOLD:
                best_score = similarity
                best_match = obj
        if best_match is not None:
            print(f"[DEBUG] Best memory match: obj_id={best_match.id}, similarity={best_score:.3f}")
        else:
            print("[DEBUG] No suitable memory match found.")
        return best_match, best_score

    def get_next_id(self):
        while self.id_counter in self.used_ids:
            self.id_counter += 1
        new_id = self.id_counter
        self.id_counter += 1
        return new_id

def match_and_assign_ids_embedding_only(current_boxes, prev_objects, frame, object_memory):
    assigned_ids = []
    matched_prev_ids = set()
    matched_current_indices = set()
    current_embeddings = []
    for box in current_boxes:
        if frame is not None:
            embedding = extract_embedding(frame, box)
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
                embedding_sim = calculate_embedding_similarity(cur_embedding, prev_obj.embedding)
            if embedding_sim > best_similarity:
                best_similarity = embedding_sim
                best_match_idx = cur_idx
        if best_similarity >= EMBEDDING_SIMILARITY_THRESHOLD and best_match_idx != -1:
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
    # Try to match remaining current objects with memory
    for cur_idx, cur_embedding in enumerate(current_embeddings):
        if cur_idx in matched_current_indices:
            continue
        memory_match, memory_similarity = object_memory.find_match(cur_embedding)
        if memory_match is not None:
            assigned_ids.append((memory_match.id, current_boxes[cur_idx], current_embeddings[cur_idx] if frame is not None else None))
            matched_current_indices.add(cur_idx)
            del object_memory.objects[memory_match.id]
    for cur_idx, cur_embedding in enumerate(current_embeddings):
        if cur_idx not in matched_current_indices:
            new_id = object_memory.get_next_id()
            assigned_ids.append((new_id, current_boxes[cur_idx], current_embeddings[cur_idx] if frame is not None else None))
    current_objects = [TrackedObject(obj_id, bbox, object_memory.frame_count, embedding) for obj_id, bbox, embedding in assigned_ids]
    object_memory.update(current_objects)
    return current_objects 