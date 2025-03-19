from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MallBase(BaseModel):
    name: str
    address: str

class MallCreate(MallBase):
    user_id: int  # ID of the mall owner
    map_image: bytes  # Required map image

class MallResponse(MallBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MallResponseWithImage(MallResponse):
    map_image: bytes

    class Config:
        from_attributes = True
