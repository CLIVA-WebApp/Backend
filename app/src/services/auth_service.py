import logging
from supabase import create_client, Client
from typing import Optional, Dict, Any, Tuple
import secrets
from app.src.config.settings import settings
from app.src.models.user import User, UserProvider
from app.src.schemas.user_schema import UserSchema, UserRegister, UserLogin
from app.src.controllers.auth_controller import auth_controller
from app.src.services.geocoding_service import GeocodingService
from app.src.utils.exceptions import AuthenticationException
from app.src.utils.password import hash_password, verify_password, is_password_strong

class AuthService:
    def __init__(self):
        self.geocoding_service = GeocodingService()
        # Use anon key for OAuth operations
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
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
    
    async def handle_oauth_callback(self, code: str, state: str = None) -> Tuple[UserSchema, str]:
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
            full_name = supabase_user.user_metadata.get("full_name") or supabase_user.user_metadata.get("name") or ""
            
            # Extract first and last name from full name
            name_parts = full_name.strip().split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
            elif len(name_parts) == 1:
                first_name = name_parts[0]
                last_name = ""
            else:
                first_name = ""
                last_name = ""
            
            user_data = {
                "email": supabase_user.email,
                "username": full_name,
                "first_name": first_name,
                "last_name": last_name,
                "provider": UserProvider.GOOGLE,
                "provider_id": supabase_user.id,
                "is_active": True
            }
            
            # Create or update user in our database
            user = await self.create_or_update_user(user_data)
            
            # Generate our own JWT token
            jwt_token = auth_controller.create_access_token({"sub": user.email, "user_id": str(user.id)})
            
            return user, jwt_token
            
        except Exception as e:
            raise AuthenticationException(f"OAuth callback failed: {str(e)}")
    
    async def register_user(self, user_data: UserRegister) -> Tuple[UserSchema, str]:
        """Register a new user with email/password"""
        try:
            # Check if user already exists
            existing_user_data = await auth_controller.get_user_by_email(user_data.email)
            if existing_user_data:
                raise AuthenticationException("User with this email already exists")
            
            # Check if username is taken
            existing_username_data = await auth_controller.get_user_by_username(user_data.username)
            if existing_username_data:
                raise AuthenticationException("Username already taken")
            
            # Validate password strength
            is_strong, error_msg = is_password_strong(user_data.password)
            if not is_strong:
                raise AuthenticationException(error_msg)
            
            # Hash password
            hashed_password = hash_password(user_data.password)
            
            # Create user data
            user_create_data = {
                "email": user_data.email,
                "username": user_data.username,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "hashed_password": hashed_password,
                "provider": UserProvider.EMAIL,
                "is_active": True
            }
            
            # Create user in database
            created_user_data = await auth_controller.create_user(user_create_data)
            user = UserSchema(**created_user_data)
            
            # Generate JWT token
            jwt_token = auth_controller.create_access_token({"sub": user.email, "user_id": str(user.id)})
            
            return user, jwt_token
            
        except AuthenticationException:
            raise
        except Exception as e:
            raise AuthenticationException(f"Registration failed: {str(e)}")
    
    async def login_user(self, login_data: UserLogin) -> Tuple[UserSchema, str]:
        """Login user with email/password"""
        try:
            # Get user by email with password for verification
            user_data = await auth_controller.get_user_by_email_with_password(login_data.email)
            if not user_data:
                raise AuthenticationException("Invalid email or password")
            
            user = UserSchema(**user_data)
            
            # Check if user has password (not OAuth only)
            if not user.hashed_password:
                raise AuthenticationException("This account was created with OAuth. Please use OAuth to login.")
            
            # Verify password
            if not verify_password(login_data.password, user.hashed_password):
                raise AuthenticationException("Invalid email or password")
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationException("Account is deactivated")
            
            # Generate JWT token
            jwt_token = auth_controller.create_access_token({"sub": user.email, "user_id": str(user.id)})
            
            return user, jwt_token
            
        except AuthenticationException:
            raise
        except Exception as e:
            raise AuthenticationException(f"Login failed: {str(e)}")
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Get user with password for verification
            user_data = await auth_controller.get_user_by_id_with_password(user_id)
            if not user_data:
                raise AuthenticationException("User not found")
            
            user = UserSchema(**user_data)
            
            # Verify current password
            if not verify_password(current_password, user.hashed_password):
                raise AuthenticationException("Current password is incorrect")
            
            # Validate new password strength
            is_strong, error_msg = is_password_strong(new_password)
            if not is_strong:
                raise AuthenticationException(error_msg)
            
            # Hash new password
            hashed_password = hash_password(new_password)
            
            # Update password
            await auth_controller.update_user_password(user_id, hashed_password)
            
            return True
            
        except AuthenticationException:
            raise
        except Exception as e:
            raise AuthenticationException(f"Password change failed: {str(e)}")
    
    async def get_current_user(self, token: str) -> Optional[UserSchema]:
        """Get current user from JWT token"""
        payload = auth_controller.verify_token(token)
        if not payload:
            return None
            
        email = payload.get("sub")
        if not email:
            return None
            
        user_data = await auth_controller.get_user_by_email(email)
        if user_data:
            return UserSchema(**user_data)
        return None
    
    async def update_user_location(self, user_id: str, location_data: dict) -> UserSchema:
        """Update user location with automatic geocoding"""
        try:
            # If address is provided, geocode it to get coordinates
            if "location_address" in location_data and location_data["location_address"]:
                address = location_data["location_address"]
                
                # Geocode the address
                geocoding_result = await self.geocoding_service.geocode_address(address)
                
                if geocoding_result:
                    # Update with both address and geometry
                    location_data["location_geom"] = geocoding_result["wkt_point"]
                # If geocoding fails, still save the address but location_geom will remain null
            
            # Update user location in database
            updated_user_data = await auth_controller.update_user_location(user_id, location_data)
            return UserSchema(**updated_user_data)
            
        except Exception as e:
            raise AuthenticationException(f"Failed to update user location: {str(e)}")
    
    async def update_user_name(self, user_id: str, name_data: dict) -> UserSchema:
        """Update user name (first_name and last_name)"""
        try:
            updated_user_data = await auth_controller.update_user_name(user_id, name_data)
            return UserSchema(**updated_user_data)
        except Exception as e:
            raise AuthenticationException(f"Failed to update user name: {str(e)}")
    
    async def create_or_update_user(self, user_data: Dict[str, Any]) -> UserSchema:
        """Create user if doesn't exist, otherwise update existing user"""
        existing_user_data = await auth_controller.get_user_by_email(user_data["email"])
        
        if existing_user_data:
            # Update existing user with new data
            update_data = {
                "username": user_data.get("username", existing_user_data["username"]),
                "email": user_data.get("email", existing_user_data["email"]),
                "first_name": user_data.get("first_name", existing_user_data["first_name"]),
                "last_name": user_data.get("last_name", existing_user_data["last_name"]),
                "provider": user_data.get("provider", existing_user_data["provider"]),
                "provider_id": user_data.get("provider_id", existing_user_data["provider_id"]),
                "is_active": user_data.get("is_active", existing_user_data["is_active"])
            }
            updated_user_data = await auth_controller.update_user(str(existing_user_data["id"]), update_data)
            return UserSchema(**updated_user_data)
        else:
            # Create new user
            created_user_data = await auth_controller.create_user(user_data)
            return UserSchema(**created_user_data)