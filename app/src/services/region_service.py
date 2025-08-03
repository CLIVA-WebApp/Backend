from typing import List, Optional
from app.src.schemas.region_schema import ProvinceSchema, RegencySchema, SubDistrictSchema, FacilitySchema
from app.src.controllers.region_controller import region_controller
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class RegionService:
    def __init__(self):
        pass  # No need to initialize database session, we'll use controller
    
    async def get_all_provinces(self) -> List[ProvinceSchema]:
        """
        Get all provinces in Indonesia.
        """
        try:
            provinces_data = await region_controller.get_all_provinces()
            
            province_schemas = []
            for province_data in provinces_data:
                province_schemas.append(ProvinceSchema(**province_data))
            
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
            
            province_data = await region_controller.get_province_by_id(province_id)
            
            if not province_data:
                logger.warning(f"Province with ID {province_id} not found")
                return None
            
            province_schema = ProvinceSchema(**province_data)
            logger.info(f"Retrieved province: {province_schema.name}")
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
            
            regencies_data = await region_controller.get_regencies_by_province(province_id)
            
            regency_schemas = []
            for regency_data in regencies_data:
                regency_schemas.append(RegencySchema(**regency_data))
            
            logger.info(f"Retrieved {len(regency_schemas)} regencies for province {province_id}")
            return regency_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving regencies for province {province_id}: {str(e)}")
            raise
    
    async def get_all_regencies(self) -> List[RegencySchema]:
        """
        Get all regencies in Indonesia.
        """
        try:
            regencies_data = await region_controller.get_all_regencies()
            
            regency_schemas = []
            for regency_data in regencies_data:
                regency_schemas.append(RegencySchema(**regency_data))
            
            logger.info(f"Retrieved {len(regency_schemas)} regencies")
            return regency_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving all regencies: {str(e)}")
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
            
            subdistricts_data = await region_controller.get_subdistricts_by_regency(regency_id)
            
            subdistrict_schemas = []
            for subdistrict_data in subdistricts_data:
                subdistrict_schemas.append(SubDistrictSchema(**subdistrict_data))
            
            logger.info(f"Retrieved {len(subdistrict_schemas)} subdistricts for regency {regency_id}")
            return subdistrict_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving subdistricts for regency {regency_id}: {str(e)}")
            raise
    
    async def get_all_subdistricts(self) -> List[SubDistrictSchema]:
        """
        Get all sub-districts in Indonesia.
        """
        try:
            subdistricts_data = await region_controller.get_all_subdistricts()
            
            subdistrict_schemas = []
            for subdistrict_data in subdistricts_data:
                subdistrict_schemas.append(SubDistrictSchema(**subdistrict_data))
            
            logger.info(f"Retrieved {len(subdistrict_schemas)} subdistricts")
            return subdistrict_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving all subdistricts: {str(e)}")
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
                        subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
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
                        subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                        sub_district_name="Kecamatan Cibinong"
                    )
                ]
                return mock_facilities
            
            facilities_data = await region_controller.get_facilities_by_regency(regency_id)
            
            facility_schemas = []
            for facility_data in facilities_data:
                facility_schemas.append(FacilitySchema(**facility_data))
            
            logger.info(f"Retrieved {len(facility_schemas)} facilities for regency {regency_id}")
            return facility_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving facilities for regency {regency_id}: {str(e)}")
            raise 