from fastapi import HTTPException, status, Depends
from typing import Optional
from src.services.auth_service import AuthService
from src.models.user import User
from src.middleware.auth_middleware import get_current_user_required
from src.utils.exceptions import AuthenticationException
from src.schemas.auth_schema import (
    GoogleAuthRequest, 
    GoogleAuthResponse, 
    AuthURLResponse,
    UserResponse
)

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
    
    async def get_google_auth_url(self) -> AuthURLResponse:
        """Generate Google OAuth authorization URL"""
        try:
            auth_url, state = self.auth_service.generate_google_auth_url()
            return AuthURLResponse(auth_url=auth_url, state=state)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate auth URL: {str(e)}"
            )
    
    async def google_callback(self, auth_request: GoogleAuthRequest) -> GoogleAuthResponse:
        """Handle Google OAuth callback"""
        try:
            user, jwt_token = await self.auth_service.authenticate_google_user(auth_request.code)
            
            return GoogleAuthResponse(
                access_token=jwt_token,
                token_type="bearer",
                expires_in=self.auth_service.token_expire_minutes * 60,
                user={
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "provider": user.provider,
                    "is_active": user.is_active
                }
            )
        
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
    
    async def get_current_user_profile(
        self, 
        current_user: User = Depends(get_current_user_required)
    ) -> UserResponse:
        """Get current authenticated user profile"""
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            avatar_url=current_user.avatar_url,
            provider=current_user.provider,
            is_active=current_user.is_active
        )
    
    async def logout(
        self, 
        current_user: User = Depends(get_current_user_required)
    ) -> dict:
        """Logout current user (client-side token removal)"""
        # In a stateless JWT system, logout is typically handled client-side
        # by removing the token. You could implement token blacklisting here
        # if needed for enhanced security
        
        return {"message": "Successfully logged out"}

# Create controller instance
auth_controller = AuthController()