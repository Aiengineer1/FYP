#!/usr/bin/env python3
"""
Simple Test Script for AI Modules System
Tests basic configuration and imports
"""

import os
import sys

def test_configuration():
    """Test basic configuration"""
    print("=== AI Modules System Test ===\n")
    
    # Test configuration import
    try:
        from config.config import config
        print("Testing configuration...")
        print(f"Available cameras: {list(config.CAMERA_MAPPINGS.keys())}")
        print(f"Camera mappings: {config.CAMERA_MAPPINGS}")
        
        # Check mapping files
        for cam_name, mapping_file in config.CAMERA_MAPPINGS.items():
            if os.path.exists(mapping_file):
                print(f"✅ {cam_name}: {mapping_file} - EXISTS")
            else:
                print(f"❌ {cam_name}: {mapping_file} - MISSING")
        
        print()
        
        # Check model files
        print("Checking model files...")
        model_files = [
            "person_detect_yolov11.pt",
            "yolo11n-seg.pt", 
            "yolov11n-face.pt",
            "ResNet-18 Age 0.60 + Gender 93.pt"
        ]
        
        for model_file in model_files:
            if os.path.exists(model_file):
                size_mb = os.path.getsize(model_file) / (1024 * 1024)
                print(f"✅ {model_file} - EXISTS ({size_mb:.1f} MB)")
            else:
                print(f"❌ {model_file} - MISSING")
        
        print()
        
        # Check floorplan
        floorplan = "floorplan_gui.png"
        print(f"Floorplan: {floorplan}")
        if os.path.exists(floorplan):
            print(f"✅ Floorplan exists")
        else:
            print(f"❌ Floorplan missing")
        
        print()
        
        # Test imports
        print("Testing imports...")
        try:
            from core.registry import GlobalPersonRegistry
            print("✅ GlobalPersonRegistry imported")
        except ImportError as e:
            print(f"❌ GlobalPersonRegistry import failed: {e}")
        
        try:
            from core.zone_utils import load_global_zone_from_json
            print("✅ zone_utils imported")
        except ImportError as e:
            print(f"❌ zone_utils import failed: {e}")
        
        try:
            from core.tracking_core import tracking_yolo_model
            print("✅ tracking_core imported")
        except ImportError as e:
            print(f"❌ tracking_core import failed: {e}")
        
        print("\n=== Test Complete ===")
        
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_configuration()