from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from geoalchemy2 import Geometry
from app.src.config.database import Base
import enum

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

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(HealthFacilityType), nullable=False)

    # Foreign key for quick administrative lookup, though spatial queries will be primary.
    subdistrict_id = Column(Integer, ForeignKey("subdistricts.id"), nullable=True)
    
    # Geometry column to store the point location of the facility.
    geom = Column(Geometry('POINT', srid=4326), nullable=False)
