#!/usr/bin/env python3
"""
Unified Main Script for AI Modules Final Year Project
Combines all functionality: Interactive, Command-line, and Pipeline modes
Supports Individual Camera, Single Camera, Multi-Camera, and Custom modes
"""

import os
import sys
import argparse
import time
import json
import threading
from typing import List, Dict, Optional, Tuple
from config.config import config
from core.registry import GlobalPersonRegistry
from core.camera_tracker import CameraTracker
from core.zone_utils import load_global_zone_from_json, analyze_camera_overlaps, validate_zone_configuration
import cv2
import numpy as np
import matplotlib.pyplot as plt
from main.performance import PerformanceMonitor

# Update config paths
CAMERA_MAPPINGS = {k: f"config/{v}" if not v.startswith("config/") else v for k, v in config.CAMERA_MAPPINGS.items()}
CAMERA_RTSP = config.CAMERA_RTSP
CAMERA_OFFSETS = config.CAMERA_OFFSETS
CAMERA_NUM_TO_NAME = config.CAMERA_NUM_TO_NAME

# Default floorplan path
DEFAULT_FLOORPLAN = "assets/floorplan_gui.png"

class UnifiedAISystem:
    """Unified AI system for camera tracking and analytics"""
    
    def __init__(self, floorplan_path: str = None):
        self.floorplan_path = floorplan_path or DEFAULT_FLOORPLAN
        self.registry = GlobalPersonRegistry(
            similarity_threshold=config.REGISTRY['similarity_threshold'],
            history_size=config.REGISTRY['history_size'],
            cleanup_interval=config.REGISTRY['cleanup_interval']
        )
        self.trackers = []
        self.performance_monitor = PerformanceMonitor()
        self.running = False
        self.current_mode = None  # Track current mode for analytics
    
    def get_mode_analytics_path(self, filename: str = None) -> str:
        """Get mode-specific analytics path"""
        if self.current_mode:
            mode_dir = f"analytics/{self.current_mode}"
        else:
            mode_dir = "analytics/default_mode"
        
        if filename:
            return f"{mode_dir}/{filename}"
        return mode_dir
        
    def validate_floorplan(self) -> bool:
        """Validate floorplan image exists and can be loaded"""
        if not os.path.exists(self.floorplan_path):
            print(f"❌ Floorplan not found: {self.floorplan_path}")
            return False
        
        try:
            img = cv2.imread(self.floorplan_path)
            if img is None:
                print(f"❌ Cannot load floorplan image: {self.floorplan_path}")
                return False
            print(f"✅ Floorplan loaded: {self.floorplan_path} ({img.shape[1]}x{img.shape[0]})")
            return True
        except Exception as e:
            print(f"❌ Error loading floorplan: {e}")
            return False
    
    def get_available_cameras(self) -> List[str]:
        """Get list of available cameras with valid mapping files"""
        available = []
        for cam_key, mapping_file in CAMERA_MAPPINGS.items():
            cam_name = CAMERA_NUM_TO_NAME.get(cam_key, cam_key)
            if os.path.exists(mapping_file):
                available.append(cam_name)
        return available
    
    def validate_camera(self, camera_name: str) -> bool:
        """Validate if a specific camera is available"""
        mapping_file = CAMERA_MAPPINGS.get(camera_name)
        if not mapping_file:
            print(f"❌ Camera {camera_name} not configured")
            return False
        
        if not os.path.exists(mapping_file):
            print(f"❌ Mapping file not found for {camera_name}: {mapping_file}")
            return False
        
        try:
            global_zone, _ = load_global_zone_from_json(mapping_file)
            print(f"✅ Camera {camera_name} validated")
            return True
        except Exception as e:
            print(f"❌ Error validating camera {camera_name}: {e}")
            return False
    
    def create_tracker(self, camera_name: str, enable_registry: bool = True) -> Optional[CameraTracker]:
        """Create a camera tracker for a specific camera"""
        if not self.validate_camera(camera_name):
            return None
        
        mapping_file = CAMERA_MAPPINGS[camera_name]
        global_zone, _ = load_global_zone_from_json(mapping_file)
        
        # Create zone configuration
        zone_polygons = {camera_name: global_zone['dst_points']}
        overlap_zones = {camera_name: global_zone['dst_points']}
        overlap_pairs = []
        
        # Create tracker
        tracker = CameraTracker(
            camera_name=camera_name,
            rtsp_url=CAMERA_RTSP[camera_name],
            mapping_json=mapping_file,
            offset=CAMERA_OFFSETS[camera_name],
            global_registry=self.registry if enable_registry else None,
            mall_map_img_path=self.floorplan_path,
            overlap_zones=overlap_zones,
            overlap_pairs=overlap_pairs,
            mode=self.current_mode
        )
        
        return tracker
    
    def run_individual_camera(self, camera_name: str, duration: int = None) -> bool:
        """Run a single camera in isolation (no registry)"""
        self.current_mode = f"individual_mode_{camera_name}"
        print(f"\n🎯 Running Individual Camera: {camera_name}")
        print("-" * 50)
        
        tracker = self.create_tracker(camera_name, enable_registry=False)
        if not tracker:
            return False
        
        try:
            tracker.start()
            self.trackers = [tracker]
            
            start_time = time.time()
            while tracker.is_alive():
                time.sleep(1)
                
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    print(f"⏰ Duration limit reached ({duration}s)")
                    break
                    
        except KeyboardInterrupt:
            print("\n⏹️  Stopping individual camera...")
        finally:
            tracker.stop()
            tracker.join()
        
        return True
    
    def run_single_camera(self, camera_name: str, duration: int = None) -> bool:
        """Run a single camera with registry (for future multi-camera expansion)"""
        self.current_mode = f"single_mode_{camera_name}"
        print(f"\n🎯 Running Single Camera Mode: {camera_name}")
        print("-" * 50)
        
        tracker = self.create_tracker(camera_name, enable_registry=True)
        if not tracker:
            return False
        
        try:
            tracker.start()
            self.trackers = [tracker]
            
            start_time = time.time()
            while tracker.is_alive():
                time.sleep(1)
                
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    print(f"⏰ Duration limit reached ({duration}s)")
                    break
                    
        except KeyboardInterrupt:
            print("\n⏹️  Stopping single camera...")
        finally:
            tracker.stop()
            tracker.join()
        
        return True
    
    def run_multi_camera(self, camera_names: List[str] = None, duration: int = None) -> bool:
        """Run multiple cameras with shared registry"""
        if camera_names is None:
            camera_names = self.get_available_cameras()
        
        if not camera_names:
            print("❌ No available cameras found")
            return False
        
        self.current_mode = "multi_mode"
        print(f"\n🎯 Running Multi-Camera Mode: {', '.join(camera_names)}")
        print("-" * 50)
        
        # Load all camera zones
        zone_polygons = {}
        for camera_name in camera_names:
            if not self.validate_camera(camera_name):
                continue
            
            mapping_file = CAMERA_MAPPINGS[camera_name]
            global_zone, _ = load_global_zone_from_json(mapping_file)
            zone_polygons[camera_name] = global_zone['dst_points']
        
        if not zone_polygons:
            print("❌ No valid cameras found")
            return False
        
        # Analyze overlaps
        overlap_pairs, overlap_zones, overlap_metrics = analyze_camera_overlaps(zone_polygons)
        
        # Validate configuration
        validation_results = validate_zone_configuration(zone_polygons, overlap_metrics)
        self._print_zone_analysis(validation_results, overlap_metrics)
        
        # Create trackers
        self.trackers = []
        for camera_name in zone_polygons:
            tracker = self.create_tracker(camera_name, enable_registry=True)
            if tracker:
                self.trackers.append(tracker)
        
        if not self.trackers:
            print("❌ No trackers created")
            return False
        
        try:
            # Start all trackers
            for tracker in self.trackers:
                tracker.start()
            
            self.running = True
            start_time = time.time()
            last_stats_time = start_time
            
            # Monitor and report
            while self.running and any(t.is_alive() for t in self.trackers):
                time.sleep(1)
                
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    print(f"⏰ Duration limit reached ({duration}s)")
                    break
                
                # Update performance stats every 10 seconds
                current_time = time.time()
                if current_time - last_stats_time > 10:
                    self.performance_monitor.update_registry_stats(self.registry)
                    self._print_performance_summary()
                    last_stats_time = current_time
                    
        except KeyboardInterrupt:
            print("\n⏹️  Stopping multi-camera system...")
        finally:
            self.running = False
            for tracker in self.trackers:
                tracker.stop()
            for tracker in self.trackers:
                tracker.join()
        
        return True
    
    def _print_zone_analysis(self, validation_results: Dict, overlap_metrics: Dict):
        """Print zone analysis results"""
        print(f"\n[Zone Configuration Analysis]")
        print(f"Total cameras: {validation_results['total_cameras']}")
        print(f"Significant overlaps: {validation_results['significant_overlaps']}")
        print(f"High quality overlaps: {validation_results['high_quality_overlaps']}")
        
        if validation_results['isolated_cameras']:
            print(f"Isolated cameras: {validation_results['isolated_cameras']}")
        
        if validation_results['recommendations']:
            print("Recommendations:")
            for rec in validation_results['recommendations']:
                print(f"  - {rec}")
    
    def _print_performance_summary(self):
        """Print performance summary"""
        summary = self.performance_monitor.get_performance_summary()
        print(f"\n{'='*50}")
        print(f"PERFORMANCE SUMMARY")
        print(f"{'='*50}")
        print(f"Runtime: {summary['runtime_seconds']:.1f} seconds")
        print(f"Total frames processed: {summary['total_frames_processed']}")
        print(f"Total frames dropped: {summary['total_frames_dropped']}")
        print(f"Drop rate: {summary['drop_rate_percent']:.2f}%")
        print(f"Overlap events: {summary['overlap_events_count']}")
        
        print(f"\nAverage FPS by Camera:")
        for cam, fps in summary['average_fps_by_camera'].items():
            print(f"  {cam}: {fps:.2f} FPS")
        
        if summary['registry_stats']:
            reg_stats = summary['registry_stats']
            print(f"\nRegistry Statistics:")
            print(f"  Total persons tracked: {reg_stats.get('total_persons', 0)}")
            print(f"  Supervisor distribution: {reg_stats.get('supervisor_distribution', {})}")
            print(f"  Lighting conditions: {reg_stats.get('lighting_conditions', {})}")
        
        print(f"{'='*50}")
    
    def generate_analytics(self):
        """Generate analytics for all cameras"""
        print("\n📊 Generating analytics...")
        
        # Determine mode-specific directory
        if self.current_mode:
            mode_dir = f"analytics/{self.current_mode}"
        else:
            mode_dir = "analytics/default_mode"
        
        # Ensure mode directory exists
        if not os.path.exists(mode_dir):
            os.makedirs(mode_dir)
        
        for cam_name in CAMERA_MAPPINGS:
            # Ensure camera subdirectory exists within mode directory
            analytics_dir = f"{mode_dir}/{cam_name}"
            if not os.path.exists(analytics_dir):
                os.makedirs(analytics_dir)
                
            json_path = f"{analytics_dir}/person_routes_{cam_name}.json"
            if os.path.exists(json_path):
                output_heatmap = f"{analytics_dir}/heatmap_overlay_{cam_name}.png"
                output_person_object = f"{analytics_dir}/person_object_interaction_{cam_name}.png"
                output_age_object = f"{analytics_dir}/age_object_interaction_{cam_name}.png"
                
                self._generate_heatmap(json_path, output_heatmap)
                self._generate_person_object_chart(json_path, output_person_object)
                self._generate_age_object_chart(json_path, output_age_object)
    
    def _generate_heatmap(self, json_path: str, output_path: str):
        """Generate heatmap from routes"""
        try:
            mall_map = cv2.imread(self.floorplan_path)
            if mall_map is None:
                return
            
            height, width = mall_map.shape[:2]
            heatmap = np.zeros((height, width), dtype=np.float32)
            
            with open(json_path, 'r') as f:
                routes_data = json.load(f)
            
            for person in routes_data.values():
                for x, y in person.get('route', []):
                    if 0 <= int(y) < height and 0 <= int(x) < width:
                        heatmap[int(y), int(x)] += 1
            
            heatmap_blur = cv2.GaussianBlur(heatmap, (0, 0), sigmaX=25, sigmaY=25)
            norm_heatmap = cv2.normalize(heatmap_blur, None, 0, 255, cv2.NORM_MINMAX)
            norm_heatmap = norm_heatmap.astype(np.uint8)
            color_heatmap = cv2.applyColorMap(norm_heatmap, cv2.COLORMAP_JET)
            overlay = cv2.addWeighted(mall_map, 0.6, color_heatmap, 0.4, 0)
            cv2.imwrite(output_path, overlay)
            print(f"✅ Heatmap saved: {output_path}")
            
        except Exception as e:
            print(f"❌ Error generating heatmap: {e}")
    
    def _generate_person_object_chart(self, json_path: str, output_path: str):
        """Generate person-object interaction chart"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            person_ids = []
            object_names = set()
            interaction_matrix = {}
            
            for pid, pdata in data.items():
                person_ids.append(pid)
                for obj, info in pdata.get('interactions', {}).items():
                    object_names.add(obj)
                    interaction_matrix.setdefault(pid, {})[obj] = info.get('duration_sec', 0)
            
            object_names = sorted(object_names)
            values = []
            for pid in person_ids:
                row = [interaction_matrix.get(pid, {}).get(obj, 0) for obj in object_names]
                values.append(row)
            
            x = np.arange(len(object_names))
            fig, ax = plt.subplots(figsize=(10, 6))
            bar_width = 0.8 / max(1, len(person_ids))
            
            for i, (pid, row) in enumerate(zip(person_ids, values)):
                ax.bar(x + i * bar_width, row, width=bar_width, label=pid)
            
            ax.set_xticks(x + bar_width * (len(person_ids) - 1) / 2)
            ax.set_xticklabels(object_names, rotation=30, ha='right')
            ax.set_ylabel('Interaction Time (sec)')
            ax.set_title('Interaction Time per Person per Object')
            ax.legend(title='Person ID')
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            print(f"✅ Person-object chart saved: {output_path}")
            
        except Exception as e:
            print(f"❌ Error generating person-object chart: {e}")
    
    def _generate_age_object_chart(self, json_path: str, output_path: str):
        """Generate age-object interaction chart"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            age_object_duration = {}
            object_names = set()
            
            for pdata in data.values():
                age = str(pdata.get('age', 'Unknown') or 'Unknown')
                for obj, info in pdata.get('interactions', {}).items():
                    object_names.add(obj)
                    age_object_duration.setdefault(age, {}).setdefault(obj, 0)
                    age_object_duration[age][obj] += info.get('duration_sec', 0)
            
            object_names = sorted(object_names)
            ages = sorted(age_object_duration.keys())
            values = []
            
            for age in ages:
                row = [age_object_duration[age].get(obj, 0) for obj in object_names]
                values.append(row)
            
            x = np.arange(len(object_names))
            fig, ax = plt.subplots(figsize=(10, 6))
            bar_width = 0.8 / max(1, len(ages))
            
            for i, (age, row) in enumerate(zip(ages, values)):
                ax.bar(x + i * bar_width, row, width=bar_width, label=age)
            
            ax.set_xticks(x + bar_width * (len(ages) - 1) / 2)
            ax.set_xticklabels(object_names, rotation=30, ha='right')
            ax.set_ylabel('Total Interaction Time (sec)')
            ax.set_title('Interaction Time per Object Grouped by Age')
            ax.legend(title='Age Group')
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            print(f"✅ Age-object chart saved: {output_path}")
            
        except Exception as e:
            print(f"❌ Error generating age-object chart: {e}")

