from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import cv2
import numpy as np
from ..schemas.camera import CameraCreate, CameraResponse
from ..crud import create_camera, get_camera, update_camera, delete_camera, get_cameras_by_mall
from ..database import get_db
from app.dependencies import get_current_user
import asyncio
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class RTSPRequest(BaseModel):
    rtsp_url: str

class HomographyMappingRequest(BaseModel):
    camera_id: int
    zones: List[Dict]

class FOVZoneRequest(BaseModel):
    camera_id: int
    zone: Dict

# Global variables
camera_connections: Dict[int, dict] = {}
_cleanup_task = None

async def cleanup_old_connections():
    while True:
        try:
            now = datetime.now()
            to_remove = []
            for camera_id, conn_info in camera_connections.items():
                if (now - conn_info['last_access']).seconds > 60:  # Remove connections inactive for 1 minute
                    conn_info['cap'].release()
                    to_remove.append(camera_id)
            for camera_id in to_remove:
                del camera_connections[camera_id]
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            print(f"Error in cleanup task: {str(e)}")
            await asyncio.sleep(30)  # Continue running even if there's an error

async def get_frame(cap, max_retries=3):
    for _ in range(max_retries):
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
    return None

@router.on_event("startup")
async def start_cleanup_task():
    global _cleanup_task
    if _cleanup_task is None:
        _cleanup_task = asyncio.create_task(cleanup_old_connections())

@router.on_event("shutdown")
async def cleanup_cameras():
    global _cleanup_task
    if _cleanup_task is not None:
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
    
    # Release all camera connections
    for conn_info in camera_connections.values():
        if 'cap' in conn_info:
            conn_info['cap'].release()
    camera_connections.clear()

