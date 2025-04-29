from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import numpy as np
from ..dependencies import get_current_user

router = APIRouter()

class RTSPRequest(BaseModel):
    rtsp_url: str

@router.post("/camera/frame")
async def get_camera_frame(
    request: RTSPRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Open RTSP stream
        cap = cv2.VideoCapture(request.rtsp_url)
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