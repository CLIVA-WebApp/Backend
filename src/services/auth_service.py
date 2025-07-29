import logging
from supabase import create_client, Client
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from src.config.settings import settings
from src.models.user import User, UserProvider, UserSchema
from src.services.user_service import UserService
from src.utils.exceptions import AuthenticationException

class AuthService:
    def __init__(self):
        self.user_service = UserService()
        # Use anon key for OAuth operations
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        self.jwt_secret = settings.jwt_secret_key
        self.jwt_algorithm = settings.jwt_algorithm
        self.token_expire_minutes = settings.access_token_expire_minutes
    
    def generate_google_auth_url(self) -> str:
        """Generate Google OAuth authorization URL - backend handles the entire flow"""
        try:
            # Generate OAuth URL that redirects back to our backend
            auth_response = self.supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": f"{settings.backend_url}/api/v1/auth/google/callback"
                }
            })
            
            return auth_response.url
            
        except Exception as e:
            raise AuthenticationException(f"Failed to generate Google OAuth URL: {str(e)}")
    
    async def handle_oauth_callback(self, code: str, state: str = None) -> tuple[UserSchema, str]:
        """Handle OAuth callback and exchange code for session"""
        try:
            # Exchange code for session
            auth_response = self.supabase.auth.exchange_code_for_session({
                "auth_code": code
            })

            logging.info(f"Auth response: {auth_response}")
            
            if not auth_response.user:
                raise AuthenticationException("No user data received from OAuth provider")
            
            supabase_user = auth_response.user
            
            # Extract user data from OAuth response
            user_data = {
                "email": supabase_user.email,
                "username": supabase_user.user_metadata.get("full_name") or supabase_user.user_metadata.get("name"),
                "provider": UserProvider.GOOGLE,
                "provider_id": supabase_user.id,
                "is_active": True  # Add this line to set is_active to True
            }
            
            # Create or update user in our database
            user = await self.user_service.create_or_update_user(user_data)
            
            # Generate our own JWT token
            jwt_token = self.create_access_token({"sub": user.email, "user_id": user.id})
            
            return user, jwt_token
            
        except Exception as e:
            raise AuthenticationException(f"OAuth callback failed: {str(e)}")
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except JWTError:
            return None
    
    async def get_current_user(self, token: str) -> Optional[UserSchema]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None
            
        email = payload.get("sub")
        if not email:
            return None
            
        return await self.user_service.get_user_by_email(email)