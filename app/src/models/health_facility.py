from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from sqlalchemy.types import Float
from app.src.config.database import Base
import enum
import uuid

class HealthFacilityType(enum.Enum):
    PUSKESMAS = "Puskesmas"
    PUSTU = "Pustu" # Puskesmas Pembantu
    KLINIK = "Klinik"
    RUMAH_SAKIT = "Rumah Sakit"

class HealthFacility(Base):
    """
    Represents a health facility like a Puskesmas, clinic, or hospital.
    Replaces the old Puskesmas model.
    """
    __tablename__ = "health_facilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(HealthFacilityType), nullable=False)
    rating = Column(Float, nullable=True)

    # Foreign key for quick administrative lookup, though spatial queries will be primary.
    subdistrict_id = Column(UUID(as_uuid=True), ForeignKey("subdistricts.id"), nullable=True)
    
    # Relationships
    sub_district = relationship("Subdistrict", back_populates="health_facilities")
    
    # Geometry column to store the point location of the facility.
    geom = Column(Geometry('POINT', srid=4326), nullable=False)