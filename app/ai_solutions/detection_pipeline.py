"""
Detection Pipeline for Mall Analytics System

This module integrates all AI detection components:
- Person detection (YOLOv11n)
- Age/Gender estimation
- Custom tracking
- Homography mapping
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import cv2
import numpy as np

# Import Saim's modules (will be available soon)
try:
    from .modules.person_detection import PersonDetector
    from .modules.age_gender import AgeGenderEstimator
    from .modules.tracking import CustomTracker
    from .modules.homography import HomographyMapper
except ImportError:
    # Fallback classes until Saim's modules are ready
    PersonDetector = None
    AgeGenderEstimator = None
    CustomTracker = None
    HomographyMapper = None

logger = logging.getLogger(__name__)

class DetectionResult:
    """Structured detection result"""
    def __init__(self, frame_id: int, timestamp: datetime, camera_id: int, mall_id: int):
        self.frame_id = frame_id
        self.timestamp = timestamp
        self.camera_id = camera_id
        self.mall_id = mall_id
        self.detections: List[Dict] = []
    
    def add_detection(self, person_id: str, bbox: List[float], age: int, 
                     gender: str, zone: str, 
                     world_coords: List[float], confidence: float = 0.95):
        """Add a detection to the result"""
        detection = {
            "person_id": person_id,
            "bbox": bbox,  # [x, y, w, h]
            "confidence": confidence,
            "age": age,
            "gender": gender,
            "zone": zone,
            "world_coords": world_coords  # [x_mall, y_mall]
        }
        self.detections.append(detection)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp.isoformat(),
            "camera_id": self.camera_id,
            "mall_id": self.mall_id,
            "detections": self.detections
        }

class MockDetectionModules:
    """Mock detection modules for development until Saim's modules are ready"""
    
    class MockPersonDetector:
        def __init__(self):
            self.frame_count = 0
        
        def detect(self, frame: np.ndarray) -> List[Dict]:
            """Mock person detection"""
            self.frame_count += 1
            # Generate 1-3 mock detections
            import random
            num_detections = random.randint(1, 3)
            detections = []
            
            for i in range(num_detections):
                x = random.randint(50, 400)
                y = random.randint(50, 300)
                w = random.randint(80, 120)
                h = random.randint(150, 200)
                
                detections.append({
                    "bbox": [x, y, w, h],
                    "confidence": random.uniform(0.85, 0.99)
                })
            
            return detections
    
    class MockAgeGenderEstimator:
        def estimate(self, person_crop: np.ndarray) -> tuple:
            """Mock age/gender estimation"""
            import random
            age = random.randint(18, 65)
            gender = random.choice(["male", "female"])
            return age, gender
    
    class MockCustomTracker:
        def __init__(self):
            self.tracks = {}
            self.next_id = 1
        
        def update(self, detections: List[Dict]) -> List[Dict]:
            """Mock tracking update"""
            tracked_detections = []
            
            for detection in detections:
                # Simple mock tracking - assign IDs
                track_id = f"P{str(self.next_id).zfill(3)}"
                self.next_id += 1
                
                tracked_detection = detection.copy()
                tracked_detection["person_id"] = track_id
                tracked_detections.append(tracked_detection)
            
            return tracked_detections
    
    class MockHomographyMapper:
        def __init__(self, camera_id: int):
            self.camera_id = camera_id
            # Mock homography matrix (identity for now)
            self.homography_matrix = np.eye(3)
        
        def map_to_world_coords(self, bbox: List[float]) -> List[float]:
            """Mock coordinate mapping"""
            # Simple mapping: center of bbox
            x_center = bbox[0] + bbox[2] / 2
            y_center = bbox[1] + bbox[3] / 2
            
            # Mock world coordinates
            world_x = x_center * 0.1  # Scale factor
            world_y = y_center * 0.1
            
            return [world_x, world_y]
        
        def get_zone(self, world_coords: List[float]) -> str:
            """Mock zone assignment"""
            import random
            zones = ["electronics", "clothing", "food_court", "entrance", "exit"]
            return random.choice(zones)

