import threading
import time
import numpy as np
import cv2 # Added for auto-detecting lighting

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
    def __init__(self, similarity_threshold=0.75, history_size=5, cleanup_interval=300):
        self.similarity_threshold = similarity_threshold
        self.history_size = history_size
        self.global_id_counter = 0
        self.registry = {}  # global_id: {'embeddings': [np.array], 'supervisor_camera': str, 'camera_names': set, 'last_seen': float}
        self.lock = threading.Lock()
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        
        # Dynamic threshold management
        self.camera_lighting_conditions = {}  # camera_name: lighting_condition
        self.camera_threshold_adjustments = {}  # camera_name: adjustment_factor
        self.base_threshold = similarity_threshold

    def set_camera_lighting_condition(self, camera_name, lighting_condition):
        """Set lighting condition for a specific camera"""
        with self.lock:
            self.camera_lighting_conditions[camera_name] = lighting_condition
            # Calculate adjustment factor based on lighting
            adjustment = self._calculate_lighting_adjustment(lighting_condition)
            self.camera_threshold_adjustments[camera_name] = adjustment
            print(f"[GlobalRegistry] Camera {camera_name} lighting set to '{lighting_condition}' (adjustment: {adjustment:+.3f})")

    def _calculate_lighting_adjustment(self, lighting_condition):
        """Calculate threshold adjustment based on lighting condition"""
        adjustments = {
            'dark': -0.15,      # Lower threshold for dark conditions
            'low_light': -0.10, # Lower threshold for low light
            'normal': 0.0,      # No adjustment for normal lighting
            'bright': 0.05,     # Slightly higher threshold for bright conditions
            'very_bright': 0.10, # Higher threshold for very bright conditions
            'backlit': -0.08,   # Lower threshold for backlit conditions
            'shadowed': -0.12   # Lower threshold for shadowed conditions
        }
        return adjustments.get(lighting_condition.lower(), 0.0)

    def get_adaptive_threshold(self, camera_name):
        """Get adaptive similarity threshold for a specific camera"""
        with self.lock:
            adjustment = self.camera_threshold_adjustments.get(camera_name, 0.0)
            adaptive_threshold = self.base_threshold + adjustment
            # Ensure threshold stays within reasonable bounds
            return max(0.5, min(0.95, adaptive_threshold))

    def match_embedding(self, embedding, camera_name, timestamp=None):
        with self.lock:
            # Periodic cleanup
            self._cleanup_old_persons()
            
            # Get adaptive threshold for this camera
            adaptive_threshold = self.get_adaptive_threshold(camera_name)
            
            best_id = None
            best_sim = adaptive_threshold
            best_supervisor = None
            
            for global_id, info in self.registry.items():
                for hist_emb in info['embeddings']:
                    sim = calculate_embedding_similarity(embedding, hist_emb)
                    if sim > best_sim:
                        best_sim = sim
                        best_id = global_id
                        best_supervisor = info['supervisor_camera']
                        
            if best_id is not None:
                print(f"[GlobalRegistry] Matched embedding to global_id={best_id} (supervisor={best_supervisor}) with sim={best_sim:.3f} (threshold={adaptive_threshold:.3f})")
                return best_id, best_supervisor
            return None, None

    def _get_available_supervisor(self):
        """Get the camera with the least number of supervised persons"""
        supervisor_counts = {}
        for info in self.registry.values():
            supervisor = info['supervisor_camera']
            supervisor_counts[supervisor] = supervisor_counts.get(supervisor, 0) + 1
        
        # If no supervisors exist, return None (first camera can register)
        if not supervisor_counts:
            return None
            
        # Return camera with least supervised persons
        return min(supervisor_counts, key=supervisor_counts.get)

    def can_register(self, camera_name):
        """Check if camera can register a new person (atomic operation)"""
        with self.lock:
            # Get the camera with least supervised persons
            best_supervisor = self._get_available_supervisor()
            
            # If this camera has the least supervised persons or no supervisors exist
            if best_supervisor is None or best_supervisor == camera_name:
                return True
                
            # Check if this camera is already supervising any person
            for info in self.registry.values():
                if info['supervisor_camera'] == camera_name:
                    return False
                    
            return True

    def register_new_atomic(self, embedding, camera_name, timestamp=None):
        """Atomic registration - check and register in single operation"""
        with self.lock:
            # Check if this camera can register
            if not self.can_register(camera_name):
                print(f"[GlobalRegistry] Camera {camera_name} cannot register new person (not optimal supervisor)")
                return None
                
            # Register the new person
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

    def register_new(self, embedding, camera_name, timestamp=None):
        """Legacy method - use register_new_atomic instead"""
        return self.register_new_atomic(embedding, camera_name, timestamp)

    def update(self, global_id, embedding, camera_name, timestamp=None):
        with self.lock:
            if global_id in self.registry:
                emb_hist = self.registry[global_id]['embeddings']
                emb_hist.append(embedding)
                if len(emb_hist) > self.history_size:
                    emb_hist.pop(0)
                self.registry[global_id]['camera_names'].add(camera_name)
                self.registry[global_id]['last_seen'] = timestamp if timestamp is not None else time.time()

    def _cleanup_old_persons(self, max_age_seconds=None):
        """Clean up old/inactive persons from registry"""
        if max_age_seconds is None:
            max_age_seconds = self.cleanup_interval
            
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
            
        to_remove = []
        for global_id, info in self.registry.items():
            if current_time - info['last_seen'] > max_age_seconds:
                to_remove.append(global_id)
                
        for global_id in to_remove:
            del self.registry[global_id]
            print(f"[GlobalRegistry] Cleaned up inactive global_id={global_id}")
            
        self.last_cleanup = current_time

    def get_registry_stats(self):
        """Get statistics about the registry"""
        with self.lock:
            total_persons = len(self.registry)
            supervisor_counts = {}
            for info in self.registry.values():
                supervisor = info['supervisor_camera']
                supervisor_counts[supervisor] = supervisor_counts.get(supervisor, 0) + 1
            return {
                'total_persons': total_persons,
                'supervisor_distribution': supervisor_counts,
                'last_cleanup': self.last_cleanup,
                'lighting_conditions': self.camera_lighting_conditions.copy(),
                'threshold_adjustments': self.camera_threshold_adjustments.copy()
            }

    def auto_detect_lighting(self, camera_name, frame):
        """Automatically detect lighting condition from frame"""
        try:
            # Convert to grayscale for brightness analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate brightness statistics
            mean_brightness = np.mean(gray)
            std_brightness = np.std(gray)
            
            # Determine lighting condition based on brightness
            if mean_brightness < 50:
                condition = 'dark'
            elif mean_brightness < 80:
                condition = 'low_light'
            elif mean_brightness < 120:
                condition = 'normal'
            elif mean_brightness < 160:
                condition = 'bright'
            else:
                condition = 'very_bright'
                
            # Adjust based on standard deviation (contrast)
            if std_brightness < 20:
                condition = 'low_contrast'
            elif std_brightness > 60:
                condition = 'high_contrast'
                
            self.set_camera_lighting_condition(camera_name, condition)
            return condition
            
        except Exception as e:
            print(f"[GlobalRegistry] Error auto-detecting lighting for {camera_name}: {e}")
            return 'normal'  # Default fallback 