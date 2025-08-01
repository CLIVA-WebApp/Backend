from fastapi import HTTPException, status, Depends, Response
from typing import Optional
from fastapi.responses import RedirectResponse
from app.src.config.settings import settings
from app.src.services.auth_service import AuthService
from app.src.schemas.user_schema import UserSchema, UserRegister, UserLogin, PasswordChange, UserLocationUpdate
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.utils.exceptions import AuthenticationException
from app.src.schemas.auth_schema import (
    GoogleAuthResponse,
    UserResponse
)

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
    
    async def get_google_auth_url(self) -> dict:
        """Generate Google OAuth authorization URL"""
        try:
            auth_url = self.auth_service.generate_google_auth_url()
            return {"auth_url": auth_url}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate auth URL: {str(e)}"
            )
    
    async def handle_google_callback(self, code: str, state: str = None) -> dict:
        """Handle Google OAuth callback and set session cookie"""
        try:
            user, jwt_token = await self.auth_service.handle_oauth_callback(code, state)
            
            response = RedirectResponse(url=f"{settings.frontend_url}/auth/success", status_code=302)

            # Set HTTP-only cookie with the JWT token
            response.set_cookie(
                key="access_token",
                value=jwt_token,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax",
                max_age=self.auth_service.token_expire_minutes * 60
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
    
    async def verify_session(self, access_token: str) -> dict:
        """Verify session and return user data"""
        try:
            user = await self.auth_service.get_current_user(access_token)
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
    
    async def logout(self, response: Response) -> dict:
        """Logout user by clearing session cookie"""
        response.delete_cookie("access_token")
        return {"message": "Successfully logged out"}
    
    async def register_user(self, user_data: UserRegister, response: Response) -> dict:
        """Register a new user with email/password"""
        try:
            user, jwt_token = await self.auth_service.register_user(user_data)
            
            # Set HTTP-only cookie with the JWT token
            response.set_cookie(
                key="access_token",
                value=jwt_token,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax",
                max_age=self.auth_service.token_expire_minutes * 60
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
    
    async def login_user(self, login_data: UserLogin, response: Response) -> dict:
        """Login user with email/password"""
        try:
            user, jwt_token = await self.auth_service.login_user(login_data)
            
            # Set HTTP-only cookie with the JWT token
            response.set_cookie(
                key="access_token",
                value=jwt_token,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax",
                max_age=self.auth_service.token_expire_minutes * 60
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
    
    async def change_password(
        self, 
        password_data: PasswordChange,
        current_user: UserSchema = Depends(get_current_user_required)
    ) -> dict:
        """Change user password"""
        try:
            success = await self.auth_service.change_password(
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
    
    async def get_current_user_profile(
        self, 
        current_user: UserSchema = Depends(get_current_user_required)
    ) -> UserResponse:
        """Get current authenticated user profile"""
        return UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            full_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.username,
            avatar_url=None,  # Not available in current schema
            provider="google",  # Default to google for OAuth users
            is_active=current_user.is_active
        )
    
    async def update_user_location(
        self, 
        location_data: UserLocationUpdate,
        current_user: UserSchema = Depends(get_current_user_required)
    ) -> dict:
        """Update user location with automatic geocoding"""
        try:
            # Convert location data to dict, excluding None values
            location_dict = {}
            if location_data.location_address is not None:
                location_dict["location_address"] = location_data.location_address
            
            updated_user = await self.auth_service.update_user_location(str(current_user.id), location_dict)
            
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

# Create controller instance
auth_controller = AuthController()