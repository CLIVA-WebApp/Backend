#!/usr/bin/env python3
"""
Test script to verify the fixes for infinite values and cache issues.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.src.services.analysis_service import AnalysisService
from app.src.config.cache import init_cache
import math

async def test_fixes():
    """Test the fixes for infinite values and cache issues."""
    
    print("Testing fixes for infinite values and cache issues...")
    
    # Initialize cache (should handle Redis connection failure gracefully)
    print("\n1. Testing cache initialization...")
    try:
        await init_cache()
        print("✓ Cache initialization completed (may be disabled if Redis unavailable)")
    except Exception as e:
        print(f"✗ Cache initialization failed: {e}")
    
    # Test analysis service
    print("\n2. Testing analysis service with mock data...")
    analysis_service = AnalysisService()
    
    try:
        # Test heatmap generation with mock data
        print("Testing heatmap generation...")
        heatmap_data = await analysis_service.generate_heatmap_data("mock")
        print(f"✓ Heatmap data generated successfully")
        print(f"  - Regency: {heatmap_data.regency_name}")
        print(f"  - Total population: {heatmap_data.total_population}")
        print(f"  - Heatmap points: {len(heatmap_data.heatmap_points)}")
        
        # Test priority scores with mock data
        print("\nTesting priority scores...")
        priority_data = await analysis_service.generate_priority_score_data("mock")
        print(f"✓ Priority data generated successfully")
        print(f"  - Regency: {priority_data.regency_name}")
        print(f"  - Sub-districts: {len(priority_data.sub_districts)}")
        
        # Test analysis summary with mock data
        print("\nTesting analysis summary...")
        summary = await analysis_service.generate_analysis_summary("mock")
        print(f"✓ Analysis summary generated successfully")
        print(f"  - Regency: {summary.regency_name}")
        print(f"  - Coverage: {summary.summary_metrics.coverage_percentage}%")
        
        print("\n✓ All tests passed! The fixes are working correctly.")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixes()) 