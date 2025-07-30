from sqlalchemy import Column, Integer, String, ForeignKey
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
    
    geom = Column(Geometry('POLYGON', srid=4326), nullable=False)