from pydantic import BaseModel, EmailStr
from typing import Optional

class GoogleAuthRequest(BaseModel):
    code: str
    state: Optional[str] = None

class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class AuthURLResponse(BaseModel):
    auth_url: str
    state: str