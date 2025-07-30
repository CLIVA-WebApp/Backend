from sqlalchemy import Column, Integer, String
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
    
    # Geometry column to store the polygon shape of the province.
    # SRID 4326 is the standard for GPS/web maps (WGS 84).
    geom = Column(Geometry('POLYGON', srid=4326), nullable=False)   