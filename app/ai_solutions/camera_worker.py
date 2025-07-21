"""
Camera Worker for Real-time Processing

This module handles:
- Real-time RTSP camera processing
- Frame capture and processing
- Detection pipeline integration
- Database logging
- WebSocket broadcasting
"""

import asyncio
import logging
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .detection_pipeline import DetectionPipeline
from .analytics_engine import AnalyticsEngine
from .websocket_manager import WebSocketManager
from ..database import get_db
from ..crud import get_camera, create_customer

logger = logging.getLogger(__name__)

class CameraWorker:
    """Real-time camera processing worker"""
    
    def __init__(self, camera_id: int):
        self.camera_id = camera_id
        self.mall_id: Optional[int] = None
        self.is_running = False
        self.detection_pipeline: Optional[DetectionPipeline] = None
        self.analytics_engine: Optional[AnalyticsEngine] = None
        self.websocket_manager: Optional[WebSocketManager] = None
        self.cap: Optional[cv2.VideoCapture] = None
        
        # Performance tracking
        self.frames_processed = 0
        self.last_frame_time = datetime.utcnow()
        self.processing_times = []
        
        # Configuration
        self.target_fps = 10  # Target processing rate
        self.frame_skip = 1   # Process every N frames
        self.frame_counter = 0
        
        logger.info(f"Camera worker initialized for camera {camera_id}")
    
    async def initialize(self):
        """Initialize camera worker components"""
        try:
            # Get camera details and validate
            async with get_db_session() as db:
                camera = get_camera(db, self.camera_id)
                if not camera:
                    raise ValueError(f"Camera {self.camera_id} not found")
                
                self.mall_id = camera.mall_id
                
                # Initialize detection pipeline
                self.detection_pipeline = DetectionPipeline(self.camera_id, self.mall_id)
                
                # Initialize analytics engine
                self.analytics_engine = AnalyticsEngine(db)
                
                # Initialize WebSocket manager
                self.websocket_manager = WebSocketManager()
                
                                        # Initialize camera connection
                rtsp_url = self._build_rtsp_url(camera)
                self.cap = cv2.VideoCapture(rtsp_url)
                
                if not self.cap.isOpened():
                    # Broadcast camera offline status
                    if self.websocket_manager:
                        await self.websocket_manager.broadcast_camera_status(
                            self.camera_id, self.mall_id, "offline"
                        )
                    raise ValueError(f"Failed to open camera stream: {rtsp_url}")
                
                # Broadcast camera online status
                if self.websocket_manager:
                    await self.websocket_manager.broadcast_camera_status(
                        self.camera_id, self.mall_id, "online"
                    )
                
                # Set camera properties for performance
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
                
                logger.info(f"Camera worker initialized successfully for camera {self.camera_id}")
                
        except Exception as e:
            logger.error(f"Failed to initialize camera worker: {str(e)}")
            raise
    
    def _build_rtsp_url(self, camera) -> str:
        """Build RTSP URL from camera configuration"""
        return f"rtsp://{camera.username}:{camera.password}@{camera.ip_address}/stream"
    
    async def start_processing(self):
        """Start the main processing loop"""
        if self.is_running:
            logger.warning(f"Camera worker {self.camera_id} is already running")
            return
        
        self.is_running = True
        logger.info(f"Starting camera processing for camera {self.camera_id}")
        
        try:
            await self._processing_loop()
        except Exception as e:
            logger.error(f"Error in camera processing loop: {str(e)}")
        finally:
            await self.stop_processing()
    
    async def _processing_loop(self):
        """Main processing loop"""
        while self.is_running:
            try:
                start_time = datetime.utcnow()
                
                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame from camera {self.camera_id}")
                    await asyncio.sleep(0.1)
                    continue
                
                self.frame_counter += 1
                
                # Skip frames if needed for performance
                if self.frame_counter % self.frame_skip != 0:
                    continue
                
                # Process frame through detection pipeline
                detection_result = await self.detection_pipeline.process_frame(frame)
                
                # Log detections to database
                await self._log_detections(detection_result)
                
                # Broadcast to WebSocket subscribers
                await self._broadcast_detections(detection_result)
                
                # Update performance metrics
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                self.processing_times.append(processing_time)
                
                # Keep only last 100 processing times
                if len(self.processing_times) > 100:
                    self.processing_times = self.processing_times[-100:]
                
                self.frames_processed += 1
                self.last_frame_time = datetime.utcnow()
                
                # Control processing rate
                target_interval = 1.0 / self.target_fps
                sleep_time = max(0, target_interval - processing_time)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error processing frame: {str(e)}")
                await asyncio.sleep(0.1)
    
    async def _log_detections(self, detection_result):
        """Log detection results to database"""
        try:
            async with get_db_session() as db:
                for detection in detection_result.detections:
                    # Create or update customer record
                    customer_data = {
                        "mall_id": self.mall_id,
                        "age": detection["age"],
                        "gender": detection["gender"],
                        "routes": [detection["zone"]],
                        "visited_zones": [detection["zone"]],
                        "entry_time": datetime.utcnow()
                    }
                    
                    # Create customer record (simplified for now)
                    # In production, we'd check for existing customers by person_id
                    create_customer(db, customer_data)
                
                logger.debug(f"Logged {len(detection_result.detections)} detections to database")
                
        except Exception as e:
            logger.error(f"Error logging detections: {str(e)}")
    
    async def _broadcast_detections(self, detection_result):
        """Broadcast detection results via WebSocket"""
        try:
            if self.websocket_manager:
                # Broadcast to camera-specific subscribers
                await self.websocket_manager.broadcast_to_camera(
                    self.camera_id, 
                    detection_result.to_dict()
                )
                
                # Broadcast analytics update to mall subscribers
                if len(detection_result.detections) > 0:
                    analytics = self.analytics_engine.calculate_real_time_metrics(self.mall_id)
                    await self.websocket_manager.broadcast_to_mall(
                        self.mall_id,
                        analytics
                    )
                
        except Exception as e:
            logger.error(f"Error broadcasting detections: {str(e)}")
    
    async def stop_processing(self):
        """Stop the processing loop and cleanup"""
        logger.info(f"Stopping camera worker for camera {self.camera_id}")
        
        self.is_running = False
        
        # Cleanup resources
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.detection_pipeline:
            await self.detection_pipeline.cleanup()
        
        logger.info(f"Camera worker stopped for camera {self.camera_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get worker status and performance metrics"""
        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )
        
        current_fps = (
            1.0 / avg_processing_time if avg_processing_time > 0 else 0
        )
        
        return {
            "camera_id": self.camera_id,
            "mall_id": self.mall_id,
            "is_running": self.is_running,
            "frames_processed": self.frames_processed,
            "last_frame_time": self.last_frame_time.isoformat(),
            "average_processing_time": round(avg_processing_time, 3),
            "current_fps": round(current_fps, 1),
            "target_fps": self.target_fps,
            "frame_skip": self.frame_skip,
            "pipeline_status": (
                self.detection_pipeline.get_pipeline_status()
                if self.detection_pipeline else None
            )
        }
    
    async def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame for streaming"""
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                return frame if ret else None
        except Exception as e:
            logger.error(f"Error getting latest frame: {str(e)}")
        return None

class CameraWorkerManager:
    """Manager for multiple camera workers"""
    
    def __init__(self):
        self.workers: Dict[int, CameraWorker] = {}
        self.tasks: Dict[int, asyncio.Task] = {}
        
        logger.info("Camera worker manager initialized")
    
    async def start_camera_worker(self, camera_id: int):
        """Start a worker for a specific camera"""
        if camera_id in self.workers:
            logger.warning(f"Worker for camera {camera_id} already exists")
            return
        
        try:
            worker = CameraWorker(camera_id)
            await worker.initialize()
            
            # Start processing task
            task = asyncio.create_task(worker.start_processing())
            
            self.workers[camera_id] = worker
            self.tasks[camera_id] = task
            
            logger.info(f"Started worker for camera {camera_id}")
            
        except Exception as e:
            logger.error(f"Failed to start worker for camera {camera_id}: {str(e)}")
            raise
    
    async def stop_camera_worker(self, camera_id: int):
        """Stop a worker for a specific camera"""
        if camera_id not in self.workers:
            logger.warning(f"No worker found for camera {camera_id}")
            return
        
        try:
            # Stop the worker
            worker = self.workers[camera_id]
            await worker.stop_processing()
            
            # Cancel the task
            task = self.tasks[camera_id]
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Remove from manager
            del self.workers[camera_id]
            del self.tasks[camera_id]
            
            logger.info(f"Stopped worker for camera {camera_id}")
            
        except Exception as e:
            logger.error(f"Error stopping worker for camera {camera_id}: {str(e)}")
    
    async def start_all_cameras(self, mall_id: int):
        """Start workers for all cameras in a mall"""
        try:
            async with get_db_session() as db:
                from ..crud import get_cameras_by_mall
                cameras = get_cameras_by_mall(db, mall_id)
                
                for camera in cameras:
                    await self.start_camera_worker(camera.id)
                
                logger.info(f"Started workers for {len(cameras)} cameras in mall {mall_id}")
                
        except Exception as e:
            logger.error(f"Error starting cameras for mall {mall_id}: {str(e)}")
    
    async def stop_all_workers(self):
        """Stop all camera workers"""
        logger.info("Stopping all camera workers")
        
        camera_ids = list(self.workers.keys())
        for camera_id in camera_ids:
            await self.stop_camera_worker(camera_id)
        
        logger.info("All camera workers stopped")
    
    def get_worker_status(self, camera_id: int) -> Optional[Dict[str, Any]]:
        """Get status of a specific worker"""
        worker = self.workers.get(camera_id)
        return worker.get_status() if worker else None
    
    def get_all_worker_statuses(self) -> Dict[int, Dict[str, Any]]:
        """Get status of all workers"""
        return {
            camera_id: worker.get_status()
            for camera_id, worker in self.workers.items()
        }

# Global camera worker manager instance
camera_worker_manager = CameraWorkerManager()

@asynccontextmanager
async def get_db_session():
    """Async context manager for database sessions"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close() 