from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from src.config.database import Base

class Puskesmas(Base):
    __tablename__ = "puskesmas"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    kode = Column(String, unique=True, index=True)
    alamat = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    kecamatan = Column(String, nullable=False)
    kabupaten = Column(String, nullable=False)
    provinsi = Column(String, nullable=False)
    kapasitas = Column(Integer, default=0)  # Kapasitas pelayanan
    radius_cover = Column(Float, default=5.0)  # Radius dalam km
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 