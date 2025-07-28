from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from src.config.database import Base

class Population(Base):
    __tablename__ = "populations"
    
    id = Column(Integer, primary_key=True, index=True)
    kecamatan = Column(String, nullable=False, index=True)
    kabupaten = Column(String, nullable=False, index=True)
    provinsi = Column(String, nullable=False, index=True)
    jumlah_penduduk = Column(Integer, default=0)
    luas_wilayah = Column(Float, default=0.0)  # dalam km²
    kepadatan = Column(Float, default=0.0)  # penduduk per km²
    tingkat_kemiskinan = Column(Float, default=0.0)  # persentase
    latitude_center = Column(Float)  # Koordinat pusat kecamatan
    longitude_center = Column(Float)
    tahun_data = Column(Integer, default=2024)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 