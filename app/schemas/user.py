from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "newpassword123"
            }
        }
    }

class UserResponse(UserBase):
    id: int
    mall_id: Optional[int] = None
    created_at: datetime
    user_id: Optional[int] = None  # Make user_id optional and computed

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        # Ensure user_id is always set to id
        self.user_id = self.id

# New schemas for settings endpoints
class UserProfileUpdate(BaseModel):
    full_name: str
    mall_contact_email: Optional[str] = None
    mall_contact_number: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "John Doe",
                "mall_contact_email": "mall@example.com",
                "mall_contact_number": "+1234567890"
            }
        }
    }

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }
    }

class CameraDefaultsUpdate(BaseModel):
    default_rtsp_username: str
    default_rtsp_password: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "default_rtsp_username": "admin",
                "default_rtsp_password": "camera123"
            }
        }
    }

class UserSettingsResponse(BaseModel):
    user: Dict[str, str | int]
    mall: Dict[str, str]
    camera_defaults: Optional[Dict[str, str]] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "user": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "id": 1,
                    "user_id": 1
                },
                "mall": {
                    "name": "Sample Mall",
                    "address": "123 Mall Street"
                },
                "camera_defaults": {
                    "username": "admin",
                    "password": "camera123"
                }
            }
        }
    }

class LoginResponse(BaseModel):
    access_token: str
    user_id: int
    email: str
    name: str
    mall_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user_id": 1,
                "email": "john@example.com",
                "name": "John Doe",
                "mall_id": 1
            }
        }
    }

class MallStatusResponse(BaseModel):
    has_mall: bool
    mall_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "has_mall": True,
                "mall_id": 1
            }
        }
    }