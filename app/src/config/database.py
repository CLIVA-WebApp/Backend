# Backend/src/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("SUPABASE_USER")
PASSWORD = os.getenv("SUPABASE_PASSWORD")
HOST = os.getenv("SUPABASE_HOST")
PORT = os.getenv("SUPABASE_PORT")
DBNAME = os.getenv("SUPABASE_DBNAME")

# Database pool configuration (with environment variable fallbacks)
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require&options=-csearch_path%3Dpublic,extensions"

# Create sync engine with proper connection pooling for Supabase
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=POOL_PRE_PING,
    pool_recycle=POOL_RECYCLE,
    pool_timeout=POOL_TIMEOUT,
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session with proper error handling
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test the connection only if environment variables are set
def test_connection():
    if not all([USER, PASSWORD, HOST, PORT, DBNAME]):
        print("⚠️  Environment variables not set. Please configure .env file")
        print("Required variables: SUPABASE_USER, SUPABASE_PASSWORD, SUPABASE_HOST, SUPABASE_PORT, SUPABASE_DBNAME")
        return False
    
    try:
        with engine.connect() as connection:
            print("✅ Sync connection successful!")
            print(f"📊 Pool configuration: size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, recycle={POOL_RECYCLE}s")
            return True
    except Exception as e:
        print(f"❌ Failed to connect (sync): {e}")
        return False

# Only test connection if this file is run directly
if __name__ == "__main__":
    test_connection()