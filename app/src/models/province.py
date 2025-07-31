from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.src.config.database import Base
import uuid

class Province(Base):
    """
    Represents a province in Indonesia.
    This is the top-level administrative boundary for filtering.
    """
    __tablename__ = "provinces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    pum_code = Column(String(50), unique=True, nullable=True, index=True)  # KDPPUM
    name = Column(String, nullable=False, index=True)
    
    # Area in square kilometers (calculated from geometry)
    area_km2 = Column(Float, nullable=True)
    
    # Geometry column to store the polygon shape of the province.
    # Using MULTIPOLYGON for 2D geometries (Z dimension stripped)
    # SRID 4326 is the standard for GPS/web maps (WGS 84).
    geom = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)