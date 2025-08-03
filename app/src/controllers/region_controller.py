from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from app.src.config.database import SessionLocal
from app.src.models.province import Province
from app.src.models.regency import Regency
from app.src.models.subdistrict import Subdistrict
from app.src.models.health_facility import HealthFacility
from app.src.utils.exceptions import DatabaseException
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class RegionController:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def _get_db_session(self) -> Session:
        """Get a fresh database session."""
        return self.db
    
    # Database operations for provinces
    async def get_all_provinces(self) -> List[Dict[str, Any]]:
        """Get all provinces from database"""
        try:
            def execute_query(db):
                provinces = db.query(Province).all()
                return [
                    {
                        'id': province.id,
                        'name': province.name,
                        'pum_code': province.pum_code,
                        'area_km2': province.area_km2
                    }
                    for province in provinces
                ]
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching provinces: {str(e)}")
            raise DatabaseException(f"Error fetching provinces: {str(e)}")
    
    async def get_province_by_id(self, province_id: UUID) -> Optional[Dict[str, Any]]:
        """Get province by ID from database"""
        try:
            def execute_query(db):
                province = db.query(Province).filter(Province.id == province_id).first()
                if province:
                    return {
                        'id': province.id,
                        'name': province.name,
                        'pum_code': province.pum_code,
                        'area_km2': province.area_km2
                    }
                return None
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching province: {str(e)}")
            raise DatabaseException(f"Error fetching province: {str(e)}")
    
    # Database operations for regencies
    async def get_regencies_by_province(self, province_id: UUID) -> List[Dict[str, Any]]:
        """Get all regencies in a province"""
        try:
            def execute_query(db):
                regencies = db.query(Regency).filter(Regency.province_id == province_id).all()
                return [
                    {
                        'id': regency.id,
                        'name': regency.name,
                        'pum_code': regency.pum_code,
                        'province_id': regency.province_id,
                        'province_name': regency.province.name if hasattr(regency, 'province') and regency.province else None,
                        'area_km2': regency.area_km2
                    }
                    for regency in regencies
                ]
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching regencies: {str(e)}")
            raise DatabaseException(f"Error fetching regencies: {str(e)}")
    
    # Database operations for subdistricts
    async def get_subdistricts_by_regency(self, regency_id: UUID) -> List[Dict[str, Any]]:
        """Get all subdistricts in a regency"""
        try:
            def execute_query(db):
                subdistricts = db.query(Subdistrict).filter(Subdistrict.regency_id == regency_id).all()
                return [
                    {
                        'id': subdistrict.id,
                        'name': subdistrict.name,
                        'pum_code': subdistrict.pum_code,
                        'regency_id': subdistrict.regency_id,
                        'regency_name': subdistrict.regency.name if hasattr(subdistrict, 'regency') and subdistrict.regency else None,
                        'population_count': subdistrict.population_count,
                        'poverty_level': subdistrict.poverty_level,
                        'area_km2': subdistrict.area_km2
                    }
                    for subdistrict in subdistricts
                ]
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching subdistricts: {str(e)}")
            raise DatabaseException(f"Error fetching subdistricts: {str(e)}")
    
    # Database operations for health facilities
    async def get_facilities_by_regency(self, regency_id: UUID) -> List[Dict[str, Any]]:
        """Get all health facilities in a regency"""
        try:
            def execute_query(db):
                facilities = db.query(HealthFacility).join(Subdistrict).filter(Subdistrict.regency_id == regency_id).all()
                result = []
                
                for facility in facilities:
                    # Extract coordinates from geometry
                    coords_query = text("""
                        SELECT 
                            ST_X(geom) as longitude,
                            ST_Y(geom) as latitude
                        FROM health_facilities 
                        WHERE id = :facility_id
                    """)
                    coords_result = db.execute(coords_query, {"facility_id": facility.id}).first()
                    
                    result.append({
                        'id': facility.id,
                        'name': facility.name,
                        'type': facility.type,
                        'latitude': coords_result.latitude if coords_result else 0.0,
                        'longitude': coords_result.longitude if coords_result else 0.0,
                        'regency_id': facility.sub_district.regency_id if hasattr(facility, 'sub_district') and facility.sub_district else None,
                        'regency_name': facility.sub_district.regency.name if hasattr(facility, 'sub_district') and facility.sub_district and hasattr(facility.sub_district, 'regency') and facility.sub_district.regency else None,
                        'sub_district_id': facility.sub_district_id,
                        'sub_district_name': facility.sub_district.name if hasattr(facility, 'sub_district') and facility.sub_district else None
                    })
                
                return result
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching facilities: {str(e)}")
            raise DatabaseException(f"Error fetching facilities: {str(e)}")

# Create controller instance
region_controller = RegionController() 