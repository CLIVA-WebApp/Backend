from fastapi import APIRouter, Depends, Query, Response, Cookie, HTTPException, status
from typing import Optional, Dict, Any
from fastapi.responses import RedirectResponse
from app.src.config.settings import settings
from app.src.services.auth_service import AuthService
from app.src.schemas.user_schema import UserSchema, UserRegister, UserLogin, PasswordChange, UserLocationUpdate, UserNameUpdate
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.schemas.auth_schema import (
    GoogleAuthResponse, 
    UserResponse
)
from app.src.utils.exceptions import AuthenticationException

# Create router with prefix and tags
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize service
auth_service = AuthService()

# OAuth endpoints
@auth_router.get("/google", summary="Redirect to Google OAuth")
async def redirect_to_google():
    """Redirect to Google OAuth - backend handles the entire flow"""
    try:
        auth_url = auth_service.generate_google_auth_url()
        return RedirectResponse(url=auth_url)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate auth URL: {str(e)}"
        )

@auth_router.get("/google/callback", summary="OAuth Callback")
async def google_callback(
    code: str = Query(...), 
    state: str = Query(None),
):
    """Handle OAuth callback and set session cookie"""
    try:
        user, jwt_token = await auth_service.handle_oauth_callback(code, state)
        
        response = RedirectResponse(url=f"{settings.frontend_url}/auth/success", status_code=302)

        # Set HTTP-only cookie with the JWT token
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=settings.access_token_expire_minutes * 60
        )
        
        return response
    
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

# Password authentication endpoints
@auth_router.post("/register", summary="Register User")
async def register_user(user_data: UserRegister, response: Response):
    """Register a new user with email/password"""
    try:
        user, jwt_token = await auth_service.register_user(user_data)
        
        # Set HTTP-only cookie with the JWT token
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=settings.access_token_expire_minutes * 60
        )
        
        return {
            "message": "Registration successful",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "location_address": user.location_address,
                "is_active": user.is_active
            }
        }
    
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@auth_router.post("/login", summary="Login User")
async def login_user(login_data: UserLogin, response: Response):
    """Login user with email/password"""
    try:
        user, jwt_token = await auth_service.login_user(login_data)
        
        # Set HTTP-only cookie with the JWT token
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=settings.access_token_expire_minutes * 60
        )
        
        return {
            "message": "Login successful",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "location_address": user.location_address,
                "is_active": user.is_active
            }
        }
    
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@auth_router.post("/change-password", summary="Change Password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserSchema = Depends(get_current_user_required)
):
    """Change user password"""
    try:
        success = await auth_service.change_password(
            str(current_user.id),
            password_data.current_password,
            password_data.new_password
        )
        
        return {"message": "Password changed successfully"}
    
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )

# Session management endpoints
@auth_router.get("/session/verify", summary="Verify Session")
async def verify_session(access_token: str = Cookie(None)):
    """Verify session and return user data"""
    if not access_token:
        raise HTTPException(status_code=401, detail="No session found")
    
    try:
        user = await auth_service.get_current_user(access_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )
        
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "location_address": user.location_address,
                "is_active": user.is_active
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session verification failed"
        )

@auth_router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current authenticated user profile information"
)
async def get_current_user_profile(
    current_user: UserSchema = Depends(get_current_user_required)
) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.username,
        avatar_url=None,  # Not available in current schema
        provider="google",  # Default to google for OAuth users
        is_active=current_user.is_active
    )

@auth_router.post("/logout", summary="Logout User")
async def logout(response: Response):
    """Logout user by clearing session cookie"""
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}

@auth_router.put("/location", summary="Update User Location")
async def update_user_location(
    location_data: UserLocationUpdate,
    current_user: UserSchema = Depends(get_current_user_required)
):
    """Update user location (address and/or geometry)"""
    try:
        # Convert location data to dict, excluding None values
        location_dict = {}
        if location_data.location_address is not None:
            location_dict["location_address"] = location_data.location_address
        
        updated_user = await auth_service.update_user_location(str(current_user.id), location_dict)
        
        # Determine if geocoding was successful
        geocoding_success = updated_user.location_geom is not None
        
        return {
            "message": "Location updated successfully" + (" (coordinates found)" if geocoding_success else " (address saved, coordinates not found)"),
            "user": {
                "id": str(updated_user.id),
                "email": updated_user.email,
                "username": updated_user.username,
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "location_address": updated_user.location_address,
                "has_coordinates": geocoding_success,
                "is_active": updated_user.is_active
            }
        }
    
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Location update failed: {str(e)}"
        )

@auth_router.put("/name", summary="Update User Name")
async def update_user_name(
    name_data: UserNameUpdate,
    current_user: UserSchema = Depends(get_current_user_required)
):
    """Update user name (first_name and last_name) - OAuth users cannot update names"""
    try:
        # Check if user is OAuth user (Google)
        if current_user.provider == "google":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="OAuth users cannot update their names. Names are managed by your Google account."
            )
        
        # Convert name data to dict, excluding None values
        name_dict = {}
        if name_data.first_name is not None:
            name_dict["first_name"] = name_data.first_name
        if name_data.last_name is not None:
            name_dict["last_name"] = name_data.last_name
        
        # Check if at least one field is provided
        if not name_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one name field (first_name or last_name) must be provided"
            )
        
        updated_user = await auth_service.update_user_name(str(current_user.id), name_dict)
        
        return {
            "message": "Name updated successfully",
            "user": {
                "id": str(updated_user.id),
                "email": updated_user.email,
                "username": updated_user.username,
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "provider": updated_user.provider,
                "is_active": updated_user.is_active
            }
        }
    
    except HTTPException:
        raise
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Name update failed: {str(e)}"
        )