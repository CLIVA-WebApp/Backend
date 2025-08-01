import requests
import logging
from typing import Optional, Tuple, Dict, Any
from app.src.utils.exceptions import GeocodingException

class GeocodingService:
    def __init__(self):
        # Using Nominatim (OpenStreetMap) as a free geocoding service
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            "User-Agent": "PuskesmasApp/1.0"  # Required by Nominatim
        }
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to coordinates using Nominatim geocoding service
        
        Returns:
            Dict with 'lat', 'lon', 'wkt_point', 'display_name' or None if not found
        """
        try:
            # Clean and encode the address
            clean_address = address.strip()
            if not clean_address:
                return None
            
            # Make geocoding request
            params = {
                "q": clean_address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
                "countrycodes": "id"  # Limit to Indonesia
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logging.warning(f"Geocoding request failed: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data:
                logging.info(f"No geocoding results found for address: {address}")
                return None
            
            # Get the first (best) result
            result = data[0]
            
            lat = float(result.get("lat", 0))
            lon = float(result.get("lon", 0))
            
            if lat == 0 and lon == 0:
                return None
            
            # Create WKT POINT format
            wkt_point = f"POINT({lon} {lat})"
            
            return {
                "lat": lat,
                "lon": lon,
                "wkt_point": wkt_point,
                "display_name": result.get("display_name", address),
                "address_details": result.get("address", {})
            }
            
        except requests.RequestException as e:
            logging.error(f"Geocoding request error: {str(e)}")
            raise GeocodingException(f"Failed to geocode address: {str(e)}")
        except Exception as e:
            logging.error(f"Geocoding error: {str(e)}")
            raise GeocodingException(f"Geocoding failed: {str(e)}")
    
    async def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates back to address (reverse geocoding)
        
        Returns:
            Human-readable address or None if not found
        """
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1
            }
            
            response = requests.get(
                f"{self.base_url}/reverse",
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            return data.get("display_name")
            
        except Exception as e:
            logging.error(f"Reverse geocoding error: {str(e)}")
            return None
    
    def create_bounding_box(self, lat: float, lon: float, radius_km: float = 1.0) -> str:
        """
        Create a simple bounding box around a point for spatial queries
        
        Returns:
            WKT POLYGON string
        """
        # Convert km to degrees (approximate)
        radius_degrees = radius_km / 111.0
        
        # Create a simple square around the point
        min_lat = lat - radius_degrees
        max_lat = lat + radius_degrees
        min_lon = lon - radius_degrees
        max_lon = lon + radius_degrees
        
        # WKT POLYGON format
        wkt_polygon = f"POLYGON(({min_lon} {min_lat}, {max_lon} {min_lat}, {max_lon} {max_lat}, {min_lon} {max_lat}, {min_lon} {min_lat}))"
        
        return wkt_polygon 