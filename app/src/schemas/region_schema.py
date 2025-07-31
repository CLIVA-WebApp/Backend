from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

class ProvinceSchema(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the province")
    name: str = Field(..., description="Name of the province")
    pum_code: Optional[str] = Field(None, description="PUM code for the province (KDPPUM)")
    area_km2: Optional[float] = Field(None, description="Area in square kilometers")
    
    class Config:
        from_attributes = True

class RegencySchema(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the regency")
    name: str = Field(..., description="Name of the regency")
    pum_code: Optional[str] = Field(None, description="PUM code for the regency (KDPKAB)")
    province_id: UUID = Field(..., description="ID of the parent province")
    province_name: Optional[str] = Field(None, description="Name of the parent province")
    area_km2: Optional[float] = Field(None, description="Area in square kilometers")
    
    class Config:
        from_attributes = True

class SubDistrictSchema(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the sub-district")
    name: str = Field(..., description="Name of the sub-district")
    pum_code: Optional[str] = Field(None, description="PUM code for the sub-district (KDCPUM)")
    regency_id: UUID = Field(..., description="ID of the parent regency")
    regency_name: Optional[str] = Field(None, description="Name of the parent regency")
    population_count: Optional[int] = Field(None, description="Population count")
    poverty_level: Optional[float] = Field(None, description="Poverty level as percentage")
    area_km2: Optional[float] = Field(None, description="Area in square kilometers")
    
    class Config:
        from_attributes = True

class FacilitySchema(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the facility")
    name: str = Field(..., description="Name of the facility")
    type: str = Field(..., description="Type of health facility (e.g., puskesmas, hospital, clinic)")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    regency_id: UUID = Field(..., description="ID of the parent regency")
    regency_name: Optional[str] = Field(None, description="Name of the parent regency")
    sub_district_id: Optional[UUID] = Field(None, description="ID of the sub-district where facility is located")
    sub_district_name: Optional[str] = Field(None, description="Name of the sub-district where facility is located")
    
    class Config:
        from_attributes = True

class ProvinceListResponse(BaseModel):
    provinces: List[ProvinceSchema]
    total: int = Field(..., description="Total number of provinces")
    
    class Config:
        from_attributes = True

class RegencyListResponse(BaseModel):
    regencies: List[RegencySchema]
    total: int = Field(..., description="Total number of regencies")
    province_id: UUID = Field(..., description="ID of the province")
    
    class Config:
        from_attributes = True

class SubDistrictListResponse(BaseModel):
    sub_districts: List[SubDistrictSchema]
    total: int = Field(..., description="Total number of sub-districts")
    regency_id: UUID = Field(..., description="ID of the regency")
    
    class Config:
        from_attributes = True

class FacilityListResponse(BaseModel):
    facilities: List[FacilitySchema]
    total: int = Field(..., description="Total number of facilities")
    regency_id: UUID = Field(..., description="ID of the regency")
    
    class Config:
        from_attributes = True 