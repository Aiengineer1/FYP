from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MallBase(BaseModel):
    name: str
    address: str
    contact_email: Optional[str] = None
    contact_number: Optional[str] = None

class MallCreate(MallBase):
    user_id: int  # ID of the mall owner
    map_image: bytes  # Required map image

class MallResponse(MallBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class MallResponseWithImage(MallResponse):
    map_image: bytes

    model_config = {"from_attributes": True}
