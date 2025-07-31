from typing import List, Optional
from app.src.schemas.region_schema import ProvinceSchema, RegencySchema, SubDistrictSchema, FacilitySchema
from app.src.config.database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class RegionService:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    async def get_all_provinces(self) -> List[ProvinceSchema]:
        """
        Get all provinces in Indonesia.
        Currently returns mock data.
        """
        try:
            # Mock data - replace with actual database query
            mock_provinces = [
                ProvinceSchema(
                    id="32",
                    name="Jawa Barat",
                    code="32"
                ),
                ProvinceSchema(
                    id="31",
                    name="DKI Jakarta",
                    code="31"
                ),
                ProvinceSchema(
                    id="36",
                    name="Banten",
                    code="36"
                )
            ]
            
            logger.info(f"Retrieved {len(mock_provinces)} provinces")
            return mock_provinces
            
        except Exception as e:
            logger.error(f"Error retrieving provinces: {str(e)}")
            raise
    
    async def get_province_by_id(self, province_id: str) -> Optional[ProvinceSchema]:
        """
        Get a specific province by ID.
        Currently returns mock data.
        """
        try:
            # Mock data - replace with actual database query
            mock_provinces = {
                "32": ProvinceSchema(id="32", name="Jawa Barat", code="32"),
                "31": ProvinceSchema(id="31", name="DKI Jakarta", code="31"),
                "36": ProvinceSchema(id="36", name="Banten", code="36")
            }
            
            province = mock_provinces.get(province_id)
            if not province:
                logger.warning(f"Province with ID {province_id} not found")
                return None
                
            logger.info(f"Retrieved province: {province.name}")
            return province
            
        except Exception as e:
            logger.error(f"Error retrieving province {province_id}: {str(e)}")
            raise
    
    async def get_regencies_by_province(self, province_id: str) -> List[RegencySchema]:
        """
        Get all regencies within a specific province.
        Currently returns mock data.
        """
        try:
            # Mock data - replace with actual database query
            mock_regencies = {
                "32": [
                    RegencySchema(
                        id="3201",
                        name="Kabupaten Bogor",
                        code="3201",
                        province_id="32",
                        province_name="Jawa Barat"
                    ),
                    RegencySchema(
                        id="3202",
                        name="Kabupaten Sukabumi",
                        code="3202",
                        province_id="32",
                        province_name="Jawa Barat"
                    )
                ],
                "31": [
                    RegencySchema(
                        id="3101",
                        name="Kabupaten Kepulauan Seribu",
                        code="3101",
                        province_id="31",
                        province_name="DKI Jakarta"
                    )
                ],
                "36": [
                    RegencySchema(
                        id="3601",
                        name="Kabupaten Pandeglang",
                        code="3601",
                        province_id="36",
                        province_name="Banten"
                    )
                ]
            }
            
            regencies = mock_regencies.get(province_id, [])
            logger.info(f"Retrieved {len(regencies)} regencies for province {province_id}")
            return regencies
            
        except Exception as e:
            logger.error(f"Error retrieving regencies for province {province_id}: {str(e)}")
            raise
    
    async def get_subdistricts_by_regency(self, regency_id: str) -> List[SubDistrictSchema]:
        """
        Get all sub-districts within a specific regency.
        Currently returns mock data.
        """
        try:
            # Mock data - replace with actual database query
            mock_subdistricts = {
                "3201": [
                    SubDistrictSchema(
                        id="320101",
                        name="Kecamatan Cibinong",
                        code="320101",
                        regency_id="3201",
                        regency_name="Kabupaten Bogor"
                    ),
                    SubDistrictSchema(
                        id="320102",
                        name="Kecamatan Gunung Putri",
                        code="320102",
                        regency_id="3201",
                        regency_name="Kabupaten Bogor"
                    ),
                    SubDistrictSchema(
                        id="320103",
                        name="Kecamatan Citeureup",
                        code="320103",
                        regency_id="3201",
                        regency_name="Kabupaten Bogor"
                    )
                ],
                "3202": [
                    SubDistrictSchema(
                        id="320201",
                        name="Kecamatan Pelabuhan Ratu",
                        code="320201",
                        regency_id="3202",
                        regency_name="Kabupaten Sukabumi"
                    ),
                    SubDistrictSchema(
                        id="320202",
                        name="Kecamatan Simpenan",
                        code="320202",
                        regency_id="3202",
                        regency_name="Kabupaten Sukabumi"
                    )
                ]
            }
            
            subdistricts = mock_subdistricts.get(regency_id, [])
            logger.info(f"Retrieved {len(subdistricts)} sub-districts for regency {regency_id}")
            return subdistricts
            
        except Exception as e:
            logger.error(f"Error retrieving sub-districts for regency {regency_id}: {str(e)}")
            raise
    
    async def get_facilities_by_regency(self, regency_id: str) -> List[FacilitySchema]:
        """
        Get all health facilities within a specific regency.
        Currently returns mock data.
        """
        try:
            # Mock data - replace with actual database query
            mock_facilities = {
                "3201": [
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
                    ),
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
                "3202": [
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
            
            facilities = mock_facilities.get(regency_id, [])
            logger.info(f"Retrieved {len(facilities)} facilities for regency {regency_id}")
            return facilities
            
        except Exception as e:
            logger.error(f"Error retrieving facilities for regency {regency_id}: {str(e)}")
            raise 