from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.src.config.database import Base
import uuid

class Subdistrict(Base):
    """
    Represents a sub-district (Kecamatan).
    This is the primary unit of analysis for the priority score.
    """
    __tablename__ = "subdistricts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    pum_code = Column(String(50), unique=True, nullable=True, index=True)  # KDCPUM
    name = Column(String, nullable=False, index=True)
    
    regency_id = Column(UUID(as_uuid=True), ForeignKey("regencies.id"), nullable=False)
    
    # Relationship to Regency
    regency = relationship("Regency", back_populates="subdistricts")
    
    # Relationship to Health Facilities
    health_facilities = relationship("HealthFacility", back_populates="sub_district")
    
    # Demographic data, to be joined from BPS sources.
    population_count = Column(Integer, nullable=True)
    poverty_level = Column(Float, nullable=True) # e.g., as a percentage
    
    # Area in square kilometers (calculated from geometry)
    area_km2 = Column(Float, nullable=True)

    # Using MULTIPOLYGON for 2D geometries (Z dimension stripped)
    geom = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)