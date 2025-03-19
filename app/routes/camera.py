from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.camera import CameraCreate, CameraResponse
from ..crud import create_camera, get_camera, update_camera, delete_camera
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=CameraResponse)
def add_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    return create_camera(db, camera)

@router.get("/{camera_id}", response_model=CameraResponse)
def read_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = get_camera(db, camera_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera_route(camera_id: int, camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = update_camera(db, camera_id, camera)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

@router.delete("/{camera_id}")
def delete_camera_route(camera_id: int, db: Session = Depends(get_db)):
    delete_camera(db, camera_id)
    return {"detail": "Camera deleted"}
