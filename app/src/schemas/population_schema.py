from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PopulationBase(BaseModel):
    kecamatan: str = Field(..., description="Nama Kecamatan")
    kabupaten: str = Field(..., description="Nama Kabupaten")
    provinsi: str = Field(..., description="Nama Provinsi")
    jumlah_penduduk: int = Field(default=0, ge=0, description="Jumlah penduduk")
    luas_wilayah: float = Field(default=0.0, ge=0, description="Luas wilayah dalam km²")
    kepadatan: float = Field(default=0.0, ge=0, description="Kepadatan penduduk per km²")
    tingkat_kemiskinan: float = Field(default=0.0, ge=0, le=100, description="Tingkat kemiskinan dalam persen")
    latitude_center: Optional[float] = Field(None, ge=-90, le=90, description="Latitude pusat kecamatan")
    longitude_center: Optional[float] = Field(None, ge=-180, le=180, description="Longitude pusat kecamatan")
    tahun_data: int = Field(default=2024, ge=2000, le=2030, description="Tahun data")

class PopulationCreate(PopulationBase):
    pass

class PopulationUpdate(BaseModel):
    kecamatan: Optional[str] = None
    kabupaten: Optional[str] = None
    provinsi: Optional[str] = None
    jumlah_penduduk: Optional[int] = Field(None, ge=0)
    luas_wilayah: Optional[float] = Field(None, ge=0)
    kepadatan: Optional[float] = Field(None, ge=0)
    tingkat_kemiskinan: Optional[float] = Field(None, ge=0, le=100)
    latitude_center: Optional[float] = Field(None, ge=-90, le=90)
    longitude_center: Optional[float] = Field(None, ge=-180, le=180)
    tahun_data: Optional[int] = Field(None, ge=2000, le=2030)

class PopulationResponse(PopulationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 