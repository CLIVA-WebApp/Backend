from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from app.src.config.database import Base

class Province(Base):
    """
    Represents a province in Indonesia.
    This is the top-level administrative boundary for filtering.
    """
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    
    # Area in square kilometers (calculated from geometry)
    area_km2 = Column(Float, nullable=True)
    
    # Geometry column to store the polygon shape of the province.
    # Using MULTIPOLYGON for 2D geometries (Z dimension stripped)
    # SRID 4326 is the standard for GPS/web maps (WGS 84).
    geom = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)   