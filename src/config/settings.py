from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Supabase configuration
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    supabase_service_key: str = Field(..., alias="SUPABASE_SERVICE_KEY")
    
    # Database connection (for alembic)
    supabase_user: str = Field(..., alias="SUPABASE_USER")
    supabase_password: str = Field(..., alias="SUPABASE_PASSWORD")
    supabase_host: str = Field(..., alias="SUPABASE_HOST")
    supabase_port: str = Field(..., alias="SUPABASE_PORT")
    supabase_dbname: str = Field(..., alias="SUPABASE_DBNAME")
    
    # Google OAuth
    google_client_id: str = Field(..., alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., alias="GOOGLE_CLIENT_SECRET")
    
    # JWT configuration
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # App configuration
    app_env: str = Field(..., alias="APP_ENV")
    app_host: str = Field(..., alias="APP_HOST")
    app_port: int = Field(..., alias="APP_PORT")
    frontend_url: str = Field(..., alias="FRONTEND_URL")
    backend_url: str = Field(..., alias="BACKEND_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # This will ignore extra fields

settings = Settings()
