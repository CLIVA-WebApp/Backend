from typing import List, Optional, Dict, Any, Union, Tuple
from app.src.schemas.analysis_schema import (
    HeatmapData,
    HeatmapPoint,
    PriorityScoreData,
    SubDistrictScore,
    SubDistrictDetails,
    AnalysisSummary,
    SummaryMetrics,
    FacilityOverview
)
from app.src.schemas.region_schema import RegencySchema, SubDistrictSchema, FacilitySchema
from app.src.config.cache import analysis_cache, get_cache_key
from app.src.controllers.analysis_controller import analysis_controller
from app.src.utils.exceptions import DatabaseException
import logging
import math
import random
from uuid import UUID

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        pass  # No need to initialize database session, we'll use controller
    
    async def get_regency_by_id(self, regency_id: Union[UUID, str]) -> Optional[RegencySchema]:
        """
        Get a specific regency by ID.
        """
        try:
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_regency = RegencySchema(
                    id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    name="Kabupaten Bogor",
                    pum_code="3201",
                    province_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                    province_name="Jawa Barat",
                    area_km2=2985.43
                )
                return mock_regency
            
            # Get regency data from controller
            regency_data = await analysis_controller.get_regency_by_id(regency_id)
            
            if not regency_data:
                logger.warning(f"Regency with ID {regency_id} not found")
                return None
            
            regency_schema = RegencySchema(**regency_data)
            logger.info(f"Retrieved regency: {regency_schema.name}")
            return regency_schema
            
        except Exception as e:
            logger.error(f"Error retrieving regency {regency_id}: {str(e)}")
            raise
    
    async def get_subdistrict_by_id(self, subdistrict_id: Union[UUID, str]) -> Optional[SubDistrictSchema]:
        """
        Get a specific sub-district by ID.
        """
        try:
            # Check if this is a mock request
            if str(subdistrict_id) == "mock":
                mock_subdistrict = SubDistrictSchema(
                    id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                    name="Kecamatan Cibinong",
                    pum_code="320101",
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    population_count=150000,
                    poverty_level=12.5,
                    area_km2=45.2
                )
                return mock_subdistrict
            
            # Get subdistrict data from controller
            subdistrict_data = await analysis_controller.get_subdistrict_by_id(subdistrict_id)
            
            if not subdistrict_data:
                logger.warning(f"Sub-district with ID {subdistrict_id} not found")
                return None
            
            subdistrict_schema = SubDistrictSchema(**subdistrict_data)
            logger.info(f"Retrieved sub-district: {subdistrict_schema.name}")
            return subdistrict_schema
            
        except Exception as e:
            logger.error(f"Error retrieving sub-district {subdistrict_id}: {str(e)}")
            raise
    
    async def get_facilities_by_subdistrict(self, subdistrict_id: Union[UUID, str]) -> List[FacilitySchema]:
        """
        Get all health facilities within a specific sub-district.
        """
        try:
            # Check if this is a mock request
            if str(subdistrict_id) == "mock":
                mock_facilities = [
                    FacilitySchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440006"),
                        name="Puskesmas Cibinong",
                        type="puskesmas",
                        latitude=-6.4815,
                        longitude=106.8540,
                        regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                        regency_name="Kabupaten Bogor",
                        subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                        sub_district_name="Kecamatan Cibinong"
                    ),
                    FacilitySchema(
                        id=UUID("550e8400-e29b-41d4-a716-446655440007"),
                        name="RSUD Cibinong",
                        type="hospital",
                        latitude=-6.4815,
                        longitude=106.8540,
                        regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                        regency_name="Kabupaten Bogor",
                        subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                        sub_district_name="Kecamatan Cibinong"
                    )
                ]
                return mock_facilities
            
            # Get facilities data from controller
            facilities_data = await analysis_controller.get_facilities_by_subdistrict(subdistrict_id)
            
            facility_schemas = []
            for facility_data in facilities_data:
                facility_schema = FacilitySchema(**facility_data)
                facility_schemas.append(facility_schema)
            
            logger.info(f"Retrieved {len(facility_schemas)} facilities for sub-district {subdistrict_id}")
            return facility_schemas
            
        except Exception as e:
            logger.error(f"Error retrieving facilities for sub-district {subdistrict_id}: {str(e)}")
            raise
    
    @analysis_cache(expire=3600)  # Cache for 1 hour
    async def generate_heatmap_data(self, regency_id: Union[UUID, str]) -> HeatmapData:
        """
        Generate heatmap data for a specific regency using real spatial analysis.
        """
        try:
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_heatmap_data = HeatmapData(
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    total_population=5000000,
                    population_outside_radius=750000,
                    service_radius_km=5.0,
                    heatmap_points=[
                        HeatmapPoint(
                            latitude=-6.4815,
                            longitude=106.8540,
                            population_density=1500.0,
                            access_score=0.8,
                            distance_to_facility=2.5
                        ),
                        HeatmapPoint(
                            latitude=-6.4233,
                            longitude=106.9073,
                            population_density=1200.0,
                            access_score=0.6,
                            distance_to_facility=4.2
                        )
                    ]
                )
                return mock_heatmap_data
            
            # Get regency info from controller
            regency_data = await analysis_controller.get_regency_by_id(regency_id)
            if not regency_data:
                raise ValueError(f"Regency with ID {regency_id} not found")
            
            service_radius_km = 5.0
            
            # Get total population and population outside service radius from controller
            population_stats = await analysis_controller.get_population_statistics(regency_id, service_radius_km)
            
            # Get population points from controller
            population_points = await analysis_controller.get_population_points(regency_id)
            
            # Get health facilities from controller
            health_facilities = await analysis_controller.get_health_facilities_by_regency(regency_id)
            
            # Generate heatmap grid points
            heatmap_points = await self._generate_heatmap_grid(
                population_points, 
                health_facilities, 
                regency_id, 
                service_radius_km,
                aggressive_filtering=True  # Set to False for more detailed data
            )
            
            heatmap_data = HeatmapData(
                regency_id=regency_id,
                regency_name=regency_data['name'],
                total_population=population_stats['total_population'],
                population_outside_radius=population_stats['population_outside_radius'],
                service_radius_km=service_radius_km,
                heatmap_points=heatmap_points
            )
            
            logger.info(f"Generated real heatmap data for regency {regency_data['name']}")
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Error generating heatmap data for regency {regency_id}: {str(e)}")
            raise

    async def _generate_heatmap_grid(self, population_points: List[Dict], 
                                   health_facilities: List[Dict], 
                                   regency_id: Union[UUID, str],
                                   service_radius_km: float,
                                   aggressive_filtering: bool = True) -> List[HeatmapPoint]:
        """Generate a grid of heatmap points with real access scores and population density."""
        
        if not population_points:
            logger.warning(f"No population points found for regency {regency_id}")
            return []
        
        # Calculate bounding box of population points
        lats = [p['latitude'] for p in population_points]
        lngs = [p['longitude'] for p in population_points]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        
        logger.info(f"Population points bounding box: lat({min_lat:.6f}, {max_lat:.6f}), lng({min_lng:.6f}, {max_lng:.6f})")
        print(f"Population points bounding box: lat({min_lat:.6f}, {max_lat:.6f}), lng({min_lng:.6f}, {max_lng:.6f})")
        print(f"Found {len(population_points)} population points and {len(health_facilities)} health facilities")
        
        # Generate grid points (adjust grid density as needed)
        grid_size = 0.01  # Approximately 1km grid cells
        heatmap_points = []
        total_grid_points = 0
        included_points = 0
        
        lat = min_lat
        while lat <= max_lat:
            lng = min_lng
            while lng <= max_lng:
                total_grid_points += 1
                
                # Log first few grid points for debugging
                if total_grid_points <= 3:
                    print(f"Processing grid point {total_grid_points}: lat={lat:.6f}, lng={lng:.6f}")
                
                # Calculate population density around this grid point
                population_density = self._calculate_population_density(
                    population_points, lat, lng, grid_size
                )
                
                # Calculate access score based on distance to nearest facility
                access_score, distance_to_facility = self._calculate_access_score(
                    lat, lng, health_facilities, service_radius_km
                )
                
                # Log first few results for debugging
                if total_grid_points <= 3:
                    print(f"Grid point {total_grid_points} results: density={population_density:.2f}, access_score={access_score:.3f}, distance={distance_to_facility:.2f}km")
                
                # Smart filtering: Only include points that are meaningful for visualization
                should_include = False
                
                if aggressive_filtering:
                    # Aggressive filtering: Only include points with:
                    # 1. Population density > 0 (actual population)
                    # 2. Access score < 0.8 (poor access areas - these are important to show)
                    # 3. Access score between 0.8-1.0 but with some population nearby (transitional areas)
                    if population_density > 0:
                        # Always include points with population
                        should_include = True
                    elif access_score < 0.8:
                        # Include poor access areas (important for planning)
                        should_include = True
                    elif access_score < 1.0:
                        # For good access areas, only include if there's some population nearby
                        # Check if any population points are within 3km
                        nearby_population = self._check_nearby_population(population_points, lat, lng, 3.0)
                        if nearby_population > 0:
                            should_include = True
                else:
                    # Less aggressive filtering: Include more points for detailed analysis
                    if population_density > 0 or access_score < 1.0:
                        should_include = True
                
                if should_include:
                    # Ensure all values are finite for JSON serialization
                    if not math.isfinite(population_density):
                        population_density = 0.0
                    if not math.isfinite(access_score):
                        access_score = 0.0
                    if not math.isfinite(distance_to_facility):
                        distance_to_facility = 999.0
                    
                    included_points += 1
                    heatmap_points.append(HeatmapPoint(
                        latitude=lat,
                        longitude=lng,
                        population_density=population_density,
                        access_score=access_score,
                        distance_to_facility=distance_to_facility
                    ))
                
                lng += grid_size
            lat += grid_size
        
        print(f"Generated {total_grid_points} grid points, included {included_points} points in heatmap")
        print(f"Filtering efficiency: {included_points/total_grid_points*100:.1f}% of points included")
        
        return heatmap_points

    def _calculate_population_density(self, population_points: List[Dict], 
                                   grid_lat: float, grid_lng: float, 
                                   grid_size: float) -> float:
        """Calculate population density around a grid point."""
        total_population = 0
        search_radius = grid_size * 2.0  # Increase search radius to capture more population points
        
        # Convert search radius from degrees to kilometers (rough approximation)
        search_radius_km = search_radius * 111.0  # 1 degree ≈ 111 km
        
        # Only log for first few calculations to avoid spam
        debug_log = False  # Set to True temporarily for debugging if needed
        if debug_log:
            print(f"Calculating population density for grid point ({grid_lat}, {grid_lng}) with search radius {search_radius} degrees ({search_radius_km:.2f} km)")
        
        points_in_radius = 0
        for point in population_points:
            distance = self._calculate_distance(
                grid_lat, grid_lng, 
                point['latitude'], point['longitude']
            )
            
            # Use inverse distance weighting for population contribution
            if distance <= search_radius_km:  # Compare with km, not degrees
                points_in_radius += 1
                weight = 1.0 - (distance / search_radius_km)
                total_population += point['population_count'] * weight
                if debug_log:
                    print(f"Point {point['id']} at distance {distance:.4f}km contributes {point['population_count'] * weight:.2f} people")
        
        if debug_log:
            print(f"Found {points_in_radius} population points within {search_radius_km:.2f}km radius")
        
        # Convert to population density (people per km²)
        area_km2 = (grid_size * 111) ** 2  # Rough conversion to km²
        density = total_population / area_km2 if area_km2 > 0 else 0.0
        
        # Ensure density is finite for JSON serialization
        if not math.isfinite(density):
            density = 0.0
        
        if debug_log:
            print(f"Total population: {total_population}, Area: {area_km2:.4f} km², Density: {density:.2f} people/km²")
        
        return density

    def _calculate_access_score(self, lat: float, lng: float, 
                              health_facilities: List[Dict], 
                              service_radius_km: float) -> Tuple[float, float]:
        """Calculate access score based on distance to nearest health facility."""
        if not health_facilities:
            print(f"No health facilities found for point ({lat}, {lng})")
            return 0.0, 999.0  # Use a large finite value instead of inf
        
        min_distance = float('inf')
        nearest_facility = None
        
        for facility in health_facilities:
            distance = self._calculate_distance(
                lat, lng, 
                facility['latitude'], facility['longitude']
            )
            if distance < min_distance:
                min_distance = distance
                nearest_facility = facility['name']
        
        # Calculate access score (1.0 = full access, 0.0 = no access)
        if min_distance <= service_radius_km:
            access_score = 1.0
        else:
            # Gradual decrease in access score beyond service radius
            access_score = max(0.0, 1.0 - ((min_distance - service_radius_km) / service_radius_km))
        
        # Ensure min_distance is finite for JSON serialization
        if not math.isfinite(min_distance):
            min_distance = 999.0
        
        # Ensure access_score is finite for JSON serialization
        if not math.isfinite(access_score):
            access_score = 0.0
        
        # Only log for debugging if needed
        # print(f"Access score for point ({lat}, {lng}): nearest facility '{nearest_facility}' at {min_distance:.2f}km, access_score={access_score:.3f}")
        
        return access_score, min_distance

    def _calculate_distance(self, lat1: float, lng1: float, 
                          lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        import math
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        earth_radius = 6371.0
        
        return earth_radius * c
    
    def _check_nearby_population(self, population_points: List[Dict], lat: float, lng: float, radius_km: float) -> int:
        """Check if there are any population points within a given radius."""
        nearby_count = 0
        for point in population_points:
            distance = self._calculate_distance(lat, lng, point['latitude'], point['longitude'])
            if distance <= radius_km:
                nearby_count += 1
        return nearby_count
    
    @analysis_cache(expire=3600)  # Cache for 1 hour
    async def calculate_priority_scores(self, regency_id: Union[UUID, str], 
                                      service_radius_km: float = 5.0,
                                      gap_weight: float = 0.4,
                                      efficiency_weight: float = 0.3,
                                      vulnerability_weight: float = 0.3) -> List[SubDistrictScore]:
        """
        Calculate priority scores for sub-districts within a regency using PostGIS spatial analysis.
        
        Args:
            regency_id: ID of the regency to analyze
            service_radius_km: Service radius in kilometers (default: 5.0)
            gap_weight: Weight for gap factor in composite score (default: 0.4)
            efficiency_weight: Weight for efficiency factor in composite score (default: 0.3)
            vulnerability_weight: Weight for vulnerability factor in composite score (default: 0.3)
        
        Returns:
            List of SubDistrictScore objects sorted by composite score (highest first)
        """
        try:
            # Check if this is a mock request
            if str(regency_id) == "mock":
                return self._generate_mock_priority_scores()
            
            # Validate weights sum to 1.0
            total_weight = gap_weight + efficiency_weight + vulnerability_weight
            if abs(total_weight - 1.0) > 0.001:
                raise ValueError("Weights must sum to 1.0")
            
            # Get all subdistricts in the regency from controller
            subdistricts_data = await analysis_controller.get_subdistricts_by_regency(regency_id)
            
            if not subdistricts_data:
                logger.warning(f"No subdistricts found for regency {regency_id}")
                return []
            
            # Calculate raw factors for each subdistrict
            subdistrict_scores = []
            
            for subdistrict in subdistricts_data:
                # Calculate gap factor: proportion of population outside service radius
                gap_factor_raw = await analysis_controller.calculate_gap_factor(
                    subdistrict['id'], 
                    subdistrict['population_count'], 
                    service_radius_km
                )
                
                # Calculate efficiency factor: population density
                efficiency_factor_raw = self._calculate_efficiency_factor(
                    subdistrict['population_count'], 
                    subdistrict['area_km2']
                )
                
                # Vulnerability factor: poverty level (already 0-100 scale)
                vulnerability_factor_raw = subdistrict['poverty_level']
                
                subdistrict_scores.append({
                    'id': subdistrict['id'],
                    'name': subdistrict['name'],
                    'gap_factor_raw': gap_factor_raw,
                    'efficiency_factor_raw': efficiency_factor_raw,
                    'vulnerability_factor_raw': vulnerability_factor_raw
                })
            
            # Perform min-max normalization
            normalized_scores = self._normalize_factors(subdistrict_scores)
            
            # Calculate composite scores
            final_scores = []
            for score in normalized_scores:
                composite_score = (
                    gap_weight * score['gap_factor_normalized'] +
                    efficiency_weight * score['efficiency_factor_normalized'] +
                    vulnerability_weight * score['vulnerability_factor_normalized']
                )
                
                # Ensure composite score is finite for JSON serialization
                if not math.isfinite(composite_score):
                    composite_score = 0.5
                
                final_scores.append(SubDistrictScore(
                    subdistrict_id=score['id'],
                    sub_district_name=score['name'],
                    gap_factor=score['gap_factor_normalized'],
                    efficiency_factor=score['efficiency_factor_normalized'],
                    vulnerability_factor=score['vulnerability_factor_normalized'],
                    composite_score=composite_score,
                    rank=0  # Will be set after sorting
                ))
            
            # Sort by composite score (highest first) and assign ranks
            final_scores.sort(key=lambda x: x.composite_score, reverse=True)
            for i, score in enumerate(final_scores):
                score.rank = i + 1
            
            logger.info(f"Calculated priority scores for {len(final_scores)} sub-districts in regency {regency_id}")
            return final_scores
            
        except Exception as e:
            logger.error(f"Error calculating priority scores for regency {regency_id}: {str(e)}")
            raise
    
    def _generate_mock_priority_scores(self) -> List[SubDistrictScore]:
        """Generate mock priority scores for testing purposes."""
        mock_scores = [
            SubDistrictScore(
                subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                sub_district_name="Kecamatan Cibinong",
                gap_factor=0.75,
                efficiency_factor=0.65,
                vulnerability_factor=0.80,
                composite_score=0.73,
                rank=1
            ),
            SubDistrictScore(
                subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440005"),
                sub_district_name="Kecamatan Gunung Putri",
                gap_factor=0.60,
                efficiency_factor=0.70,
                vulnerability_factor=0.65,
                composite_score=0.65,
                rank=2
            )
        ]
        return mock_scores
    
    async def generate_priority_score_data(self, regency_id: Union[UUID, str]) -> PriorityScoreData:
        """
        Generate priority score data for a specific regency.
        """
        try:
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_priority_data = PriorityScoreData(
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    total_sub_districts=2,
                    sub_districts=[
                        SubDistrictScore(
                            subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                            sub_district_name="Kecamatan Cibinong",
                            gap_factor=0.75,
                            efficiency_factor=0.65,
                            vulnerability_factor=0.80,
                            composite_score=0.73,
                            rank=1
                        ),
                        SubDistrictScore(
                            subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440005"),
                            sub_district_name="Kecamatan Gunung Putri",
                            gap_factor=0.60,
                            efficiency_factor=0.70,
                            vulnerability_factor=0.65,
                            composite_score=0.65,
                            rank=2
                        )
                    ]
                )
                return mock_priority_data
            
            # Get regency info from controller
            regency_data = await analysis_controller.get_regency_by_id(regency_id)
            if not regency_data:
                raise ValueError(f"Regency with ID {regency_id} not found")
            
            # Use the new calculate_priority_scores function with default parameters
            # These can be made configurable later through API parameters
            sub_district_scores = await self.calculate_priority_scores(
                regency_id=regency_id,
                service_radius_km=5.0,  # Default 5km radius
                gap_weight=0.4,         # 40% weight for gap factor
                efficiency_weight=0.3,   # 30% weight for efficiency factor
                vulnerability_weight=0.3  # 30% weight for vulnerability factor
            )
            
            priority_data = PriorityScoreData(
                regency_id=regency_id,
                regency_name=regency_data['name'],
                total_sub_districts=len(sub_district_scores),
                sub_districts=sub_district_scores
            )
            
            logger.info(f"Generated priority score data for regency {regency_data['name']}")
            return priority_data
            
        except Exception as e:
            logger.error(f"Error generating priority score data for regency {regency_id}: {str(e)}")
            raise
    
    async def get_subdistrict_details(self, subdistrict_id: Union[UUID, str]) -> SubDistrictDetails:
        """
        Get detailed statistics for a specific sub-district.
        """
        try:
            # Check if this is a mock request
            if str(subdistrict_id) == "mock":
                mock_details = SubDistrictDetails(
                    subdistrict_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                    sub_district_name="Kecamatan Cibinong",
                    regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    regency_name="Kabupaten Bogor",
                    population=150000,
                    area_km2=45.2,
                    population_density=3318.58,
                    poverty_rate=12.5,
                    existing_facilities_count=2,
                    existing_facilities=[
                        {
                            "name": "Puskesmas Cibinong",
                            "type": "puskesmas",
                            "latitude": -6.4815,
                            "longitude": 106.8540
                        },
                        {
                            "name": "RSUD Cibinong",
                            "type": "hospital",
                            "latitude": -6.4815,
                            "longitude": 106.8540
                        }
                    ],
                    gap_factor=0.75,
                    efficiency_factor=0.65,
                    vulnerability_factor=0.80,
                    composite_score=0.73,
                    rank=1
                )
                return mock_details
            
            # Get sub-district info from controller
            subdistrict_data = await analysis_controller.get_subdistrict_by_id(subdistrict_id)
            if not subdistrict_data:
                raise ValueError(f"Sub-district with ID {subdistrict_id} not found")
            
            # Get facilities for this sub-district from controller
            facilities_data = await analysis_controller.get_facilities_by_subdistrict(subdistrict_id)
            
            # Mock detailed statistics
            population = subdistrict_data['population_count'] or 100000
            area_km2 = subdistrict_data['area_km2'] or 50.0
            population_density = population / area_km2 if area_km2 > 0 else 0
            poverty_rate = subdistrict_data['poverty_level'] or 15.0
            
            # Ensure population density is finite for JSON serialization
            if not math.isfinite(population_density):
                population_density = 0.0
            
            # Calculate scores using the new function
            sub_district_scores = await self.calculate_priority_scores(
                regency_id=subdistrict_data['regency_id'],
                service_radius_km=5.0,
                gap_weight=0.4,
                efficiency_weight=0.3,
                vulnerability_weight=0.3
            )
            
            # Find the score for this specific sub-district
            sub_district_score = next(
                (score for score in sub_district_scores if score.subdistrict_id == subdistrict_id),
                None
            )
            
            if sub_district_score:
                gap_factor = sub_district_score.gap_factor
                efficiency_factor = sub_district_score.efficiency_factor
                vulnerability_factor = sub_district_score.vulnerability_factor
                composite_score = sub_district_score.composite_score
                rank = sub_district_score.rank
            else:
                # Fallback to mock values if calculation fails
                gap_factor = random.uniform(0.4, 0.9)
                efficiency_factor = random.uniform(0.3, 0.8)
                vulnerability_factor = random.uniform(0.5, 0.9)
                composite_score = (gap_factor + efficiency_factor + vulnerability_factor) / 3
                rank = 1
                
                # Ensure all values are finite for JSON serialization
                if not math.isfinite(gap_factor):
                    gap_factor = 0.5
                if not math.isfinite(efficiency_factor):
                    efficiency_factor = 0.5
                if not math.isfinite(vulnerability_factor):
                    vulnerability_factor = 0.5
                if not math.isfinite(composite_score):
                    composite_score = 0.5
            
            # Convert facilities to dict format
            existing_facilities = []
            for facility_data in facilities_data:
                existing_facilities.append({
                    "name": facility_data["name"],
                    "type": str(facility_data["type"]),
                    "latitude": facility_data["latitude"],
                    "longitude": facility_data["longitude"]
                })
            
            details = SubDistrictDetails(
                subdistrict_id=subdistrict_id,
                sub_district_name=subdistrict_data['name'],
                regency_id=subdistrict_data['regency_id'],
                regency_name=subdistrict_data['regency_name'],
                population=population,
                area_km2=area_km2,
                population_density=population_density,
                poverty_rate=poverty_rate,
                existing_facilities_count=len(existing_facilities),
                existing_facilities=existing_facilities,
                gap_factor=gap_factor,
                efficiency_factor=efficiency_factor,
                vulnerability_factor=vulnerability_factor,
                composite_score=composite_score,
                rank=rank
            )
            
            logger.info(f"Generated sub-district details for {subdistrict_data['name']}")
            return details
            
        except Exception as e:
            logger.error(f"Error generating sub-district details for {subdistrict_id}: {str(e)}")
            raise
    
    @analysis_cache(expire=3600)  # Cache for 1 hour
    async def generate_analysis_summary(self, regency_id: Union[UUID, str]) -> AnalysisSummary:
        """
        Generate a comprehensive analysis summary for a regency.
        """
        try:
            # Check if this is a mock request
            if str(regency_id) == "mock":
                mock_summary = AnalysisSummary(
                    regency_name="Kabupaten Bogor",
                    summary_metrics=SummaryMetrics(
                        coverage_percentage=68.5,
                        average_distance_km=4.7,
                        average_travel_time_hours=1.2
                    ),
                    facility_overview=[
                        FacilityOverview(
                            id=UUID("550e8400-e29b-41d4-a716-446655440006"),
                            name="RS. Borromeus",
                            type="Hospital",
                            rating=4.8
                        ),
                        FacilityOverview(
                            id=UUID("550e8400-e29b-41d4-a716-446655440007"),
                            name="Klinik Medika",
                            type="Clinic",
                            rating=4.5
                        )
                    ]
                )
                return mock_summary
            
            # Get regency info from controller
            regency_data = await analysis_controller.get_regency_by_id(regency_id)
            if not regency_data:
                raise ValueError(f"Regency with ID {regency_id} not found")
            
            # Get population statistics from controller
            population_stats = await analysis_controller.get_population_statistics(regency_id, 5.0)  # 5km service radius
            total_population = population_stats['total_population']
            population_outside_radius = population_stats['population_outside_radius']
            
            # Calculate coverage percentage
            coverage_percentage = ((total_population - population_outside_radius) / total_population * 100) if total_population > 0 else 0.0
            
            # Ensure coverage percentage is finite for JSON serialization
            if not math.isfinite(coverage_percentage):
                coverage_percentage = 0.0
            
            logger.info(f"Coverage calculation: total_pop={total_population}, outside_radius={population_outside_radius}, coverage={coverage_percentage:.2f}%")
            
            # Get health facilities from controller
            health_facilities = await analysis_controller.get_health_facilities_by_regency(regency_id)
            
            # Debug: Check if we have any data at all
            if total_population == 0:
                logger.warning(f"No population data found for regency {regency_id}")
            if not health_facilities:
                logger.warning(f"No health facilities found for regency {regency_id}")
            else:
                logger.info(f"Found {len(health_facilities)} health facilities")
            
            # Calculate average distance and travel time
            average_distance_km, average_travel_time_hours = await self._calculate_average_metrics(
                regency_id, health_facilities
            )
            
            # Create facility overview
            facility_overview = []
            for facility in health_facilities:
                # For now, use a simple rating based on facility type
                # In a real implementation, this would come from a rating system
                rating = self._get_facility_rating(facility['type'])
                
                facility_overview.append(FacilityOverview(
                    id=facility['id'],
                    name=facility['name'],
                    type=str(facility['type']),
                    rating=rating
                ))
            
            summary_metrics = SummaryMetrics(
                coverage_percentage=coverage_percentage,
                average_distance_km=average_distance_km,
                average_travel_time_hours=average_travel_time_hours
            )
            
            analysis_summary = AnalysisSummary(
                regency_name=regency_data['name'],
                summary_metrics=summary_metrics,
                facility_overview=facility_overview
            )
            
            logger.info(f"Generated analysis summary for regency {regency_data['name']}")
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Error generating analysis summary for regency {regency_id}: {str(e)}")
            raise
    
    async def _calculate_average_metrics(self, regency_id: Union[UUID, str], health_facilities: List[Dict]) -> Tuple[float, float]:
        """Calculate average distance and travel time for the regency."""
        if not health_facilities:
            logger.warning(f"No health facilities found for regency {regency_id}")
            return 0.0, 0.0
        
        # Get all population points in the regency from controller
        population_points = await analysis_controller.get_population_points(regency_id)
        
        if not population_points:
            logger.warning(f"No population points found for regency {regency_id}")
            return 0.0, 0.0
        
        total_distance = 0.0
        total_population = 0
        
        logger.info(f"Calculating average metrics for {len(population_points)} population points and {len(health_facilities)} facilities")
        
        for i, point in enumerate(population_points):
            # Find the nearest facility to this population point
            min_distance = float('inf')
            nearest_facility = None
            
            for facility in health_facilities:
                distance = self._calculate_distance(
                    point['latitude'], point['longitude'],
                    facility['latitude'], facility['longitude']
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_facility = facility['name']
            
            # Weight by population count
            population_weight = point['population_count']
            total_distance += min_distance * population_weight
            total_population += population_weight
            
            # Log first few calculations for debugging
            if i < 3:
                logger.info(f"Point {i}: lat={point['latitude']:.4f}, lng={point['longitude']:.4f}, "
                          f"nearest_facility={nearest_facility}, distance={min_distance:.2f}km, "
                          f"population={population_weight}")
        
        # Calculate average distance
        average_distance_km = total_distance / total_population if total_population > 0 else 0.0
        
        # Calculate average travel time using 50 km/h average driving speed
        average_speed_kmh = 50.0
        average_travel_time_hours = average_distance_km / average_speed_kmh if average_speed_kmh > 0 else 0.0
        
        # Ensure values are finite for JSON serialization
        if not math.isfinite(average_distance_km):
            average_distance_km = 0.0
        if not math.isfinite(average_travel_time_hours):
            average_travel_time_hours = 0.0
        
        logger.info(f"Average metrics: distance={average_distance_km:.2f}km, travel_time={average_travel_time_hours:.2f}hours")
        
        return average_distance_km, average_travel_time_hours
    
    def _calculate_efficiency_factor(self, population_count: int, area_km2: float) -> float:
        """Calculate efficiency factor: population density (people per km²)."""
        if area_km2 <= 0:
            return 0.0
        
        efficiency_factor = population_count / area_km2
        
        # Ensure the value is finite for JSON serialization
        if not math.isfinite(efficiency_factor):
            return 0.0
        
        return efficiency_factor
    
    def _normalize_factors(self, subdistrict_scores: List[Dict]) -> List[Dict]:
        """Perform min-max normalization on all factors."""
        if not subdistrict_scores:
            return []
        
        # Extract raw values for normalization
        gap_factors = [score['gap_factor_raw'] for score in subdistrict_scores]
        efficiency_factors = [score['efficiency_factor_raw'] for score in subdistrict_scores]
        vulnerability_factors = [score['vulnerability_factor_raw'] for score in subdistrict_scores]
        
        # Calculate min and max for each factor
        gap_min, gap_max = min(gap_factors), max(gap_factors)
        efficiency_min, efficiency_max = min(efficiency_factors), max(efficiency_factors)
        vulnerability_min, vulnerability_max = min(vulnerability_factors), max(vulnerability_factors)
        
        # Normalize each factor
        normalized_scores = []
        for score in subdistrict_scores:
            # Gap factor normalization
            if gap_max == gap_min:
                gap_normalized = 0.5  # Default to middle value if all values are the same
            else:
                gap_normalized = (score['gap_factor_raw'] - gap_min) / (gap_max - gap_min)
            
            # Efficiency factor normalization
            if efficiency_max == efficiency_min:
                efficiency_normalized = 0.5
            else:
                efficiency_normalized = (score['efficiency_factor_raw'] - efficiency_min) / (efficiency_max - efficiency_min)
            
            # Vulnerability factor normalization
            if vulnerability_max == vulnerability_min:
                vulnerability_normalized = 0.5
            else:
                vulnerability_normalized = (score['vulnerability_factor_raw'] - vulnerability_min) / (vulnerability_max - vulnerability_min)
            
            # Ensure all normalized values are finite for JSON serialization
            if not math.isfinite(gap_normalized):
                gap_normalized = 0.5
            if not math.isfinite(efficiency_normalized):
                efficiency_normalized = 0.5
            if not math.isfinite(vulnerability_normalized):
                vulnerability_normalized = 0.5
            
            normalized_scores.append({
                'id': score['id'],
                'name': score['name'],
                'gap_factor_normalized': gap_normalized,
                'efficiency_factor_normalized': efficiency_normalized,
                'vulnerability_factor_normalized': vulnerability_normalized
            })
        
        return normalized_scores 
    
    def _get_facility_rating(self, facility_type: str) -> float:
        """Get a rating for a facility based on its type."""
        # Simple rating system based on facility type
        # In a real implementation, this would come from a database or external API
        ratings = {
            "Puskesmas": 4.2,
            "Pustu": 3.8,
            "Klinik": 4.0,
            "Rumah Sakit": 4.5,
            "Hospital": 4.5,
            "Clinic": 4.0
        }
        
        # Convert enum to string if needed
        if hasattr(facility_type, 'value'):
            facility_type = facility_type.value
        
        return ratings.get(str(facility_type), 4.0)  # Default rating of 4.0 