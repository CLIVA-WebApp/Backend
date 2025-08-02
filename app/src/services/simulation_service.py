from typing import List, Dict, Any, Optional, Tuple, Union
from app.src.schemas.analysis_schema import OptimizedFacility, SimulationResult
from app.src.config.database import SessionLocal
from app.src.models.regency import Regency
from app.src.models.subdistrict import Subdistrict
from app.src.models.health_facility import HealthFacility
from app.src.models.population_point import PopulationPoint
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import haversine_distances
import math
from uuid import UUID
import random

logger = logging.getLogger(__name__)

class SimulationService:
    def __init__(self):
        self.db: Session = SessionLocal()
        
        # Default facility costs (in Indonesian Rupiah)
        self.facility_costs = {
            'Puskesmas': 2_000_000_000,  # 2 Billion IDR
            'Pustu': 500_000_000,        # 500 Million IDR
        }
        
        # Coverage radius for each facility type (in meters)
        self.coverage_radius = {
            'Puskesmas': 5000,  # 5km
            'Pustu': 3000,      # 3km
        }
    
    def set_facility_costs(self, costs: Dict[str, int]):
        """
        Set custom facility costs.
        
        Args:
            costs: Dictionary with facility type as key and cost in IDR as value
        """
        self.facility_costs.update(costs)
        logger.info(f"Updated facility costs: {self.facility_costs}")
    
    def set_coverage_radius(self, radius: Dict[str, int]):
        """
        Set custom coverage radius for facility types.
        
        Args:
            radius: Dictionary with facility type as key and radius in meters as value
        """
        self.coverage_radius.update(radius)
        logger.info(f"Updated coverage radius: {self.coverage_radius}")
    
    async def run_greedy_simulation(self, budget: float, regency_id: Union[UUID, str]) -> SimulationResult:
        """
        Run greedy simulation for facility placement optimization.
        
        Args:
            budget: Available budget in IDR
            regency_id: ID of the regency to optimize
        
        Returns:
            SimulationResult with optimized facility recommendations
        """
        try:
            print(f"Starting simulation for regency {regency_id} with budget {budget}")
            
            # Check if this is a mock request
            if str(regency_id) == "mock":
                print("Using mock simulation result")
                return self._generate_mock_simulation_result(budget)
            
            # Get regency info
            print(f"Getting regency info for {regency_id}")
            regency = self.db.query(Regency).filter(Regency.id == regency_id).first()
            if not regency:
                raise ValueError(f"Regency with ID {regency_id} not found")
            print(f"Found regency: {regency.name}")
            
            # Get all population points in the regency
            print("Getting population points...")
            population_points = self._get_population_points(regency_id)
            print(f"Found {len(population_points)} population points")
            if not population_points:
                raise ValueError(f"No population points found for regency {regency_id}")
            
            # Get existing health facilities
            print("Getting existing facilities...")
            existing_facilities = self._get_existing_facilities(regency_id)
            print(f"Found {len(existing_facilities)} existing facilities")
            
            # Identify underserved population points
            print("Identifying underserved points...")
            underserved_points = self._identify_underserved_points(
                population_points, existing_facilities
            )
            print(f"Found {len(underserved_points)} underserved points")
            
            if not underserved_points:
                print("No underserved points found, returning empty result")
                return SimulationResult(
                    regency_id=regency_id,
                    regency_name=regency.name,
                    total_budget=budget,
                    budget_used=0,
                    facilities_recommended=0,
                    total_population_covered=0,
                    coverage_percentage=100.0,
                    optimized_facilities=[]
                )
            
            # Cluster underserved points to find candidate locations
            print("Clustering population points...")
            candidate_locations = self._cluster_population_points(underserved_points)
            print(f"Found {len(candidate_locations)} candidate locations")
            
            # Run greedy algorithm
            print("Running greedy algorithm...")
            optimized_facilities, budget_used, total_covered = self._run_greedy_algorithm(
                candidate_locations, underserved_points, budget
            )
            print(f"Algorithm completed: {len(optimized_facilities)} facilities recommended")
            
            # Calculate coverage percentage
            total_population = sum(point['population_count'] for point in population_points)
            coverage_percentage = (total_covered / total_population * 100) if total_population > 0 else 0
            print(f"Coverage percentage: {coverage_percentage:.2f}%")
            
            return SimulationResult(
                regency_id=regency_id,
                regency_name=regency.name,
                total_budget=budget,
                budget_used=budget_used,
                facilities_recommended=len(optimized_facilities),
                total_population_covered=int(total_covered),
                coverage_percentage=coverage_percentage,
                optimized_facilities=optimized_facilities
            )
            
        except Exception as e:
            print(f"Error running simulation for regency {regency_id}: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _get_population_points(self, regency_id: Union[UUID, str]) -> List[Dict[str, Any]]:
        """Get all population points in the regency."""
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
        
        result = self.db.execute(query, {"regency_id": regency_id})
        
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
    
    def _get_existing_facilities(self, regency_id: Union[UUID, str]) -> List[Dict[str, Any]]:
        """Get existing health facilities in the regency."""
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
        
        result = self.db.execute(query, {"regency_id": regency_id})
        
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
    
    def _identify_underserved_points(self, population_points: List[Dict], 
                                   existing_facilities: List[Dict]) -> List[Dict]:
        """Identify population points that are not covered by existing facilities."""
        underserved_points = []
        
        for point in population_points:
            is_covered = False
            
            # Check if point is covered by any existing facility
            for facility in existing_facilities:
                distance = self._calculate_distance(
                    point['latitude'], point['longitude'],
                    facility['latitude'], facility['longitude']
                )
                
                # Use the maximum coverage radius for existing facilities
                max_radius = max(self.coverage_radius.values())
                if distance <= max_radius:
                    is_covered = True
                    break
            
            if not is_covered:
                underserved_points.append(point)
        
        return underserved_points
    
    def _cluster_population_points(self, points: List[Dict], n_clusters: int = 10) -> List[Dict]:
        """Cluster population points to find candidate locations."""
        if len(points) == 0:
            return []
        
        # Extract coordinates for clustering
        coordinates = np.array([[p['latitude'], p['longitude']] for p in points])
        
        # Determine number of clusters (min of n_clusters or number of points)
        n_clusters = min(n_clusters, len(points))
        
        if n_clusters == 1:
            # If only one cluster, use the centroid of all points
            centroid = np.mean(coordinates, axis=0)
            # Get the most common subdistrict_id from the points
            subdistrict_ids = [p.get('subdistrict_id') for p in points if p.get('subdistrict_id')]
            most_common_subdistrict_id = max(set(subdistrict_ids), key=subdistrict_ids.count) if subdistrict_ids else None
            
            return [{
                'latitude': centroid[0],
                'longitude': centroid[1],
                'population_count': sum(p['population_count'] for p in points),
                'subdistrict_id': most_common_subdistrict_id
            }]
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(coordinates)
        
        # Create candidate locations from cluster centroids
        candidates = []
        for i in range(n_clusters):
            cluster_points = [p for j, p in enumerate(points) if cluster_labels[j] == i]
            centroid = kmeans.cluster_centers_[i]
            
            # Get the most common subdistrict_id from the cluster points
            subdistrict_ids = [p.get('subdistrict_id') for p in cluster_points if p.get('subdistrict_id')]
            most_common_subdistrict_id = max(set(subdistrict_ids), key=subdistrict_ids.count) if subdistrict_ids else None
            
            candidates.append({
                'latitude': centroid[0],
                'longitude': centroid[1],
                'population_count': sum(p['population_count'] for p in cluster_points),
                'subdistrict_id': most_common_subdistrict_id,
                'cluster_points': cluster_points
            })
        
        return candidates
    
    def _run_greedy_algorithm(self, candidate_locations: List[Dict], 
                             underserved_points: List[Dict], budget: float) -> Tuple[List[OptimizedFacility], float, float]:
        """Run greedy algorithm to select optimal facility locations."""
        remaining_budget = budget
        selected_facilities = []
        covered_points = set()
        total_covered = 0
        
        # Minimum cost to continue
        min_cost = min(self.facility_costs.values())
        
        while remaining_budget >= min_cost and len(candidate_locations) > 0:
            best_facility = None
            best_coverage_increase = 0
            best_cost_efficiency = 0
            best_location = None
            best_type = None
            
            # Evaluate each candidate location
            for location in candidate_locations:
                for facility_type, cost in self.facility_costs.items():
                    if cost > remaining_budget:
                        continue
                    
                    # Calculate coverage increase for this facility
                    coverage_increase = self._calculate_coverage_increase(
                        location, underserved_points, covered_points, facility_type
                    )
                    
                    if coverage_increase > 0:
                        cost_efficiency = coverage_increase / cost
                        
                        if cost_efficiency > best_cost_efficiency:
                            best_cost_efficiency = cost_efficiency
                            best_coverage_increase = coverage_increase
                            best_location = location
                            best_type = facility_type
            
            # If no improvement found, break
            if best_location is None:
                break
            
            # Add the best facility
            facility = OptimizedFacility(
                latitude=best_location['latitude'],
                longitude=best_location['longitude'],
                sub_district_id=best_location.get('subdistrict_id'),
                sub_district_name=self._get_subdistrict_name(best_location.get('subdistrict_id')),
                estimated_cost=self.facility_costs[best_type],
                population_covered=int(best_coverage_increase),
                coverage_radius_km=self.coverage_radius[best_type] / 1000
            )
            
            selected_facilities.append(facility)
            remaining_budget -= self.facility_costs[best_type]
            total_covered += best_coverage_increase
            
            # Update covered points
            self._update_covered_points(best_location, underserved_points, covered_points, best_type)
            
            # Remove the selected location from candidates
            candidate_locations.remove(best_location)
        
        return selected_facilities, budget - remaining_budget, total_covered
    
    def _calculate_coverage_increase(self, location: Dict, underserved_points: List[Dict], 
                                   covered_points: set, facility_type: str) -> float:
        """Calculate the increase in population coverage for a facility at the given location."""
        coverage_radius = self.coverage_radius[facility_type]
        coverage_increase = 0
        
        for point in underserved_points:
            if point['id'] in covered_points:
                continue
            
            distance = self._calculate_distance(
                location['latitude'], location['longitude'],
                point['latitude'], point['longitude']
            )
            
            if distance <= coverage_radius:
                coverage_increase += point['population_count']
        
        return coverage_increase
    
    def _update_covered_points(self, location: Dict, underserved_points: List[Dict], 
                             covered_points: set, facility_type: str):
        """Update the set of covered points after adding a facility."""
        coverage_radius = self.coverage_radius[facility_type]
        
        for point in underserved_points:
            if point['id'] in covered_points:
                continue
            
            distance = self._calculate_distance(
                location['latitude'], location['longitude'],
                point['latitude'], point['longitude']
            )
            
            if distance <= coverage_radius:
                covered_points.add(point['id'])
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters using Haversine formula."""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in meters
        r = 6371000
        return c * r
    
    async def get_regency_by_id(self, regency_id: Union[UUID, str]):
        """Get regency by ID."""
        try:
            print(f"Getting regency by ID: {regency_id}")
            regency = self.db.query(Regency).filter(Regency.id == regency_id).first()
            if regency:
                print(f"Found regency: {regency.name}")
            else:
                print(f"Regency not found: {regency_id}")
            return regency
        except Exception as e:
            print(f"Error getting regency: {str(e)}")
            raise
    
    def _get_subdistrict_name(self, subdistrict_id: Optional[UUID]) -> Optional[str]:
        """Get subdistrict name by ID."""
        if not subdistrict_id:
            return None
        
        subdistrict = self.db.query(Subdistrict).filter(Subdistrict.id == subdistrict_id).first()
        return subdistrict.name if subdistrict else None
    
    def _generate_mock_simulation_result(self, budget: float) -> SimulationResult:
        """Generate mock simulation result for testing."""
        mock_facilities = [
            OptimizedFacility(
                latitude=-6.4815,
                longitude=106.8540,
                sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                sub_district_name="Kecamatan Cibinong",
                estimated_cost=2_000_000_000,
                population_covered=50000,
                coverage_radius_km=5.0
            ),
            OptimizedFacility(
                latitude=-6.4233,
                longitude=106.9073,
                sub_district_id=UUID("550e8400-e29b-41d4-a716-446655440005"),
                sub_district_name="Kecamatan Gunung Putri",
                estimated_cost=500_000_000,
                population_covered=25000,
                coverage_radius_km=3.0
            )
        ]
        
        budget_used = sum(f.estimated_cost for f in mock_facilities)
        total_covered = sum(f.population_covered for f in mock_facilities)
        
        return SimulationResult(
            regency_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
            regency_name="Kabupaten Bogor",
            total_budget=budget,
            budget_used=budget_used,
            facilities_recommended=len(mock_facilities),
            total_population_covered=total_covered,
            coverage_percentage=85.5,
            optimized_facilities=mock_facilities
        ) 