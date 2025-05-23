from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import numpy as np
from typing import Optional
import io

router = APIRouter()

class RTSPRequest(BaseModel):
    rtsp_url: str

@router.post("/camera/frame")
async def get_camera_frame(request: RTSPRequest):
    try:
        # Open RTSP stream
        cap = cv2.VideoCapture(request.rtsp_url)
        
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Failed to open RTSP stream")
        
        # Read a frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=400, detail="Failed to read frame from stream")
        
        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = io.BytesIO(buffer.tobytes())
        
        return StreamingResponse(frame_bytes, media_type="image/jpeg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 