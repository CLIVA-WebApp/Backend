from sqlalchemy import Column, Integer, Float, ForeignKey
from geoalchemy2 import Geometry
from app.src.config.database import Base
class PopulationPoint(Base):
    """
    Represents a single point of population distribution.
    Each point represents a certain number of people at a specific coordinate.
    This is a proxy for village-level data and is used for accurate coverage analysis.
    """
    __tablename__ = "population_points"

    id = Column(Integer, primary_key=True, index=True)
    
    # How many people this single point represents.
    population_count = Column(Float, nullable=False)

    # Foreign key for linking back to the sub-district it belongs to.
    subdistrict_id = Column(Integer, ForeignKey("subdistricts.id"), nullable=False)

    geom = Column(Geometry('POINT', srid=4326), nullable=False)