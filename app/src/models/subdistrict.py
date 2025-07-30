from sqlalchemy import Column, Integer, String, Float, ForeignKey
from geoalchemy2 import Geometry
from app.src.config.database import Base

class Subdistrict(Base):
    """
    Represents a sub-district (Kecamatan).
    This is the primary unit of analysis for the priority score.
    """
    __tablename__ = "subdistricts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    
    regency_id = Column(Integer, ForeignKey("regencies.id"), nullable=False)
    
    # Demographic data, to be joined from BPS sources.
    population_count = Column(Integer, nullable=True)
    poverty_level = Column(Float, nullable=True) # e.g., as a percentage

    geom = Column(Geometry('POLYGON', srid=4326), nullable=False)