"""
Analytics API Routes for Frontend Integration

This module provides comprehensive analytics endpoints:
- Real-time mall analytics
- Camera-specific analytics
- Heatmap data
- Historical trends
- WebSocket support
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..dependencies import get_current_user
from ..ai_solutions.analytics_engine import AnalyticsEngine
from ..ai_solutions.websocket_manager import websocket_manager
from ..ai_solutions.camera_worker import camera_worker_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/mall/{mall_id}")
async def get_mall_analytics(
    mall_id: int,
    time_range: Optional[str] = Query("24h", description="Time range: 1h, 24h, 7d, 30d"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a mall in frontend-compatible format"""
    try:
        analytics_engine = AnalyticsEngine(db)
        # Use frontend-compatible format
        metrics = analytics_engine.get_frontend_compatible_analytics(mall_id)
        
        logger.info(f"Retrieved analytics for mall {mall_id}")
        return metrics  # Return data directly without wrapper
        
    except Exception as e:
        logger.error(f"Error getting mall analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/{mall_id}")
async def get_realtime_metrics(
    mall_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time metrics for dashboard in frontend-compatible format"""
    try:
        analytics_engine = AnalyticsEngine(db)
        # Use frontend-compatible realtime format
        metrics = analytics_engine.get_realtime_status(mall_id)
        
        logger.info(f"Retrieved real-time metrics for mall {mall_id}")
        return metrics  # Return data directly without wrapper
        
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mall/{mall_id}/heatmap")
async def get_heatmap_data(
    mall_id: int,
    time_range: Optional[str] = Query("1h", description="Time range for heatmap"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get heatmap data for mall visualization"""
    try:
        analytics_engine = AnalyticsEngine(db)
        
        # Get heatmap data
        heatmap_data = analytics_engine._generate_heatmap(mall_id, datetime.utcnow())
        
        # Get zone definitions (mock for now)
        zone_definitions = [
            {"id": "electronics", "name": "Electronics", "coordinates": [0, 0, 3, 3]},
            {"id": "clothing", "name": "Clothing", "coordinates": [3, 0, 6, 3]},
            {"id": "food_court", "name": "Food Court", "coordinates": [6, 0, 10, 3]},
            {"id": "shoes", "name": "Shoes", "coordinates": [0, 3, 3, 6]},
            {"id": "accessories", "name": "Accessories", "coordinates": [3, 3, 6, 6]}
        ]
        
        return {
            "success": True,
            "data": {
                "heatmap_matrix": heatmap_data,
                "zones": zone_definitions,
                "dimensions": {"width": 10, "height": 10},
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting heatmap data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/camera/{camera_id}/details")
async def get_camera_analytics(
    camera_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific camera"""
    try:
        analytics_engine = AnalyticsEngine(db)
        camera_analytics = analytics_engine.calculate_camera_analytics(camera_id)
        
        # Get worker status if available
        worker_status = camera_worker_manager.get_worker_status(camera_id)
        
        return {
            "success": True,
            "data": {
                **camera_analytics,
                "worker_status": worker_status
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting camera analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/status")
async def get_system_status(
    current_user: dict = Depends(get_current_user)
):
    """Get system-wide analytics status"""
    try:
        # Get worker statuses
        worker_statuses = camera_worker_manager.get_all_worker_statuses()
        
        # Get WebSocket statistics
        websocket_stats = websocket_manager.get_statistics()
        
        return {
            "success": True,
            "data": {
                "camera_workers": worker_statuses,
                "websocket_stats": websocket_stats,
                "system_health": "healthy",
                "uptime": "active",
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/{camera_id}/start")
async def start_camera_processing(
    camera_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Start processing for a specific camera"""
    try:
        await camera_worker_manager.start_camera_worker(camera_id)
        
        return {
            "success": True,
            "message": f"Started processing for camera {camera_id}",
            "camera_id": camera_id
        }
        
    except Exception as e:
        logger.error(f"Error starting camera processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/{camera_id}/stop")
async def stop_camera_processing(
    camera_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Stop processing for a specific camera"""
    try:
        await camera_worker_manager.stop_camera_worker(camera_id)
        
        return {
            "success": True,
            "message": f"Stopped processing for camera {camera_id}",
            "camera_id": camera_id
        }
        
    except Exception as e:
        logger.error(f"Error stopping camera processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mall/{mall_id}/start_all_cameras")
async def start_all_mall_cameras(
    mall_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Start processing for all cameras in a mall"""
    try:
        await camera_worker_manager.start_all_cameras(mall_id)
        
        return {
            "success": True,
            "message": f"Started processing for all cameras in mall {mall_id}",
            "mall_id": mall_id
        }
        
    except Exception as e:
        logger.error(f"Error starting all cameras: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket Endpoints
@router.websocket("/ws/mall/{mall_id}")
async def websocket_mall_analytics(websocket: WebSocket, mall_id: int):
    """WebSocket endpoint for real-time mall analytics"""
    try:
        # Accept connection
        connection = await websocket_manager.connect(websocket)
        
        # Subscribe to mall room
        await websocket_manager.join_room(websocket, f"mall_{mall_id}")
        
        # Send initial data
        db = next(get_db())
        analytics_engine = AnalyticsEngine(db)
        initial_data = analytics_engine.calculate_real_time_metrics(mall_id)
        
        await connection.send_message({
            "type": "initial_data",
            "data": initial_data
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                message = await websocket.receive_text()
                await websocket_manager.handle_client_message(websocket, message)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket communication: {str(e)}")
                break
        
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket_manager.disconnect(websocket)

@router.websocket("/ws/camera/{camera_id}")
async def websocket_camera_detections(websocket: WebSocket, camera_id: int):
    """WebSocket endpoint for real-time camera detections"""
    try:
        # Accept connection
        connection = await websocket_manager.connect(websocket)
        
        # Subscribe to camera room
        await websocket_manager.join_room(websocket, f"camera_{camera_id}")
        
        # Send initial status
        worker_status = camera_worker_manager.get_worker_status(camera_id)
        await connection.send_message({
            "type": "camera_status",
            "data": worker_status
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                message = await websocket.receive_text()
                await websocket_manager.handle_client_message(websocket, message)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in camera WebSocket: {str(e)}")
                break
        
    except Exception as e:
        logger.error(f"Camera WebSocket error: {str(e)}")
    finally:
        await websocket_manager.disconnect(websocket)

@router.websocket("/ws/system")
async def websocket_system_status(websocket: WebSocket):
    """WebSocket endpoint for system-wide status updates"""
    try:
        # Accept connection
        connection = await websocket_manager.connect(websocket)
        
        # Subscribe to system room
        await websocket_manager.join_room(websocket, "system")
        
        # Send initial system status
        worker_statuses = camera_worker_manager.get_all_worker_statuses()
        websocket_stats = websocket_manager.get_statistics()
        
        await connection.send_message({
            "type": "system_status",
            "data": {
                "camera_workers": worker_statuses,
                "websocket_stats": websocket_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        # Keep connection alive
        while True:
            try:
                message = await websocket.receive_text()
                await websocket_manager.handle_client_message(websocket, message)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in system WebSocket: {str(e)}")
                break
        
    except Exception as e:
        logger.error(f"System WebSocket error: {str(e)}")
    finally:
        await websocket_manager.disconnect(websocket) 