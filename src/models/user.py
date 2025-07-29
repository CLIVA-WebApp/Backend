from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Index
from sqlalchemy.sql import func
from src.config.database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum as PydanticEnum

# SQLAlchemy User Model for Database
class UserProvider(str, PydanticEnum):
    GOOGLE = "google"
    EMAIL = "email"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic Models for API Schemas
class UserProviderEnum(str, PydanticEnum):
    GOOGLE = "google"
    EMAIL = "email"

class UserSchema(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserInDB(UserSchema):
    hashed_password: Optional[str] = None