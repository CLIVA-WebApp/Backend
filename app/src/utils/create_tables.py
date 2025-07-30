"""
Utility script to create all database tables before loading data.
This ensures the database schema is ready for the GDB data.
"""

from sqlalchemy import text
from app.src.config.database import engine, Base
from app.src.models.province import Province
from app.src.models.regency import Regency
from app.src.models.subdistrict import Subdistrict
from app.src.models.population_point import PopulationPoint
from app.src.models.health_facility import HealthFacility
from app.src.models.user import User

def create_all_tables():
    """Create all tables defined in the models"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Verify PostGIS extension is enabled
        with engine.connect() as conn:
            result = conn.execute(text("SELECT PostGIS_Version();"))
            version = result.fetchone()[0]
            print(f"✅ PostGIS version: {version}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_all_tables() 