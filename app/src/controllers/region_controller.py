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
    async def get_all_regencies(self) -> List[Dict[str, Any]]:
        """Get all regencies from database"""
        try:
            def execute_query(db):
                regencies = db.query(Regency).all()
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
            logger.error(f"Error fetching all regencies: {str(e)}")
            raise DatabaseException(f"Error fetching all regencies: {str(e)}")
    
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
    async def get_all_subdistricts(self) -> List[Dict[str, Any]]:
        """Get all subdistricts from database"""
        try:
            def execute_query(db):
                subdistricts = db.query(Subdistrict).all()
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
            logger.error(f"Error fetching all subdistricts: {str(e)}")
            raise DatabaseException(f"Error fetching all subdistricts: {str(e)}")
    
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
                        'subdistrict_id': facility.subdistrict_id,
                        'sub_district_name': facility.sub_district.name if hasattr(facility, 'sub_district') and facility.sub_district else None
                    })
                
                return result
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching facilities: {str(e)}")
            raise DatabaseException(f"Error fetching facilities: {str(e)}")

    # New method for bounding box spatial search
    async def get_regions_by_bounding_box(
        self, 
        north_east_lat: float, 
        north_east_lng: float, 
        south_west_lat: float, 
        south_west_lng: float,
        min_coverage_percentage: float = 10.0
    ) -> Dict[str, Any]:
        """
        Get administrative regions intersecting with bounding box.
        Returns primary region and all significant intersecting regions.
        """
        try:
            def execute_query(db):
                # Create bounding box geometry
                bbox_wkt = f"POLYGON(({south_west_lng} {south_west_lat}, {north_east_lng} {south_west_lat}, {north_east_lng} {north_east_lat}, {south_west_lng} {north_east_lat}, {south_west_lng} {south_west_lat}))"
                
                # Query for provinces with intersection data
                provinces_query = text("""
                    SELECT 
                        'province' as type,
                        p.id,
                        p.name,
                        p.pum_code,
                        p.area_km2 as total_area_km2,
                        ST_Area(ST_Intersection(p.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / 1000000 as intersection_area_km2,
                        (ST_Area(ST_Intersection(p.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / ST_Area(p.geom::geography)) * 100 as coverage_percentage
                    FROM provinces p
                    WHERE ST_Intersects(p.geom, ST_GeomFromText(:bbox_wkt, 4326))
                    AND (ST_Area(ST_Intersection(p.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / ST_Area(p.geom::geography)) * 100 >= :min_coverage
                    ORDER BY intersection_area_km2 DESC
                """)
                
                # Query for regencies with intersection data
                regencies_query = text("""
                    SELECT 
                        'regency' as type,
                        r.id,
                        r.name,
                        r.pum_code,
                        r.area_km2 as total_area_km2,
                        ST_Area(ST_Intersection(r.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / 1000000 as intersection_area_km2,
                        (ST_Area(ST_Intersection(r.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / ST_Area(r.geom::geography)) * 100 as coverage_percentage,
                        r.province_id,
                        p.name as province_name
                    FROM regencies r
                    JOIN provinces p ON r.province_id = p.id
                    WHERE ST_Intersects(r.geom, ST_GeomFromText(:bbox_wkt, 4326))
                    AND (ST_Area(ST_Intersection(r.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / ST_Area(r.geom::geography)) * 100 >= :min_coverage
                    ORDER BY intersection_area_km2 DESC
                """)
                
                # Query for subdistricts with intersection data
                subdistricts_query = text("""
                    SELECT 
                        'subdistrict' as type,
                        sd.id,
                        sd.name,
                        sd.pum_code,
                        sd.area_km2 as total_area_km2,
                        ST_Area(ST_Intersection(sd.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / 1000000 as intersection_area_km2,
                        (ST_Area(ST_Intersection(sd.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / ST_Area(sd.geom::geography)) * 100 as coverage_percentage,
                        sd.regency_id,
                        r.name as regency_name
                    FROM subdistricts sd
                    JOIN regencies r ON sd.regency_id = r.id
                    WHERE ST_Intersects(sd.geom, ST_GeomFromText(:bbox_wkt, 4326))
                    AND (ST_Area(ST_Intersection(sd.geom, ST_GeomFromText(:bbox_wkt, 4326))::geography) / ST_Area(sd.geom::geography)) * 100 >= :min_coverage
                    ORDER BY intersection_area_km2 DESC
                """)
                
                # Execute all queries
                provinces_result = db.execute(provinces_query, {
                    "bbox_wkt": bbox_wkt,
                    "min_coverage": min_coverage_percentage
                })
                
                regencies_result = db.execute(regencies_query, {
                    "bbox_wkt": bbox_wkt,
                    "min_coverage": min_coverage_percentage
                })
                
                subdistricts_result = db.execute(subdistricts_query, {
                    "bbox_wkt": bbox_wkt,
                    "min_coverage": min_coverage_percentage
                })
                
                # Combine all results
                all_regions = []
                
                # Process provinces
                for row in provinces_result:
                    all_regions.append({
                        'type': row.type,
                        'id': row.id,
                        'name': row.name,
                        'pum_code': row.pum_code,
                        'coverage_percentage': float(row.coverage_percentage),
                        'intersection_area_km2': float(row.intersection_area_km2),
                        'total_area_km2': float(row.total_area_km2) if row.total_area_km2 else None,
                        'parent_region_id': None,
                        'parent_region_name': None
                    })
                
                # Process regencies
                for row in regencies_result:
                    all_regions.append({
                        'type': row.type,
                        'id': row.id,
                        'name': row.name,
                        'pum_code': row.pum_code,
                        'coverage_percentage': float(row.coverage_percentage),
                        'intersection_area_km2': float(row.intersection_area_km2),
                        'total_area_km2': float(row.total_area_km2) if row.total_area_km2 else None,
                        'parent_region_id': row.province_id,
                        'parent_region_name': row.province_name
                    })
                
                # Process subdistricts
                for row in subdistricts_result:
                    all_regions.append({
                        'type': row.type,
                        'id': row.id,
                        'name': row.name,
                        'pum_code': row.pum_code,
                        'coverage_percentage': float(row.coverage_percentage),
                        'intersection_area_km2': float(row.intersection_area_km2),
                        'total_area_km2': float(row.total_area_km2) if row.total_area_km2 else None,
                        'parent_region_id': row.regency_id,
                        'parent_region_name': row.regency_name
                    })
                
                # Sort by intersection area to find primary region
                all_regions.sort(key=lambda x: x['intersection_area_km2'], reverse=True)
                
                # Find primary region (highest intersection area)
                primary_region = all_regions[0] if all_regions else None
                
                return {
                    'primary_region': primary_region,
                    'intersecting_regions': all_regions,
                    'total_regions_found': len(all_regions)
                }
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error fetching regions by bounding box: {str(e)}")
            raise DatabaseException(f"Error fetching regions by bounding box: {str(e)}")

# Create controller instance
region_controller = RegionController() 