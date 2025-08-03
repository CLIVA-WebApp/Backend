import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Optional
from uuid import UUID
import traceback

from app.src.controllers.simulation_controller import simulation_controller
from app.src.schemas.simulation_schema import (
    SimulationResponse, SimulationSummary, Recommendation, 
    Coordinates, FacilityType, LegacySimulationResponse, OptimizedFacility,
    GeographicLevel
)

class SimulationService:
    def __init__(self):
        # Configurable parameters
        self.facility_costs = {
            'Hospital': 10_000_000_000,  # 10 Billion IDR
            'Clinic': 4_500_000_000,     # 4.5 Billion IDR
            'Puskesmas': 2_000_000_000,  # 2 Billion IDR
            'Pustu': 500_000_000         # 500 Million IDR
        }
        self.coverage_radius_km = 5.0  # 5km coverage radius
        self.min_cost = min(self.facility_costs.values())
    
    def set_facility_costs(self, costs: Dict[str, float]):
        """Set custom facility costs"""
        self.facility_costs.update(costs)
        self.min_cost = min(self.facility_costs.values())
    
    def set_coverage_radius(self, radius_km: float):
        """Set custom coverage radius"""
        self.coverage_radius_km = radius_km
    
    async def get_subdistrict_by_id(self, subdistrict_id: UUID) -> Optional[Dict[str, Any]]:
        """Get subdistrict by ID"""
        return await simulation_controller.get_subdistrict_by_id(subdistrict_id)
    
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
    
    async def _get_subdistrict_ids_by_level(self, geographic_level: GeographicLevel, area_ids: List[UUID]) -> List[UUID]:
        """Get subdistrict IDs based on the geographic level"""
        return await simulation_controller.get_subdistrict_ids_by_level(geographic_level, area_ids)
    
    async def _get_population_data(self, subdistrict_ids: List[UUID]) -> List[Dict[str, Any]]:
        """Get population data for specified subdistricts"""
        return await simulation_controller.get_population_data(subdistrict_ids)
    
    async def _get_existing_facilities(self, subdistrict_ids: List[UUID]) -> List[Dict[str, Any]]:
        """Get existing health facilities in the specified subdistricts"""
        return await simulation_controller.get_existing_facilities(subdistrict_ids)
    
    def _calculate_initial_coverage(self, population_points: List[Dict[str, Any]], 
                                  existing_facilities: List[Dict[str, Any]]) -> float:
        """Calculate initial population coverage percentage"""
        if not population_points:
            return 0.0
        
        total_population = sum(point['population'] for point in population_points)
        covered_population = 0
        
        for point in population_points:
            is_covered = False
            for facility in existing_facilities:
                distance = self._calculate_distance(
                    point['latitude'], point['longitude'],
                    facility['latitude'], facility['longitude']
                )
                if distance <= self.coverage_radius_km:
                    is_covered = True
                    break
            
            if is_covered:
                covered_population += point['population']
        
        return (covered_population / total_population * 100) if total_population > 0 else 0.0
    
    def _cluster_population_points(self, population_points: List[Dict[str, Any]], facility_types: List[FacilityType]) -> List[Dict[str, Any]]:
        """Cluster population points to find candidate facility locations"""
        if not population_points:
            return []
        
        # Extract coordinates for clustering
        coordinates = np.array([[point['latitude'], point['longitude']] for point in population_points])
        
        # Determine number of clusters based on facility types and population size
        n_clusters = min(len(facility_types) * 5, len(coordinates), 20)  # Max 20 clusters
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(coordinates)
        
        # Create candidate locations from cluster centers
        candidate_locations = []
        for i, center in enumerate(kmeans.cluster_centers_):
            # Find the population point closest to this cluster center
            distances = [self._calculate_distance(center[0], center[1], point['latitude'], point['longitude']) 
                       for point in population_points]
            closest_point_idx = np.argmin(distances)
            closest_point = population_points[closest_point_idx]
            
            # Create candidates for each facility type
            for facility_type in facility_types:
                candidate_locations.append({
                    'latitude': center[0],
                    'longitude': center[1],
                    'subdistrict_id': closest_point['subdistrict_id'],
                    'subdistrict_name': closest_point['subdistrict_name'],
                    'location_name': closest_point['subdistrict_name'],
                    'type': facility_type
                })
        
        return candidate_locations
    
    def _calculate_covered_population(self, population_data: List[Dict[str, Any]], existing_facilities: List[Dict[str, Any]]) -> int:
        """Calculate how many people are covered by existing facilities"""
        covered_population = 0
        
        for point in population_data:
            is_covered = False
            for facility in existing_facilities:
                distance = self._calculate_distance(
                    point['latitude'], point['longitude'],
                    facility['latitude'], facility['longitude']
                )
                if distance <= self.coverage_radius_km:
                    is_covered = True
                    break
            
            if is_covered:
                covered_population += point['population']
        
        return covered_population
    
    def _calculate_coverage_increase(self, population_data: List[Dict[str, Any]], 
                                   existing_facilities: List[Dict[str, Any]], 
                                   recommendations: List[Recommendation], 
                                   candidate: Dict[str, Any]) -> int:
        """Calculate how many new people would be covered by placing a facility at the candidate location"""
        new_covered = 0
        
        for point in population_data:
            # Check if already covered by existing facilities
            is_covered = False
            for facility in existing_facilities:
                distance = self._calculate_distance(
                    point['latitude'], point['longitude'],
                    facility['latitude'], facility['longitude']
                )
                if distance <= self.coverage_radius_km:
                    is_covered = True
                    break
            
            # Check if already covered by existing recommendations
            if not is_covered:
                for rec in recommendations:
                    distance = self._calculate_distance(
                        point['latitude'], point['longitude'],
                        rec.coordinates.lat, rec.coordinates.lon
                    )
                    if distance <= self.coverage_radius_km:
                        is_covered = True
                        break
            
            # Check if would be covered by new candidate
            if not is_covered:
                distance = self._calculate_distance(
                    point['latitude'], point['longitude'],
                    candidate['latitude'], candidate['longitude']
                )
                if distance <= self.coverage_radius_km:
                    new_covered += point['population']
        
        return new_covered
    
    def _generate_automated_reasoning(self, recommendations: List[Recommendation], simulation_summary: SimulationSummary, 
                                    geographic_level: GeographicLevel, area_ids: List[UUID]) -> str:
        """Generate automated reasoning text for the simulation results"""
        try:
            if not recommendations:
                return "No facilities were recommended due to budget constraints or lack of suitable locations."
            
            # Count facilities by type
            facility_counts = {}
            for rec in recommendations:
                facility_type = rec.type.value
                facility_counts[facility_type] = facility_counts.get(facility_type, 0) + 1
            
            # Generate facility type summary
            facility_summary = []
            for facility_type, count in facility_counts.items():
                facility_summary.append(f"{count} {facility_type}")
            
            facility_text = ", ".join(facility_summary)
            
            # Generate location summary
            location_names = [rec.location_name for rec in recommendations]
            location_text = ", ".join(location_names[:3])  # Show first 3 locations
            if len(location_names) > 3:
                location_text += f" and {len(location_names) - 3} other locations"
            
            # Generate reasoning based on results
            budget_utilization = (simulation_summary.total_cost / simulation_summary.budget_remaining + simulation_summary.total_cost) * 100
            coverage_improvement = simulation_summary.coverage_increase_percent
            
            reasoning_parts = []
            
            # Budget reasoning
            if budget_utilization > 90:
                reasoning_parts.append("utilized nearly the entire budget")
            elif budget_utilization > 70:
                reasoning_parts.append("efficiently utilized the available budget")
            else:
                reasoning_parts.append("conservatively allocated the budget")
            
            # Coverage reasoning
            if coverage_improvement > 20:
                reasoning_parts.append("achieved significant coverage improvement")
            elif coverage_improvement > 10:
                reasoning_parts.append("achieved moderate coverage improvement")
            else:
                reasoning_parts.append("achieved modest coverage improvement")
            
            # Facility placement reasoning
            if len(recommendations) == 1:
                reasoning_parts.append("strategically placed a single facility")
            else:
                reasoning_parts.append(f"strategically distributed {len(recommendations)} facilities")
            
            reasoning_text = " and ".join(reasoning_parts)
            
            # Geographic level context
            level_text = geographic_level.value.capitalize()
            
            # Final template
            reasoning = f"The greedy algorithm analyzed {level_text} areas and {reasoning_text}. " \
                       f"Recommended {facility_text} at {location_text} to maximize population coverage " \
                       f"while staying within budget constraints. " \
                       f"Projected coverage increased from {simulation_summary.initial_coverage:.1f}% to {simulation_summary.projected_coverage:.1f}% " \
                       f"({coverage_improvement:.1f}% improvement) with {simulation_summary.total_cost:,.0f} IDR investment."
            
            return reasoning
            
        except Exception as e:
            print(f"Error generating automated reasoning: {e}")
            return "The greedy algorithm analyzed the area and recommended facility placements based on population coverage and budget constraints."

    def run_simulation(self, geographic_level: GeographicLevel, area_ids: List[UUID], 
                       budget: float, facility_types: List[FacilityType]) -> SimulationResponse:
        """Run simulation for multiple areas and facility types"""
        try:
            print(f"Starting simulation for {len(area_ids)} areas at {geographic_level.value} level with budget {budget}")
            
            # Get subdistrict IDs based on geographic level
            subdistrict_ids = self._get_subdistrict_ids_by_level(geographic_level, area_ids)
            print(f"Found {len(subdistrict_ids)} subdistricts to analyze")
            
            if not subdistrict_ids:
                raise ValueError("No subdistricts found for the specified areas")
            
            # Get population data
            population_data = self._get_population_data(subdistrict_ids)
            print(f"Found {len(population_data)} population points")
            
            if not population_data:
                raise ValueError("No population data found for the specified areas")
            
            # Get existing facilities
            existing_facilities = self._get_existing_facilities(subdistrict_ids)
            print(f"Found {len(existing_facilities)} existing facilities")
            
            # Calculate initial coverage
            total_population = sum(point['population'] for point in population_data)
            covered_population = self._calculate_initial_coverage(population_data, existing_facilities)
            initial_coverage = (covered_population / total_population * 100) if total_population > 0 else 0
            
            print(f"Initial coverage: {initial_coverage:.1f}% ({covered_population:,} / {total_population:,})")
            
            # Run greedy algorithm
            recommendations = []
            remaining_budget = budget
            current_coverage = covered_population
            
            # Generate candidate locations using clustering
            candidate_locations = self._cluster_population_points(population_data, facility_types)
            print(f"Generated {len(candidate_locations)} candidate locations")
            
            # Greedy selection loop
            while remaining_budget > min(self.facility_costs.values()) and candidate_locations:
                best_candidate = None
                best_ratio = 0
                
                for candidate in candidate_locations:
                    facility_cost = self.facility_costs[candidate['type']]
                    
                    if facility_cost > remaining_budget:
                        continue
                    
                    # Calculate coverage increase
                    coverage_increase = self._calculate_coverage_increase(
                        population_data, existing_facilities, recommendations, candidate
                    )
                    
                    # Calculate efficiency ratio
                    ratio = coverage_increase / facility_cost if facility_cost > 0 else 0
                    
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_candidate = candidate
                
                if best_candidate:
                    # Add best candidate to recommendations
                    recommendations.append(Recommendation(
                        type=best_candidate['type'],
                        subdistrict_id=best_candidate['subdistrict_id'],
                        location_name=best_candidate['location_name'],
                        coordinates=Coordinates(
                            lat=best_candidate['latitude'],
                            lon=best_candidate['longitude']
                        ),
                        estimated_cost=self.facility_costs[best_candidate['type']]
                    ))
                    
                    # Update budget and coverage
                    remaining_budget -= self.facility_costs[best_candidate['type']]
                    current_coverage += self._calculate_coverage_increase(
                        population_data, existing_facilities, recommendations[:-1], best_candidate
                    )
                    
                    # Remove selected candidate from list
                    candidate_locations.remove(best_candidate)
                    
                    print(f"Selected {best_candidate['type'].value} at {best_candidate['location_name']}, "
                          f"cost: {self.facility_costs[best_candidate['type']]:,.0f}, "
                          f"coverage increase: {best_ratio:.2f}")
                else:
                    break
            
            # Calculate final metrics
            total_cost = budget - remaining_budget
            projected_coverage = (current_coverage / total_population * 100) if total_population > 0 else 0
            coverage_increase_percent = projected_coverage - initial_coverage
            
            # Generate automated reasoning
            simulation_summary = SimulationSummary(
                initial_coverage=initial_coverage,
                projected_coverage=projected_coverage,
                coverage_increase_percent=coverage_increase_percent,
                total_cost=total_cost,
                budget_remaining=remaining_budget
            )
            
            automated_reasoning = self._generate_automated_reasoning(
                recommendations, simulation_summary, geographic_level, area_ids
            )
            
            print(f"Simulation completed: {len(recommendations)} facilities recommended, "
                  f"coverage: {initial_coverage:.1f}% → {projected_coverage:.1f}% (+{coverage_increase_percent:.1f}%), "
                  f"cost: {total_cost:,.0f} IDR")
            
            return SimulationResponse(
                simulation_summary=simulation_summary,
                recommendations=recommendations,
                automated_reasoning=automated_reasoning  # Add automated reasoning
            )
            
        except Exception as e:
            print(f"Error in run_simulation: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
            raise
    
    # Legacy method for backward compatibility
    def run_greedy_simulation(self, budget: float, regency_id: UUID) -> LegacySimulationResponse:
        """Legacy method for backward compatibility"""
        try:
            print(f"Starting legacy simulation for regency {regency_id} with budget {budget}")
            
            # Get regency info
            db = next(get_db())
            regency = db.query(Regency).filter(Regency.id == regency_id).first()
            if not regency:
                raise ValueError(f"Regency with ID {regency_id} not found")
            
            # Get subdistricts in the regency
            subdistricts = db.query(Subdistrict).filter(Subdistrict.regency_id == regency_id).all()
            if not subdistricts:
                return LegacySimulationResponse(
                    regency_id=regency_id,
                    regency_name=regency.name,
                    total_budget=budget,
                    budget_used=0,
                    facilities_recommended=0,
                    total_population_covered=0,
                    coverage_percentage=0,
                    optimized_facilities=[],
                    automated_reasoning="No subdistricts found in this regency."
                )
            
            # Run simulation with all subdistricts in the regency
            area_ids = [subdistrict.id for subdistrict in subdistricts]
            facility_types = [FacilityType.PUSKESMAS, FacilityType.PUSTU]  # Default types
            
            result = self.run_simulation(GeographicLevel.SUBDISTRICT, area_ids, budget, facility_types)
            
            # Convert to legacy format
            optimized_facilities = []
            for rec in result.recommendations:
                optimized_facilities.append(OptimizedFacility(
                    latitude=rec.coordinates.lat,
                    longitude=rec.coordinates.lon,
                    sub_district_id=rec.subdistrict_id,
                    sub_district_name=rec.location_name,
                    estimated_cost=rec.estimated_cost,
                    population_covered=0,  # Would need to calculate this
                    coverage_radius_km=self.coverage_radius_km,
                    facility_type=rec.type
                ))
            
            reasoning = f"The greedy algorithm analyzed {regency.name} and allocated {result.simulation_summary.total_cost:,.0f} IDR to recommend {len(result.recommendations)} facilities, achieving {result.simulation_summary.projected_coverage:.1f}% population coverage with a {result.simulation_summary.coverage_increase_percent:.1f}% increase."
            
            return LegacySimulationResponse(
                regency_id=regency_id,
                regency_name=regency.name,
                total_budget=budget,
                budget_used=result.simulation_summary.total_cost,
                facilities_recommended=len(result.recommendations),
                total_population_covered=0,  # Would need to calculate this
                coverage_percentage=result.simulation_summary.projected_coverage,
                optimized_facilities=optimized_facilities,
                automated_reasoning=reasoning
            )
            
        except Exception as e:
            print(f"Error in legacy simulation: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
            raise 