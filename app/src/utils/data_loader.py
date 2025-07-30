"""
Data loader for importing GDB (Geodatabase) files into PostGIS database.
Handles the administrative hierarchy: Province -> Regency -> Subdistrict
"""

import geopandas as gpd
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, List, Optional
import logging
from pathlib import Path
from shapely.geometry import MultiPolygon
from shapely import force_2d

from app.src.config.database import SessionLocal
from app.src.models.province import Province
from app.src.models.regency import Regency
from app.src.models.subdistrict import Subdistrict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GDBDataLoader:
    """Handles loading of GDB data into PostGIS database"""
    
    def __init__(self, gdb_path: str):
        self.gdb_path = Path(gdb_path)
        self.db = SessionLocal()
        
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'db'):
            self.db.close()
    
    def strip_z_dimension(self, geometry):
        """Strip Z dimension from geometry if present"""
        try:
            return force_2d(geometry)
        except Exception as e:
            logger.warning(f"Could not strip Z dimension from geometry: {e}")
            return geometry
    
    def load_gdb_layer(self, layer_name: str = 'ADMINISTRASI_AR_DESAKEL') -> gpd.GeoDataFrame:
        """Load a specific layer from the GDB file"""
        try:
            logger.info(f"Loading layer: {layer_name}")
            gdf = gpd.read_file(self.gdb_path, layer=layer_name)
            
            # Convert to WGS84 (EPSG:4326) if needed
            if gdf.crs != 'EPSG:4326':
                logger.info(f"Converting CRS from {gdf.crs} to EPSG:4326")
                gdf = gdf.to_crs('EPSG:4326')
            
            # Strip Z dimension from geometries
            logger.info("Processing geometries...")
            gdf['geometry'] = gdf['geometry'].apply(self.strip_z_dimension)
            
            logger.info(f"Loaded {len(gdf)} features")
            return gdf
            
        except Exception as e:
            logger.error(f"Error loading GDB layer: {e}")
            raise
    
    def extract_administrative_hierarchy(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Extract unique administrative units from the GDB data"""
        
        # Group by administrative codes to get unique units
        provinces = gdf.groupby(['KDPPUM', 'WADMPR']).agg({
            'geometry': 'first'  # Take the first geometry (they should be the same for same province)
        }).reset_index()
        
        regencies = gdf.groupby(['KDPKAB', 'WADMKK', 'KDPPUM']).agg({
            'geometry': 'first'
        }).reset_index()
        
        subdistricts = gdf.groupby(['KDCPUM', 'WADMKC', 'KDPKAB']).agg({
            'geometry': 'first',
            'LUASWH': 'sum',  # Sum area for subdistrict
            'TIPADM': 'first'  # Take first admin type
        }).reset_index()
        
        return {
            'provinces': provinces,
            'regencies': regencies,
            'subdistricts': subdistricts
        }
    
    def load_provinces(self, provinces_df: pd.DataFrame) -> Dict[str, int]:
        """Load provinces into database and return mapping of codes to IDs"""
        province_mapping = {}
        
        for _, row in provinces_df.iterrows():
            # Check if province already exists
            existing = self.db.query(Province).filter(
                Province.name == row['WADMPR']
            ).first()
            
            if existing:
                province_mapping[row['KDPPUM']] = existing.id
                continue
            
            # Calculate area in square kilometers
            area_km2 = row['geometry'].area * 111.32 * 111.32  # Approximate conversion to km²
            
            # Create new province
            province = Province(
                name=row['WADMPR'],
                area_km2=area_km2,
                geom=f"SRID=4326;{row['geometry'].wkt}"
            )
            
            self.db.add(province)
            self.db.flush()  # Get the ID
            province_mapping[row['KDPPUM']] = province.id
            
            logger.info(f"Added province: {row['WADMPR']}")
        
        self.db.commit()
        logger.info(f"Loaded {len(province_mapping)} provinces")
        return province_mapping
    
    def load_regencies(self, regencies_df: pd.DataFrame, province_mapping: Dict[str, int]) -> Dict[str, int]:
        """Load regencies into database and return mapping of codes to IDs"""
        regency_mapping = {}
        
        for _, row in regencies_df.iterrows():
            province_id = province_mapping.get(row['KDPPUM'])
            if not province_id:
                logger.warning(f"Skipping regency {row['WADMKK']} - province not found")
                continue
            
            # Check if regency already exists
            existing = self.db.query(Regency).filter(
                Regency.name == row['WADMKK'],
                Regency.province_id == province_id
            ).first()
            
            if existing:
                regency_mapping[row['KDPKAB']] = existing.id
                continue
            
            # Calculate area in square kilometers
            area_km2 = row['geometry'].area * 111.32 * 111.32  # Approximate conversion to km²
            
            # Create new regency
            regency = Regency(
                name=row['WADMKK'],
                province_id=province_id,
                area_km2=area_km2,
                geom=f"SRID=4326;{row['geometry'].wkt}"
            )
            
            self.db.add(regency)
            self.db.flush()
            regency_mapping[row['KDPKAB']] = regency.id
            
            logger.info(f"Added regency: {row['WADMKK']}")
        
        self.db.commit()
        logger.info(f"Loaded {len(regency_mapping)} regencies")
        return regency_mapping
    
    def load_subdistricts(self, subdistricts_df: pd.DataFrame, regency_mapping: Dict[str, int]):
        """Load subdistricts into database"""
        count = 0
        
        for _, row in subdistricts_df.iterrows():
            regency_id = regency_mapping.get(row['KDPKAB'])
            if not regency_id:
                logger.warning(f"Skipping subdistrict {row['WADMKC']} - regency not found")
                continue
            
            # Check if subdistrict already exists
            existing = self.db.query(Subdistrict).filter(
                Subdistrict.name == row['WADMKC'],
                Subdistrict.regency_id == regency_id
            ).first()
            
            if existing:
                continue
            
            # Calculate area in square kilometers
            area_km2 = row['geometry'].area * 111.32 * 111.32  # Approximate conversion to km²
            
            # Create new subdistrict
            subdistrict = Subdistrict(
                name=row['WADMKC'],
                regency_id=regency_id,
                area_km2=area_km2,
                geom=f"SRID=4326;{row['geometry'].wkt}"
            )
            
            self.db.add(subdistrict)
            count += 1
            
            # Commit every 100 subdistricts to show progress
            if count % 100 == 0:
                self.db.commit()
                logger.info(f"Processed {count} subdistricts...")
        
        # Final commit for remaining subdistricts
        self.db.commit()
        logger.info(f"Loaded {count} subdistricts")
    
    def load_all_data(self):
        """Main method to load all administrative data"""
        try:
            # Load GDB data
            gdf = self.load_gdb_layer()
            
            # Extract hierarchy
            hierarchy = self.extract_administrative_hierarchy(gdf)
            
            # Load provinces first
            province_mapping = self.load_provinces(hierarchy['provinces'])
            
            # Load regencies
            regency_mapping = self.load_regencies(hierarchy['regencies'], province_mapping)
            
            # Load subdistricts
            self.load_subdistricts(hierarchy['subdistricts'], regency_mapping)
            
            logger.info("✅ Data loading completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error during data loading: {e}")
            self.db.rollback()
            raise

def main():
    """Main function to run the data loader"""
    # Update this path to your GDB file location
    gdb_path = "../raw_data/RBI10K_ADMINISTRASI_DESA_20230928.gdb"
    
    loader = GDBDataLoader(gdb_path)
    loader.load_all_data()

if __name__ == "__main__":
    main() 