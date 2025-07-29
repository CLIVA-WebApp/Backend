from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.services.auth_service import AuthService
from src.models.user import User

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self):
        self.auth_service = AuthService()
    
    async def get_current_user_optional(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[User]:
        """Get current user from token, return None if not authenticated"""
        if not credentials:
            return None
            
        token = credentials.credentials
        user = await self.auth_service.get_current_user(token)
        return user
    
    async def get_current_user_required(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """Get current user from token, raise exception if not authenticated"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = credentials.credentials
        user = await self.auth_service.get_current_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
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
    user: Optional[User] = Depends(auth_middleware.get_current_user_optional)
) -> Optional[User]:
    return user

async def get_current_user_required(
    user: User = Depends(auth_middleware.get_current_user_required)
) -> User:
    return user