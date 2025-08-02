import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from uuid import UUID

from app.src.config.database import get_db
from app.src.models.regency import Regency
from app.src.models.population_point import PopulationPoint
from app.src.models.health_facility import HealthFacility
from app.src.schemas.simulation_schema import SimulationResponse, OptimizedFacility, FacilityType

class SimulationService:
    def __init__(self):
        # Configurable parameters
        self.facility_costs = {
            'Puskesmas': 2_000_000_000,  # 2 Billion IDR
            'Pustu': 500_000_000  # 500 Million IDR
        }
        self.coverage_radius_km = 5.0  # 5km coverage radius
        self.min_cost = min(self.facility_costs.values())
    
    def set_facility_costs(self, puskesmas_cost: float, pustu_cost: float):
        """Set custom facility costs"""
        self.facility_costs['Puskesmas'] = puskesmas_cost
        self.facility_costs['Pustu'] = pustu_cost
        self.min_cost = min(self.facility_costs.values())
    
    def set_coverage_radius(self, radius_km: float):
        """Set custom coverage radius"""
        self.coverage_radius_km = radius_km
    
    def get_regency_by_id(self, regency_id: UUID) -> Regency:
        """Get regency by ID"""
        db = next(get_db())
        return db.query(Regency).filter(Regency.id == regency_id).first()
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _get_underserved_population(self, regency_id: UUID) -> List[Dict[str, Any]]:
        """Get population points that are not within coverage radius of existing facilities"""
        db = next(get_db())
        
        # Get all population points in the regency
        query = text("""
            SELECT 
                pp.id,
                pp.latitude,
                pp.longitude,
                pp.population,
                pp.subdistrict_id,
                s.name as subdistrict_name
            FROM population_points pp
            JOIN subdistricts s ON pp.subdistrict_id = s.id
            WHERE s.regency_id = :regency_id
        """)
        
        population_points = db.execute(query, {"regency_id": str(regency_id)}).fetchall()
        
        # Get existing health facilities
        facilities_query = text("""
            SELECT 
                hf.id,
                hf.latitude,
                hf.longitude,
                hf.type
            FROM health_facilities hf
            JOIN subdistricts s ON hf.subdistrict_id = s.id
            WHERE s.regency_id = :regency_id
        """)
        
        existing_facilities = db.execute(facilities_query, {"regency_id": str(regency_id)}).fetchall()
        
        # Filter out population points that are already covered
        underserved_points = []
        
        for pop_point in population_points:
            is_covered = False
            
            for facility in existing_facilities:
                distance = self._calculate_distance(
                    pop_point.latitude, pop_point.longitude,
                    facility.latitude, facility.longitude
                )
                
                if distance <= self.coverage_radius_km:
                    is_covered = True
                    break
            
            if not is_covered:
                underserved_points.append({
                    'id': pop_point.id,
                    'latitude': pop_point.latitude,
                    'longitude': pop_point.longitude,
                    'population': pop_point.population,
                    'subdistrict_id': pop_point.subdistrict_id,
                    'subdistrict_name': pop_point.subdistrict_name
                })
        
        return underserved_points
    
    def _cluster_population_points(self, population_points: List[Dict[str, Any]], n_clusters: int = 10) -> List[Dict[str, Any]]:
        """Cluster population points to find candidate facility locations"""
        if not population_points:
            return []
        
        # Extract coordinates for clustering
        coordinates = np.array([[point['latitude'], point['longitude']] for point in population_points])
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=min(n_clusters, len(coordinates)), random_state=42)
        cluster_labels = kmeans.fit_predict(coordinates)
        
        # Create candidate locations from cluster centers
        candidate_locations = []
        for i, center in enumerate(kmeans.cluster_centers_):
            # Find the population point closest to this cluster center
            distances = [self._calculate_distance(center[0], center[1], point['latitude'], point['longitude']) 
                       for point in population_points]
            closest_point_idx = np.argmin(distances)
            closest_point = population_points[closest_point_idx]
            
            candidate_locations.append({
                'latitude': center[0],
                'longitude': center[1],
                'subdistrict_id': closest_point['subdistrict_id'],
                'subdistrict_name': closest_point['subdistrict_name']
            })
        
        return candidate_locations
    
    def _calculate_coverage_increase(self, candidate_location: Dict[str, Any], 
                                   underserved_points: List[Dict[str, Any]], 
                                   covered_points: set) -> Tuple[int, set]:
        """Calculate how many new people would be covered by placing a facility at the candidate location"""
        new_covered = set()
        
        for point in underserved_points:
            if point['id'] in covered_points:
                continue
                
            distance = self._calculate_distance(
                candidate_location['latitude'], candidate_location['longitude'],
                point['latitude'], point['longitude']
            )
            
            if distance <= self.coverage_radius_km:
                new_covered.add(point['id'])
        
        total_population = sum(point['population'] for point in underserved_points 
                             if point['id'] in new_covered)
        
        return total_population, new_covered
    
    def run_greedy_simulation(self, budget: float, regency_id: UUID) -> SimulationResponse:
        """Run greedy simulation to optimize facility placement"""
        print(f"Starting greedy simulation for regency {regency_id} with budget {budget}")
        
        # Validate regency exists
        regency = self.get_regency_by_id(regency_id)
        if not regency:
            raise ValueError(f"Regency with ID {regency_id} not found")
        
        print(f"Found regency: {regency.name}")
        
        # Get underserved population points
        underserved_points = self._get_underserved_population(regency_id)
        print(f"Found {len(underserved_points)} underserved population points")
        
        if not underserved_points:
            return SimulationResponse(
                regency_id=regency_id,
                regency_name=regency.name,
                total_budget=budget,
                budget_used=0,
                facilities_recommended=0,
                total_population_covered=0,
                coverage_percentage=0,
                optimized_facilities=[],
                automated_reasoning="No underserved population found in this regency."
            )
        
        # Generate candidate locations
        candidate_locations = self._cluster_population_points(underserved_points)
        print(f"Generated {len(candidate_locations)} candidate locations")
        
        # Initialize tracking variables
        remaining_budget = budget
        covered_points = set()
        recommended_facilities = []
        total_population_covered = 0
        
        # Greedy algorithm loop
        while remaining_budget >= self.min_cost and candidate_locations:
            best_candidate = None
            best_coverage_increase = 0
            best_cost_effectiveness = 0
            best_new_covered = set()
            best_facility_type = None
            
            print(f"Evaluating {len(candidate_locations)} candidates with remaining budget: {remaining_budget}")
            
            for candidate in candidate_locations:
                # Try both facility types
                for facility_type, cost in self.facility_costs.items():
                    if cost > remaining_budget:
                        continue
                    
                    coverage_increase, new_covered = self._calculate_coverage_increase(
                        candidate, underserved_points, covered_points
                    )
                    
                    if coverage_increase > 0:
                        cost_effectiveness = coverage_increase / cost
                        
                        if cost_effectiveness > best_cost_effectiveness:
                            best_candidate = candidate
                            best_coverage_increase = coverage_increase
                            best_cost_effectiveness = cost_effectiveness
                            best_new_covered = new_covered
                            best_facility_type = facility_type
            
            if best_candidate is None:
                break
            
            # Add the best facility
            facility_cost = self.facility_costs[best_facility_type]
            recommended_facilities.append(OptimizedFacility(
                latitude=best_candidate['latitude'],
                longitude=best_candidate['longitude'],
                sub_district_id=best_candidate['subdistrict_id'],
                sub_district_name=best_candidate['subdistrict_name'],
                estimated_cost=facility_cost,
                population_covered=best_coverage_increase,
                coverage_radius_km=self.coverage_radius_km,
                facility_type=FacilityType(best_facility_type)
            ))
            
            remaining_budget -= facility_cost
            covered_points.update(best_new_covered)
            total_population_covered += best_coverage_increase
            
            print(f"Added {best_facility_type} facility at ({best_candidate['latitude']:.4f}, {best_candidate['longitude']:.4f})")
            print(f"Coverage increase: {best_coverage_increase}, Cost: {facility_cost}, Remaining budget: {remaining_budget}")
            
            # Remove the selected candidate from future consideration
            candidate_locations = [c for c in candidate_locations if c != best_candidate]
        
        # Calculate coverage percentage
        total_population = sum(point['population'] for point in underserved_points)
        coverage_percentage = (total_population_covered / total_population * 100) if total_population > 0 else 0
        
        # Generate automated reasoning
        reasoning = self._generate_automated_reasoning(
            regency.name, budget, remaining_budget, len(recommended_facilities),
            total_population_covered, coverage_percentage, recommended_facilities
        )
        
        print(f"Simulation complete. Facilities recommended: {len(recommended_facilities)}")
        print(f"Total population covered: {total_population_covered}")
        print(f"Coverage percentage: {coverage_percentage:.2f}%")
        
        return SimulationResponse(
            regency_id=regency_id,
            regency_name=regency.name,
            total_budget=budget,
            budget_used=budget - remaining_budget,
            facilities_recommended=len(recommended_facilities),
            total_population_covered=total_population_covered,
            coverage_percentage=coverage_percentage,
            optimized_facilities=recommended_facilities,
            automated_reasoning=reasoning
        )
    
    def _generate_automated_reasoning(self, regency_name: str, total_budget: float, 
                                    remaining_budget: float, facilities_recommended: int,
                                    total_population_covered: int, coverage_percentage: float,
                                    facilities: List[OptimizedFacility]) -> str:
        """Generate automated reasoning explaining the greedy algorithm's decisions"""
        
        budget_used = total_budget - remaining_budget
        budget_efficiency = (budget_used / total_budget * 100) if total_budget > 0 else 0
        
        # Analyze facility type distribution
        puskesmas_count = sum(1 for f in facilities if f.facility_type == FacilityType.PUSKESMAS)
        pustu_count = sum(1 for f in facilities if f.facility_type == FacilityType.PUSTU)
        
        reasoning = f"The greedy algorithm analyzed {regency_name} and allocated {budget_used:,.0f} IDR ({budget_efficiency:.1f}% of total budget) to recommend {facilities_recommended} facilities, achieving {coverage_percentage:.1f}% population coverage for {total_population_covered:,} people. "
        
        if facilities_recommended > 0:
            reasoning += f"The algorithm prioritized cost-effectiveness by recommending {puskesmas_count} Puskesmas and {pustu_count} Pustu facilities based on population density and coverage gaps in underserved areas."
        else:
            reasoning += "No facilities were recommended due to budget constraints or lack of underserved areas."
        
        return reasoning 