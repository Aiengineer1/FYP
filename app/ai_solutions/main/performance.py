import os
import time
import json
from typing import Dict
from core.registry import GlobalPersonRegistry

class PerformanceMonitor:
    """Performance monitoring for the AI tracking system"""
    def __init__(self):
        self.start_time = time.time()
        self.camera_stats = {}
        self.registry_stats = {}
        self.overlap_events = []

    def update_camera_stats(self, camera_name: str, fps: float, frames_processed: int, frames_dropped: int):
        if camera_name not in self.camera_stats:
            self.camera_stats[camera_name] = {
                'fps_history': [],
                'frames_processed': 0,
                'frames_dropped': 0,
                'start_time': time.time()
            }
        self.camera_stats[camera_name]['fps_history'].append(fps)
        if len(self.camera_stats[camera_name]['fps_history']) > 100:
            self.camera_stats[camera_name]['fps_history'].pop(0)
        self.camera_stats[camera_name]['frames_processed'] = frames_processed
        self.camera_stats[camera_name]['frames_dropped'] = frames_dropped

    def update_registry_stats(self, registry: GlobalPersonRegistry):
        self.registry_stats = registry.get_registry_stats()

    def log_overlap_event(self, person_id: str, camera1: str, camera2: str, timestamp: float = None):
        if timestamp is None:
            timestamp = time.time()
        self.overlap_events.append({
            'person_id': person_id,
            'camera1': camera1,
            'camera2': camera2,
            'timestamp': timestamp
        })

    def get_performance_summary(self) -> Dict:
        runtime = time.time() - self.start_time
        total_frames = sum(stats['frames_processed'] for stats in self.camera_stats.values())
        total_dropped = sum(stats['frames_dropped'] for stats in self.camera_stats.values())
        avg_fps = {}
        for cam, stats in self.camera_stats.items():
            if stats['fps_history']:
                avg_fps[cam] = sum(stats['fps_history']) / len(stats['fps_history'])
            else:
                avg_fps[cam] = 0.0
        return {
            'runtime_seconds': runtime,
            'total_frames_processed': total_frames,
            'total_frames_dropped': total_dropped,
            'drop_rate_percent': (total_dropped / max(1, total_frames)) * 100,
            'average_fps_by_camera': avg_fps,
            'overlap_events_count': len(self.overlap_events),
            'registry_stats': self.registry_stats
        }

    def save_performance_report(self, filename='analytics/performance_report.json'):
        analytics_dir = os.path.dirname(filename)
        if analytics_dir and not os.path.exists(analytics_dir):
            os.makedirs(analytics_dir)
        summary = self.get_performance_summary()
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"Performance report saved to {filename}") 