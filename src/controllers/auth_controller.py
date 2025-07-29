from fastapi import HTTPException, status, Depends, Response
from typing import Optional

from fastapi.responses import RedirectResponse
from src.config.settings import settings
from src.services.auth_service import AuthService
from src.models.user import User, UserProvider, UserSchema
from src.middleware.auth_middleware import get_current_user_required
from src.utils.exceptions import AuthenticationException
from src.schemas.auth_schema import (
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
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
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
    
    async def get_current_user_profile(
        self, 
        current_user: UserSchema = Depends(get_current_user_required)
    ) -> UserResponse:
        """Get current authenticated user profile"""
        return UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.username,  # Use username as full_name
            avatar_url=None,  # Not available in current schema
            provider="google",  # Default to google for OAuth users
            is_active=current_user.is_active
        )

# Create controller instance
auth_controller = AuthController()