@router.post("/camera/frame")
async def get_camera_frame(
    request: RTSPRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Open RTSP stream
        cap = cv2.VideoCapture(request.rtsp_url)
        print(request.rtsp_url)
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Failed to open camera stream")
        
        # Read a frame
        ret, frame = cap.read()
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to read frame")
        
        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Release resources
        cap.release()
        
        # Return frame as JPEG
        return StreamingResponse(
            iter([frame_bytes]),
            media_type="image/jpeg"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_camera", response_model=CameraResponse)
def add_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    camera_data = camera.model_dump()
    return create_camera(db, camera_data)

@router.get("/{camera_id}", response_model=CameraResponse)
def read_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = get_camera(db, camera_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

@router.get("/mall/{mall_id}/cameras", response_model=List[CameraResponse])
def read_cameras_by_mall(mall_id: int, db: Session = Depends(get_db)):
    cameras = get_cameras_by_mall(db, mall_id)
    return cameras

@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera_route(
    camera_id: int, 
    camera: CameraCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"=== Starting camera update process for camera ID: {camera_id} ===")
        
        # First check if camera exists
        existing_camera = get_camera(db, camera_id)
        if not existing_camera:
            logger.error(f"Camera {camera_id} not found in database")
            raise HTTPException(status_code=404, detail="Camera not found")
        
        logger.info(f"Current camera data: {existing_camera.__dict__}")
        
        # Convert the camera model to dict and validate required fields
        camera_data = camera.model_dump()
        logger.info(f"Received update data: {camera_data}")
        
        required_fields = ['name', 'ip_address', 'username', 'password', 'location', 'mall_id']
        for field in required_fields:
            if field not in camera_data or camera_data[field] is None:
                logger.error(f"Missing required field: {field}")
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Ensure mall_id matches
        if 'mall_id' in camera_data and camera_data['mall_id'] != existing_camera.mall_id:
            logger.error(f"Cannot change mall_id of camera")
            raise HTTPException(status_code=400, detail="Cannot change mall_id of camera")
        
        try:
            # Update the camera
            logger.info("Attempting to update camera in database...")
            db_camera = update_camera(db, camera_id, camera_data)
            
            if db_camera is None:
                logger.error("Update operation returned None")
                raise HTTPException(status_code=500, detail="Failed to update camera")
            
            logger.info(f"Updated camera data: {db_camera.__dict__}")
            
            # If this camera has an active connection, we should refresh it
            if camera_id in camera_connections:
                logger.info(f"Closing existing camera connection for camera {camera_id}")
                try:
                    camera_connections[camera_id]['cap'].release()
                    del camera_connections[camera_id]
                    logger.info("Successfully closed existing camera connection")
                except Exception as conn_err:
                    logger.error(f"Error closing camera connection: {str(conn_err)}")
            
            logger.info(f"=== Successfully completed camera update for camera ID: {camera_id} ===")
            return db_camera
            
        except Exception as update_err:
            logger.error(f"Database update error: {str(update_err)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(update_err)}")
            
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error in update route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{camera_id}")
def delete_camera_route(camera_id: int, db: Session = Depends(get_db)):
    delete_camera(db, camera_id)
    return {"detail": "Camera deleted"}

@router.get("/{camera_id}/live")
async def get_camera_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    logger.info(f"Received stream request for camera {camera_id}")
    
    async def generate_frames():
        try:
            # Get or create camera connection
            if camera_id not in camera_connections:
                logger.info(f"Creating new connection for camera {camera_id}")
                camera = get_camera(db, camera_id)
                if not camera:
                    logger.error(f"Camera {camera_id} not found in database")
                    raise HTTPException(status_code=404, detail="Camera not found")
                
                rtsp_url = f"rtsp://{camera.username}:{camera.password}@{camera.ip_address}/stream1"
                logger.info(f"Attempting to connect to RTSP URL: {rtsp_url}")
                
                cap = cv2.VideoCapture(rtsp_url)
                
                if not cap.isOpened():
                    logger.error(f"Failed to open camera stream for camera {camera_id}")
                    raise HTTPException(status_code=500, detail="Failed to open camera stream")
                
                # Configure capture settings
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer size
                
                camera_connections[camera_id] = {
                    'cap': cap,
                    'last_access': datetime.now()
                }
                logger.info(f"Successfully created connection for camera {camera_id}")
            else:
                logger.info(f"Reusing existing connection for camera {camera_id}")
            
            conn_info = camera_connections[camera_id]
            cap = conn_info['cap']
            
            # Update last access time
            conn_info['last_access'] = datetime.now()
            
            frame_interval = 1/15  # Reduce to 15 FPS for better performance
            last_frame_time = 0
            frames_sent = 0
            
            while True:
                current_time = time.time()
                if current_time - last_frame_time >= frame_interval:
                    frame_bytes = await get_frame(cap)
                    if frame_bytes is None:
                        logger.error(f"Failed to get frame from camera {camera_id}")
                        break
                    
                    frames_sent += 1
                    if frames_sent % 100 == 0:  # Log every 100 frames
                        logger.info(f"Sent {frames_sent} frames for camera {camera_id}")
                    
                    yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                    last_frame_time = current_time
                else:
                    await asyncio.sleep(0.001)
                
        except Exception as e:
            logger.error(f"Error in generate_frames for camera {camera_id}: {str(e)}")
            if camera_id in camera_connections:
                camera_connections[camera_id]['cap'].release()
                del camera_connections[camera_id]
            raise HTTPException(status_code=500, detail=str(e))

    try:
        return StreamingResponse(
            generate_frames(),
            media_type='multipart/x-mixed-replace; boundary=frame',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
    except Exception as e:
        logger.error(f"Error creating StreamingResponse for camera {camera_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/homography/save-mappings")
async def save_homography_mappings(
    request: HomographyMappingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get camera
        camera = get_camera(db, request.camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")

        # Update camera with new homography mappings
        camera_data = {
            "homography_map": {
                "zones": request.zones
            }
        }
        
        updated_camera = update_camera(db, request.camera_id, camera_data)
        if not updated_camera:
            raise HTTPException(status_code=500, detail="Failed to update camera mappings")

        return {"message": "Homography mappings saved successfully", "camera": updated_camera}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fov/update-zone")
async def update_fov_zone(
    request: FOVZoneRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get camera
        camera = get_camera(db, request.camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")

        # Get existing FOV zones or initialize empty list
        current_fov_zones = camera.fov_zones.get("zones", []) if camera.fov_zones else []

        # Check if zone with same name exists
        zone_index = next((i for i, z in enumerate(current_fov_zones) 
                          if z.get("name") == request.zone.get("name")), -1)

        if zone_index >= 0:
            # Update existing zone
            current_fov_zones[zone_index] = request.zone
        else:
            # Add new zone
            current_fov_zones.append(request.zone)

        # Update camera with new FOV zones
        camera_data = {
            "fov_zones": {
                "zones": current_fov_zones
            }
        }
        
        updated_camera = update_camera(db, request.camera_id, camera_data)
        if not updated_camera:
            raise HTTPException(status_code=500, detail="Failed to update FOV zones")

        return {"message": "FOV zone updated successfully", "camera": updated_camera}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/fov/delete-zone/{camera_id}/{zone_name}")
async def delete_fov_zone(
    camera_id: int,
    zone_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get camera
        camera = get_camera(db, camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")

        # Get existing FOV zones
        current_fov_zones = camera.fov_zones.get("zones", []) if camera.fov_zones else []

        # Remove zone with matching name
        updated_zones = [z for z in current_fov_zones if z.get("name") != zone_name]

        # Update camera with new FOV zones
        camera_data = {
            "fov_zones": {
                "zones": updated_zones
            }
        }
        
        updated_camera = update_camera(db, camera_id, camera_data)
        if not updated_camera:
            raise HTTPException(status_code=500, detail="Failed to delete FOV zone")

        return {"message": "FOV zone deleted successfully", "camera": updated_camera}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
