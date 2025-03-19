from pydantic import BaseModel
from datetime import datetime

class CameraBase(BaseModel):
    name: str
    ip_address: str
    username: str
    password: str
    location: str
    homography_map: dict
    fov_zones: dict

class CameraCreate(CameraBase):
    mall_id: int

class CameraResponse(CameraBase):
    id: int
    mall_id: int
    created_at: datetime

    class Config:
        from_attributes = True
