# 🤖 AI Modules Integration Guide for Saim

## 📋 **Module Requirements**

You need to create **5 Python files** in this directory (`app/ai_solutions/modules/`):

### **1. person_detection.py**
```python
import cv2
import numpy as np
from typing import List, Dict

class PersonDetector:
    def __init__(self):
        """Initialize YOLOv11n model"""
        # Load your YOLOv11n model here
        pass
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect persons in frame
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            List of detections with format:
            [
                {
                    "bbox": [x, y, w, h],  # Bounding box coordinates
                    "confidence": 0.95     # Detection confidence
                },
                ...
            ]
        """
        # Your YOLOv11n detection logic here
        pass
```

### **2. age_gender.py**
```python
import cv2
import numpy as np

class AgeGenderEstimator:
    def __init__(self):
        """Initialize age/gender model"""
        # Load your model or use random generator
        pass
    
    def estimate(self, person_crop: np.ndarray) -> tuple:
        """
        Estimate age and gender from person crop
        
        Args:
            person_crop: Cropped person image
            
        Returns:
            tuple: (age: int, gender: str)
            Example: (25, "male") or (32, "female")
        """
        # Your age/gender estimation logic here
        # OR use random generator for demo:
        import random
        age = random.randint(18, 65)
        gender = random.choice(["male", "female"])
        return age, gender
```

### **3. trolley_detection.py**
```python
import cv2
import numpy as np
from typing import List

class TrolleyDetector:
    def __init__(self):
        """Initialize trolley detection logic"""
        pass
    
    def detect(self, bbox: List[float], frame: np.ndarray) -> bool:
        """
        Detect if person has trolley using rule-based logic
        
        Args:
            bbox: Person bounding box [x, y, w, h]
            frame: Full frame
            
        Returns:
            bool: True if person has trolley, False otherwise
        """
        # Rule-based trolley detection:
        # 1. Check area below person
        # 2. Look for rectangular shape
        # 3. Check aspect ratio
        
        x, y, w, h = bbox
        
        # Check region below person (trolley area)
        trolley_region = frame[int(y + h):int(y + h + 50), int(x):int(x + w)]
        
        # Simple rule: random for demo (replace with your logic)
        import random
        return random.choice([True, False])
```

### **4. tracking.py**
```python
import numpy as np
from typing import List, Dict

class CustomTracker:
    def __init__(self):
        """Initialize custom tracking pipeline"""
        self.tracks = {}
        self.next_id = 1
        # Your ResNet-18 or tracking logic here
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        Update tracks with new detections
        
        Args:
            detections: List of person detections
            
        Returns:
            List of tracked detections with person_id:
            [
                {
                    "bbox": [x, y, w, h],
                    "confidence": 0.95,
                    "person_id": "P001"  # Added tracking ID
                },
                ...
            ]
        """
        tracked_detections = []
        
        for detection in detections:
            # Your tracking logic here (centroid, correlation, etc.)
            
            # For demo, assign new IDs (replace with your logic)
            track_id = f"P{str(self.next_id).zfill(3)}"
            self.next_id += 1
            
            tracked_detection = detection.copy()
            tracked_detection["person_id"] = track_id
            tracked_detections.append(tracked_detection)
        
        return tracked_detections
```

### **5. homography.py**
```python
import cv2
import numpy as np
from typing import List

class HomographyMapper:
    def __init__(self, camera_id: int):
        """Initialize homography mapping for camera"""
        self.camera_id = camera_id
        
        # Load calibration data or use identity matrix
        self.homography_matrix = np.eye(3)  # Replace with actual calibration
    
    def map_to_world_coords(self, bbox: List[float]) -> List[float]:
        """
        Map camera coordinates to mall floor coordinates
        
        Args:
            bbox: Person bounding box [x, y, w, h]
            
        Returns:
            List[float]: [world_x, world_y] coordinates on mall map
        """
        # Get person foot position (center-bottom of bbox)
        x_center = bbox[0] + bbox[2] / 2
        y_foot = bbox[1] + bbox[3]
        
        # Apply homography transformation
        point = np.array([[x_center, y_foot]], dtype=np.float32)
        point = point.reshape(-1, 1, 2)
        
        # Transform using homography (replace with your matrix)
        world_point = cv2.perspectiveTransform(point, self.homography_matrix)
        
        world_x = float(world_point[0][0][0])
        world_y = float(world_point[0][0][1])
        
        return [world_x, world_y]
    
    def get_zone(self, world_coords: List[float]) -> str:
        """
        Determine which zone the person is in
        
        Args:
            world_coords: [world_x, world_y]
            
        Returns:
            str: Zone name ("electronics", "clothing", etc.)
        """
        # Zone assignment logic based on world coordinates
        x, y = world_coords
        
        # Simple grid-based zones (replace with your logic)
        if x < 50:
            return "electronics"
        elif x < 100:
            return "clothing" 
        elif x < 150:
            return "food_court"
        else:
            return "shoes"
```

## 🔧 **Integration Steps**

### **Step 1: Create Your Modules**
1. Create all 5 files in `app/ai_solutions/modules/`
2. Implement the classes with the exact signatures above
3. Test each module individually

### **Step 2: Update __init__.py**
Uncomment the imports in `app/ai_solutions/modules/__init__.py`:

```python
from .person_detection import PersonDetector
from .age_gender import AgeGenderEstimator
from .trolley_detection import TrolleyDetector
from .tracking import CustomTracker
from .homography import HomographyMapper

__all__ = [
    'PersonDetector',
    'AgeGenderEstimator',
    'TrolleyDetector',
    'CustomTracker',
    'HomographyMapper'
]
```

### **Step 3: Test Integration**
The system will automatically switch from mock modules to your real modules once they're available.

## 📊 **Data Flow**

Your modules will be called in this sequence:

```
Frame → PersonDetector.detect() 
     → CustomTracker.update() 
     → AgeGenderEstimator.estimate() 
     → TrolleyDetector.detect() 
     → HomographyMapper.map_to_world_coords() 
     → Database Logging
```

## 🚀 **Quick Start Tips**

1. **Start Simple**: Use random generators initially to test integration
2. **Test Individually**: Test each module with sample data first
3. **Check Formats**: Ensure your return formats match exactly
4. **Performance**: Aim for <100ms processing time per frame
5. **Error Handling**: Add try-catch blocks for robustness

## 📞 **Support**

If you need help with integration:
1. Check the mock implementations in `detection_pipeline.py`
2. Test with the existing mock data first
3. Ask Ghulam for backend integration support

## 🎯 **Success Criteria**

✅ All 5 modules created with correct signatures  
✅ Person detection working on live camera feed  
✅ Tracking IDs assigned consistently  
✅ Age/gender estimation (real or random)  
✅ Trolley detection logic implemented  
✅ Homography mapping functional  
✅ Integration tested end-to-end  

Good luck! 🚀 