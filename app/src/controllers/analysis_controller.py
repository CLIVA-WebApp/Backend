from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from sqlalchemy.exc import OperationalError, DisconnectionError
from app.src.config.database import SessionLocal
from app.src.models.regency import Regency
from app.src.models.subdistrict import Subdistrict
from app.src.models.health_facility import HealthFacility
from app.src.models.population_point import PopulationPoint
from app.src.schemas.region_schema import RegencySchema, SubDistrictSchema, FacilitySchema
from app.src.utils.exceptions import DatabaseException
import logging
import time
from uuid import UUID

logger = logging.getLogger(__name__)

class AnalysisController:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def _get_db_session(self) -> Session:
        """Get a fresh database session with retry logic."""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Test the connection
                self.db.execute(text("SELECT 1"))
                return self.db
            except (OperationalError, DisconnectionError) as e:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    # Create a new session
                    self.db.close()
                    self.db = SessionLocal()
                else:
                    logger.error("All database connection attempts failed")
                    raise
            except Exception as e:
                logger.error(f"Unexpected database error: {e}")
                raise
    
    def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute a database operation with retry logic."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Check if operation expects a database session as first argument
                import inspect
                sig = inspect.signature(operation)
                if len(sig.parameters) > 0 and list(sig.parameters.keys())[0] == 'db':
                    # Operation expects db session as first argument
                    db = self._get_db_session()
                    return operation(db, *args, **kwargs)
                else:
                    # Operation doesn't expect db session, just call it directly
                    return operation(*args, **kwargs)
            except (OperationalError, DisconnectionError) as e:
                logger.warning(f"Database operation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("All database operation attempts failed")
                    raise
            except Exception as e:
                logger.error(f"Unexpected database error: {e}")
                raise
    
    # Database operations for regencies
    async def get_regency_by_id(self, regency_id: Union[UUID, str]) -> Optional[Dict[str, Any]]:
        """Get regency by ID from database"""
        try:
            def execute_query(db):
                regency = db.query(Regency).filter(Regency.id == regency_id).first()
                if regency:
                    return {
                        'id': regency.id,
                        'name': regency.name,
                        'pum_code': regency.pum_code,
                        'province_id': regency.province_id,
                        'province_name': regency.province.name if hasattr(regency, 'province') and regency.province else None,
                        'area_km2': regency.area_km2
                    }
                return None
            
            return self._execute_with_retry(execute_query)
        except Exception as e:
            raise DatabaseException(f"Error fetching regency: {str(e)}")
    
    # Database operations for subdistricts
    async def get_subdistrict_by_id(self, subdistrict_id: Union[UUID, str]) -> Optional[Dict[str, Any]]:
        """Get subdistrict by ID from database"""
        try:
            def execute_query(db):
                subdistrict = db.query(Subdistrict).filter(Subdistrict.id == subdistrict_id).first()
                if subdistrict:
                    return {
                        'id': subdistrict.id,
                        'name': subdistrict.name,
                        'pum_code': subdistrict.pum_code,
                        'regency_id': subdistrict.regency_id,
                        'regency_name': subdistrict.regency.name if hasattr(subdistrict, 'regency') and subdistrict.regency else None,
                        'population_count': subdistrict.population_count,
                        'poverty_level': subdistrict.poverty_level,
                        'area_km2': subdistrict.area_km2
                    }
                return None
            
            return self._execute_with_retry(execute_query)
        except Exception as e:
            raise DatabaseException(f"Error fetching subdistrict: {str(e)}")
    
    async def get_subdistricts_by_regency(self, regency_id: Union[UUID, str]) -> List[Dict[str, Any]]:
        """Get all subdistricts in a regency"""
        try:
            def execute_query(db):
                subdistricts = db.query(Subdistrict).filter(Subdistrict.regency_id == regency_id).all()
                result = []
                for subdistrict in subdistricts:
                    result.append({
                        'id': subdistrict.id,
                        'name': subdistrict.name,
                        'poverty_level': subdistrict.poverty_level or 0,
                        'area_km2': subdistrict.area_km2 or 0,
                        'population_count': subdistrict.population_count
                    })
                return result
            
            return self._execute_with_retry(execute_query)
        except Exception as e:
            raise DatabaseException(f"Error fetching subdistricts: {str(e)}")
    
    # Database operations for health facilities
    async def get_facilities_by_subdistrict(self, subdistrict_id: Union[UUID, str]) -> List[Dict[str, Any]]:
        """Get all health facilities in a subdistrict"""
        try:
            def execute_query(db):
                facilities = db.query(HealthFacility).filter(HealthFacility.subdistrict_id == subdistrict_id).all()
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
                        'subdistrict_id': facility.subdistrict_id,
                        'sub_district_name': facility.sub_district.name if hasattr(facility, 'sub_district') and facility.sub_district else None
                    })
                return result
            
            return self._execute_with_retry(execute_query)
        except Exception as e:
            raise DatabaseException(f"Error fetching facilities: {str(e)}")
    
    async def get_health_facilities_by_regency(self, regency_id: Union[UUID, str]) -> List[Dict[str, Any]]:
        """Get all health facilities in a regency"""
        try:
            def execute_query(db):
                query = text("""
                    SELECT 
                        hf.id,
                        hf.name,
                        hf.type,
                        ST_X(hf.geom) as longitude,
                        ST_Y(hf.geom) as latitude
                    FROM health_facilities hf
                    JOIN subdistricts sd ON hf.subdistrict_id = sd.id
                    WHERE sd.regency_id = :regency_id
                """)
                
                result = db.execute(query, {"regency_id": regency_id})
                facilities = []
                for row in result:
                    facilities.append({
                        'id': row.id,
                        'name': row.name,
                        'type': row.type,
                        'longitude': row.longitude,
                        'latitude': row.latitude
                    })
                return facilities
            
            return self._execute_with_retry(execute_query)
        except Exception as e:
            raise DatabaseException(f"Error fetching health facilities: {str(e)}")
    
    # Database operations for population data
    async def get_population_statistics(self, regency_id: Union[UUID, str], service_radius_km: float) -> Dict[str, int]:
        """Get population statistics for a regency"""
        try:
            def execute_query(db):
                query = text("""
                    SELECT 
                        COALESCE(SUM(pp.population_count), 0) as total_population,
                        COALESCE(SUM(
                            CASE 
                                WHEN NOT EXISTS (
                                    SELECT 1 FROM health_facilities hf
                                    JOIN subdistricts sd ON hf.subdistrict_id = sd.id
                                    WHERE sd.regency_id = :regency_id
                                    AND ST_DWithin(
                                        pp.geom::geography,
                                        hf.geom::geography,
                                        :service_radius_meters
                                    )
                                ) THEN pp.population_count
                                ELSE 0
                            END
                        ), 0) as population_outside_radius
                    FROM population_points pp
                    JOIN subdistricts sd ON pp.subdistrict_id = sd.id
                    WHERE sd.regency_id = :regency_id
                """)
                
                result = db.execute(query, {
                    "regency_id": regency_id,
                    "service_radius_meters": service_radius_km * 1000
                })
                row = result.fetchone()
                
                total_population = int(row.total_population) if row else 0
                population_outside_radius = int(row.population_outside_radius) if row else 0
                
                return {
                    'total_population': total_population,
                    'population_outside_radius': population_outside_radius
                }
            
            return self._execute_with_retry(execute_query)
        except Exception as e:
            raise DatabaseException(f"Error fetching population statistics: {str(e)}")
    
    async def get_population_points(self, regency_id: Union[UUID, str]) -> List[Dict[str, Any]]:
        """Get all population points in a regency"""
        try:
            def execute_query(db):
                query = text("""
                    SELECT 
                        pp.id,
                        pp.population_count,
                        ST_X(pp.geom) as longitude,
                        ST_Y(pp.geom) as latitude,
                        pp.subdistrict_id
                    FROM population_points pp
                    JOIN subdistricts sd ON pp.subdistrict_id = sd.id
                    WHERE sd.regency_id = :regency_id
                """)
                
                result = db.execute(query, {"regency_id": regency_id})
                points = []
                for row in result:
                    points.append({
                        'id': row.id,
                        'population_count': row.population_count,
                        'longitude': row.longitude,
                        'latitude': row.latitude,
                        'subdistrict_id': row.subdistrict_id
                    })
                return points
            
            return self._execute_with_retry(execute_query)
        except Exception as e:
            raise DatabaseException(f"Error fetching population points: {str(e)}")
    
    # Database operations for gap factor calculations
    async def calculate_gap_factor(self, subdistrict_id: UUID, total_population: int, service_radius_km: float) -> float:
        """Calculate gap factor for a subdistrict"""
        try:
            def execute_query(db):
                query = text("""
                    SELECT COALESCE(SUM(pp.population_count), 0) as population_outside
                    FROM population_points pp
                    WHERE pp.subdistrict_id = :subdistrict_id
                    AND NOT EXISTS (
                        SELECT 1 FROM health_facilities hf
                        WHERE ST_DWithin(
                            pp.geom::geography, 
                            hf.geom::geography, 
                            :service_radius_meters
                        )
                    )
                """)
                
                result = db.execute(query, {
                    "subdistrict_id": subdistrict_id,
                    "service_radius_meters": service_radius_km * 1000
                })
                
                row = result.fetchone()
                population_outside = row.population_outside if row else 0
                
                return population_outside / total_population if total_population > 0 else 0.0
            
            return self._execute_with_retry(execute_query)
        except Exception as e:
            raise DatabaseException(f"Error calculating gap factor: {str(e)}")

# Create controller instance
analysis_controller = AnalysisController() 