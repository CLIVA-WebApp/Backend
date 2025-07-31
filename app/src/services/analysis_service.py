from typing import List, Optional, Dict, Any
from app.src.schemas.analysis_schema import (
    HeatmapData,
    HeatmapPoint,
    PriorityScoreData,
    SubDistrictScore,
    SubDistrictDetails
)
from app.src.schemas.region_schema import RegencySchema, SubDistrictSchema, FacilitySchema
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
        Get a specific regency by ID.
        Currently returns mock data.
        """
        try:
            # Mock data - replace with actual database query
            mock_regencies = {
                "3201": RegencySchema(
                    id="3201",
                    name="Kabupaten Bogor",
                    code="3201",
                    province_id="32",
                    province_name="Jawa Barat"
                ),
                "3202": RegencySchema(
                    id="3202",
                    name="Kabupaten Sukabumi",
                    code="3202",
                    province_id="32",
                    province_name="Jawa Barat"
                )
            }
            
            regency = mock_regencies.get(regency_id)
            if not regency:
                logger.warning(f"Regency with ID {regency_id} not found")
                return None
                
            logger.info(f"Retrieved regency: {regency.name}")
            return regency
            
        except Exception as e:
            logger.error(f"Error retrieving regency {regency_id}: {str(e)}")
            raise
    
    async def get_subdistrict_by_id(self, subdistrict_id: str) -> Optional[SubDistrictSchema]:
        """
        Get a specific sub-district by ID.
        Currently returns mock data.
        """
        try:
            # Mock data - replace with actual database query
            mock_subdistricts = {
                "320101": SubDistrictSchema(
                    id="320101",
                    name="Kecamatan Cibinong",
                    code="320101",
                    regency_id="3201",
                    regency_name="Kabupaten Bogor"
                ),
                "320102": SubDistrictSchema(
                    id="320102",
                    name="Kecamatan Gunung Putri",
                    code="320102",
                    regency_id="3201",
                    regency_name="Kabupaten Bogor"
                ),
                "320201": SubDistrictSchema(
                    id="320201",
                    name="Kecamatan Pelabuhan Ratu",
                    code="320201",
                    regency_id="3202",
                    regency_name="Kabupaten Sukabumi"
                )
            }
            
            subdistrict = mock_subdistricts.get(subdistrict_id)
            if not subdistrict:
                logger.warning(f"Sub-district with ID {subdistrict_id} not found")
                return None
                
            logger.info(f"Retrieved sub-district: {subdistrict.name}")
            return subdistrict
            
        except Exception as e:
            logger.error(f"Error retrieving sub-district {subdistrict_id}: {str(e)}")
            raise
    
    async def get_facilities_by_subdistrict(self, subdistrict_id: str) -> List[FacilitySchema]:
        """
        Get all health facilities within a specific sub-district.
        Currently returns mock data.
        """
        try:
            # Mock data - replace with actual database query
            mock_facilities = {
                "320101": [
                    FacilitySchema(
                        id="F001",
                        name="Puskesmas Cibinong",
                        type="puskesmas",
                        latitude=-6.4815,
                        longitude=106.8540,
                        regency_id="3201",
                        regency_name="Kabupaten Bogor",
                        sub_district_id="320101",
                        sub_district_name="Kecamatan Cibinong"
                    ),
                    FacilitySchema(
                        id="F002",
                        name="RSUD Cibinong",
                        type="hospital",
                        latitude=-6.4815,
                        longitude=106.8540,
                        regency_id="3201",
                        regency_name="Kabupaten Bogor",
                        sub_district_id="320101",
                        sub_district_name="Kecamatan Cibinong"
                    )
                ],
                "320102": [
                    FacilitySchema(
                        id="F003",
                        name="Puskesmas Gunung Putri",
                        type="puskesmas",
                        latitude=-6.4233,
                        longitude=106.9073,
                        regency_id="3201",
                        regency_name="Kabupaten Bogor",
                        sub_district_id="320102",
                        sub_district_name="Kecamatan Gunung Putri"
                    )
                ],
                "320201": [
                    FacilitySchema(
                        id="F004",
                        name="Puskesmas Pelabuhan Ratu",
                        type="puskesmas",
                        latitude=-7.0294,
                        longitude=106.5500,
                        regency_id="3202",
                        regency_name="Kabupaten Sukabumi",
                        sub_district_id="320201",
                        sub_district_name="Kecamatan Pelabuhan Ratu"
                    )
                ]
            }
            
            facilities = mock_facilities.get(subdistrict_id, [])
            logger.info(f"Retrieved {len(facilities)} facilities for sub-district {subdistrict_id}")
            return facilities
            
        except Exception as e:
            logger.error(f"Error retrieving facilities for sub-district {subdistrict_id}: {str(e)}")
            raise
    
    async def generate_heatmap_data(self, regency_id: str) -> HeatmapData:
        """
        Generate heatmap data for a specific regency.
        Currently returns mock data.
        """
        try:
            # Get regency info
            regency = await self.get_regency_by_id(regency_id)
            if not regency:
                raise ValueError(f"Regency with ID {regency_id} not found")
            
            # Mock heatmap data
            total_population = 50000
            population_outside_radius = 15000
            service_radius_km = 5.0
            
            # Generate mock heatmap points
            heatmap_points = []
            for i in range(20):  # Generate 20 sample points
                lat = -6.4815 + (random.uniform(-0.1, 0.1))
                lng = 106.8540 + (random.uniform(-0.1, 0.1))
                
                heatmap_points.append(HeatmapPoint(
                    latitude=lat,
                    longitude=lng,
                    population_density=random.uniform(100, 1000),
                    access_score=random.uniform(0.1, 1.0),
                    distance_to_facility=random.uniform(0.5, 10.0)
                ))
            
            heatmap_data = HeatmapData(
                regency_id=regency_id,
                regency_name=regency.name,
                total_population=total_population,
                population_outside_radius=population_outside_radius,
                service_radius_km=service_radius_km,
                heatmap_points=heatmap_points
            )
            
            logger.info(f"Generated heatmap data for regency {regency_id}")
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Error generating heatmap data for regency {regency_id}: {str(e)}")
            raise
    
    async def generate_priority_score_data(self, regency_id: str) -> PriorityScoreData:
        """
        Generate priority score data for a specific regency.
        Currently returns mock data.
        """
        try:
            # Get regency info
            regency = await self.get_regency_by_id(regency_id)
            if not regency:
                raise ValueError(f"Regency with ID {regency_id} not found")
            
            # Mock sub-district scores
            mock_subdistricts = [
                {
                    "id": "320101",
                    "name": "Kecamatan Cibinong",
                    "gap_factor": 0.8,
                    "efficiency_factor": 0.6,
                    "vulnerability_factor": 0.7
                },
                {
                    "id": "320102",
                    "name": "Kecamatan Gunung Putri",
                    "gap_factor": 0.9,
                    "efficiency_factor": 0.5,
                    "vulnerability_factor": 0.8
                },
                {
                    "id": "320103",
                    "name": "Kecamatan Citeureup",
                    "gap_factor": 0.7,
                    "efficiency_factor": 0.7,
                    "vulnerability_factor": 0.6
                }
            ]
            
            # Calculate composite scores and rank
            sub_district_scores = []
            for i, subdistrict in enumerate(mock_subdistricts):
                composite_score = (
                    subdistrict["gap_factor"] * 0.4 +
                    subdistrict["efficiency_factor"] * 0.3 +
                    subdistrict["vulnerability_factor"] * 0.3
                )
                
                sub_district_scores.append(SubDistrictScore(
                    sub_district_id=subdistrict["id"],
                    sub_district_name=subdistrict["name"],
                    gap_factor=subdistrict["gap_factor"],
                    efficiency_factor=subdistrict["efficiency_factor"],
                    vulnerability_factor=subdistrict["vulnerability_factor"],
                    composite_score=composite_score,
                    rank=i + 1
                ))
            
            # Sort by composite score (highest first)
            sub_district_scores.sort(key=lambda x: x.composite_score, reverse=True)
            
            # Update ranks
            for i, score in enumerate(sub_district_scores):
                score.rank = i + 1
            
            priority_data = PriorityScoreData(
                regency_id=regency_id,
                regency_name=regency.name,
                total_sub_districts=len(sub_district_scores),
                sub_districts=sub_district_scores
            )
            
            logger.info(f"Generated priority score data for regency {regency_id}")
            return priority_data
            
        except Exception as e:
            logger.error(f"Error generating priority score data for regency {regency_id}: {str(e)}")
            raise
    
    async def get_subdistrict_details(self, subdistrict_id: str) -> SubDistrictDetails:
        """
        Get detailed statistics for a specific sub-district.
        Currently returns mock data.
        """
        try:
            # Get sub-district info
            subdistrict = await self.get_subdistrict_by_id(subdistrict_id)
            if not subdistrict:
                raise ValueError(f"Sub-district with ID {subdistrict_id} not found")
            
            # Get facilities for this sub-district
            facilities = await self.get_facilities_by_subdistrict(subdistrict_id)
            
            # Mock detailed statistics
            population = 25000
            area_km2 = 45.5
            population_density = population / area_km2
            poverty_rate = 12.5
            
            # Calculate scores (similar to priority score calculation)
            gap_factor = 0.8
            efficiency_factor = 0.6
            vulnerability_factor = 0.7
            composite_score = (
                gap_factor * 0.4 +
                efficiency_factor * 0.3 +
                vulnerability_factor * 0.3
            )
            
            # Mock rank (in practice, this would be calculated across all sub-districts)
            rank = 1
            
            # Convert facilities to dict format for response
            existing_facilities = []
            for facility in facilities:
                existing_facilities.append({
                    "id": facility.id,
                    "name": facility.name,
                    "type": facility.type,
                    "latitude": facility.latitude,
                    "longitude": facility.longitude
                })
            
            details = SubDistrictDetails(
                sub_district_id=subdistrict_id,
                sub_district_name=subdistrict.name,
                regency_id=subdistrict.regency_id,
                regency_name=subdistrict.regency_name,
                population=population,
                area_km2=area_km2,
                population_density=population_density,
                poverty_rate=poverty_rate,
                existing_facilities_count=len(facilities),
                existing_facilities=existing_facilities,
                gap_factor=gap_factor,
                efficiency_factor=efficiency_factor,
                vulnerability_factor=vulnerability_factor,
                composite_score=composite_score,
                rank=rank
            )
            
            logger.info(f"Generated detailed statistics for sub-district {subdistrict_id}")
            return details
            
        except Exception as e:
            logger.error(f"Error generating sub-district details for {subdistrict_id}: {str(e)}")
            raise 