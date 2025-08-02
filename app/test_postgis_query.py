#!/usr/bin/env python3
"""
Test script to verify PostGIS priority score calculation.
Run this script to test the calculate_priority_scores function.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.src.services.analysis_service import AnalysisService
from app.src.config.database import SessionLocal
from app.src.models.regency import Regency
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgis_query():
    """Test the PostGIS priority score calculation."""
    try:
        # Initialize service
        service = AnalysisService()
        
        # Get a sample regency from the database
        db = SessionLocal()
        sample_regency = db.query(Regency).first()
        
        if not sample_regency:
            logger.warning("No regencies found in database. Using mock data.")
            # Test with mock data
            scores = service.calculate_priority_scores("mock")
            logger.info(f"Mock test successful. Found {len(scores)} sub-districts.")
            for score in scores:
                logger.info(f"  {score.sub_district_name}: {score.composite_score:.3f}")
            return
        
        logger.info(f"Testing with regency: {sample_regency.name} (ID: {sample_regency.id})")
        
        # Test the calculation
        scores = service.calculate_priority_scores(
            regency_id=sample_regency.id,
            service_radius_km=5.0,
            gap_weight=0.4,
            efficiency_weight=0.3,
            vulnerability_weight=0.3
        )
        
        logger.info(f"Calculation successful. Found {len(scores)} sub-districts.")
        
        # Display results
        for i, score in enumerate(scores[:5]):  # Show top 5
            logger.info(f"  {i+1}. {score.sub_district_name}")
            logger.info(f"      Gap: {score.gap_factor:.3f}, Efficiency: {score.efficiency_factor:.3f}, Vulnerability: {score.vulnerability_factor:.3f}")
            logger.info(f"      Composite Score: {score.composite_score:.3f}")
        
        if len(scores) > 5:
            logger.info(f"  ... and {len(scores) - 5} more sub-districts")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_postgis_query() 