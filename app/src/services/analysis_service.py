from typing import List, Optional, Dict, Any
from app.src.schemas.analysis_schema import (
    HeatmapData,
    HeatmapPoint,
    PriorityScoreData,
    SubDistrictScore
)
from app.src.schemas.region_schema import RegencySchema
from app.src.config.database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import math
import random

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    async def get_regency_by_id(self, regency_id: str) -> Optional[RegencySchema]:
        """
        Retrieve a specific regency by ID.
        
        Args:
            regency_id: The unique identifier of the regency
            
        Returns:
            Optional[RegencySchema]: Regency data if found, None otherwise
        """
        try:
            # This is a placeholder implementation
            # In a real implementation, you would query your database
            
            # Mock data for demonstration
            regencies = {
                "3201": RegencySchema(
                    id="3201",
                    name="Kabupaten Bogor",
                    code="3201",
                    province_id="32",
                    province_name="Jawa Barat"
                ),
                "3171": RegencySchema(
                    id="3171",
                    name="Kota Jakarta Selatan",
                    code="3171",
                    province_id="31",
                    province_name="DKI Jakarta"
                )
            }
            
            return regencies.get(regency_id)
        except Exception as e:
            logger.error(f"Error retrieving regency {regency_id}: {str(e)}")
            raise
    
    async def generate_heatmap_data(self, regency_id: str) -> HeatmapData:
        """
        Generate heatmap data for a specific regency.
        
        This method calculates health access scores based on the proportion
        of the population living outside a defined service radius of the
        nearest health facility.
        
        Args:
            regency_id: The unique identifier of the regency
            
        Returns:
            HeatmapData: Heatmap data including grid points and access scores
        """
        try:
            # This is a placeholder implementation
            # In a real implementation, you would:
            # 1. Query population data for the regency
            # 2. Query existing health facility locations
            # 3. Calculate distances from population centers to facilities
            # 4. Generate grid points for visualization
            # 5. Calculate access scores based on service radius
            
            # Mock data for demonstration
            regency = await self.get_regency_by_id(regency_id)
            if not regency:
                raise ValueError(f"Regency {regency_id} not found")
            
            # Generate mock heatmap points
            heatmap_points = []
            service_radius_km = 5.0  # Default service radius
            
            # Generate a grid of points for the regency
            for i in range(10):  # 10x10 grid
                for j in range(10):
                    # Mock coordinates (in real implementation, these would be actual coordinates)
                    lat = -6.2088 + (i * 0.01)  # Base latitude for Indonesia
                    lng = 106.8456 + (j * 0.01)  # Base longitude for Indonesia
                    
                    # Mock calculations
                    population_density = random.uniform(100, 1000)
                    distance_to_facility = random.uniform(0, 15)
                    access_score = max(0, 1 - (distance_to_facility / service_radius_km))
                    
                    heatmap_points.append(HeatmapPoint(
                        latitude=lat,
                        longitude=lng,
                        population_density=population_density,
                        access_score=access_score,
                        distance_to_facility=distance_to_facility
                    ))
            
            # Calculate summary statistics
            total_population = sum(point.population_density for point in heatmap_points)
            population_outside_radius = sum(
                point.population_density 
                for point in heatmap_points 
                if point.distance_to_facility > service_radius_km
            )
            
            return HeatmapData(
                regency_id=regency_id,
                regency_name=regency.name,
                total_population=int(total_population),
                population_outside_radius=int(population_outside_radius),
                service_radius_km=service_radius_km,
                heatmap_points=heatmap_points
            )
        except Exception as e:
            logger.error(f"Error generating heatmap data for regency {regency_id}: {str(e)}")
            raise
    
    async def generate_priority_score_data(self, regency_id: str) -> PriorityScoreData:
        """
        Generate priority score data for a specific regency.
        
        This method calculates the Equity Prioritization Score based on:
        - Gap Factor: Measures the gap in health service access
        - Efficiency Factor: Evaluates the efficiency of current health infrastructure
        - Vulnerability Factor: Assesses the vulnerability of the population
        
        Args:
            regency_id: The unique identifier of the regency
            
        Returns:
            PriorityScoreData: Priority score data including ranked sub-districts
        """
        try:
            # This is a placeholder implementation
            # In a real implementation, you would:
            # 1. Query sub-district data for the regency
            # 2. Calculate gap factors based on health facility coverage
            # 3. Calculate efficiency factors based on facility utilization
            # 4. Calculate vulnerability factors based on demographic data
            # 5. Compute composite scores and rankings
            
            # Mock data for demonstration
            regency = await self.get_regency_by_id(regency_id)
            if not regency:
                raise ValueError(f"Regency {regency_id} not found")
            
            # Generate mock sub-district scores
            sub_districts = []
            for i in range(5):  # Mock 5 sub-districts
                gap_factor = random.uniform(0.1, 1.0)
                efficiency_factor = random.uniform(0.1, 1.0)
                vulnerability_factor = random.uniform(0.1, 1.0)
                
                # Composite score calculation (weighted average)
                composite_score = (
                    gap_factor * 0.4 +
                    efficiency_factor * 0.3 +
                    vulnerability_factor * 0.3
                )
                
                sub_districts.append(SubDistrictScore(
                    sub_district_id=f"{regency_id}0{i+1}",
                    sub_district_name=f"Kecamatan {i+1}",
                    gap_factor=gap_factor,
                    efficiency_factor=efficiency_factor,
                    vulnerability_factor=vulnerability_factor,
                    composite_score=composite_score,
                    rank=0  # Will be set after sorting
                ))
            
            # Sort by composite score (descending) and assign ranks
            sub_districts.sort(key=lambda x: x.composite_score, reverse=True)
            for i, sub_district in enumerate(sub_districts):
                sub_district.rank = i + 1
            
            return PriorityScoreData(
                regency_id=regency_id,
                regency_name=regency.name,
                total_sub_districts=len(sub_districts),
                sub_districts=sub_districts
            )
        except Exception as e:
            logger.error(f"Error generating priority score data for regency {regency_id}: {str(e)}")
            raise 