from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.src.config.database import Base
import uuid

class PopulationPoint(Base):
    """
    Represents a single point of population distribution.
    Each point represents a certain number of people at a specific coordinate.
    This is a proxy for village-level data and is used for accurate coverage analysis.
    """
    __tablename__ = "population_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # How many people this single point represents.
    population_count = Column(Float, nullable=False)

    # Foreign key for linking back to the sub-district it belongs to.
    subdistrict_id = Column(UUID(as_uuid=True), ForeignKey("subdistricts.id"), nullable=False)

    geom = Column(Geometry('POINT', srid=4326), nullable=False)