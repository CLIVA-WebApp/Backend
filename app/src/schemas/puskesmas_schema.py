from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class HealthFacilityType(str, Enum):
    PUSKESMAS = "Puskesmas"
    PUSTU = "Pustu"  # Puskesmas Pembantu
    KLINIK = "Klinik"
    RUMAH_SAKIT = "Rumah Sakit"

class HealthFacilityBase(BaseModel):
    name: str = Field(..., description="Name of the health facility")
    type: HealthFacilityType = Field(..., description="Type of health facility")
    subdistrict_id: Optional[UUID] = Field(None, description="ID of the sub-district where facility is located")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")

class HealthFacilityCreate(HealthFacilityBase):
    pass

class HealthFacilityUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[HealthFacilityType] = None
    subdistrict_id: Optional[UUID] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class HealthFacilityResponse(HealthFacilityBase):
    id: UUID
    subdistrict_name: Optional[str] = Field(None, description="Name of the sub-district")
    regency_name: Optional[str] = Field(None, description="Name of the regency")
    province_name: Optional[str] = Field(None, description="Name of the province")

    class Config:
        from_attributes = True

# Legacy Puskesmas schemas for backward compatibility
class PuskesmasBase(BaseModel):
    nama: str = Field(..., description="Nama Puskesmas")
    kode: str = Field(..., description="Kode Puskesmas")
    alamat: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    kecamatan: str = Field(..., description="Nama Kecamatan")
    kabupaten: str = Field(..., description="Nama Kabupaten")
    provinsi: str = Field(..., description="Nama Provinsi")
    kapasitas: int = Field(default=0, ge=0, description="Kapasitas pelayanan")
    radius_cover: float = Field(default=5.0, ge=0, description="Radius coverage dalam km")

class PuskesmasCreate(PuskesmasBase):
    pass

class PuskesmasUpdate(BaseModel):
    nama: Optional[str] = None
    kode: Optional[str] = None
    alamat: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    kecamatan: Optional[str] = None
    kabupaten: Optional[str] = None
    provinsi: Optional[str] = None
    kapasitas: Optional[int] = Field(None, ge=0)
    radius_cover: Optional[float] = Field(None, ge=0)

class PuskesmasResponse(PuskesmasBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 