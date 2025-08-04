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
    subdistrict_id: Optional[UUID] = Field(None, description="ID of the sub-district where facility is located")
    sub_district_name: Optional[str] = Field(None, description="Name of the sub-district where facility is located")
    
    class Config:
        from_attributes = True

# New schemas for bounding box search
class CoordinateSchema(BaseModel):
    lat: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    lng: float = Field(..., description="Longitude coordinate", ge=-180, le=180)

class BoundingBoxSchema(BaseModel):
    north_east: CoordinateSchema = Field(..., description="North-east corner coordinates")
    south_west: CoordinateSchema = Field(..., description="South-west corner coordinates")

class IntersectingRegionSchema(BaseModel):
    type: str = Field(..., description="Type of region (province, regency, or subdistrict)")
    id: UUID = Field(..., description="Unique identifier for the region")
    name: str = Field(..., description="Name of the region")
    coverage_percentage: float = Field(..., description="Percentage of region area covered by bounding box", ge=0, le=100)
    intersection_area_km2: float = Field(..., description="Area of intersection in square kilometers")
    total_area_km2: Optional[float] = Field(None, description="Total area of the region in square kilometers")
    
    # Additional context for hierarchical information
    parent_region_id: Optional[UUID] = Field(None, description="ID of parent region (for regencies: province_id, for subdistricts: regency_id)")
    parent_region_name: Optional[str] = Field(None, description="Name of parent region")
    
    class Config:
        from_attributes = True

class BoundingBoxSearchResponse(BaseModel):
    primary_region: IntersectingRegionSchema = Field(..., description="The region with the highest coverage percentage")
    intersecting_regions: List[IntersectingRegionSchema] = Field(..., description="All regions that intersect with the bounding box")
    bounding_box: BoundingBoxSchema = Field(..., description="The input bounding box coordinates")
    total_regions_found: int = Field(..., description="Total number of intersecting regions")
    
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

class AllRegencyListResponse(BaseModel):
    regencies: List[RegencySchema]
    total: int = Field(..., description="Total number of regencies")
    
    class Config:
        from_attributes = True

class SubDistrictListResponse(BaseModel):
    sub_districts: List[SubDistrictSchema]
    total: int = Field(..., description="Total number of sub-districts")
    regency_id: UUID = Field(..., description="ID of the regency")
    
    class Config:
        from_attributes = True

class AllSubDistrictListResponse(BaseModel):
    sub_districts: List[SubDistrictSchema]
    total: int = Field(..., description="Total number of sub-districts")
    
    class Config:
        from_attributes = True

class FacilityListResponse(BaseModel):
    facilities: List[FacilitySchema]
    total: int = Field(..., description="Total number of facilities")
    regency_id: UUID = Field(..., description="ID of the regency")
    
    class Config:
        from_attributes = True 