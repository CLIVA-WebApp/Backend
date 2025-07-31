from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.src.config.database import Base
import uuid

class Regency(Base):
    """
    Represents a regency or city (Kabupaten/Kota).
    This is the primary scope for most analyses.
    """
    __tablename__ = "regencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    pum_code = Column(String(50), unique=True, nullable=True, index=True)  # KDPKAB
    name = Column(String, nullable=False, index=True)
    
    province_id = Column(UUID(as_uuid=True), ForeignKey("provinces.id"), nullable=False)
    
    # Area in square kilometers (calculated from geometry)
    area_km2 = Column(Float, nullable=True)
    
    # Using MULTIPOLYGON for 2D geometries (Z dimension stripped)
    geom = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)