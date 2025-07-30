from datetime import datetime
from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.src.config.settings import settings
from app.src.schemas.user_schema import UserSchema, UserSchemaWithPassword
from app.src.utils.exceptions import DatabaseException

class UserService:
    def __init__(self):
        # Use service role key for admin database operations
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key  # Changed from anon_key
        )
    
    async def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        """Get user by email from database"""
        try:
            result = self.supabase.table("users").select("*").eq("email", email).execute()
            
            if result.data:
                user_data = result.data[0]
                return UserSchema(**user_data)
            return None
            
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_email_with_password(self, email: str) -> Optional[UserSchemaWithPassword]:
        """Get user by email from database with hashed_password for authentication"""
        try:
            result = self.supabase.table("users").select("*").eq("email", email).execute()
            
            if result.data:
                user_data = result.data[0]
                return UserSchemaWithPassword(**user_data)
            return None
            
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_username(self, username: str) -> Optional[UserSchema]:
        """Get user by username from database"""
        try:
            result = self.supabase.table("users").select("*").eq("username", username).execute()
            
            if result.data:
                user_data = result.data[0]
                return UserSchema(**user_data)
            return None
            
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserSchema]:
        """Get user by ID from database"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if result.data:
                user_data = result.data[0]
                return UserSchema(**user_data)
            return None
            
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_id_with_password(self, user_id: int) -> Optional[UserSchemaWithPassword]:
        """Get user by ID from database with hashed_password for password changes"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if result.data:
                user_data = result.data[0]
                return UserSchemaWithPassword(**user_data)
            return None
            
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def create_user(self, user_data: Dict[str, Any]) -> UserSchema:
        """Create a new user in database"""
        try:
            # Add timestamps
            user_data["created_at"] = datetime.utcnow().isoformat()
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Debug logging
            print(f"Creating user with data: {user_data}")
            
            result = self.supabase.table("users").insert(user_data).execute()
            
            # Debug logging
            print(f"Insert result: {result}")
            
            if result.data:
                created_user = result.data[0]
                return UserSchema(**created_user)
            else:
                raise DatabaseException("Failed to create user - no data returned")
                
        except Exception as e:
            print(f"Error creating user: {str(e)}")  # Debug logging
            raise DatabaseException(f"Error creating user: {str(e)}")
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> UserSchema:
        """Update existing user in database"""
        try:
            # Add updated timestamp
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.supabase.table("users").update(user_data).eq("id", user_id).execute()
            
            if result.data:
                updated_user = result.data[0]
                return UserSchema(**updated_user)
            else:
                raise DatabaseException("Failed to update user")
                
        except Exception as e:
            raise DatabaseException(f"Error updating user: {str(e)}")
    
    async def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """Update user password"""
        try:
            result = self.supabase.table("users").update({
                "hashed_password": hashed_password,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            raise DatabaseException(f"Error updating password: {str(e)}")
    
    async def create_or_update_user(self, user_data: Dict[str, Any]) -> UserSchema:
        """Create user if doesn't exist, otherwise update existing user"""
        print(f"create_or_update_user called with: {user_data}")  # Debug logging
        
        existing_user = await self.get_user_by_email(user_data["email"])
        
        if existing_user:
            print(f"User exists, updating: {existing_user.email}")  # Debug logging
            # Update existing user with new data
            update_data = {
                "username": user_data.get("username", existing_user.username),
                "email": user_data.get("email", existing_user.email),
                "provider": user_data.get("provider", existing_user.provider),
                "provider_id": user_data.get("provider_id", existing_user.provider_id),
                "is_active": user_data.get("is_active", existing_user.is_active)
            }
            return await self.update_user(existing_user.id, update_data)
        else:
            print(f"User doesn't exist, creating new user for: {user_data['email']}")  # Debug logging
            # Create new user
            return await self.create_user(user_data)
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        try:
            result = self.supabase.table("users").update({
                "is_active": False,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            raise DatabaseException(f"Error deactivating user: {str(e)}")