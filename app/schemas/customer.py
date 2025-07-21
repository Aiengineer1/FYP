from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CustomerBase(BaseModel):
    age: int
    gender: str
    entry_time: datetime
    exit_time: Optional[datetime]
    routes: dict
    interactions: dict
    visited_zones: List[str]

class CustomerCreate(CustomerBase):
    mall_id: int

class CustomerResponse(CustomerBase):
    id: int
    mall_id: int

    class Config:
        from_attributes = True