def interactive_mode():
    """Interactive mode with user prompts"""
    print("🤖 AI MODULES FINAL YEAR PROJECT")
    print("   Multi-Camera Person Tracking and Analytics System")
    print("=" * 70)
    
    # Get floorplan path
    floorplan_path = input(f"Enter path to floorplan/mall map image (default: {DEFAULT_FLOORPLAN}): ").strip()
    if not floorplan_path:
        floorplan_path = DEFAULT_FLOORPLAN
    if not os.path.exists(floorplan_path):
        print(f"[ERROR] Floorplan image not found at {floorplan_path}")
        return
    
    # Save the selected path
    config_dir = 'config'
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    with open('config/selected_lab_map.txt', 'w') as f:
        f.write(floorplan_path)
    
    # Create system
    system = UnifiedAISystem(floorplan_path)
    
    # Validate floorplan
    if not system.validate_floorplan():
        return
    
    # Get operation mode
    print("\n🎯 Select Operation Mode:")
    print("1. Individual Camera Mode (no registry - isolated tracking)")
    print("2. Single Camera Mode (with registry - for future expansion)")
    print("3. Multi-Camera Mode (all available cameras)")
    print("4. Custom Camera Selection")
    
    while True:
        mode = input("Enter mode (1-4): ").strip()
        if mode in ['1', '2', '3', '4']:
            break
        else:
            print("❌ Please enter 1, 2, 3, or 4")
    
    # Execute based on mode
    if mode == "1":  # Individual Camera Mode
        camera_name = prompt_camera_selection()
        if camera_name:
            system.run_individual_camera(camera_name)
    
    elif mode == "2":  # Single Camera Mode
        camera_name = prompt_camera_selection()
        if camera_name:
            system.run_single_camera(camera_name)
    
    elif mode == "3":  # Multi-Camera Mode
        system.run_multi_camera()
    
    elif mode == "4":  # Custom Camera Selection
        camera_names = prompt_custom_cameras()
        if camera_names:
            system.run_multi_camera(camera_names)
    
    # Generate analytics
    system.generate_analytics()
    
    # Save performance report
    performance_path = system.get_mode_analytics_path('performance_report.json')
    system.performance_monitor.save_performance_report(filename=performance_path)
    
    print("\n🎉 System execution completed!")

