from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum as PydanticEnum
import uuid

# Pydantic Models for API Schemas
class UserProviderEnum(str, PydanticEnum):
    GOOGLE = "google"
    EMAIL = "email"

class UserSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    provider: Optional[str] = None
    provider_id: Optional[str] = None
    location_geom: Optional[str] = None  # WKT format for geometry
    location_address: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }

class UserSchemaWithPassword(UserSchema):
    """Internal schema that includes hashed_password for authentication"""
    hashed_password: Optional[str] = None

class UserInDB(UserSchema):
    hashed_password: Optional[str] = None

# Password Authentication Schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLocationUpdate(BaseModel):
    """Schema for updating user location"""
    location_address: Optional[str] = None
    
    @validator('location_address')
    def validate_location_address(cls, v):
        if v is not None and len(v.strip()) < 5:
            raise ValueError('Address must be at least 5 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v