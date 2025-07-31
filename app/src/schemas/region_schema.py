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