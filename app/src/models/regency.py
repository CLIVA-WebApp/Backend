from sqlalchemy import Column, Integer, String, Float, ForeignKey
from geoalchemy2 import Geometry
from app.src.config.database import Base

class Regency(Base):
    """
    Represents a regency or city (Kabupaten/Kota).
    This is the primary scope for most analyses.
    """
    __tablename__ = "regencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    
    # Area in square kilometers (calculated from geometry)
    area_km2 = Column(Float, nullable=True)
    
    # Using MULTIPOLYGON for 2D geometries (Z dimension stripped)
    geom = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)