from fastapi import HTTPException, status, Response
from typing import Optional, Dict, Any
from fastapi.responses import RedirectResponse
from app.src.config.settings import settings
from app.src.schemas.user_schema import UserSchema, UserRegister, UserLogin, PasswordChange, UserLocationUpdate, UserNameUpdate
from app.src.utils.exceptions import AuthenticationException, DatabaseException
from app.src.schemas.auth_schema import (
    GoogleAuthResponse,
    UserResponse
)
from supabase import create_client, Client
from datetime import datetime, timedelta
from jose import JWTError, jwt

class AuthController:
    def __init__(self):
        # Use service role key for admin database operations
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        self.jwt_secret = settings.jwt_secret_key
        self.jwt_algorithm = settings.jwt_algorithm
        self.token_expire_minutes = settings.access_token_expire_minutes
    
    # Database operations
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from database"""
        try:
            result = self.supabase.table("users").select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_email_with_password(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from database with hashed_password for authentication"""
        try:
            result = self.supabase.table("users").select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username from database"""
        try:
            result = self.supabase.table("users").select("*").eq("username", username).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from database"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_id_with_password(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from database with hashed_password for password changes"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in database"""
        try:
            # Generate UUID for user ID if not provided
            if "id" not in user_data:
                import uuid
                user_data["id"] = str(uuid.uuid4())
            
            # Add timestamps
            user_data["created_at"] = datetime.utcnow().isoformat()
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.supabase.table("users").insert(user_data).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise DatabaseException("Failed to create user - no data returned")
                
        except Exception as e:
            raise DatabaseException(f"Error creating user: {str(e)}")
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing user in database"""
        try:
            # Add updated timestamp
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.supabase.table("users").update(user_data).eq("id", user_id).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise DatabaseException("Failed to update user")
                
        except Exception as e:
            raise DatabaseException(f"Error updating user: {str(e)}")
    
    async def update_user_password(self, user_id: str, hashed_password: str) -> bool:
        """Update user password"""
        try:
            result = self.supabase.table("users").update({
                "hashed_password": hashed_password,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            raise DatabaseException(f"Error updating password: {str(e)}")
    
    async def update_user_location(self, user_id: str, location_data: dict) -> Dict[str, Any]:
        """Update user location in database"""
        try:
            update_data = {
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Add location fields if provided
            if "location_address" in location_data:
                update_data["location_address"] = location_data["location_address"]
            if "location_geom" in location_data:
                update_data["location_geom"] = location_data["location_geom"]
            
            result = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise DatabaseException("Failed to update user location")
                
        except Exception as e:
            raise DatabaseException(f"Error updating user location: {str(e)}")
    
    async def update_user_name(self, user_id: str, name_data: dict) -> Dict[str, Any]:
        """Update user name in database"""
        try:
            update_data = {
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Add name fields if provided
            if "first_name" in name_data and name_data["first_name"] is not None:
                update_data["first_name"] = name_data["first_name"].strip()
            
            if "last_name" in name_data and name_data["last_name"] is not None:
                update_data["last_name"] = name_data["last_name"].strip()
            
            result = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise DatabaseException("Failed to update user name")
                
        except Exception as e:
            raise DatabaseException(f"Error updating user name: {str(e)}")
    
    # JWT operations
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

# Create controller instance
auth_controller = AuthController()