from fastapi import HTTPException, Depends, status, Cookie
from typing import Optional
from app.src.services.auth_service import AuthService
from app.src.schemas.user_schema import UserSchema

class AuthMiddleware:
    def __init__(self):
        self.auth_service = AuthService()
    
    async def get_current_user_optional(
        self, 
        access_token: str = Cookie(None)
    ) -> Optional[UserSchema]:
        """Get current user from cookie token, return None if not authenticated"""
        if not access_token:
            return None
            
        user = await self.auth_service.get_current_user(access_token)
        return user
    
    async def get_current_user_required(
        self, 
        access_token: str = Cookie(None)
    ) -> UserSchema:
        """Get current user from cookie token, raise exception if not authenticated"""
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
            
        user = await self.auth_service.get_current_user(access_token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
            
        return user

# Create middleware instance
auth_middleware = AuthMiddleware()

# Dependency functions
async def get_current_user_optional(
    user: Optional[UserSchema] = Depends(auth_middleware.get_current_user_optional)
) -> Optional[UserSchema]:
    return user

async def get_current_user_required(
    user: UserSchema = Depends(auth_middleware.get_current_user_required)
) -> UserSchema:
    return user