def prompt_camera_selection() -> Optional[str]:
    """Prompt user for camera selection"""
    print("\n📹 Available cameras:")
    available_cameras = []
    for cam_key, mapping_file in CAMERA_MAPPINGS.items():
        cam_name = CAMERA_NUM_TO_NAME.get(cam_key, cam_key)
        if os.path.exists(mapping_file):
            available_cameras.append(cam_name)
            print(f"  ✅ {cam_name}: {mapping_file}")
        else:
            print(f"  ❌ {cam_name}: {mapping_file} (missing)")
    
    if not available_cameras:
        print("❌ No cameras with valid mapping files found")
        return None
    
    while True:
        cam_input = input(f"Enter camera name ({', '.join(available_cameras)}): ").strip()
        cam_name = CAMERA_NUM_TO_NAME.get(cam_input, cam_input)
        if cam_name in available_cameras:
            return cam_name
        else:
            print(f"❌ Invalid camera: {cam_input}")

def prompt_custom_cameras() -> List[str]:
    """Prompt user for custom camera selection"""
    print("\n📹 Custom Camera Selection:")
    available_cameras = []
    for cam_key, mapping_file in CAMERA_MAPPINGS.items():
        cam_name = CAMERA_NUM_TO_NAME.get(cam_key, cam_key)
        if os.path.exists(mapping_file):
            available_cameras.append(cam_name)
    
    if not available_cameras:
        print("❌ No cameras with valid mapping files found")
        return []
    
    print("Available cameras:")
    for cam in available_cameras:
        print(f"  - {cam}")
    
    while True:
        camera_input = input("Enter camera names (space-separated): ").strip()
        selected_cameras = camera_input.split()
        
        # Validate all selected cameras
        valid_cameras = []
        invalid_cameras = []
        
        for cam in selected_cameras:
            if cam in available_cameras:
                valid_cameras.append(cam)
            else:
                invalid_cameras.append(cam)
        
        if invalid_cameras:
            print(f"❌ Invalid cameras: {', '.join(invalid_cameras)}")
            continue
        
        if not valid_cameras:
            print("❌ No valid cameras selected")
            continue
        
        return valid_cameras

