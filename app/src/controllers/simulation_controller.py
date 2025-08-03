from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.src.config.database import SessionLocal
from app.src.models.regency import Regency
from app.src.models.subdistrict import Subdistrict
from app.src.models.province import Province
from app.src.models.population_point import PopulationPoint
from app.src.models.health_facility import HealthFacility
from app.src.schemas.simulation_schema import GeographicLevel
from app.src.utils.exceptions import DatabaseException
import logging
import traceback
from uuid import UUID

logger = logging.getLogger(__name__)

class SimulationController:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def _get_db_session(self) -> Session:
        """Get a fresh database session."""
        return self.db
    
    async def get_subdistrict_by_id(self, subdistrict_id: UUID) -> Optional[Dict[str, Any]]:
        """Get subdistrict by ID from database"""
        try:
            def execute_query(db):
                subdistrict = db.query(Subdistrict).filter(Subdistrict.id == subdistrict_id).first()
                if subdistrict:
                    return {
                        'id': subdistrict.id,
                        'name': subdistrict.name,
                        'regency_id': subdistrict.regency_id,
                        'population_count': subdistrict.population_count,
                        'area_km2': subdistrict.area_km2,
                        'poverty_level': subdistrict.poverty_level
                    }
                return None
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching subdistrict: {str(e)}")
            raise DatabaseException(f"Error fetching subdistrict: {str(e)}")
    
    async def get_subdistrict_ids_by_level(self, geographic_level: GeographicLevel, area_ids: List[UUID]) -> List[UUID]:
        """Get subdistrict IDs based on the geographic level"""
        try:
            def execute_query(db):
                if geographic_level == GeographicLevel.SUBDISTRICT:
                    return area_ids
                elif geographic_level == GeographicLevel.REGENCY:
                    # Get all subdistricts in the specified regencies
                    query = text("""
                        SELECT id FROM subdistricts 
                        WHERE regency_id = ANY(CAST(:regency_ids AS uuid[]))
                    """)
                    result = db.execute(query, {"regency_ids": [str(id) for id in area_ids]}).fetchall()
                    return [row.id for row in result]
                elif geographic_level == GeographicLevel.PROVINCE:
                    # Get all subdistricts in the specified provinces
                    query = text("""
                        SELECT s.id FROM subdistricts s
                        JOIN regencies r ON s.regency_id = r.id
                        WHERE r.province_id = ANY(CAST(:province_ids AS uuid[]))
                    """)
                    result = db.execute(query, {"province_ids": [str(id) for id in area_ids]}).fetchall()
                    return [row.id for row in result]
                else:
                    raise ValueError(f"Unsupported geographic level: {geographic_level}")
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error in get_subdistrict_ids_by_level: {e}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise DatabaseException(f"Error getting subdistrict IDs: {str(e)}")
    
    async def get_population_data(self, subdistrict_ids: List[UUID]) -> List[Dict[str, Any]]:
        """Get population data for specified subdistricts"""
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
                    WHERE pp.subdistrict_id = ANY(CAST(:subdistrict_ids AS uuid[]))
                """)
                
                result = db.execute(query, {"subdistrict_ids": [str(id) for id in subdistrict_ids]})
                population_data = []
                
                for row in result:
                    population_data.append({
                        'id': row.id,
                        'population_count': row.population_count,
                        'longitude': row.longitude,
                        'latitude': row.latitude,
                        'subdistrict_id': row.subdistrict_id
                    })
                
                return population_data
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error getting population data: {str(e)}")
            raise DatabaseException(f"Error getting population data: {str(e)}")
    
    async def get_existing_facilities(self, subdistrict_ids: List[UUID]) -> List[Dict[str, Any]]:
        """Get existing health facilities for specified subdistricts"""
        try:
            def execute_query(db):
                query = text("""
                    SELECT 
                        hf.id,
                        hf.name,
                        hf.type,
                        ST_X(hf.geom) as longitude,
                        ST_Y(hf.geom) as latitude,
                        hf.subdistrict_id
                    FROM health_facilities hf
                    WHERE hf.subdistrict_id = ANY(CAST(:subdistrict_ids AS uuid[]))
                """)
                
                result = db.execute(query, {"subdistrict_ids": [str(id) for id in subdistrict_ids]})
                facilities = []
                
                for row in result:
                    facilities.append({
                        'id': row.id,
                        'name': row.name,
                        'type': row.type,
                        'longitude': row.longitude,
                        'latitude': row.latitude,
                        'subdistrict_id': row.subdistrict_id
                    })
                
                return facilities
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error getting existing facilities: {str(e)}")
            raise DatabaseException(f"Error getting existing facilities: {str(e)}")
    
    async def get_regency_by_id(self, regency_id: UUID) -> Optional[Dict[str, Any]]:
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
                        'area_km2': regency.area_km2
                    }
                return None
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching regency: {str(e)}")
            raise DatabaseException(f"Error fetching regency: {str(e)}")

# Create controller instance
simulation_controller = SimulationController() 