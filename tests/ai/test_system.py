#!/usr/bin/env python3
"""
Test script for AI Modules Final Year Project
Validates system components and provides diagnostic information
"""

import os
import sys
import json
import time
import cv2
import numpy as np
import torch
from config.config import config
from core.registry import GlobalPersonRegistry
from core.zone_utils import load_global_zone_from_json, analyze_camera_overlaps, validate_zone_configuration

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA device: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics YOLO imported successfully")
    except ImportError as e:
        print(f"❌ Ultralytics import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ Matplotlib imported successfully")
    except ImportError as e:
        print(f"❌ Matplotlib import failed: {e}")
        return False
    
    return True

def test_model_files():
    """Test if all required model files exist"""
    print("\n🔍 Testing model files...")
    
    all_exist = True
    for model_name, model_path in config.MODEL_PATHS.items():
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print(f"✅ {model_name}: {model_path} ({size_mb:.1f} MB)")
        else:
            print(f"❌ {model_name}: {model_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_mapping_files():
    """Test if camera mapping files exist and are valid JSON"""
    print("\n🔍 Testing camera mapping files...")
    
    all_valid = True
    for camera_name, mapping_file in config.CAMERA_MAPPINGS.items():
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r') as f:
                    data = json.load(f)
                
                # Check if global_zone exists
                has_global_zone = any(obj.get('name') == 'global_zone' for obj in data)
                if has_global_zone:
                    print(f"✅ {camera_name}: {mapping_file} (valid JSON, has global_zone)")
                else:
                    print(f"⚠️  {camera_name}: {mapping_file} (valid JSON, missing global_zone)")
                    all_valid = False
                    
            except json.JSONDecodeError as e:
                print(f"❌ {camera_name}: {mapping_file} - Invalid JSON: {e}")
                all_valid = False
        else:
            print(f"❌ {camera_name}: {mapping_file} - NOT FOUND")
            all_valid = False
    
    return all_valid

def test_floorplan():
    """Test if floorplan image exists and can be loaded"""
    print("\n🔍 Testing floorplan image...")
    
    floorplan_path = config.PATHS['floorplan_default']
    if os.path.exists(floorplan_path):
        try:
            img = cv2.imread(floorplan_path)
            if img is not None:
                height, width = img.shape[:2]
                print(f"✅ Floorplan: {floorplan_path} ({width}x{height} pixels)")
                return True
            else:
                print(f"❌ Floorplan: {floorplan_path} - Cannot load image")
                return False
        except Exception as e:
            print(f"❌ Floorplan: {floorplan_path} - Error loading: {e}")
            return False
    else:
        print(f"❌ Floorplan: {floorplan_path} - NOT FOUND")
        return False

def test_registry():
    """Test the Global Person Registry functionality"""
    print("\n🔍 Testing Global Person Registry...")
    
    try:
        # Create registry
        registry = GlobalPersonRegistry(
            similarity_threshold=config.REGISTRY['similarity_threshold'],
            history_size=config.REGISTRY['history_size'],
            cleanup_interval=config.REGISTRY['cleanup_interval']
        )
        print("✅ Registry created successfully")
        
        # Test lighting condition setting
        registry.set_camera_lighting_condition('cam1', 'normal')
        registry.set_camera_lighting_condition('cam2', 'dark')
        print("✅ Lighting conditions set successfully")
        
        # Test adaptive threshold
        threshold1 = registry.get_adaptive_threshold('cam1')
        threshold2 = registry.get_adaptive_threshold('cam2')
        print(f"✅ Adaptive thresholds: cam1={threshold1:.3f}, cam2={threshold2:.3f}")
        
        # Test stats
        stats = registry.get_registry_stats()
        print(f"✅ Registry stats: {stats['total_persons']} persons tracked")
        
        return True
        
    except Exception as e:
        print(f"❌ Registry test failed: {e}")
        return False

def test_zone_analysis():
    """Test zone analysis functionality"""
    print("\n🔍 Testing zone analysis...")
    
    try:
        # Create test polygons
        test_zones = {
            'cam1': [(0, 0), (100, 0), (100, 100), (0, 100)],
            'cam2': [(50, 50), (150, 50), (150, 150), (50, 150)],
            'cam3': [(200, 200), (300, 200), (300, 300), (200, 300)]
        }
        
        # Test overlap analysis
        overlap_pairs, overlap_zones, overlap_metrics = analyze_camera_overlaps(test_zones)
        print(f"✅ Overlap analysis: {len(overlap_pairs)} significant overlaps found")
        
        # Test validation
        validation = validate_zone_configuration(test_zones, overlap_metrics)
        print(f"✅ Zone validation: {validation['total_cameras']} cameras analyzed")
        
        return True
        
    except Exception as e:
        print(f"❌ Zone analysis test failed: {e}")
        return False

def test_yolo_models():
    """Test YOLO model loading"""
    print("\n🔍 Testing YOLO models...")
    
    try:
        from ultralytics import YOLO
        
        # Test person detection model
        if os.path.exists(config.MODEL_PATHS['person_detection']):
            model = YOLO(config.MODEL_PATHS['person_detection'])
            print("✅ Person detection model loaded successfully")
        else:
            print(f"⚠️  Person detection model not found: {config.MODEL_PATHS['person_detection']}")
        
        # Test face detection model
        if os.path.exists(config.MODEL_PATHS['face_detection']):
            face_model = YOLO(config.MODEL_PATHS['face_detection'])
            print("✅ Face detection model loaded successfully")
        else:
            print(f"⚠️  Face detection model not found: {config.MODEL_PATHS['face_detection']}")
        
        return True
        
    except Exception as e:
        print(f"❌ YOLO model test failed: {e}")
        return False

def test_configuration():
    """Test configuration validation"""
    print("\n🔍 Testing configuration...")
    
    try:
        # Print config summary
        config.print_config_summary()
        
        # Validate configuration
        is_valid = config.validate_config()
        if is_valid:
            print("✅ Configuration validation passed")
        else:
            print("⚠️  Configuration validation failed - some files missing")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("TEST REPORT SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the system.")
    
    print("="*60)

def main():
    """Run all system tests"""
    print("🚀 AI MODULES SYSTEM TEST")
    print("="*60)
    
    # Run all tests
    test_results = {
        "Module Imports": test_imports(),
        "Model Files": test_model_files(),
        "Mapping Files": test_mapping_files(),
        "Floorplan Image": test_floorplan(),
        "Registry Functionality": test_registry(),
        "Zone Analysis": test_zone_analysis(),
        "YOLO Models": test_yolo_models(),
        "Configuration": test_configuration()
    }
    
    # Generate report
    generate_test_report(test_results)
    
    # Save detailed report
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"
    
    detailed_report = {
        "timestamp": timestamp,
        "test_results": test_results,
        "system_info": {
            "python_version": sys.version,
            "opencv_version": cv2.__version__ if 'cv2' in sys.modules else "N/A",
            "torch_version": torch.__version__ if 'torch' in sys.modules else "N/A",
            "cuda_available": torch.cuda.is_available() if 'torch' in sys.modules else False
        },
        "config_summary": {
            "cameras_configured": len(config.CAMERA_MAPPINGS),
            "models_available": len(config.MODEL_PATHS),
            "registry_threshold": config.REGISTRY['similarity_threshold']
        }
    }
    
    with open(report_file, 'w') as f:
        json.dump(detailed_report, f, indent=2)
    
    print(f"\n📄 Detailed test report saved to: {report_file}")
    
    return all(test_results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 