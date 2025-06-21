"""
AI Solutions Package for Mall Analytics System

This package contains all AI-related modules for the InsightCart system:
- Detection pipeline integration
- Tracking algorithms
- Analytics processing
- Real-time inference
"""

from .detection_pipeline import DetectionPipeline
from .analytics_engine import AnalyticsEngine
from .camera_worker import CameraWorker
from .websocket_manager import WebSocketManager

__all__ = [
    'DetectionPipeline',
    'AnalyticsEngine', 
    'CameraWorker',
    'WebSocketManager'
] 