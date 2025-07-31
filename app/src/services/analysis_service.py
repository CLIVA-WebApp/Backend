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
from app.src.models.regency import Regency
from app.src.models.subdistrict import Subdistrict
from app.src.models.health_facility import HealthFacility
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import math
import random
from uuid import UUID

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    async def get_regency_by_id(self, regency_id: UUID) -> Optional[RegencySchema]:
        """
        Get a specific regency by ID.
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
                logger.warning(f"Regency with ID {regency_id} not found")
                return None
            
            regency_schema = RegencySchema(
                id=regency.id,
                name=regency.name,
                pum_code=regency.pum_code,
                province_id=regency.province_id,
                province_name=regency.province.name if regency.province else None,
                area_km2=regency.area_km2
            )
                
            logger.info(f"Retrieved regency: {regency.name}")
            return regency_schema
            
        except Exception as e:
            logger.error(f"Error retrieving regency {regency_id}: {str(e)}")
            raise
    
    async def get_subdistrict_by_id(self, subdistrict_id: UUID) -> Optional[SubDistrictSchema]:
        """
        Get a specific sub-district by ID.
        """
        try:
            # Check if this is a mock request
            if str(subdistrict_id) == "mock":
                mock_subdistrict = SubDistrictSchema(
                    id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                    name="Kecamatan Cibinong",
                    pum_code="320101",
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    population_count=150000,
                    poverty_level=12.5,
                    area_km2=45.2
                )
                return mock_subdistrict
            
            subdistrict = self.db.query(Subdistrict).filter(Subdistrict.id == subdistrict_id).first()
            
            if not subdistrict:
                logger.warning(f"Sub-district with ID {subdistrict_id} not found")
                return None
            
            subdistrict_schema = SubDistrictSchema(
                id=subdistrict.id,
                name=subdistrict.name,
                pum_code=subdistrict.pum_code,
                regency_id=subdistrict.regency_id,
                regency_name=subdistrict.regency.name if subdistrict.regency else None,
                population_count=subdistrict.population_count,
                poverty_level=subdistrict.poverty_level,
                area_km2=subdistrict.area_km2
            )
                
            logger.info(f"Retrieved sub-district: {subdistrict.name}")
            return subdistrict_schema
            
        except Exception as e:
            logger.error(f"Error retrieving sub-district {subdistrict_id}: {str(e)}")
            raise
    
    async def get_facilities_by_subdistrict(self, subdistrict_id: UUID) -> List[FacilitySchema]:
        """
        Get all health facilities within a specific sub-district.
        """
        try:
            # Check if this is a mock request
            if str(subdistrict_id) == "mock":
                mock_facilities = [
                    FacilitySchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440006"),
                        name="Puskesmas Cibinong",
                        type="puskesmas",
                        latitude=-6.4815,
                        longitude=106.8540,
                        regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                        regency_name="Kabupaten Bogor",
                        sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                        sub_district_name="Kecamatan Cibinong"
                    ),
                    FacilitySchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440007"),
                        name="RSUD Cibinong",
                        type="hospital",
                        latitude=-6.4815,
                        longitude=106.8540,
                        regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                        regency_name="Kabupaten Bogor",
                        sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                        sub_district_name="Kecamatan Cibinong"
                    )
                ]
                return mock_facilities
            
            facilities = self.db.query(HealthFacility).filter(HealthFacility.sub_district_id == subdistrict_id).all()
            
            facility_schemas = []
            for facility in facilities:
                facility_schema = FacilitySchema(
                    id=facility.id,
                    name=facility.name,
                    type=facility.type,
                    latitude=facility.latitude,
                    longitude=facility.longitude,
                    regency_id=facility.regency_id,
                    regency_name=facility.regency.name if facility.regency else None,
                    sub_district_id=facility.sub_district_id,
                    sub_district_name=facility.sub_district.name if facility.sub_district else None
                )
                facility_schemas.append(facility_schema)
            
            logger.info(f"Retrieved {len(facility_schemas)} facilities for sub-district {subdistrict_id}")
            return facility_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving facilities for sub-district {subdistrict_id}: {str(e)}")
            raise
    
    async def generate_heatmap_data(self, regency_id: UUID) -> HeatmapData:
        """
        Generate heatmap data for a specific regency.
        """
        try:
            # Get regency info
            regency = self.db.query(Regency).filter(Regency.id == regency_id).first()
            if not regency:
                raise ValueError(f"Regency with ID {regency_id} not found")
            
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_heatmap_data = HeatmapData(
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    total_population=5000000,
                    population_outside_radius=750000,
                    service_radius_km=5.0,
                    heatmap_points=[
                        HeatmapPoint(
                            latitude=-6.4815,
                            longitude=106.8540,
                            population_density=1500.0,
                            access_score=0.8,
                            distance_to_facility=2.5
                        ),
                        HeatmapPoint(
                            latitude=-6.4233,
                            longitude=106.9073,
                            population_density=1200.0,
                            access_score=0.6,
                            distance_to_facility=4.2
                        )
                    ]
                )
                return mock_heatmap_data
            
            # Mock heatmap generation for now
            # In reality, this would involve complex spatial analysis
            heatmap_points = []
            total_population = 5000000
            population_outside_radius = 750000
            service_radius_km = 5.0
            
            # Generate mock heatmap points
            for i in range(10):
                lat = -6.4 + (random.random() - 0.5) * 0.2
                lng = 106.8 + (random.random() - 0.5) * 0.2
                heatmap_points.append(HeatmapPoint(
                    latitude=lat,
                    longitude=lng,
                    population_density=random.uniform(800, 2000),
                    access_score=random.uniform(0.3, 0.9),
                    distance_to_facility=random.uniform(1.0, 8.0)
                ))
            
            heatmap_data = HeatmapData(
                regency_id=regency_id,
                regency_name=regency.name,
                total_population=total_population,
                population_outside_radius=population_outside_radius,
                service_radius_km=service_radius_km,
                heatmap_points=heatmap_points
            )
            
            logger.info(f"Generated heatmap data for regency {regency.name}")
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Error generating heatmap data for regency {regency_id}: {str(e)}")
            raise
    
    async def generate_priority_score_data(self, regency_id: UUID) -> PriorityScoreData:
        """
        Generate priority score data for a specific regency.
        """
        try:
            # Get regency info
            regency = self.db.query(Regency).filter(Regency.id == regency_id).first()
            if not regency:
                raise ValueError(f"Regency with ID {regency_id} not found")
            
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_priority_data = PriorityScoreData(
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    total_sub_districts=2,
                    sub_districts=[
                        SubDistrictScore(
                            sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                            sub_district_name="Kecamatan Cibinong",
                            gap_factor=0.75,
                            efficiency_factor=0.65,
                            vulnerability_factor=0.80,
                            composite_score=0.73,
                            rank=1
                        ),
                        SubDistrictScore(
                            sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440005"),
                            sub_district_name="Kecamatan Gunung Putri",
                            gap_factor=0.60,
                            efficiency_factor=0.70,
                            vulnerability_factor=0.65,
                            composite_score=0.65,
                            rank=2
                        )
                    ]
                )
                return mock_priority_data
            
            # Mock priority score generation for now
            # In reality, this would involve complex calculations
            sub_districts = self.db.query(Subdistrict).filter(Subdistrict.regency_id == regency_id).all()
            
            sub_district_scores = []
            for i, subdistrict in enumerate(sub_districts):
                # Mock calculations for demonstration
                gap_factor = random.uniform(0.4, 0.9)
                efficiency_factor = random.uniform(0.3, 0.8)
                vulnerability_factor = random.uniform(0.5, 0.9)
                composite_score = (gap_factor + efficiency_factor + vulnerability_factor) / 3
                
                sub_district_scores.append(SubDistrictScore(
                    sub_district_id=subdistrict.id,
                    sub_district_name=subdistrict.name,
                    gap_factor=gap_factor,
                    efficiency_factor=efficiency_factor,
                    vulnerability_factor=vulnerability_factor,
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
            
            logger.info(f"Generated priority score data for regency {regency.name}")
            return priority_data
            
        except Exception as e:
            logger.error(f"Error generating priority score data for regency {regency_id}: {str(e)}")
            raise
    
    async def get_subdistrict_details(self, subdistrict_id: UUID) -> SubDistrictDetails:
        """
        Get detailed statistics for a specific sub-district.
        """
        try:
            # Get sub-district info
            subdistrict = self.db.query(Subdistrict).filter(Subdistrict.id == subdistrict_id).first()
            if not subdistrict:
                raise ValueError(f"Sub-district with ID {subdistrict_id} not found")
            
            # Check if this is a mock request
            if str(subdistrict_id) == "mock":
                mock_details = SubDistrictDetails(
                    sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                    sub_district_name="Kecamatan Cibinong",
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    population=150000,
                    area_km2=45.2,
                    population_density=3318.58,
                    poverty_rate=12.5,
                    existing_facilities_count=2,
                    existing_facilities=[
                        {
                            "name": "Puskesmas Cibinong",
                            "type": "puskesmas",
                            "latitude": -6.4815,
                            "longitude": 106.8540
                        },
                        {
                            "name": "RSUD Cibinong",
                            "type": "hospital",
                            "latitude": -6.4815,
                            "longitude": 106.8540
                        }
                    ],
                    gap_factor=0.75,
                    efficiency_factor=0.65,
                    vulnerability_factor=0.80,
                    composite_score=0.73,
                    rank=1
                )
                return mock_details
            
            # Get facilities for this sub-district
            facilities = self.db.query(HealthFacility).filter(HealthFacility.sub_district_id == subdistrict_id).all()
            
            # Mock detailed statistics
            population = subdistrict.population_count or 100000
            area_km2 = subdistrict.area_km2 or 50.0
            population_density = population / area_km2 if area_km2 > 0 else 0
            poverty_rate = subdistrict.poverty_level or 15.0
            
            # Mock calculated scores
            gap_factor = random.uniform(0.4, 0.9)
            efficiency_factor = random.uniform(0.3, 0.8)
            vulnerability_factor = random.uniform(0.5, 0.9)
            composite_score = (gap_factor + efficiency_factor + vulnerability_factor) / 3
            
            # Convert facilities to dict format
            existing_facilities = []
            for facility in facilities:
                existing_facilities.append({
                    "name": facility.name,
                    "type": facility.type.value if hasattr(facility.type, 'value') else str(facility.type),
                    "latitude": facility.latitude,
                    "longitude": facility.longitude
                })
            
            details = SubDistrictDetails(
                sub_district_id=subdistrict.id,
                sub_district_name=subdistrict.name,
                regency_id=subdistrict.regency_id,
                regency_name=subdistrict.regency.name if subdistrict.regency else None,
                population=population,
                area_km2=area_km2,
                population_density=population_density,
                poverty_rate=poverty_rate,
                existing_facilities_count=len(existing_facilities),
                existing_facilities=existing_facilities,
                gap_factor=gap_factor,
                efficiency_factor=efficiency_factor,
                vulnerability_factor=vulnerability_factor,
                composite_score=composite_score,
                rank=1  # Mock rank
            )
            
            logger.info(f"Generated sub-district details for {subdistrict.name}")
            return details
            
        except Exception as e:
            logger.error(f"Error generating sub-district details for {subdistrict_id}: {str(e)}")
            raise 