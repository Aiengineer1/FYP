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

router = APIRouter()

class RTSPRequest(BaseModel):
    rtsp_url: str

class HomographyMappingRequest(BaseModel):
    camera_id: int
    zones: List[Dict]

class FOVZoneRequest(BaseModel):
    camera_id: int
    zone: Dict

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
def update_camera_route(camera_id: int, camera: CameraCreate, db: Session = Depends(get_db)):
    camera_data = camera.model_dump()
    db_camera = update_camera(db, camera_id, camera_data)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

@router.delete("/{camera_id}")
def delete_camera_route(camera_id: int, db: Session = Depends(get_db)):
    delete_camera(db, camera_id)
    return {"detail": "Camera deleted"}

@router.get("/{camera_id}/view")
async def get_camera_view(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get camera details from database
        camera = get_camera(db, camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        # Construct RTSP URL from camera credentials
        rtsp_url = f"rtsp://{camera.username}:{camera.password}@{camera.ip_address}/stream1"
        
        # Open RTSP stream
        cap = cv2.VideoCapture(rtsp_url)
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
    



# ... existing code ...

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
