from fastapi import APIRouter, Depends, Query, Response, Cookie, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Optional, Dict, Any
from src.config.settings import settings
from src.controllers.auth_controller import auth_controller
from src.models.user import User, UserProvider
from src.middleware.auth_middleware import get_current_user_required
from src.schemas.auth_schema import (
    GoogleAuthResponse, 
    UserResponse
)
from supabase import create_client, Client
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.utils.exceptions import AuthenticationException

# Create router with prefix and tags
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

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
    
    # Redirect to frontend with success message
    return result

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
    current_user: User = Depends(get_current_user_required)
) -> UserResponse:
    return await auth_controller.get_current_user_profile(current_user)

@auth_router.post("/logout", summary="Logout User")
async def logout(response: Response):
    """Logout user by clearing session cookie"""
    return await auth_controller.logout(response)