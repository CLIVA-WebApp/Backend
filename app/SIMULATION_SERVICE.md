# Simulation Service

This document describes the implementation of the simulation service with a greedy algorithm for facility placement optimization.

## Overview

The simulation service implements a greedy algorithm that optimizes health facility placement within budget constraints. The algorithm considers population distribution, existing facilities, and cost-effectiveness to recommend optimal facility locations.

## Algorithm Steps

### 1. Data Collection
- **Population Points**: Retrieves all population points within the specified regency
- **Existing Facilities**: Gets current health facility locations
- **Budget Constraints**: Validates available budget against minimum facility costs

### 2. Underserved Population Identification
- Identifies population points not covered by existing facilities
- Uses maximum coverage radius of existing facilities (5km for Puskesmas, 3km for Pustu)
- Calculates distance using Haversine formula for geographic accuracy

### 3. Candidate Location Generation
- **K-Means Clustering**: Groups underserved population points into clusters
- **Centroid Calculation**: Uses cluster centroids as candidate facility locations
- **Population Aggregation**: Sums population within each cluster

### 4. Greedy Algorithm Execution
```
While budget >= minimum_cost:
    For each candidate location:
        For each facility type:
            Calculate coverage_increase / cost
            Track best cost_efficiency
    
    Select facility with highest cost_efficiency
    Add to results
    Update covered points
    Decrease budget
    Remove selected location from candidates
```

## Facility Types and Costs

### Default Costs (Indonesian Rupiah)
- **Puskesmas**: 2,000,000,000 IDR (2 Billion)
- **Pustu**: 500,000,000 IDR (500 Million)

### Default Coverage Radius
- **Puskesmas**: 5,000 meters (5km)
- **Pustu**: 3,000 meters (3km)

## API Usage

### Basic Simulation
```json
POST /api/v1/simulation/run
{
    "regency_id": "mock",
    "budget": 5000000000
}
```

### Custom Costs and Coverage
```json
POST /api/v1/simulation/run
{
    "regency_id": "mock",
    "budget": 5000000000,
    "facility_costs": {
        "Puskesmas": 2500000000,
        "Pustu": 600000000
    },
    "coverage_radius": {
        "Puskesmas": 6000,
        "Pustu": 4000
    }
}
```

## Response Format

```json
{
    "regency_id": "uuid",
    "regency_name": "Kabupaten Bogor",
    "total_budget": 5000000000,
    "budget_used": 4500000000,
    "facilities_recommended": 2,
    "total_population_covered": 75000,
    "coverage_percentage": 85.5,
    "optimized_facilities": [
        {
            "latitude": -6.4815,
            "longitude": 106.8540,
            "sub_district_id": "uuid",
            "sub_district_name": "Kecamatan Cibinong",
            "estimated_cost": 2000000000,
            "population_covered": 50000,
            "coverage_radius_km": 5.0
        }
    ]
}
```

## Algorithm Features

### Cost-Effectiveness Optimization
- Calculates `coverage_increase / cost` for each candidate
- Prioritizes facilities with highest cost-efficiency
- Ensures maximum population coverage per budget unit

### Budget Management
- Tracks remaining budget throughout iterations
- Stops when budget < minimum facility cost
- Reports total budget used vs allocated

### Geographic Accuracy
- Uses Haversine formula for distance calculations
- Considers Earth's curvature for accurate measurements
- Handles geographic coordinates properly

### Clustering Strategy
- Uses K-Means clustering for candidate generation
- Adapts cluster count based on population density
- Balances computational efficiency with accuracy

## Performance Considerations

### Time Complexity
- **Population Analysis**: O(n) where n = population points
- **Clustering**: O(k * n * i) where k = clusters, i = iterations
- **Greedy Algorithm**: O(m * f * c) where m = candidates, f = facility types, c = coverage calculations

### Space Complexity
- **Population Storage**: O(n)
- **Candidate Storage**: O(k)
- **Coverage Tracking**: O(n)

## Customization Options

### Facility Costs
```python
simulation_service.set_facility_costs({
    'Puskesmas': 2500000000,  # 2.5 Billion IDR
    'Pustu': 600000000,        # 600 Million IDR
    'Klinik': 1000000000       # 1 Billion IDR
})
```

### Coverage Radius
```python
simulation_service.set_coverage_radius({
    'Puskesmas': 6000,  # 6km
    'Pustu': 4000,      # 4km
    'Klinik': 2000      # 2km
})
```

## Error Handling

### Validation Checks
- Budget must be > 0
- Regency must exist in database
- Population points must be available
- Facility costs must be > 0
- Coverage radius must be > 0

### Edge Cases
- **No Underserved Population**: Returns empty result with 100% coverage
- **Insufficient Budget**: Returns empty result with 0% coverage
- **No Population Data**: Raises validation error

## Testing

### Mock Data
Use `regency_id: "mock"` for testing without database:
```json
{
    "regency_id": "mock",
    "budget": 5000000000
}
```

### Expected Mock Results
- 2 recommended facilities
- 85.5% coverage percentage
- 4.5 billion IDR budget used
- 75,000 population covered

## Dependencies

### Required Packages
```
scikit-learn>=1.0.0
numpy>=1.20.0
```

### Database Requirements
- `population_points` table with geometry
- `health_facilities` table with geometry
- `subdistricts` table with geometry
- PostGIS extension enabled

## Best Practices

### Budget Planning
- Start with realistic budget estimates
- Consider facility maintenance costs
- Account for operational expenses

### Coverage Optimization
- Balance coverage radius with population density
- Consider transportation infrastructure
- Account for geographic barriers

### Performance Tuning
- Adjust cluster count based on population size
- Monitor algorithm execution time
- Cache frequently accessed data

## Future Enhancements

### Algorithm Improvements
- Multi-objective optimization
- Genetic algorithm implementation
- Machine learning-based predictions

### Additional Factors
- Transportation accessibility
- Infrastructure constraints
- Environmental considerations
- Political boundaries 