class DetectionPipeline:
    """Main detection pipeline integrating all AI modules"""
    
    def __init__(self, camera_id: int, mall_id: int):
        self.camera_id = camera_id
        self.mall_id = mall_id
        self.frame_count = 0
        
        # Initialize AI modules (use Saim's when available, otherwise mock)
        self._initialize_modules()
        
        logger.info(f"Detection pipeline initialized for camera {camera_id}, mall {mall_id}")
    
    def _initialize_modules(self):
        """Initialize AI detection modules"""
        if PersonDetector is not None:
            # Use Saim's actual modules
            self.person_detector = PersonDetector()
            self.age_gender_estimator = AgeGenderEstimator()
            self.tracker = CustomTracker()
            self.homography_mapper = HomographyMapper(self.camera_id)
            logger.info("Using Saim's AI modules")
        else:
            # Use mock modules for development
            mock = MockDetectionModules()
            self.person_detector = mock.MockPersonDetector()
            self.age_gender_estimator = mock.MockAgeGenderEstimator()
            self.tracker = mock.MockCustomTracker()
            self.homography_mapper = mock.MockHomographyMapper(self.camera_id)
            logger.info("Using mock AI modules for development")
    
    async def process_frame(self, frame: np.ndarray) -> DetectionResult:
        """
        Process a single frame through the complete AI pipeline
        
        Pipeline: Frame → Detection → Tracking → Metadata → Mapping
        """
        self.frame_count += 1
        timestamp = datetime.utcnow()
        
        # Create result container
        result = DetectionResult(
            frame_id=self.frame_count,
            timestamp=timestamp,
            camera_id=self.camera_id,
            mall_id=self.mall_id
        )
        
        try:
            # Step 1: Person Detection (YOLOv11n)
            detections = self.person_detector.detect(frame)
            
            if not detections:
                logger.debug(f"No persons detected in frame {self.frame_count}")
                return result
            
            # Step 2: Tracking Update
            tracked_detections = self.tracker.update(detections)
            
            # Step 3: Process each tracked person
            for detection in tracked_detections:
                bbox = detection["bbox"]
                person_id = detection.get("person_id", f"P{self.frame_count}")
                
                # Extract person crop for age/gender estimation
                x, y, w, h = bbox
                person_crop = frame[int(y):int(y+h), int(x):int(x+w)]
                
                # Step 4: Age/Gender Estimation
                age, gender = self.age_gender_estimator.estimate(person_crop)
                
                # Step 5: Homography Mapping
                world_coords = self.homography_mapper.map_to_world_coords(bbox)
                zone = self.homography_mapper.get_zone(world_coords)
                
                # Add to result
                result.add_detection(
                    person_id=person_id,
                    bbox=bbox,
                    age=age,
                    gender=gender,
                    zone=zone,
                    world_coords=world_coords,
                    confidence=detection.get("confidence", 0.95)
                )
            
            logger.debug(f"Processed frame {self.frame_count}: {len(result.detections)} detections")
            
        except Exception as e:
            logger.error(f"Error processing frame {self.frame_count}: {str(e)}")
        
        return result
    
    def get_pipeline_status(self) -> Dict:
        """Get pipeline status and statistics"""
        return {
            "camera_id": self.camera_id,
            "mall_id": self.mall_id,
            "frames_processed": self.frame_count,
            "status": "active",
            "modules": {
                "person_detector": "active",
                "age_gender_estimator": "active", 
                "tracker": "active",
                "homography_mapper": "active"
            }
        }
    
    async def cleanup(self):
        """Cleanup pipeline resources"""
        logger.info(f"Cleaning up detection pipeline for camera {self.camera_id}")
        # Add any cleanup logic here 