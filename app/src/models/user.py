from sqlalchemy import Column, String, Boolean, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.src.config.database import Base
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum as PydanticEnum
import uuid

# SQLAlchemy User Model for Database
class UserProvider(str, PydanticEnum):
    GOOGLE = "google"
    EMAIL = "email"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    provider = Column(String, nullable=True) # Added
    provider_id = Column(String, nullable=True) # Added
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic Models for API Schemas
class UserProviderEnum(str, PydanticEnum):
    GOOGLE = "google"
    EMAIL = "email"

class UserSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    username: Optional[str] = None
    provider: Optional[str] = None # Added
    provider_id: Optional[str] = None # Added
    is_active: Optional[bool] = True # Changed to Optional[bool]
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

# Password Authentication Schemas # New section
class UserRegister(BaseModel):
    email: EmailStr
    username: str
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

