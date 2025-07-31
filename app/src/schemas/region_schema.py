from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProvinceSchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the province")
    name: str = Field(..., description="Name of the province")
    code: str = Field(..., description="Province code")
    
    class Config:
        from_attributes = True

class RegencySchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the regency")
    name: str = Field(..., description="Name of the regency")
    code: str = Field(..., description="Regency code")
    province_id: str = Field(..., description="ID of the parent province")
    province_name: str = Field(..., description="Name of the parent province")
    
    class Config:
        from_attributes = True

class SubDistrictSchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the sub-district")
    name: str = Field(..., description="Name of the sub-district")
    code: str = Field(..., description="Sub-district code")
    regency_id: str = Field(..., description="ID of the parent regency")
    regency_name: str = Field(..., description="Name of the parent regency")
    
    class Config:
        from_attributes = True

class FacilitySchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the facility")
    name: str = Field(..., description="Name of the facility")
    type: str = Field(..., description="Type of health facility (e.g., puskesmas, hospital, clinic)")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    regency_id: str = Field(..., description="ID of the parent regency")
    regency_name: str = Field(..., description="Name of the parent regency")
    sub_district_id: str = Field(..., description="ID of the sub-district where facility is located")
    sub_district_name: str = Field(..., description="Name of the sub-district where facility is located")
    
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
    province_id: str = Field(..., description="ID of the province")
    
    class Config:
        from_attributes = True

class SubDistrictListResponse(BaseModel):
    sub_districts: List[SubDistrictSchema]
    total: int = Field(..., description="Total number of sub-districts")
    regency_id: str = Field(..., description="ID of the regency")
    
    class Config:
        from_attributes = True

class FacilityListResponse(BaseModel):
    facilities: List[FacilitySchema]
    total: int = Field(..., description="Total number of facilities")
    regency_id: str = Field(..., description="ID of the regency")
    
    class Config:
        from_attributes = True 