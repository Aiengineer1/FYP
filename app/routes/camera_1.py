from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import cv2
import numpy as np
import io
from datetime import datetime
from ..schemas.camera import CameraCreate, CameraResponse
from ..crud import create_camera, get_camera, update_camera, delete_camera, get_cameras_by_mall, get_mall
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

@router.post("/homography/test-mapping")
async def test_mapping(
    camera_id: int,
    frame: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get camera details from database
        camera = get_camera(db, camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")

        # Get mall details to get the mall map
        mall = get_mall(db, camera.mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        if not mall.map_image:
            raise HTTPException(status_code=404, detail="Mall map image not found")

        # Read frame data
        frame_data = await frame.read()
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None or frame.size == 0:
            raise HTTPException(status_code=400, detail="Invalid frame data")

        # Get target size from camera settings or use default
        target_size = (1366, 768)
        frame_resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
        if frame_resized.size == 0:
            raise HTTPException(status_code=400, detail="Failed to resize frame")

        # Get homography mappings from camera data
        if not camera.homography_map or "zones" not in camera.homography_map:
            raise HTTPException(status_code=404, detail="No homography mappings found for this camera")

        mappings = camera.homography_map["zones"]

        # Load mall map from database
        try:
            # Convert the map image from database to numpy array
            nparr = np.frombuffer(mall.map_image, np.uint8)
            mall_map = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if mall_map is None:
                raise HTTPException(status_code=404, detail="Failed to decode mall map image")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading mall map: {str(e)}")

        # Process each mapping
        processed_frame = frame_resized.copy()
        for zone in mappings:
            for obj in zone.get("objects", []):
                src_pts = np.array(obj["src_points"], dtype=np.float32)
                dst_pts = np.array(obj["dst_points"], dtype=np.float32)

                # Validate points
                if len(src_pts) != 4 or len(dst_pts) != 4:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid number of points for {zone['name']} - {obj['name']}. Expected 4 points, got {len(src_pts)} source and {len(dst_pts)} destination points."
                    )

                # Compute Homography
                try:
                    H, _ = cv2.findHomography(dst_pts, src_pts, method=cv2.RANSAC)
                    if H is None:
                        raise HTTPException(status_code=500, detail=f"Failed to compute homography for {zone['name']} - {obj['name']}")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error computing homography: {str(e)}")

                # Warp mall map onto the frame
                warped_map = cv2.warpPerspective(mall_map, H, target_size)

                # Create mask and overlay
                mask = np.zeros_like(frame_resized, dtype=np.uint8)
                cv2.fillConvexPoly(mask, np.int32(src_pts), (255, 255, 255))
                masked_warped = cv2.bitwise_and(warped_map, mask)
                processed_frame = cv2.addWeighted(processed_frame, 1, masked_warped, 0.6, 0)

                # Draw zone boundaries
                cv2.polylines(processed_frame, [np.int32(src_pts)], True, (0, 255, 0), 2)
                
                # Add zone and object name labels
                zone_name = zone["name"]
                object_name = obj["name"]
                label = f"{zone_name} - {object_name}"
                cv2.putText(processed_frame, label, 
                           (int(src_pts[0][0]), int(src_pts[0][1] - 10)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert processed frame to bytes
        _, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()

        # Return the processed frame as a streaming response
        return StreamingResponse(
            io.BytesIO(frame_bytes),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename=processed_frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/homography/test-mapping-stream")
async def test_mapping_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cap = None
    try:
        # Get camera details from database
        camera = get_camera(db, camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")

        # Get mall details to get the mall map
        mall = get_mall(db, camera.mall_id)
        if not mall:
            raise HTTPException(status_code=404, detail="Mall not found")
        
        if not mall.map_image:
            raise HTTPException(status_code=404, detail="Mall map image not found")

        # Construct RTSP URL
        rtsp_url = f"rtsp://{camera.username}:{camera.password}@{camera.ip_address}:554/cam/realmonitor?channel=1&subtype=0"
        
        # Open RTSP stream
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Failed to open camera stream")

        # Get homography mappings
        if not camera.homography_map or "zones" not in camera.homography_map:
            raise HTTPException(status_code=404, detail="No homography mappings found for this camera")

        mappings = camera.homography_map["zones"]

        # Load mall map from database
        try:
            # Convert the map image from database to numpy array
            nparr = np.frombuffer(mall.map_image, np.uint8)
            mall_map = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if mall_map is None:
                raise HTTPException(status_code=404, detail="Failed to decode mall map image")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading mall map: {str(e)}")

        target_size = (1366, 768)

        async def generate_frames():
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret or frame is None or frame.size == 0:
                        continue

                    try:
                        # Resize frame
                        frame_resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
                        if frame_resized.size == 0:
                            continue
                        processed_frame = frame_resized.copy()

                        # Process each mapping
                        for zone in mappings:
                            for obj in zone.get("objects", []):
                                src_pts = np.array(obj["src_points"], dtype=np.float32)
                                dst_pts = np.array(obj["dst_points"], dtype=np.float32)

                                # Validate points
                                if len(src_pts) != 4 or len(dst_pts) != 4:
                                    continue

                                # Compute Homography
                                try:
                                    H, _ = cv2.findHomography(dst_pts, src_pts, method=cv2.RANSAC)
                                    if H is None:
                                        continue
                                except Exception as e:
                                    print(f"Error computing homography: {str(e)}")
                                    continue

                                # Warp mall map onto the frame
                                warped_map = cv2.warpPerspective(mall_map, H, target_size)

                                # Create mask and overlay
                                mask = np.zeros_like(frame_resized, dtype=np.uint8)
                                cv2.fillConvexPoly(mask, np.int32(src_pts), (255, 255, 255))
                                masked_warped = cv2.bitwise_and(warped_map, mask)
                                processed_frame = cv2.addWeighted(processed_frame, 1, masked_warped, 0.6, 0)

                                # Draw zone boundaries
                                cv2.polylines(processed_frame, [np.int32(src_pts)], True, (0, 255, 0), 2)
                                
                                # Add zone and object name labels
                                zone_name = zone["name"]
                                object_name = obj["name"]
                                label = f"{zone_name} - {object_name}"
                                cv2.putText(processed_frame, label, 
                                           (int(src_pts[0][0]), int(src_pts[0][1] - 10)),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # Convert frame to JPEG
                        _, buffer = cv2.imencode('.jpg', processed_frame)
                        frame_bytes = buffer.tobytes()

                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

                    except Exception as e:
                        print(f"Error processing frame: {str(e)}")
                        continue

            except Exception as e:
                print(f"Error in frame generation: {str(e)}")
            finally:
                if cap is not None:
                    cap.release()

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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cap is not None:
            cap.release()