def main():
    """Main function with command line and interactive support"""
    parser = argparse.ArgumentParser(description='Unified AI Camera Tracking System')
    parser.add_argument('--mode', choices=['individual', 'single', 'multi', 'interactive'], 
                       default='interactive', help='Operation mode')
    parser.add_argument('--cameras', nargs='+', help='Camera names to use')
    parser.add_argument('--floorplan', default=DEFAULT_FLOORPLAN, 
                       help='Path to floorplan image')
    parser.add_argument('--duration', type=int, help='Duration limit in seconds')
    parser.add_argument('--list-cameras', action='store_true', help='List available cameras')
    parser.add_argument('--test', action='store_true', help='Run system test first')
    
    args = parser.parse_args()
    
    # List available cameras
    if args.list_cameras:
        system = UnifiedAISystem()
        available = system.get_available_cameras()
        print("Available cameras:")
        for cam in available:
            print(f"  - {cam}")
        return
    
    # Run system test
    if args.test:
        print("🧪 Running system test...")
        result = os.system(f"{sys.executable} test_main.py")
        if result != 0:
            print("❌ System test failed")
            return
    
    # Interactive mode
    if args.mode == 'interactive':
        interactive_mode()
        return
    
    # Command line modes
    system = UnifiedAISystem(args.floorplan)
    
    # Validate floorplan
    if not system.validate_floorplan():
        return
    
    # Run based on mode
    if args.mode == 'individual':
        if not args.cameras or len(args.cameras) != 1:
            print("❌ Individual mode requires exactly one camera")
            return
        system.run_individual_camera(args.cameras[0], args.duration)
    
    elif args.mode == 'single':
        if not args.cameras or len(args.cameras) != 1:
            print("❌ Single mode requires exactly one camera")
            return
        system.run_single_camera(args.cameras[0], args.duration)
    
    elif args.mode == 'multi':
        system.run_multi_camera(args.cameras, args.duration)
    
    # Generate analytics
    system.generate_analytics()
    
    # Save performance report
    performance_path = system.get_mode_analytics_path('performance_report.json')
    system.performance_monitor.save_performance_report(filename=performance_path)

if __name__ == "__main__":
    main() 