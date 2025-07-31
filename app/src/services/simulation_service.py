from typing import List, Optional, Dict, Any
from app.src.schemas.analysis_schema import (
    SimulationResult,
    OptimizedFacility
)
from app.src.schemas.region_schema import RegencySchema
from app.src.config.database import SessionLocal
from app.src.models.regency import Regency
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import math
import random
from uuid import UUID

logger = logging.getLogger(__name__)

class SimulationService:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    async def get_regency_by_id(self, regency_id: UUID) -> Optional[RegencySchema]:
        """
        Retrieve a specific regency by ID.
        
        Args:
            regency_id: The unique identifier of the regency
            
        Returns:
            Optional[RegencySchema]: Regency data if found, None otherwise
        """
        try:
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_regency = RegencySchema(
                    id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    name="Kabupaten Bogor",
                    pum_code="3201",
                    province_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                    province_name="Jawa Barat",
                    area_km2=2985.43
                )
                return mock_regency
            
            regency = self.db.query(Regency).filter(Regency.id == regency_id).first()
            
            if not regency:
                return None
            
            regency_schema = RegencySchema(
                id=regency.id,
                name=regency.name,
                pum_code=regency.pum_code,
                province_id=regency.province_id,
                province_name=regency.province.name if regency.province else None,
                area_km2=regency.area_km2
            )
            
            return regency_schema
        except Exception as e:
            logger.error(f"Error retrieving regency {regency_id}: {str(e)}")
            raise
    
    async def run_optimization_simulation(
        self,
        regency_id: UUID,
        budget: float,
        facility_type: str,
        optimization_criteria: List[str]
    ) -> SimulationResult:
        """
        Run optimization simulation for health facility placement.
        
        This method implements the "'What-If' Optimization Simulator" which:
        1. Analyzes population distribution
        2. Considers existing health facilities
        3. Evaluates transportation infrastructure
        4. Optimizes facility placement within budget constraints
        5. Maximizes population coverage
        
        Args:
            regency_id: The unique identifier of the regency
            budget: Available budget in currency units
            facility_type: Type of health facility to optimize
            optimization_criteria: List of optimization criteria to consider
            
        Returns:
            SimulationResult: Optimization results including recommended facility locations
        """
        try:
            # Validate regency exists
            regency = await self.get_regency_by_id(regency_id)
            if not regency:
                raise ValueError(f"Regency {regency_id} not found")
            
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_simulation_result = SimulationResult(
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    total_budget=budget,
                    budget_used=budget * 0.85,
                    facilities_recommended=3,
                    total_population_covered=450000,
                    coverage_percentage=90.0,
                    optimized_facilities=[
                        OptimizedFacility(
                            latitude=-6.4233,
                            longitude=106.9073,
                            sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440005"),
                            sub_district_name="Kecamatan Gunung Putri",
                            estimated_cost=budget * 0.3,
                            population_covered=150000,
                            coverage_radius_km=5.0
                        ),
                        OptimizedFacility(
                            latitude=-6.4815,
                            longitude=106.8540,
                            sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                            sub_district_name="Kecamatan Cibinong",
                            estimated_cost=budget * 0.35,
                            population_covered=200000,
                            coverage_radius_km=5.0
                        ),
                        OptimizedFacility(
                            latitude=-6.5000,
                            longitude=106.8000,
                            sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                            sub_district_name="Kecamatan Cibinong",
                            estimated_cost=budget * 0.2,
                            population_covered=100000,
                            coverage_radius_km=5.0
                        )
                    ]
                )
                return mock_simulation_result
            
            # Mock optimization simulation
            # In reality, this would involve complex algorithms
            
            # Calculate number of facilities based on budget
            # Mock cost per facility
            cost_per_facility = 5000000  # 5 million currency units
            max_facilities = int(budget / cost_per_facility)
            
            # Generate mock optimized facilities
            optimized_facilities = []
            budget_used = 0
            total_population_covered = 0
            
            for i in range(min(max_facilities, 3)):  # Mock 3 facilities max
                # Mock facility location
                lat = -6.2088 + (i * 0.02)  # Spread facilities
                lng = 106.8456 + (i * 0.02)
                
                # Mock facility data
                estimated_cost = cost_per_facility * (1 + random.uniform(-0.1, 0.1))
                population_covered = random.randint(5000, 15000)
                coverage_radius = random.uniform(3.0, 8.0)
                
                optimized_facilities.append(OptimizedFacility(
                    latitude=lat,
                    longitude=lng,
                    sub_district_id=f"{regency_id}0{i+1}",
                    sub_district_name=f"Kecamatan {i+1}",
                    estimated_cost=estimated_cost,
                    population_covered=population_covered,
                    coverage_radius_km=coverage_radius
                ))
                
                budget_used += estimated_cost
                total_population_covered += population_covered
            
            # Calculate coverage percentage
            total_population = 50000  # Mock total population
            coverage_percentage = (total_population_covered / total_population) * 100
            
            return SimulationResult(
                regency_id=regency_id,
                regency_name=regency.name,
                total_budget=budget,
                budget_used=budget_used,
                facilities_recommended=len(optimized_facilities),
                total_population_covered=total_population_covered,
                coverage_percentage=coverage_percentage,
                optimized_facilities=optimized_facilities
            )
        except Exception as e:
            logger.error(f"Error running optimization simulation for regency {regency_id}: {str(e)}")
            raise
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lng1: Coordinates of first point
            lat2, lng2: Coordinates of second point
            
        Returns:
            float: Distance in kilometers
        """
        # Haversine formula implementation
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _optimize_facility_placement(
        self,
        population_centers: List[Dict[str, Any]],
        existing_facilities: List[Dict[str, Any]],
        budget: float,
        facility_type: str
    ) -> List[OptimizedFacility]:
        """
        Optimize facility placement using advanced algorithms.
        
        This is a placeholder for the actual optimization algorithm.
        In a real implementation, this would use sophisticated algorithms
        like genetic algorithms, linear programming, or machine learning.
        
        Args:
            population_centers: List of population centers with coordinates and population
            existing_facilities: List of existing health facilities
            budget: Available budget
            facility_type: Type of facility to optimize
            
        Returns:
            List[OptimizedFacility]: Optimized facility locations
        """
        # Placeholder implementation
        # In reality, this would implement complex optimization algorithms
        
        optimized_facilities = []
        # Algorithm implementation would go here
        
        return optimized_facilities 