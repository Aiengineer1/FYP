#!/usr/bin/env python3
"""
Test version of main.py without interactive input
"""

import os
import sys
from core.registry import GlobalPersonRegistry
from core.camera_tracker import CameraTracker
from core.zone_utils import load_global_zone_from_json, analyze_camera_overlaps, validate_zone_configuration
from config.config import config
import threading
import time

# Import configuration variables
CAMERA_MAPPINGS = config.CAMERA_MAPPINGS
CAMERA_RTSP = config.CAMERA_RTSP
CAMERA_OFFSETS = config.CAMERA_OFFSETS
CAMERA_NUM_TO_NAME = config.CAMERA_NUM_TO_NAME

def test_single_camera():
    """Test single camera mode"""
    print("=== Testing Single Camera Mode ===")
    
    # Use cam1 for testing
    cam_name = "cam1"
    floorplan_path = "floorplan_gui.png"
    
    print(f"Testing camera: {cam_name}")
    print(f"Floorplan: {floorplan_path}")
    
    # Check if files exist
    mapping_json = CAMERA_MAPPINGS.get(cam_name)
    if not mapping_json or not os.path.exists(mapping_json):
        print(f"❌ Mapping file not found: {mapping_json}")
        return False
    
    if not os.path.exists(floorplan_path):
        print(f"❌ Floorplan not found: {floorplan_path}")
        return False
    
    print("✅ All files found")
    
    # Create registry
    registry = GlobalPersonRegistry(similarity_threshold=0.75, history_size=5)
    
    # Load zone configuration
    try:
        global_zone, _ = load_global_zone_from_json(mapping_json)
        zone_polygons = {cam_name: global_zone['dst_points']}
        overlap_zones = {cam_name: global_zone['dst_points']}
        overlap_pairs = []
        print("✅ Zone configuration loaded")
    except Exception as e:
        print(f"❌ Error loading zone configuration: {e}")
        return False
    
    # Create tracker (but don't start it to avoid RTSP connection issues)
    try:
        tracker = CameraTracker(
            camera_name=cam_name,
            rtsp_url=CAMERA_RTSP[cam_name],
            mapping_json=mapping_json,
            offset=CAMERA_OFFSETS[cam_name],
            global_registry=registry,
            mall_map_img_path=floorplan_path,
            overlap_zones=overlap_zones,
            overlap_pairs=overlap_pairs
        )
        print("✅ Camera tracker created successfully")
        print(f"RTSP URL: {CAMERA_RTSP[cam_name]}")
        print(f"Mapping file: {mapping_json}")
        print(f"Offset: {CAMERA_OFFSETS[cam_name]}")
        return True
    except Exception as e:
        print(f"❌ Error creating camera tracker: {e}")
        return False

def test_multi_camera():
    """Test multi-camera configuration"""
    print("\n=== Testing Multi-Camera Configuration ===")
    
    # Check available cameras
    zone_polygons = {}
    for cam_key, mapping_json in CAMERA_MAPPINGS.items():
        cam_name = CAMERA_NUM_TO_NAME.get(cam_key, cam_key)
        if os.path.exists(mapping_json):
            try:
                global_zone, _ = load_global_zone_from_json(mapping_json)
                zone_polygons[cam_name] = global_zone['dst_points']
                print(f"✅ {cam_name}: {mapping_json}")
            except Exception as e:
                print(f"❌ {cam_name}: Error loading {mapping_json} - {e}")
        else:
            print(f"❌ {cam_name}: {mapping_json} - File missing")
    
    if not zone_polygons:
        print("❌ No valid cameras found")
        return False
    
    # Analyze overlaps
    try:
        overlap_pairs, overlap_zones, overlap_metrics = analyze_camera_overlaps(zone_polygons)
        print(f"✅ Overlap analysis complete")
        print(f"   Cameras: {list(zone_polygons.keys())}")
        print(f"   Overlap pairs: {len(overlap_pairs)}")
        
        # Validate configuration
        validation_results = validate_zone_configuration(zone_polygons, overlap_metrics)
        print(f"✅ Zone validation complete")
        print(f"   Total cameras: {validation_results['total_cameras']}")
        print(f"   Significant overlaps: {validation_results['significant_overlaps']}")
        
        return True
    except Exception as e:
        print(f"❌ Error in overlap analysis: {e}")
        return False

if __name__ == "__main__":
    print("=== AI Modules System Test ===\n")
    
    # Test single camera
    single_success = test_single_camera()
    
    # Test multi-camera
    multi_success = test_multi_camera()
    
    print("\n=== Test Results ===")
    print(f"Single Camera Test: {'✅ PASS' if single_success else '❌ FAIL'}")
    print(f"Multi-Camera Test: {'✅ PASS' if multi_success else '❌ FAIL'}")
    
    if single_success and multi_success:
        print("\n🎉 All tests passed! System is ready to run.")
        print("\nTo run the full system:")
        print("python main.py")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.") 