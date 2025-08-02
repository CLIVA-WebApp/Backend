from fastapi import APIRouter, Depends, Query, Response, Cookie, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Optional, Dict, Any
from app.src.config.settings import settings
from app.src.controllers.auth_controller import auth_controller
from app.src.schemas.user_schema import UserSchema, UserRegister, UserLogin, PasswordChange, UserLocationUpdate, UserNameUpdate
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.schemas.auth_schema import (
    GoogleAuthResponse, 
    UserResponse
)
from supabase import create_client, Client
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets
from app.src.services.auth_service import AuthService
from app.src.services.user_service import UserService
from app.src.utils.exceptions import AuthenticationException

# Create router with prefix and tags
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth endpoints
@auth_router.get("/google", summary="Redirect to Google OAuth")
async def redirect_to_google():
    """Redirect to Google OAuth - backend handles the entire flow"""
    auth_data = await auth_controller.get_google_auth_url()
    return RedirectResponse(url=auth_data["auth_url"])

@auth_router.get("/google/callback", summary="OAuth Callback")
async def google_callback(
    code: str = Query(...), 
    state: str = Query(None),
):
    """Handle OAuth callback and set session cookie"""
    result = await auth_controller.handle_google_callback(code, state)
    return result

# Password authentication endpoints
@auth_router.post("/register", summary="Register User")
async def register_user(user_data: UserRegister, response: Response):
    """Register a new user with email/password"""
    return await auth_controller.register_user(user_data, response)

@auth_router.post("/login", summary="Login User")
async def login_user(login_data: UserLogin, response: Response):
    """Login user with email/password"""
    return await auth_controller.login_user(login_data, response)

@auth_router.post("/change-password", summary="Change Password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserSchema = Depends(get_current_user_required)
):
    """Change user password"""
    return await auth_controller.change_password(password_data, current_user)

# Session management endpoints
@auth_router.get("/session/verify", summary="Verify Session")
async def verify_session(access_token: str = Cookie(None)):
    """Verify session and return user data"""
    if not access_token:
        raise HTTPException(status_code=401, detail="No session found")
    
    return await auth_controller.verify_session(access_token)

@auth_router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current authenticated user profile information"
)
async def get_current_user_profile(
    current_user: UserSchema = Depends(get_current_user_required)
) -> UserResponse:
    return await auth_controller.get_current_user_profile(current_user)

@auth_router.post("/logout", summary="Logout User")
async def logout(response: Response):
    """Logout user by clearing session cookie"""
    return await auth_controller.logout(response)

@auth_router.put("/location", summary="Update User Location")
async def update_user_location(
    location_data: UserLocationUpdate,
    current_user: UserSchema = Depends(get_current_user_required)
):
    """Update user location (address and/or geometry)"""
    return await auth_controller.update_user_location(location_data, current_user)

@auth_router.put("/name", summary="Update User Name")
async def update_user_name(
    name_data: UserNameUpdate,
    current_user: UserSchema = Depends(get_current_user_required)
):
    """Update user name (first_name and last_name) - OAuth users cannot update names"""
    return await auth_controller.update_user_name(name_data, current_user)