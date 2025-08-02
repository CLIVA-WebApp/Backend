from datetime import datetime
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from app.src.config.settings import settings
from app.src.schemas.user_schema import UserSchema, UserSchemaWithPassword
from app.src.utils.exceptions import DatabaseException
from app.src.services.geocoding_service import GeocodingService

class UserService:
    def __init__(self):
        # Use service role key for admin database operations
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key  # Changed from anon_key
        )
        self.geocoding_service = GeocodingService()
    
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
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserSchema]:
        """Get user by ID from database"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if result.data:
                user_data = result.data[0]
                return UserSchema(**user_data)
            return None
            
        except Exception as e:
            raise DatabaseException(f"Error fetching user: {str(e)}")
    
    async def get_user_by_id_with_password(self, user_id: str) -> Optional[UserSchemaWithPassword]:
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
            # Generate UUID for user ID if not provided
            if "id" not in user_data:
                import uuid
                user_data["id"] = str(uuid.uuid4())
            
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
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> UserSchema:
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
    
    async def update_user_location(self, user_id: str, location_data: dict) -> UserSchema:
        """Update user location with automatic geocoding"""
        try:
            update_data = {
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # If address is provided, geocode it to get coordinates
            if "location_address" in location_data and location_data["location_address"]:
                address = location_data["location_address"]
                
                # Geocode the address
                geocoding_result = await self.geocoding_service.geocode_address(address)
                
                if geocoding_result:
                    # Update with both address and geometry
                    update_data["location_address"] = address
                    update_data["location_geom"] = geocoding_result["wkt_point"]
                else:
                    # If geocoding fails, still save the address but log warning
                    update_data["location_address"] = address
                    # location_geom will remain null
            elif "location_geom" in location_data and location_data["location_geom"]:
                # If geometry is directly provided (for advanced use cases)
                update_data["location_geom"] = location_data["location_geom"]
            
            result = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
            
            if result.data:
                updated_user = result.data[0]
                return UserSchema(**updated_user)
            else:
                raise DatabaseException("Failed to update user location")
                
        except Exception as e:
            raise DatabaseException(f"Error updating user location: {str(e)}")
    
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
                "first_name": user_data.get("first_name", existing_user.first_name),
                "last_name": user_data.get("last_name", existing_user.last_name),
                "provider": user_data.get("provider", existing_user.provider),
                "provider_id": user_data.get("provider_id", existing_user.provider_id),
                "is_active": user_data.get("is_active", existing_user.is_active)
            }
            return await self.update_user(str(existing_user.id), update_data)
        else:
            print(f"User doesn't exist, creating new user for: {user_data['email']}")  # Debug logging
            # Create new user
            return await self.create_user(user_data)
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            result = self.supabase.table("users").update({
                "is_active": False,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            raise DatabaseException(f"Error deactivating user: {str(e)}")
    
    async def find_users_by_proximity(self, center_lat: float, center_lng: float, radius_km: float = 10.0) -> List[UserSchema]:
        """Find users within a specified radius of a point"""
        try:
            # Convert radius from km to degrees (approximate)
            radius_degrees = radius_km / 111.0  # Rough conversion
            
            # Create a bounding box for the search area
            min_lat = center_lat - radius_degrees
            max_lat = center_lat + radius_degrees
            min_lng = center_lng - radius_degrees
            max_lng = center_lng + radius_degrees
            
            # Query users within the bounding box
            result = self.supabase.table("users").select("*").execute()
            
            users = []
            for user_data in result.data:
                if user_data.get("location_geom"):
                    # For now, we'll return all users with location data
                    # In a real implementation, you'd use PostGIS spatial functions
                    users.append(UserSchema(**user_data))
            
            return users
            
        except Exception as e:
            raise DatabaseException(f"Error finding users by proximity: {str(e)}")
    
    async def update_user_name(self, user_id: str, name_data: dict) -> UserSchema:
        """Update user name (first_name and last_name)"""
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
                updated_user = result.data[0]
                return UserSchema(**updated_user)
            else:
                raise DatabaseException("Failed to update user name")
                
        except Exception as e:
            raise DatabaseException(f"Error updating user name: {str(e)}")