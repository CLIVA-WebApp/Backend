from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.src.config.database import Base

class Population(Base):
    __tablename__ = "population"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    alamat = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 