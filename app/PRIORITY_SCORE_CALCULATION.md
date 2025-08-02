# Priority Score Calculation

This document describes the implementation of the priority score calculation system using PostGIS spatial analysis.

## Overview

The priority score calculation system analyzes sub-districts within a regency to determine which areas have the highest priority for health infrastructure investment. The system uses three main factors:

1. **Gap Factor**: Proportion of population living outside the service radius of health facilities
2. **Efficiency Factor**: Population density (people per km²)
3. **Vulnerability Factor**: Poverty level of the population

## Implementation

### Core Function

The main calculation is performed by the `calculate_priority_scores` function in `AnalysisService`:

```python
def calculate_priority_scores(self, regency_id: Union[UUID, str], 
                            service_radius_km: float = 5.0,
                            gap_weight: float = 0.4,
                            efficiency_weight: float = 0.3,
                            vulnerability_weight: float = 0.3) -> List[SubDistrictScore]
```

### Parameters

- `regency_id`: ID of the regency to analyze
- `service_radius_km`: Service radius in kilometers (default: 5.0)
- `gap_weight`: Weight for gap factor in composite score (default: 0.4)
- `efficiency_weight`: Weight for efficiency factor in composite score (default: 0.3)
- `vulnerability_weight`: Weight for vulnerability factor in composite score (default: 0.3)

### PostGIS Query

The calculation uses a complex PostGIS SQL query that:

1. **Calculates Gap Factor**: Uses `ST_DWithin` to find population points outside the service radius of health facilities
2. **Calculates Efficiency Factor**: Computes population density (population / area)
3. **Calculates Vulnerability Factor**: Uses existing poverty level data
4. **Performs Min-Max Normalization**: Normalizes all factors to 0-1 range
5. **Computes Composite Score**: Applies weighted combination of normalized factors

### API Endpoint

The calculation is exposed through the `/analysis/priority-score` endpoint:

```
GET /analysis/priority-score?regency_id={id}&service_radius_km=5.0&gap_weight=0.4&efficiency_weight=0.3&vulnerability_weight=0.3
```

### Response Format

```json
{
  "regency_id": "uuid",
  "regency_name": "Kabupaten Bogor",
  "total_sub_districts": 25,
  "sub_districts": [
    {
      "sub_district_id": "uuid",
      "sub_district_name": "Kecamatan Cibinong",
      "gap_factor": 0.75,
      "efficiency_factor": 0.65,
      "vulnerability_factor": 0.80,
      "composite_score": 0.73,
      "rank": 1
    }
  ]
}
```

## Database Requirements

The calculation requires the following tables with PostGIS geometry columns:

- `subdistricts`: Contains sub-district boundaries and demographic data
- `health_facilities`: Contains health facility locations as points
- `population_points`: Contains population distribution as points

## Testing

Run the test script to verify the PostGIS functionality:

```bash
cd Backend/app
python test_postgis_query.py
```

## Customization

The system is designed to be easily customizable:

1. **Service Radius**: Adjust `service_radius_km` parameter
2. **Weights**: Modify the three weight parameters to change factor importance
3. **Factors**: The SQL query can be extended to include additional factors

## Error Handling

- Validates that weights sum to 1.0
- Handles missing data gracefully with COALESCE
- Provides fallback to mock data for testing
- Comprehensive error logging

## Performance Considerations

- Uses spatial indexes on geometry columns
- Efficient PostGIS spatial functions
- Single query execution for all calculations
- Results are cached at the service level 