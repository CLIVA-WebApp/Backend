from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from enum import Enum

class GeographicLevel(str, Enum):
    PROVINCE = "province"
    REGENCY = "regency"
    SUBDISTRICT = "subdistrict"

class FacilityType(str, Enum):
    HOSPITAL = "Hospital"
    CLINIC = "Clinic"
    PUSKESMAS = "Puskesmas"
    PUSTU = "Pustu"

class Coordinates(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    
    class Config:
        from_attributes = True

class Recommendation(BaseModel):
    type: FacilityType = Field(..., description="Type of facility being recommended")
    subdistrict_id: UUID = Field(..., description="ID of the subdistrict")
    location_name: str = Field(..., description="Name of the location")
    coordinates: Coordinates = Field(..., description="Geographic coordinates")
    estimated_cost: float = Field(..., description="Estimated cost of the facility")
    
    class Config:
        from_attributes = True

class SimulationSummary(BaseModel):
    initial_coverage: float = Field(..., description="Initial population coverage percentage")
    projected_coverage: float = Field(..., description="Projected population coverage percentage after recommendations")
    coverage_increase_percent: float = Field(..., description="Percentage increase in coverage")
    total_cost: float = Field(..., description="Total cost of all recommendations")
    budget_remaining: float = Field(..., description="Remaining budget after recommendations")
    
    class Config:
        from_attributes = True

class SimulationRequest(BaseModel):
    geographic_level: GeographicLevel = Field(..., description="Geographic level of the area_ids")
    area_ids: List[UUID] = Field(..., description="List of area IDs at the specified geographic level")
    budget: float = Field(..., description="Total budget available for facility construction")
    facility_types: List[FacilityType] = Field(..., description="Types of facilities to consider")
    
    class Config:
        from_attributes = True

class SimulationResponse(BaseModel):
    simulation_summary: SimulationSummary = Field(..., description="Summary of simulation results")
    recommendations: List[Recommendation] = Field(..., description="List of facility recommendations")
    automated_reasoning: str = Field(..., description="Automated reasoning explaining the greedy algorithm's decisions")
    
    class Config:
        from_attributes = True

# Legacy schemas for backward compatibility
class OptimizedFacility(BaseModel):
    latitude: float = Field(..., description="Latitude of the facility location")
    longitude: float = Field(..., description="Longitude of the facility location")
    subdistrict_id: UUID = Field(..., description="ID of the sub-district")
    sub_district_name: str = Field(..., description="Name of the sub-district")
    estimated_cost: float = Field(..., description="Estimated cost of the facility")
    population_covered: int = Field(..., description="Population covered by this facility")
    coverage_radius_km: float = Field(..., description="Coverage radius in kilometers")
    facility_type: FacilityType = Field(..., description="Type of facility being recommended")
    
    class Config:
        from_attributes = True

class LegacySimulationResponse(BaseModel):
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