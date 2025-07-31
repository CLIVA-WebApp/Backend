from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum
from decimal import Decimal

# Heatmap Analysis Schemas
class HeatmapPoint(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    population_density: float = Field(..., description="Population density at this point")
    access_score: float = Field(..., description="Health access score (0-1)")
    distance_to_facility: float = Field(..., description="Distance to nearest health facility in km")
    
    class Config:
        from_attributes = True

class HeatmapData(BaseModel):
    regency_id: str = Field(..., description="ID of the regency")
    regency_name: str = Field(..., description="Name of the regency")
    total_population: int = Field(..., description="Total population of the regency")
    population_outside_radius: int = Field(..., description="Population living outside service radius")
    service_radius_km: float = Field(..., description="Service radius in kilometers")
    heatmap_points: List[HeatmapPoint] = Field(..., description="Grid points for heatmap visualization")
    
    class Config:
        from_attributes = True

# Priority Score Analysis Schemas
class SubDistrictScore(BaseModel):
    sub_district_id: str = Field(..., description="ID of the sub-district")
    sub_district_name: str = Field(..., description="Name of the sub-district")
    gap_factor: float = Field(..., description="Gap factor score")
    efficiency_factor: float = Field(..., description="Efficiency factor score")
    vulnerability_factor: float = Field(..., description="Vulnerability factor score")
    composite_score: float = Field(..., description="Composite priority score")
    rank: int = Field(..., description="Ranking position")
    
    class Config:
        from_attributes = True

class PriorityScoreData(BaseModel):
    regency_id: str = Field(..., description="ID of the regency")
    regency_name: str = Field(..., description="Name of the regency")
    total_sub_districts: int = Field(..., description="Total number of sub-districts")
    sub_districts: List[SubDistrictScore] = Field(..., description="Ranked list of sub-districts")
    
    class Config:
        from_attributes = True

# Simulation Schemas
class SimulationRequest(BaseModel):
    regency_id: str = Field(..., description="ID of the regency for simulation")
    budget: float = Field(..., gt=0, description="Available budget in currency units")
    facility_type: str = Field(..., description="Type of health facility to optimize")
    optimization_criteria: List[str] = Field(
        default=["population_coverage", "cost_efficiency"],
        description="Optimization criteria to consider"
    )
    
    @validator('budget')
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError('Budget must be greater than 0')
        return v

class OptimizedFacility(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate of optimal location")
    longitude: float = Field(..., description="Longitude coordinate of optimal location")
    sub_district_id: str = Field(..., description="ID of the sub-district")
    sub_district_name: str = Field(..., description="Name of the sub-district")
    estimated_cost: float = Field(..., description="Estimated cost for this facility")
    population_covered: int = Field(..., description="Population that would be covered")
    coverage_radius_km: float = Field(..., description="Coverage radius in kilometers")
    
    class Config:
        from_attributes = True

class SimulationResult(BaseModel):
    regency_id: str = Field(..., description="ID of the regency")
    regency_name: str = Field(..., description="Name of the regency")
    total_budget: float = Field(..., description="Total budget allocated")
    budget_used: float = Field(..., description="Budget actually used")
    facilities_recommended: int = Field(..., description="Number of facilities recommended")
    total_population_covered: int = Field(..., description="Total population covered")
    coverage_percentage: float = Field(..., description="Percentage of population covered")
    optimized_facilities: List[OptimizedFacility] = Field(..., description="List of optimal facility locations")
    
    class Config:
        from_attributes = True 