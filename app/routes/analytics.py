"""
Analytics API Routes for Frontend Integration

This module provides comprehensive analytics endpoints matching frontend requirements:
- Real-time mall analytics
- Camera-specific analytics
- Heatmap data
- Historical trends
- Section/rack analytics
- Customer insights
- Alerts & notifications
- Time series data
- WebSocket support
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..database import get_db
from ..dependencies import get_current_user
from app.ai_solutions.analytics_engine import AnalyticsEngine
from app.ai_solutions.communication.websocket_manager import websocket_manager
from app.ai_solutions.camera_worker import camera_worker_manager
from app.ai_solutions.modules.person_tracking import PersonTracker
from app.crud import get_cameras_by_mall, get_mall, get_camera
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

# Pydantic models for response validation
class MallAnalytics(BaseModel):
    totalVisitors: int
    activeVisitors: int
    averageDwellTime: int
    peakHours: List[str]
    popularSections: List[Dict[str, Any]]

class RealTimeMetrics(BaseModel):
    activeVisitors: int
    currentPeakHour: bool
    timestamp: str

class HeatmapZone(BaseModel):
    name: str
    visitorCount: int
    coordinates: List[List[int]]
    density: float

class HeatmapData(BaseModel):
    mallId: int
    zones: List[HeatmapZone]
    timestamp: str

class SectionAnalytics(BaseModel):
    name: str
    section: str
    male: int
    female: int
    total: int
    averageDwellTime: int

class CustomerStats(BaseModel):
    total: int
    male: int
    female: int
    averageAge: int
    ageGroups: Dict[str, int]

class CameraAnalytics(BaseModel):
    id: int
    name: str
    location: str
    status: str
    visitorCount: int
    lastActive: Optional[str]
    healthStatus: str

class Alert(BaseModel):
    id: int
    type: str
    message: str
    severity: str
    zone: str
    time: str

class TimeSeriesPoint(BaseModel):
    time: str
    visitors: int
    interactions: int

# ===== 1. MALL ANALYTICS (SUMMARY) =====
@router.get("/mall/{mall_id}", response_model=MallAnalytics)
async def get_mall_analytics(
    mall_id: int,
    range: Optional[str] = Query("day", description="Time range: hour, day, week, month"),
    gender: Optional[str] = Query(None, description="Filter by gender: male, female, all"),
    ageGroup: Optional[str] = Query(None, description="Filter by age group: 18-25, 26-35, 36-45, 46-55, 55+"),
    zone: Optional[str] = Query(None, description="Filter by zone/section"),
    cameraId: Optional[int] = Query(None, description="Filter by camera ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a mall from database"""
    try:
        # Verify mall exists and user has access
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        # Create analytics engine
        analytics_engine = AnalyticsEngine(db)
        
        # Get analytics with filters
        analytics = analytics_engine.get_frontend_compatible_analytics(
            mall_id=mall_id,
            time_range=range,
            gender_filter=gender,
            age_filter=ageGroup,
            zone_filter=zone,
            camera_filter=cameraId
        )
        
        if "error" in analytics:
            raise HTTPException(status_code=500, detail=analytics["error"])
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_mall_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 2. REAL-TIME METRICS =====
@router.get("/mall/{mall_id}/realtime", response_model=RealTimeMetrics)
async def get_realtime_metrics(
    mall_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time metrics from database"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        analytics_engine = AnalyticsEngine(db)
        realtime_data = analytics_engine.get_realtime_status(mall_id)
        
        if "error" in realtime_data:
            raise HTTPException(status_code=500, detail=realtime_data["error"])
        
        return realtime_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_realtime_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 3. HEATMAP DATA =====
@router.get("/mall/{mall_id}/heatmap", response_model=HeatmapData)
async def get_heatmap_data(
    mall_id: int,
    range: Optional[str] = Query("day", description="Time range: hour, day, week, month"),
    gender: Optional[str] = Query(None, description="Filter by gender: male, female, all"),
    ageGroup: Optional[str] = Query(None, description="Filter by age group"),
    timeOfDay: Optional[str] = Query(None, description="Filter by time of day: morning, afternoon, evening, night"),
    zone: Optional[str] = Query(None, description="Filter by zone"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get heatmap data from camera zones and customer data"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        analytics_engine = AnalyticsEngine(db)
        heatmap_data = analytics_engine.get_heatmap_data(
            mall_id=mall_id,
            time_range=range,
            gender_filter=gender,
            age_filter=ageGroup,
            time_of_day=timeOfDay,
            zone_filter=zone
        )
        
        if "error" in heatmap_data:
            raise HTTPException(status_code=500, detail=heatmap_data["error"])
        
        return heatmap_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_heatmap_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 4. SECTION ANALYTICS =====
@router.get("/mall/{mall_id}/sections", response_model=List[SectionAnalytics])
async def get_section_analytics(
    mall_id: int,
    range: Optional[str] = Query("day", description="Time range: hour, day, week, month"),
    gender: Optional[str] = Query(None, description="Filter by gender: male, female, all"),
    ageGroup: Optional[str] = Query(None, description="Filter by age group"),
    section: Optional[str] = Query(None, description="Filter by section name"),
    rack: Optional[str] = Query(None, description="Filter by rack name"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get section/rack analytics from camera zones"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        analytics_engine = AnalyticsEngine(db)
        sections = analytics_engine.get_section_analytics(
            mall_id=mall_id,
            time_range=range,
            gender_filter=gender,
            age_filter=ageGroup,
            section_filter=section,
            rack_filter=rack
        )
        
        return sections
        
    except Exception as e:
        logger.error(f"Error in get_section_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 5. CUSTOMER INSIGHTS =====
@router.get("/mall/{mall_id}/customers", response_model=CustomerStats)
async def get_customer_insights(
    mall_id: int,
    range: Optional[str] = Query("day", description="Time range: hour, day, week, month"),
    gender: Optional[str] = Query(None, description="Filter by gender: male, female, all"),
    ageGroup: Optional[str] = Query(None, description="Filter by age group"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get customer demographics and insights from database"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        analytics_engine = AnalyticsEngine(db)
        customer_stats = analytics_engine.get_customer_insights(
            mall_id=mall_id,
            time_range=range,
            gender_filter=gender,
            age_filter=ageGroup
        )
        
        if "error" in customer_stats:
            raise HTTPException(status_code=500, detail=customer_stats["error"])
        
        return customer_stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_customer_insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 6. CAMERA LIST =====
@router.get("/mall/{mall_id}/cameras")
async def get_camera_list(
    mall_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of cameras for a mall"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        cameras = get_cameras_by_mall(db, mall_id)
        
        camera_list = []
        for camera in cameras:
            camera_list.append({
                "id": camera.id,
                "name": camera.name,
                "location": camera.location,
                "status": "active" if camera.fov_zones else "inactive",
                "lastActive": camera.created_at.isoformat() if camera.created_at else None
            })
        
        return camera_list
        
    except Exception as e:
        logger.error(f"Error in get_camera_list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 7. CAMERA ANALYTICS =====
@router.get("/cameras/mall/{mall_id}", response_model=List[CameraAnalytics])
async def get_camera_analytics(
    mall_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get camera analytics from database"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        analytics_engine = AnalyticsEngine(db)
        camera_analytics = analytics_engine.get_camera_analytics(mall_id)
        
        return camera_analytics
        
    except Exception as e:
        logger.error(f"Error in get_camera_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 8. ALERTS =====
@router.get("/mall/{mall_id}/alerts", response_model=List[Alert])
async def get_alerts(
    mall_id: int,
    since: Optional[str] = Query(None, description="Get alerts since timestamp"),
    zone: Optional[str] = Query(None, description="Filter by zone"),
    severity: Optional[str] = Query(None, description="Filter by severity: info, warning, error"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts based on customer data and zone activity"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        analytics_engine = AnalyticsEngine(db)
        alerts = analytics_engine.get_alerts(
            mall_id=mall_id,
            since=since,
            zone_filter=zone,
            severity_filter=severity
        )
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error in get_alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 9. TIME SERIES DATA =====
@router.get("/mall/{mall_id}/timeseries", response_model=List[TimeSeriesPoint])
async def get_timeseries_data(
    mall_id: int,
    metric: str = Query("visitors", description="Metric: visitors, interactions, dwellTime"),
    range: Optional[str] = Query("day", description="Time range: hour, day, week, month"),
    zone: Optional[str] = Query(None, description="Filter by zone"),
    cameraId: Optional[int] = Query(None, description="Filter by camera ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time series data for graphs"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        analytics_engine = AnalyticsEngine(db)
        timeseries = analytics_engine.get_timeseries_data(
            mall_id=mall_id,
            metric=metric,
            time_range=range,
            zone_filter=zone,
            camera_filter=cameraId
        )
        
        return timeseries
        
    except Exception as e:
        logger.error(f"Error in get_timeseries_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 10. SYSTEM STATUS =====
@router.get("/system/status")
async def get_system_status(
    current_user: dict = Depends(get_current_user)
):
    """Get overall system status"""
    try:
        # Get camera worker status
        camera_status = camera_worker_manager.get_status()
        
        # Get WebSocket status
        websocket_status = websocket_manager.get_status()
        
        return {
            "status": "operational",
            "cameras": camera_status,
            "websockets": websocket_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in get_system_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 11. CAMERA CONTROL =====
@router.post("/camera/{camera_id}/start")
async def start_camera(
    camera_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start camera processing"""
    try:
        # Verify camera exists in database
        camera = get_camera(db, camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        # Check if camera worker exists, if not create it
        if camera_id not in camera_worker_manager.workers:
            # Create RTSP URL from camera data
            rtsp_url = f"rtsp://{camera.username}:{camera.password}@{camera.ip_address}/stream"
            camera_worker_manager.add_camera(camera_id, camera.name, rtsp_url)
        
        # Start camera worker
        success = camera_worker_manager.start_camera(camera_id)
        
        if success:
            return {"message": f"Camera {camera_id} started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start camera")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in start_camera: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/{camera_id}/stop")
async def stop_camera(
    camera_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop camera processing"""
    try:
        # Verify camera exists in database
        camera = get_camera(db, camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        # Check if camera worker exists
        if camera_id not in camera_worker_manager.workers:
            return {"message": f"Camera {camera_id} is not running"}
        
        # Stop camera worker
        success = camera_worker_manager.stop_camera(camera_id)
        
        if success:
            return {"message": f"Camera {camera_id} stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop camera")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stop_camera: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mall/{mall_id}/start_all_cameras")
async def start_all_cameras(
    mall_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start all cameras for a mall"""
    try:
        # Verify mall exists
        mall = get_mall(db, mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        # Get all cameras for mall
        cameras = get_cameras_by_mall(db, mall_id)
        
        started_count = 0
        for camera in cameras:
            # Check if camera worker exists, if not create it
            if camera.id not in camera_worker_manager.workers:
                rtsp_url = f"rtsp://{camera.username}:{camera.password}@{camera.ip_address}/stream"
                camera_worker_manager.add_camera(camera.id, camera.name, rtsp_url)
            
            # Start camera worker
            if camera_worker_manager.start_camera(camera.id):
                started_count += 1
        
        return {
            "message": f"Started {started_count} out of {len(cameras)} cameras",
            "started": started_count,
            "total": len(cameras)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in start_all_cameras: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 12. WEBSOCKET ENDPOINTS =====
@router.websocket("/ws/analytics/{mall_id}")
async def websocket_analytics(
    websocket: WebSocket,
    mall_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket for real-time analytics updates"""
    try:
        await websocket_manager.connect(websocket, f"analytics_{mall_id}")
        
        # Send initial data
        analytics_engine = AnalyticsEngine(db)
        initial_data = analytics_engine.get_frontend_compatible_analytics(mall_id)
        await websocket.send_json({
            "type": "analytics_update",
            "data": initial_data
        })
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                # Handle any client messages if needed
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, f"analytics_{mall_id}")
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if websocket.client_state.value != 3:  # Not disconnected
            await websocket.close()

@router.websocket("/ws/camera/{camera_id}")
async def websocket_camera(
    websocket: WebSocket,
    camera_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket for camera-specific updates"""
    try:
        await websocket_manager.connect(websocket, f"camera_{camera_id}")
        
        try:
            while True:
                # Keep connection alive
                data = await websocket.receive_text()
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, f"camera_{camera_id}")
            
    except Exception as e:
        logger.error(f"Camera WebSocket error: {str(e)}")
        if websocket.client_state.value != 3:
            await websocket.close()

@router.websocket("/ws/system")
async def websocket_system(websocket: WebSocket):
    """WebSocket for system-wide updates"""
    try:
        await websocket_manager.connect(websocket, "system")
        
        try:
            while True:
                # Keep connection alive
                data = await websocket.receive_text()
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, "system")
            
    except Exception as e:
        logger.error(f"System WebSocket error: {str(e)}")
        if websocket.client_state.value != 3:
            await websocket.close()