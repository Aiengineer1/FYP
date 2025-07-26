import threading
import time
import numpy as np

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

class GlobalPersonRegistry:
    def __init__(self, similarity_threshold=0.75, history_size=5):
        self.similarity_threshold = similarity_threshold
        self.history_size = history_size
        self.global_id_counter = 0
        self.registry = {}  # global_id: {'embeddings': [np.array], 'supervisor_camera': str, 'camera_names': set, 'last_seen': float}
        self.lock = threading.Lock()

    def match_embedding(self, embedding, camera_name, timestamp=None):
        with self.lock:
            best_id = None
            best_sim = self.similarity_threshold
            best_supervisor = None
            for global_id, info in self.registry.items():
                for hist_emb in info['embeddings']:
                    sim = calculate_embedding_similarity(embedding, hist_emb)
                    if sim > best_sim:
                        best_sim = sim
                        best_id = global_id
                        best_supervisor = info['supervisor_camera']
            if best_id is not None:
                print(f"[GlobalRegistry] Matched embedding to global_id={best_id} (supervisor={best_supervisor}) with sim={best_sim:.3f}")
                return best_id, best_supervisor
            return None, None

    def can_register(self, camera_name):
        # Only allow registration if this camera is not already a supervisor for any person
        for info in self.registry.values():
            if info['supervisor_camera'] == camera_name:
                return False
        return True

    def register_new(self, embedding, camera_name, timestamp=None):
        with self.lock:
            if not self.can_register(camera_name):
                print(f"[GlobalRegistry] Camera {camera_name} is not allowed to register a new global ID (already supervisor for another person).")
                return None
            global_id = self.global_id_counter
            self.global_id_counter += 1
            self.registry[global_id] = {
                'embeddings': [embedding],
                'supervisor_camera': camera_name,
                'camera_names': {camera_name},
                'last_seen': timestamp if timestamp is not None else time.time()
            }
            print(f"[GlobalRegistry] Registered new global_id={global_id} (supervisor={camera_name})")
            return global_id

    def update(self, global_id, embedding, camera_name, timestamp=None):
        with self.lock:
            if global_id in self.registry:
                emb_hist = self.registry[global_id]['embeddings']
                emb_hist.append(embedding)
                if len(emb_hist) > self.history_size:
                    emb_hist.pop(0)
                self.registry[global_id]['camera_names'].add(camera_name)
                self.registry[global_id]['last_seen'] = timestamp if timestamp is not None else time.time() 