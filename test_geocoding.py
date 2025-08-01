#!/usr/bin/env python3
"""
Simple test script for the geocoding service
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.src.services.geocoding_service import GeocodingService

async def test_geocoding():
    """Test the geocoding service with Indonesian addresses"""
    
    geocoding_service = GeocodingService()
    
    # Test addresses in Indonesia
    test_addresses = [
        "Jl. Sudirman No. 123, Jakarta Pusat",
        "Jl. Thamrin, Jakarta",
        "Bundaran HI, Jakarta",
        "Monas, Jakarta Pusat",
        "Invalid Address That Should Not Work"
    ]
    
    print("Testing Geocoding Service")
    print("=" * 50)
    
    for address in test_addresses:
        print(f"\nTesting address: {address}")
        try:
            result = await geocoding_service.geocode_address(address)
            
            if result:
                print(f"✅ SUCCESS")
                print(f"   Coordinates: {result['lat']}, {result['lon']}")
                print(f"   WKT Point: {result['wkt_point']}")
                print(f"   Display Name: {result['display_name']}")
            else:
                print(f"❌ NO RESULTS FOUND")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_geocoding()) 