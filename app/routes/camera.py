from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import cv2
import numpy as np
from ..schemas.camera import CameraCreate, CameraResponse
from ..crud import create_camera, get_camera, update_camera, delete_camera, get_cameras_by_mall, get_mall
from ..database import get_db
from app.dependencies import get_current_user
import asyncio
from datetime import datetime
import time
import logging
import os

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
    request: dict,  # {"rtsp_url": "rtsp://..."}
    current_user: dict = Depends(get_current_user)
):
    """Get latest camera frame for frontend polling with optimized headers"""
    try:
        rtsp_url = request.get("rtsp_url")
        if not rtsp_url:
            raise HTTPException(status_code=400, detail="rtsp_url is required")
        
        # Try to get frame from camera worker first (if available)
        try:
            from ..ai_solutions.camera_worker import camera_worker_manager
            # Extract camera_id from request if available
            camera_id = request.get("camera_id")
            if camera_id and camera_id in camera_worker_manager.workers:
                worker = camera_worker_manager.workers[camera_id]
                frame = await worker.get_latest_frame()
                if frame is not None:
                    frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
                    print("Resized frame shape:", frame.shape)
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    frame_bytes = buffer.tobytes()
                    
                    return Response(
                        content=frame_bytes,
                        media_type="image/jpeg",
                        headers={
                            "Cache-Control": "no-cache, no-store, must-revalidate",
                            "Pragma": "no-cache",
                            "Expires": "0",
                            "Access-Control-Allow-Origin": "*"
                        }
                    )
        except Exception:
            pass  # Fall through to direct RTSP capture
        
        # Fallback to direct RTSP capture
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            raise HTTPException(status_code=404, detail="Camera frame not available")
        
        # Read a frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=404, detail="Failed to capture frame")
        
        frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
        print("Resized frame shape:", frame.shape)

        # Convert frame to JPEG with quality optimization
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()
        
        # Return frame with proper headers for frontend polling
        return Response(
            content=frame_bytes,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache", 
                "Expires": "0",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting camera frame: {str(e)}")
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

@router.get("/{camera_id}/stream")
async def get_optimized_camera_stream(
    camera_id: int,
    quality: str = Query("medium", description="Stream quality: low, medium, high"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get optimized camera stream with quality control"""
    try:
        from ..ai_solutions.camera_worker import camera_worker_manager
        
        # Get camera details
        db_camera = get_camera(db, camera_id)
        if not db_camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        # Check if worker is running and get latest frame
        worker = camera_worker_manager.workers.get(camera_id)
        if worker:
            frame = await worker.get_latest_frame()
            if frame is not None:
                # Encode frame with quality settings
                quality_settings = {
                    "low": 50,
                    "medium": 75,
                    "high": 95
                }
                encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality_settings.get(quality, 75)]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                return StreamingResponse(
                    iter([buffer.tobytes()]),
                    media_type="image/jpeg",
                    headers={"Cache-Control": "no-cache"}
                )
        
        # Fallback to direct RTSP if worker not available
        rtsp_url = f"rtsp://{db_camera.username}:{db_camera.password}@{db_camera.ip_address}/stream"
        cap = cv2.VideoCapture(rtsp_url)
        
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Camera stream unavailable")
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        
        frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
        print("Resized frame shape:", frame.shape)
        _, buffer = cv2.imencode('.jpg', frame)
        return StreamingResponse(
            iter([buffer.tobytes()]),
            media_type="image/jpeg"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
        # Get existing homography mappings
        current_homography_map = camera.homography_map if camera.homography_map else {"zones": []}
        
        # Remove zone with matching name from FOV zones
        updated_fov_zones = [z for z in current_fov_zones if z.get("name") != zone_name]
        
        # Remove all mappings (objects) from the deleted zone
        updated_homography_zones = []
        for zone in current_homography_map.get("zones", []):
            if zone.get("name") != zone_name:
                updated_homography_zones.append(zone)
        
        # Update camera with new FOV zones and homography mappings
        camera_data = {
            "fov_zones": {
                "zones": updated_fov_zones
            },
            "homography_map": {
                "zones": updated_homography_zones
            }
        }
        
        updated_camera = update_camera(db, camera_id, camera_data)
        if not updated_camera:
            raise HTTPException(status_code=500, detail="Failed to delete FOV zone")

        return {"message": "FOV zone and its mappings deleted successfully", "camera": updated_camera}

    except Exception as e:
        logger.error(f"Error deleting FOV zone: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Define target size for frame resizing
TARGET_SIZE = (1280, 720)

@router.get("/camera/{camera_id}/test-mappings")
async def test_camera_mappings(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get camera and its mappings
        camera = get_camera(db, camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")

        if not camera.homography_map or not camera.homography_map.get("zones"):
            raise HTTPException(status_code=400, detail="No homography mappings found for this camera")

        # Get mall and its map image
        mall = get_mall(db, camera.mall_id)
        if not mall or not mall.map_image:
            raise HTTPException(status_code=404, detail="Mall map image not found")

        # Convert mall map image bytes to numpy array
        nparr = np.frombuffer(mall.map_image, np.uint8)
        mall_map_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if mall_map_img is None:
            raise ValueError("Failed to decode mall map image")
        
        # Resize mall map to target size for consistency
        mall_map_img = cv2.resize(mall_map_img, TARGET_SIZE, interpolation=cv2.INTER_AREA)
        print("Resized mall map shape:", mall_map_img.shape)

        # Create a blank camera frame for demonstration (or get actual camera frame)
        camera_img = np.zeros((TARGET_SIZE[1], TARGET_SIZE[0], 3), dtype=np.uint8)
        camera_img[:] = (50, 50, 50)  # Dark gray background
        
        # Get real-time camera frame using the correct RTSP URL format
        try:
            rtsp_url = f"rtsp://{camera.username}:{camera.password}@{camera.ip_address}:554/cam/realmonitor?channel=1&subtype=0"
            print(f"Getting camera frame from: {rtsp_url}")
            
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                raise Exception("Could not open RTSP stream")
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise Exception("Failed to read frame from RTSP")
            
            camera_img = cv2.resize(frame, TARGET_SIZE)
            print("Successfully got real-time camera frame")
            
        except Exception as e:
            print(f"Could not get real-time camera frame: {e}")
            # Use blank frame as fallback
            print("Using blank frame as fallback")
            camera_img = np.zeros((TARGET_SIZE[1], TARGET_SIZE[0], 3), dtype=np.uint8)
            camera_img[:] = (50, 50, 50)  # Dark gray background

        # Process each zone and apply homography transformation (exactly like test_homography_api.py)
        final_result = camera_img.copy()
        homography_applied = False
        
        for zone in camera.homography_map["zones"]:
            # First, process zone-level homography if zone has points
            if len(zone.get("src_points", [])) == 4 and len(zone.get("dst_points", [])) == 4:
                zone_src_points = np.array(zone["src_points"], dtype=np.float32)  # Camera frame points
                zone_dst_points = np.array(zone["dst_points"], dtype=np.float32)  # Mall map points
                
                print(f"Processing zone: {zone.get('name', 'unknown')}")
                print(f"zone_src_points (camera): {zone_src_points}")
                print(f"zone_dst_points (mall): {zone_dst_points}")
                
                # Compute homography matrix for zone (warp mall map onto camera frame)
                H_zone, status_zone = cv2.findHomography(zone_dst_points, zone_src_points, method=cv2.RANSAC)
                if H_zone is not None:
                    print(f"Homography Matrix for zone {zone.get('name', 'unknown')}:\n{H_zone}")
                    
                    # Warp mall map to camera frame perspective for zone
                    warped_map_zone = cv2.warpPerspective(mall_map_img, H_zone, TARGET_SIZE)
                    
                    # Create mask for the zone polygon (on camera frame)
                    mask_zone = np.zeros_like(camera_img, dtype=np.uint8)
                    cv2.fillConvexPoly(mask_zone, np.int32(zone_src_points), (255, 255, 255))
                    
                    # Masked warped map for zone (only inside polygon)
                    masked_warped_zone = cv2.bitwise_and(warped_map_zone, mask_zone)
                    
                    # Blend masked warped map with camera frame for zone (blue color for zone)
                    blended_zone = cv2.addWeighted(final_result, 1, masked_warped_zone, 0.4, 0)
                    
                    # Draw zone polygon outline on blended image (blue for zone)
                    cv2.polylines(blended_zone, [np.int32(zone_src_points)], True, (255, 0, 0), 3)
                    
                    final_result = blended_zone.copy()
                    homography_applied = True
                    print(f"Successfully applied homography transformation for zone {zone.get('name', 'unknown')}")
                else:
                    print(f"Failed to compute homography for zone {zone.get('name', 'unknown')}")
            
            # Then process objects within the zone
            if not zone.get("objects"):
                continue
                
            for obj in zone["objects"]:
                # Check if we have both src_points (camera) and dst_points (mall map)
                if len(obj.get("src_points", [])) != 4 or len(obj.get("dst_points", [])) != 4:
                    print(f"Skipping {obj.get('name', 'unknown')}: insufficient points")
                    continue
                
                src_points = np.array(obj["src_points"], dtype=np.float32)  # Camera frame points
                dst_points = np.array(obj["dst_points"], dtype=np.float32)  # Mall map points
                
                print(f"Processing object: {obj['name']}")
                print(f"src_points (camera): {src_points}")
                print(f"dst_points (mall): {dst_points}")
                
                # Compute homography matrix (warp mall map onto camera frame) - EXACTLY like test_homography_api.py
                H, status = cv2.findHomography(dst_points, src_points, method=cv2.RANSAC)
                if H is None:
                    print(f"Failed to compute homography for {obj['name']}")
                    continue
                
                print(f"Homography Matrix for {obj['name']}:\n{H}")
                
                # Warp mall map to camera frame perspective - EXACTLY like test_homography_api.py
                warped_map = cv2.warpPerspective(mall_map_img, H, TARGET_SIZE)
                
                # Create mask for the selected polygon (on camera frame) - EXACTLY like test_homography_api.py
                mask = np.zeros_like(camera_img, dtype=np.uint8)
                cv2.fillConvexPoly(mask, np.int32(src_points), (255, 255, 255))
                
                # Masked warped map (only inside polygon) - EXACTLY like test_homography_api.py
                masked_warped = cv2.bitwise_and(warped_map, mask)
                
                # Blend masked warped map with camera frame - EXACTLY like test_homography_api.py
                blended = cv2.addWeighted(final_result, 1, masked_warped, 0.6, 0)
                
                # Draw polygon outline on blended image - EXACTLY like test_homography_api.py
                cv2.polylines(blended, [np.int32(src_points)], True, (0, 255, 0), 2)
                
                final_result = blended.copy()
                homography_applied = True
                print(f"Successfully applied homography transformation for {obj['name']}")
        
        # If no homography transformations were applied, show debug info
        if not homography_applied:
            print("No homography transformations applied - showing debug info")
            final_result = camera_img.copy()
            # Draw debug information
            for zone in camera.homography_map["zones"]:
                if not zone.get("objects"):
                    continue
                for obj in zone["objects"]:
                    if len(obj.get("src_points", [])) == 4:
                        src_pts = np.array(obj["src_points"], dtype=np.float32)
                        cv2.polylines(final_result, [np.int32(src_pts)], True, (0, 0, 255), 3)
                        center_x = int(np.mean(src_pts[:, 0]))
                        center_y = int(np.mean(src_pts[:, 1]))
                        cv2.putText(final_result, obj["name"], (center_x - 50, center_y), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Encode the final result as JPEG
        _, buffer = cv2.imencode('.jpg', final_result)
        frame_bytes = buffer.tobytes()
        
        return StreamingResponse(
            iter([frame_bytes]),
            media_type="image/jpeg"
        )

    except Exception as e:
        logger.error(f"Error in test_camera_mappings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
