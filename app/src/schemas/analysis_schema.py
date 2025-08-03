from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime
from enum import Enum
from decimal import Decimal
from uuid import UUID

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
    regency_id: UUID = Field(..., description="ID of the regency")
    regency_name: str = Field(..., description="Name of the regency")
    total_population: int = Field(..., description="Total population of the regency")
    population_outside_radius: int = Field(..., description="Population living outside service radius")
    service_radius_km: float = Field(..., description="Service radius in kilometers")
    heatmap_points: List[HeatmapPoint] = Field(..., description="Grid points for heatmap visualization")
    
    class Config:
        from_attributes = True

# Priority Score Analysis Schemas
class SubDistrictScore(BaseModel):
    subdistrict_id: UUID = Field(..., description="ID of the sub-district")
    sub_district_name: str = Field(..., description="Name of the sub-district")
    gap_factor: float = Field(..., description="Gap factor score")
    efficiency_factor: float = Field(..., description="Efficiency factor score")
    vulnerability_factor: float = Field(..., description="Vulnerability factor score")
    composite_score: float = Field(..., description="Composite priority score")
    rank: int = Field(..., description="Ranking position")
    
    class Config:
        from_attributes = True

class PriorityScoreData(BaseModel):
    regency_id: UUID = Field(..., description="ID of the regency")
    regency_name: str = Field(..., description="Name of the regency")
    total_sub_districts: int = Field(..., description="Total number of sub-districts")
    sub_districts: List[SubDistrictScore] = Field(..., description="Ranked list of sub-districts")
    
    class Config:
        from_attributes = True

# SubDistrict Details Schema
class SubDistrictDetails(BaseModel):
    subdistrict_id: UUID = Field(..., description="ID of the sub-district")
    sub_district_name: str = Field(..., description="Name of the sub-district")
    regency_id: UUID = Field(..., description="ID of the parent regency")
    regency_name: str = Field(..., description="Name of the parent regency")
    population: int = Field(..., description="Total population")
    area_km2: float = Field(..., description="Area in square kilometers")
    population_density: float = Field(..., description="Population density (people per km²)")
    poverty_rate: float = Field(..., description="Poverty rate as percentage")
    existing_facilities_count: int = Field(..., description="Number of existing health facilities")
    existing_facilities: List[Dict[str, Any]] = Field(..., description="List of existing facilities")
    gap_factor: float = Field(..., description="Gap factor score")
    efficiency_factor: float = Field(..., description="Efficiency factor score")
    vulnerability_factor: float = Field(..., description="Vulnerability factor score")
    composite_score: float = Field(..., description="Composite priority score")
    rank: int = Field(..., description="Ranking position")
    
    class Config:
        from_attributes = True

# Simulation Schemas
class SimulationRequest(BaseModel):
    regency_id: Union[UUID, str] = Field(..., description="ID of the regency for simulation (use 'mock' for testing)")
    budget: float = Field(..., gt=0, description="Available budget in Indonesian Rupiah (IDR)")
    facility_costs: Optional[Dict[str, int]] = Field(
        default=None,
        description="Custom facility costs in IDR (e.g., {'Puskesmas': 2000000000, 'Pustu': 500000000})"
    )
    coverage_radius: Optional[Dict[str, int]] = Field(
        default=None,
        description="Custom coverage radius in meters (e.g., {'Puskesmas': 5000, 'Pustu': 3000})"
    )
    
    @validator('budget')
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError('Budget must be greater than 0')
        return v
    
    @validator('facility_costs')
    def validate_facility_costs(cls, v):
        if v is not None:
            for facility_type, cost in v.items():
                if cost <= 0:
                    raise ValueError(f'Cost for {facility_type} must be greater than 0')
        return v
    
    @validator('coverage_radius')
    def validate_coverage_radius(cls, v):
        if v is not None:
            for facility_type, radius in v.items():
                if radius <= 0:
                    raise ValueError(f'Coverage radius for {facility_type} must be greater than 0')
        return v

class OptimizedFacility(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate of optimal location")
    longitude: float = Field(..., description="Longitude coordinate of optimal location")
    subdistrict_id: UUID = Field(..., description="ID of the sub-district")
    sub_district_name: str = Field(..., description="Name of the sub-district")
    estimated_cost: float = Field(..., description="Estimated cost for this facility")
    population_covered: int = Field(..., description="Population that would be covered")
    coverage_radius_km: float = Field(..., description="Coverage radius in kilometers")
    
    class Config:
        from_attributes = True

class SimulationResult(BaseModel):
    regency_id: UUID = Field(..., description="ID of the regency")
    regency_name: str = Field(..., description="Name of the regency")
    total_budget: float = Field(..., description="Total budget allocated")
    budget_used: float = Field(..., description="Budget actually used")
    facilities_recommended: int = Field(..., description="Number of facilities recommended")
    total_population_covered: int = Field(..., description="Total population covered")
    coverage_percentage: float = Field(..., description="Percentage of population covered")
    optimized_facilities: List[OptimizedFacility] = Field(..., description="List of optimal facility locations")
    
    class Config:
        from_attributes = True

# Summary Analysis Schemas
class SummaryMetrics(BaseModel):
    coverage_percentage: float = Field(..., description="The proportion of the population covered by health facilities")
    average_distance_km: float = Field(..., description="Average distance to the nearest facility in kilometers")
    average_travel_time_hours: float = Field(..., description="Average travel time to the nearest facility in hours")
    
    class Config:
        from_attributes = True

class FacilityOverview(BaseModel):
    id: UUID = Field(..., description="ID of the health facility")
    name: str = Field(..., description="Name of the health facility")
    type: str = Field(..., description="Type of health facility")
    rating: float = Field(..., description="Rating of the facility (0-5 scale)")
    
    class Config:
        from_attributes = True

class AnalysisSummary(BaseModel):
    regency_name: str = Field(..., description="Name of the regency")
    summary_metrics: SummaryMetrics = Field(..., description="Summary metrics for the regency")
    facility_overview: List[FacilityOverview] = Field(..., description="Overview of health facilities in the regency")
    
    class Config:
        from_attributes = True

# Report Export Schemas
class ReportExportRequest(BaseModel):
    report_type: str = Field(..., description="Type of report to generate (simulation_results, priority_ranking, heatmap_analysis)")
    data: Dict[str, Any] = Field(..., description="Data from analysis or simulation results")
    format: str = Field(default="pdf", description="Output format (pdf, csv)")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        valid_types = ["simulation_results", "priority_ranking", "heatmap_analysis"]
        if v not in valid_types:
            raise ValueError(f'Report type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('format')
    def validate_format(cls, v):
        valid_formats = ["pdf", "csv"]
        if v not in valid_formats:
            raise ValueError(f'Format must be one of: {", ".join(valid_formats)}')
        return v

class ReportExportResponse(BaseModel):
    filename: str = Field(..., description="Generated filename")
    download_url: str = Field(..., description="URL to download the generated report")
    file_size_bytes: int = Field(..., description="Size of the generated file in bytes")
    generated_at: datetime = Field(..., description="Timestamp when report was generated")
    
    class Config:
        from_attributes = True 