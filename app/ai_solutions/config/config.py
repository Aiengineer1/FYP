"""
Configuration file for AI Modules Final Year Project
Multi-Camera Person Tracking and Analytics System
"""

import os
from typing import Dict, Any

class Config:
    """Central configuration class for the AI tracking system"""
    
    # ===== CAMERA CONFIGURATION =====
    CAMERA_MAPPINGS = {
        'cam1': 'homography_mappings_cam1.json',
        'cam2': 'homography_mappings_cam2.json',
        'cam3': 'homography_mappings_cam3.json',
        'cam4': 'homography_mappings_cam4.json',
    }
    
    CAMERA_RTSP = {
        'cam1': 'rtsp://admin:admin1234@192.168.0.2:554/cam/realmonitor?channel=1&subtype=0',
        'cam2': 'rtsp://admin:admin1234@192.168.0.3:554/cam/realmonitor?channel=1&subtype=0',
        'cam3': 'rtsp://admin:admin1234@192.168.0.4:554/cam/realmonitor?channel=1&subtype=0',
        'cam4': 'rtsp://admin:admin1234@192.168.0.5:554/cam/realmonitor?channel=1&subtype=0',
    }
    
    CAMERA_OFFSETS = {
        'cam1': {'x_offset': 250, 'y_offset': -120},
        'cam2': {'x_offset': 0, 'y_offset': -200},
        'cam3': {'x_offset': 0, 'y_offset': 0},
        'cam4': {'x_offset': -50, 'y_offset': 150},
    }
    
    CAMERA_NUM_TO_NAME = {'1': 'cam1', '2': 'cam2', '3': 'cam3', '4': 'cam4'}
    
    # ===== MODEL PATHS =====
    MODEL_PATHS = {
        'person_detection': os.path.join(os.path.dirname(__file__), "..", "ml_models", "detection", "person_detect_yolov11.pt"),
        'segmentation': os.path.join(os.path.dirname(__file__), "..", "ml_models", "segmentation", "yolo11n-seg.pt"),
        'face_detection': os.path.join(os.path.dirname(__file__), "..", "ml_models", "face_recognition", "yolov11n-face.pt"),
        'age_gender': os.path.join(os.path.dirname(__file__), "..", "ml_models", "age_gender", "ResNet-18 Age 0.60 + Gender 93.pt")
    }
    
    # ===== TRACKING PARAMETERS =====
    TRACKING = {
        'person_class_id': 0,
        'embedding_similarity_threshold': 0.88,
        'memory_duration': 250,
        'memory_embedding_threshold': 0.80,
        'min_embedding_similarity': 0.75,
        'fps_log_interval': 30,
        'age_gender_skip': 5,  # Only run age/gender every N frames
    }
    
    # ===== REGISTRY PARAMETERS =====
    REGISTRY = {
        'similarity_threshold': 0.75,
        'history_size': 5,
        'cleanup_interval': 300,  # seconds
    }
    
    # ===== ZONE ANALYSIS PARAMETERS =====
    ZONE_ANALYSIS = {
        'min_overlap_area': 100.0,
        'min_overlap_percent': 0.05,
        'proximity_threshold': 100,  # pixels for interaction detection
    }
    
    # ===== PERFORMANCE MONITORING =====
    PERFORMANCE = {
        'stats_update_interval': 10,  # seconds
        'fps_history_size': 100,
        'performance_report_file': 'performance_report.json',
    }
    
    # ===== VISUALIZATION SETTINGS =====
    VISUALIZATION = {
        'frame_size': (1280, 720),
        'heatmap_blur_sigma': 25,
        'overlay_alpha': 0.4,
        'route_line_thickness': 2,
        'person_bbox_thickness': 2,
        'zone_overlay_alpha': 0.3,
    }
    
    # ===== FILE PATHS =====
    PATHS = {
        'floorplan_default': 'assets/floorplan_gui.png',
        'selected_map_file': 'config/selected_lab_map.txt',
        'output_dir': 'analytics',
    }
    
    # ===== LIGHTING CONDITIONS =====
    LIGHTING_ADJUSTMENTS = {
        'dark': -0.15,
        'low_light': -0.10,
        'normal': 0.0,
        'bright': 0.05,
        'very_bright': 0.10,
        'backlit': -0.08,
        'shadowed': -0.12,
        'low_contrast': -0.05,
        'high_contrast': 0.03,
    }
    
    # ===== AGE GROUPS =====
    AGE_GROUPS = ['00-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
    
    # ===== LOGGING =====
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'ai_modules.log',
    }
    
    @classmethod
    def get_camera_config(cls, camera_name: str) -> Dict[str, Any]:
        """Get complete configuration for a specific camera"""
        return {
            'name': camera_name,
            'rtsp_url': cls.CAMERA_RTSP.get(camera_name),
            'mapping_file': cls.CAMERA_MAPPINGS.get(camera_name),
            'offset': cls.CAMERA_OFFSETS.get(camera_name, {'x_offset': 0, 'y_offset': 0}),
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate the configuration and return True if valid"""
        errors = []
        
        # Check if model files exist
        for model_name, model_path in cls.MODEL_PATHS.items():
            if not os.path.exists(model_path):
                errors.append(f"Model file not found: {model_path}")
        
        # Check if mapping files exist
        for camera_name, mapping_file in cls.CAMERA_MAPPINGS.items():
            if not os.path.exists(mapping_file):
                errors.append(f"Mapping file not found for {camera_name}: {mapping_file}")
        
        # Check if floorplan exists
        if not os.path.exists(cls.PATHS['floorplan_default']):
            errors.append(f"Default floorplan not found: {cls.PATHS['floorplan_default']}")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def print_config_summary(cls):
        """Print a summary of the current configuration"""
        print("=" * 60)
        print("AI MODULES CONFIGURATION SUMMARY")
        print("=" * 60)
        print(f"Cameras configured: {len(cls.CAMERA_MAPPINGS)}")
        print(f"Models available: {len(cls.MODEL_PATHS)}")
        print(f"Registry similarity threshold: {cls.REGISTRY['similarity_threshold']}")
        print(f"Tracking memory duration: {cls.TRACKING['memory_duration']} frames")
        print(f"Performance monitoring: {cls.PERFORMANCE['stats_update_interval']}s interval")
        print("=" * 60)

# Environment-specific overrides
class DevelopmentConfig(Config):
    """Development environment configuration"""
    LOGGING = {
        'level': 'DEBUG',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'ai_modules_dev.log',
    }
    PERFORMANCE = {
        'stats_update_interval': 5,  # More frequent updates in dev
        'fps_history_size': 50,
        'performance_report_file': 'performance_report_dev.json',
    }

class ProductionConfig(Config):
    """Production environment configuration"""
    LOGGING = {
        'level': 'WARNING',
        'format': '%(asctime)s - %(levelname)s - %(message)s',
        'file': 'ai_modules_prod.log',
    }
    PERFORMANCE = {
        'stats_update_interval': 30,  # Less frequent updates in prod
        'fps_history_size': 200,
        'performance_report_file': 'performance_report_prod.json',
    }

# Configuration factory
def get_config(environment: str = 'development') -> Config:
    """Get configuration based on environment"""
    if environment.lower() == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()

# Default configuration instance
config = get_config() 