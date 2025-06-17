from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict

class CameraBase(BaseModel):
    name: str
    ip_address: str
    username: str
    password: str
    location: str
    homography_map: Optional[Dict] = Field(default_factory=dict)
    fov_zones: Optional[Dict] = Field(default_factory=dict)

class CameraCreate(CameraBase):
    mall_id: int

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    location: Optional[str] = None
    homography_map: Optional[Dict] = None
    fov_zones: Optional[Dict] = None

class CameraResponse(CameraBase):
    id: int
    mall_id: int
    created_at: datetime

    class Config:
        from_attributes = True
