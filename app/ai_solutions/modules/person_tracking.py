"""
Person Tracking Module for AI Solutions
Provides person detection and tracking functionality
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class PersonTracker:
    """Person detection and tracking system"""
    
    def __init__(self, camera_id: int, camera_name: str):
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.is_active = False
        self.detection_count = 0
        self.tracked_persons = {}
        self.last_detection = None
        self.stats = {
            "total_detections": 0,
            "active_tracks": 0,
            "frames_processed": 0,
            "start_time": None
        }
    
    def start_tracking(self):
        """Start person tracking"""
        try:
            self.is_active = True
            self.stats["start_time"] = datetime.utcnow()
            logger.info(f"Started person tracking for camera {self.camera_name}")
            return True
        except Exception as e:
            logger.error(f"Error starting person tracking for {self.camera_name}: {str(e)}")
            return False
    
    def stop_tracking(self):
        """Stop person tracking"""
        try:
            self.is_active = False
            logger.info(f"Stopped person tracking for camera {self.camera_name}")
            return True
        except Exception as e:
            logger.error(f"Error stopping person tracking for {self.camera_name}: {str(e)}")
            return False
    
    def process_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Process a frame and detect/track persons"""
        if not self.is_active:
            return []
        
        try:
            self.stats["frames_processed"] += 1
            
            # Mock person detection (in real implementation, this would use YOLO or similar)
            detections = self._mock_detect_persons(frame)
            
            # Update tracking
            self._update_tracking(detections)
            
            # Update stats
            self.stats["total_detections"] += len(detections)
            self.stats["active_tracks"] = len(self.tracked_persons)
            
            if detections:
                self.last_detection = datetime.utcnow()
            
            return detections
            
        except Exception as e:
            logger.error(f"Error processing frame for {self.camera_name}: {str(e)}")
            return []
    
    def _mock_detect_persons(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Mock person detection (replace with real YOLO detection)"""
        # Simulate detections based on frame size
        height, width = frame.shape[:2]
        
        detections = []
        num_persons = np.random.randint(0, 4)  # 0-3 persons per frame
        
        for i in range(num_persons):
            # Generate random bounding box
            x1 = np.random.randint(0, width - 100)
            y1 = np.random.randint(0, height - 200)
            x2 = x1 + np.random.randint(50, 100)
            y2 = y1 + np.random.randint(100, 200)
            
            # Generate random confidence
            confidence = np.random.uniform(0.7, 0.95)
            
            # Generate random person ID
            person_id = f"person_{self.camera_id}_{i}_{self.stats['frames_processed']}"
            
            detection = {
                "person_id": person_id,
                "bbox": [x1, y1, x2, y2],
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat(),
                "camera_id": self.camera_id
            }
            
            detections.append(detection)
        
        return detections
    
    def _update_tracking(self, detections: List[Dict[str, Any]]):
        """Update person tracking"""
        current_time = datetime.utcnow()
        
        # Update existing tracks
        for person_id in list(self.tracked_persons.keys()):
            track = self.tracked_persons[person_id]
            
            # Check if person is still detected
            found = False
            for detection in detections:
                if detection["person_id"] == person_id:
                    track["last_seen"] = current_time
                    track["bbox"] = detection["bbox"]
                    track["confidence"] = detection["confidence"]
                    found = True
                    break
            
            # Remove old tracks (not seen for 5 seconds)
            if not found and (current_time - track["last_seen"]).total_seconds() > 5:
                del self.tracked_persons[person_id]
        
        # Add new tracks
        for detection in detections:
            person_id = detection["person_id"]
            if person_id not in self.tracked_persons:
                self.tracked_persons[person_id] = {
                    "person_id": person_id,
                    "first_seen": current_time,
                    "last_seen": current_time,
                    "bbox": detection["bbox"],
                    "confidence": detection["confidence"],
                    "track_duration": 0
                }
    
    def get_tracking_status(self) -> Dict[str, Any]:
        """Get current tracking status"""
        return {
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "is_active": self.is_active,
            "last_detection": self.last_detection.isoformat() if self.last_detection else None,
            "active_tracks": len(self.tracked_persons),
            "stats": self.stats.copy(),
            "tracked_persons": list(self.tracked_persons.keys())
        }
    
    def get_person_tracks(self) -> List[Dict[str, Any]]:
        """Get all current person tracks"""
        return list(self.tracked_persons.values())
    
    def get_person_track(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Get specific person track"""
        return self.tracked_persons.get(person_id) 