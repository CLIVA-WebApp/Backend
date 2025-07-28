# Backend/src/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
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

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Create sync engine for regular operations
engine = create_engine(DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session
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
            return True
    except Exception as e:
        print(f"❌ Failed to connect (sync): {e}")
        return False

# Only test connection if this file is run directly
if __name__ == "__main__":
    test_connection()