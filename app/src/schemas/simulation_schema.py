from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from enum import Enum

class FacilityType(str, Enum):
    PUSKESMAS = "Puskesmas"
    PUSTU = "Pustu"

class OptimizedFacility(BaseModel):
    latitude: float = Field(..., description="Latitude of the facility location")
    longitude: float = Field(..., description="Longitude of the facility location")
    sub_district_id: UUID = Field(..., description="ID of the sub-district")
    sub_district_name: str = Field(..., description="Name of the sub-district")
    estimated_cost: float = Field(..., description="Estimated cost of the facility")
    population_covered: int = Field(..., description="Population covered by this facility")
    coverage_radius_km: float = Field(..., description="Coverage radius in kilometers")
    facility_type: FacilityType = Field(..., description="Type of facility being recommended")
    
    class Config:
        from_attributes = True

class SimulationRequest(BaseModel):
    budget: float = Field(..., description="Total budget available for facility construction")
    regency_id: UUID = Field(..., description="ID of the regency to analyze")
    
    class Config:
        from_attributes = True

class SimulationResponse(BaseModel):
    regency_id: UUID = Field(..., description="ID of the regency")
    regency_name: str = Field(..., description="Name of the regency")
    total_budget: float = Field(..., description="Total budget allocated")
    budget_used: float = Field(..., description="Budget actually used")
    facilities_recommended: int = Field(..., description="Number of facilities recommended")
    total_population_covered: int = Field(..., description="Total population covered")
    coverage_percentage: float = Field(..., description="Percentage of population covered")
    optimized_facilities: List[OptimizedFacility] = Field(..., description="List of optimized facility locations")
    automated_reasoning: str = Field(..., description="Automated reasoning explaining the greedy algorithm's decisions")
    
    class Config:
        from_attributes = True 