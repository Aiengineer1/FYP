"""
Camera Worker Manager for AI Solutions
Manages camera processing workers and their lifecycle
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)

class CameraWorker:
    """Individual camera worker for processing camera streams"""
    
    def __init__(self, camera_id: int, camera_name: str, rtsp_url: str):
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.rtsp_url = rtsp_url
        self.is_running = False
        self.is_active = False
        self.last_seen = None
        self.thread = None
        self.stats = {
            "frames_processed": 0,
            "frames_dropped": 0,
            "detections_count": 0,
            "start_time": None,
            "last_activity": None
        }
    
    def start(self):
        """Start the camera worker"""
        if self.is_running:
            logger.warning(f"Camera worker {self.camera_name} is already running")
            return False
        
        try:
            self.is_running = True
            self.is_active = True
            self.stats["start_time"] = datetime.utcnow()
            self.stats["last_activity"] = datetime.utcnow()
            
            # Start processing thread
            self.thread = threading.Thread(target=self._process_stream, daemon=True)
            self.thread.start()
            
            logger.info(f"Started camera worker for {self.camera_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera worker {self.camera_name}: {str(e)}")
            self.is_running = False
            self.is_active = False
            return False
    
    def stop(self):
        """Stop the camera worker"""
        if not self.is_running:
            logger.warning(f"Camera worker {self.camera_name} is not running")
            return False
        
        try:
            self.is_running = False
            self.is_active = False
            
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5.0)
            
            logger.info(f"Stopped camera worker for {self.camera_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping camera worker {self.camera_name}: {str(e)}")
            return False
    
    def _process_stream(self):
        """Process camera stream (mock implementation)"""
        try:
            logger.info(f"Starting stream processing for {self.camera_name}")
            
            while self.is_running:
                # Simulate frame processing
                time.sleep(0.1)  # 10 FPS simulation
                
                self.stats["frames_processed"] += 1
                self.stats["last_activity"] = datetime.utcnow()
                
                # Simulate occasional detections
                if self.stats["frames_processed"] % 30 == 0:  # Every 3 seconds
                    self.stats["detections_count"] += 1
                    self.last_seen = datetime.utcnow()
                
                # Simulate occasional frame drops
                if self.stats["frames_processed"] % 100 == 0:
                    self.stats["frames_dropped"] += 1
                
                # Simulate connection issues
                if self.stats["frames_processed"] % 1000 == 0:
                    logger.debug(f"Camera {self.camera_name} processing frame {self.stats['frames_processed']}")
            
        except Exception as e:
            logger.error(f"Error in stream processing for {self.camera_name}: {str(e)}")
            self.is_active = False
        finally:
            self.is_running = False
            logger.info(f"Stopped stream processing for {self.camera_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the camera worker"""
        return {
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "is_running": self.is_running,
            "is_active": self.is_active,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "stats": self.stats.copy()
        }

class CameraWorkerManager:
    """Manager for multiple camera workers"""
    
    def __init__(self):
        self.workers: Dict[int, CameraWorker] = {}
        self.lock = threading.Lock()
    
    def add_camera(self, camera_id: int, camera_name: str, rtsp_url: str) -> bool:
        """Add a new camera worker"""
        with self.lock:
            if camera_id in self.workers:
                logger.warning(f"Camera worker {camera_id} already exists")
                return False
            
            worker = CameraWorker(camera_id, camera_name, rtsp_url)
            self.workers[camera_id] = worker
            logger.info(f"Added camera worker for {camera_name}")
            return True
    
    def remove_camera(self, camera_id: int) -> bool:
        """Remove a camera worker"""
        with self.lock:
            if camera_id not in self.workers:
                logger.warning(f"Camera worker {camera_id} not found")
                return False
            
            worker = self.workers[camera_id]
            if worker.is_running:
                worker.stop()
            
            del self.workers[camera_id]
            logger.info(f"Removed camera worker {camera_id}")
            return True
    
    def start_camera(self, camera_id: int) -> bool:
        """Start a specific camera worker"""
        with self.lock:
            if camera_id not in self.workers:
                logger.warning(f"Camera worker {camera_id} not found")
                return False
            
            return self.workers[camera_id].start()
    
    def stop_camera(self, camera_id: int) -> bool:
        """Stop a specific camera worker"""
        with self.lock:
            if camera_id not in self.workers:
                logger.warning(f"Camera worker {camera_id} not found")
                return False
            
            return self.workers[camera_id].stop()
    
    def start_all_cameras(self) -> Dict[int, bool]:
        """Start all camera workers"""
        results = {}
        with self.lock:
            for camera_id, worker in self.workers.items():
                results[camera_id] = worker.start()
        
        logger.info(f"Started {sum(results.values())} out of {len(results)} camera workers")
        return results
    
    def stop_all_cameras(self) -> Dict[int, bool]:
        """Stop all camera workers"""
        results = {}
        with self.lock:
            for camera_id, worker in self.workers.items():
                results[camera_id] = worker.stop()
        
        logger.info(f"Stopped {sum(results.values())} out of {len(results)} camera workers")
        return results
    
    def get_camera_status(self, camera_id: int) -> Optional[Dict[str, Any]]:
        """Get status of a specific camera worker"""
        with self.lock:
            if camera_id not in self.workers:
                return None
            
            return self.workers[camera_id].get_status()
    
    def get_all_status(self) -> Dict[int, Dict[str, Any]]:
        """Get status of all camera workers"""
        with self.lock:
            return {camera_id: worker.get_status() for camera_id, worker in self.workers.items()}
    
    def get_active_cameras(self) -> List[int]:
        """Get list of active camera IDs"""
        with self.lock:
            return [camera_id for camera_id, worker in self.workers.items() if worker.is_active]
    
    def get_running_cameras(self) -> List[int]:
        """Get list of running camera IDs"""
        with self.lock:
            return [camera_id for camera_id, worker in self.workers.items() if worker.is_running]
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall status for API compatibility"""
        return {
            "total_cameras": len(self.workers),
            "active_cameras": len(self.get_active_cameras()),
            "running_cameras": len(self.get_running_cameras()),
            "cameras": self.get_all_status()
        }

# Global instance
camera_worker_manager = CameraWorkerManager() 