from fastapi import HTTPException, Depends, status, Cookie
from typing import Optional
from app.src.controllers.auth_controller import auth_controller
from app.src.schemas.user_schema import UserSchema

class AuthMiddleware:
    def __init__(self):
        pass  # No need to initialize service, we'll use controller directly
    
    async def get_current_user_optional(
        self, 
        access_token: str = Cookie(None)
    ) -> Optional[UserSchema]:
        """Get current user from cookie token, return None if not authenticated"""
        if not access_token:
            return None
            
        # Use controller directly for token verification and user retrieval
        payload = auth_controller.verify_token(access_token)
        if not payload:
            return None
            
        email = payload.get("sub")
        if not email:
            return None
            
        user_data = await auth_controller.get_user_by_email(email)
        if user_data:
            return UserSchema(**user_data)
        return None
    
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
            
        # Use controller directly for token verification and user retrieval
        payload = auth_controller.verify_token(access_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
            
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
            
        user_data = await auth_controller.get_user_by_email(email)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
            
        user = UserSchema(**user_data)
        
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