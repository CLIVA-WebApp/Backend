from typing import List, Optional
from app.src.schemas.region_schema import ProvinceSchema, RegencySchema, SubDistrictSchema, FacilitySchema
from app.src.config.database import SessionLocal
from app.src.models.province import Province
from app.src.models.regency import Regency
from app.src.models.subdistrict import Subdistrict
from app.src.models.health_facility import HealthFacility
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class RegionService:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    async def get_all_provinces(self) -> List[ProvinceSchema]:
        """
        Get all provinces in Indonesia.
        """
        try:
            provinces = self.db.query(Province).all()
            
            province_schemas = []
            for province in provinces:
                province_schemas.append(ProvinceSchema(
                    id=province.id,
                    name=province.name,
                    pum_code=province.pum_code,
                    area_km2=province.area_km2
                ))
            
            logger.info(f"Retrieved {len(province_schemas)} provinces")
            return province_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving provinces: {str(e)}")
            raise
    
    async def get_province_by_id(self, province_id: UUID) -> Optional[ProvinceSchema]:
        """
        Get a specific province by ID.
        """
        try:
            # Check if this is a mock request
            if str(province_id) == "mock":
                mock_provinces = {
                    "mock": ProvinceSchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                        name="Jawa Barat",
                        pum_code="32",
                        area_km2=35377.76
                    )
                }
                return mock_provinces.get("mock")
            
            province = self.db.query(Province).filter(Province.id == province_id).first()
            
            if not province:
                logger.warning(f"Province with ID {province_id} not found")
                return None
            
            province_schema = ProvinceSchema(
                id=province.id,
                name=province.name,
                pum_code=province.pum_code,
                area_km2=province.area_km2
            )
                
            logger.info(f"Retrieved province: {province.name}")
            return province_schema
            
        except Exception as e:
            logger.error(f"Error retrieving province {province_id}: {str(e)}")
            raise
    
    async def get_regencies_by_province(self, province_id: UUID) -> List[RegencySchema]:
        """
        Get all regencies within a specific province.
        """
        try:
            # Check if this is a mock request
            if str(province_id) == "mock":
                mock_regencies = [
                    RegencySchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                        name="Kabupaten Bogor",
                        pum_code="3201",
                        province_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                        province_name="Jawa Barat",
                        area_km2=2985.43
                    ),
                    RegencySchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440003"),
                        name="Kabupaten Sukabumi",
                        pum_code="3202",
                        province_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                        province_name="Jawa Barat",
                        area_km2=4181.77
                    )
                ]
                return mock_regencies
            
            regencies = self.db.query(Regency).filter(Regency.province_id == province_id).all()
            
            regency_schemas = []
            for regency in regencies:
                regency_schemas.append(RegencySchema(
                    id=regency.id,
                    name=regency.name,
                    pum_code=regency.pum_code,
                    province_id=regency.province_id,
                    province_name=regency.province.name if hasattr(regency, 'province') and regency.province else None,
                    area_km2=regency.area_km2
                ))
            
            logger.info(f"Retrieved {len(regency_schemas)} regencies for province {province_id}")
            return regency_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving regencies for province {province_id}: {str(e)}")
            raise
    
    async def get_subdistricts_by_regency(self, regency_id: UUID) -> List[SubDistrictSchema]:
        """
        Get all sub-districts within a specific regency.
        """
        try:
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_subdistricts = [
                    SubDistrictSchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                        name="Kecamatan Cibinong",
                        pum_code="320101",
                        regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                        regency_name="Kabupaten Bogor",
                        population_count=150000,
                        poverty_level=12.5,
                        area_km2=45.2
                    ),
                    SubDistrictSchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440005"),
                        name="Kecamatan Gunung Putri",
                        pum_code="320102",
                        regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                        regency_name="Kabupaten Bogor",
                        population_count=120000,
                        poverty_level=10.8,
                        area_km2=38.7
                    )
                ]
                return mock_subdistricts
            
            subdistricts = self.db.query(Subdistrict).filter(Subdistrict.regency_id == regency_id).all()
            
            subdistrict_schemas = []
            for subdistrict in subdistricts:
                subdistrict_schemas.append(SubDistrictSchema(
                    id=subdistrict.id,
                    name=subdistrict.name,
                    pum_code=subdistrict.pum_code,
                    regency_id=subdistrict.regency_id,
                    regency_name=subdistrict.regency.name if hasattr(subdistrict, 'regency') and subdistrict.regency else None,
                    population_count=subdistrict.population_count,
                    poverty_level=subdistrict.poverty_level,
                    area_km2=subdistrict.area_km2
                ))
            
            logger.info(f"Retrieved {len(subdistrict_schemas)} subdistricts for regency {regency_id}")
            return subdistrict_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving subdistricts for regency {regency_id}: {str(e)}")
            raise
    
    async def get_facilities_by_regency(self, regency_id: UUID) -> List[FacilitySchema]:
        """
        Get all health facilities within a specific regency.
        """
        try:
            # Check if this is a mock request
            if str(regency_id) == "mock":
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
            
            facilities = self.db.query(HealthFacility).join(Subdistrict).filter(Subdistrict.regency_id == regency_id).all()
            
            facility_schemas = []
            for facility in facilities:
                # Extract coordinates from geometry
                coords_query = text("""
                    SELECT 
                        ST_X(geom) as longitude,
                        ST_Y(geom) as latitude
                    FROM health_facilities 
                    WHERE id = :facility_id
                """)
                coords_result = self.db.execute(coords_query, {"facility_id": facility.id}).first()
                
                facility_schemas.append(FacilitySchema(
                    id=facility.id,
                    name=facility.name,
                    type=facility.type.value if hasattr(facility.type, 'value') else str(facility.type),
                    latitude=coords_result.latitude if coords_result else 0.0,
                    longitude=coords_result.longitude if coords_result else 0.0,
                    regency_id=facility.sub_district.regency_id if hasattr(facility, 'sub_district') and facility.sub_district else None,
                    regency_name=facility.sub_district.regency.name if hasattr(facility, 'sub_district') and facility.sub_district and hasattr(facility.sub_district, 'regency') and facility.sub_district.regency else None,
                    sub_district_id=facility.subdistrict_id,
                    sub_district_name=facility.sub_district.name if hasattr(facility, 'sub_district') and facility.sub_district else None
                ))
            
            logger.info(f"Retrieved {len(facility_schemas)} facilities for regency {regency_id}")
            return facility_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving facilities for regency {regency_id}: {str(e)}")
            raise 