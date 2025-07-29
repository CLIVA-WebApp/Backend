from supabase import create_client, Client
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from src.config.settings import settings
from src.models.user import User, UserProvider
from src.services.user_service import UserService
from src.utils.exceptions import AuthenticationException

class AuthService:
    def __init__(self):
        self.user_service = UserService()
        # Use service role key for admin operations
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        self.jwt_secret = settings.jwt_secret_key
        self.jwt_algorithm = settings.jwt_algorithm
        self.token_expire_minutes = settings.access_token_expire_minutes
    
    def generate_google_auth_url(self) -> tuple[str, str]:
        """Generate Google OAuth authorization URL using Supabase Auth"""
        state = secrets.token_urlsafe(32)
        
        # Use Supabase Auth for Google OAuth
        redirect_url = f"{settings.frontend_url}/auth/callback"
        
        try:
            # Supabase Auth Google OAuth URL
            auth_response = self.supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": redirect_url,
                    "query_params": {
                        "state": state
                    }
                }
            })
            
            return auth_response.url, state
            
        except Exception as e:
            raise AuthenticationException(f"Failed to generate Supabase auth URL: {str(e)}")
    
    async def authenticate_google_user(self, code: str) -> tuple[User, str]:
        """Complete Google OAuth flow using Supabase Auth and return user with JWT token"""
        try:
            # Exchange code for session using Supabase Auth
            auth_response = self.supabase.auth.exchange_code_for_session({
                "auth_code": code
            })
            
            if not auth_response.user:
                raise AuthenticationException("No user data received from Supabase")
            
            supabase_user = auth_response.user
            
            # Extract user data from Supabase Auth response
            user_data = {
                "email": supabase_user.email,
                "full_name": supabase_user.user_metadata.get("full_name") or supabase_user.user_metadata.get("name"),
                "avatar_url": supabase_user.user_metadata.get("avatar_url") or supabase_user.user_metadata.get("picture"),
                "provider": UserProvider.GOOGLE,
                "provider_id": supabase_user.id
            }
            
            # Create or update user in your custom users table
            user = await self.user_service.create_or_update_user(user_data)
            
            # Generate your own JWT token (or you can use Supabase's access_token)
            jwt_token = self.create_access_token({"sub": user.email, "user_id": user.id})
            
            return user, jwt_token
            
        except Exception as e:
            raise AuthenticationException(f"Supabase authentication failed: {str(e)}")
    
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
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None
            
        email = payload.get("sub")
        if not email:
            return None
            
        return await self.user_service.get_user_by_email(email)