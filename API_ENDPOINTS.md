# API Endpoints Documentation

This document describes the API endpoints for the Health Access Analysis and Optimization System.

## Authentication

All endpoints require authentication. The system uses cookie-based authentication with JWT tokens.

## Base URL

All endpoints are prefixed with `/api/v1`

## Endpoints

### Regions

#### GET /api/v1/regions/provinces

Retrieve a list of all provinces in Indonesia.

**Purpose**: Foundational endpoint for populating dropdown menus in the frontend, allowing users to begin their analysis by selecting a province.

**Authentication**: Required

**Response**:
```json
{
  "provinces": [
    {
      "id": "32",
      "name": "Jawa Barat",
      "code": "32"
    },
    {
      "id": "31",
      "name": "DKI Jakarta",
      "code": "31"
    }
  ],
  "total": 2
}
```

#### GET /api/v1/regions/regencies?province_id={id}

Retrieve all regencies (Kabupaten/Kota) within a specific province.

**Purpose**: Next step in the user's journey, narrowing down the area of interest.

**Authentication**: Required

**Parameters**:
- `province_id` (required): ID of the province to get regencies for

**Response**:
```json
{
  "regencies": [
    {
      "id": "3201",
      "name": "Kabupaten Bogor",
      "code": "3201",
      "province_id": "32",
      "province_name": "Jawa Barat"
    }
  ],
  "total": 1,
  "province_id": "32"
}
```

#### GET /api/v1/regions/subdistricts?regency_id={id}

Retrieve all sub-districts (Kecamatan) within a specific regency.

**Purpose**: Provides detailed administrative boundaries for analysis and filtering.

**Authentication**: Required

**Parameters**:
- `regency_id` (required): ID of the regency to get sub-districts for

**Response**:
```json
{
  "sub_districts": [
    {
      "id": "320101",
      "name": "Kecamatan Cibinong",
      "code": "320101",
      "regency_id": "3201",
      "regency_name": "Kabupaten Bogor"
    }
  ],
  "total": 2,
  "regency_id": "3201"
}
```

#### GET /api/v1/regions/facilities?regency_id={id}

Retrieve all health facilities within a specific regency.

**Purpose**: Provides the existing healthcare landscape for analysis and visualization.

**Authentication**: Required

**Parameters**:
- `regency_id` (required): ID of the regency to get facilities for

**Response**:
```json
{
  "facilities": [
    {
      "id": "F001",
      "name": "Puskesmas Cibinong",
      "type": "puskesmas",
      "latitude": -6.4815,
      "longitude": 106.8540,
      "regency_id": "3201",
      "regency_name": "Kabupaten Bogor",
      "sub_district_id": "320101",
      "sub_district_name": "Kecamatan Cibinong"
    },
    {
      "id": "F002",
      "name": "RSUD Cibinong",
      "type": "hospital",
      "latitude": -6.4815,
      "longitude": 106.8540,
      "regency_id": "3201",
      "regency_name": "Kabupaten Bogor",
      "sub_district_id": "320101",
      "sub_district_name": "Kecamatan Cibinong"
    }
  ],
  "total": 2,
  "regency_id": "3201"
}
```

### Analysis

#### GET /api/v1/analysis/heatmap?regency_id={id}

Calculate and return data needed to generate the Health Access Heatmap for a chosen regency.

**Purpose**: Core feature endpoint that calculates health access scores based on the proportion of the population living outside a defined service radius of the nearest health facility.

**Authentication**: Required

**Parameters**:
- `regency_id` (required): ID of the regency for heatmap analysis

**Response**:
```json
{
  "regency_id": "3201",
  "regency_name": "Kabupaten Bogor",
  "total_population": 50000,
  "population_outside_radius": 15000,
  "service_radius_km": 5.0,
  "heatmap_points": [
    {
      "latitude": -6.2088,
      "longitude": 106.8456,
      "population_density": 500.0,
      "access_score": 0.8,
      "distance_to_facility": 2.0
    }
  ]
}
```

#### GET /api/v1/analysis/priority-score?regency_id={id}

Deliver the Equity Prioritization Score.

**Purpose**: Returns a ranked list of sub-districts based on the composite score defined in the project brief (Gap Factor, Efficiency Factor, Vulnerability Factor).

**Authentication**: Required

**Parameters**:
- `regency_id` (required): ID of the regency for priority score analysis

**Response**:
```json
{
  "regency_id": "3201",
  "regency_name": "Kabupaten Bogor",
  "total_sub_districts": 5,
  "sub_districts": [
    {
      "sub_district_id": "320101",
      "sub_district_name": "Kecamatan Cibinong",
      "gap_factor": 0.8,
      "efficiency_factor": 0.6,
      "vulnerability_factor": 0.7,
      "composite_score": 0.71,
      "rank": 1
    }
  ]
}
```

#### GET /api/v1/analysis/subdistrict-details?subdistrict_id={id}

Retrieve detailed statistics for a specific sub-district.

**Purpose**: Provides comprehensive information about a sub-district including population, area, poverty rate, existing facilities, and calculated scores.

**Authentication**: Required

**Parameters**:
- `subdistrict_id` (required): ID of the sub-district for detailed analysis

**Response**:
```json
{
  "sub_district_id": "320101",
  "sub_district_name": "Kecamatan Cibinong",
  "regency_id": "3201",
  "regency_name": "Kabupaten Bogor",
  "population": 150000,
  "area_km2": 45.2,
  "population_density": 3318.58,
  "poverty_rate": 12.5,
  "existing_facilities_count": 2,
  "existing_facilities": [
    {
      "name": "Puskesmas Cibinong",
      "type": "Puskesmas",
      "latitude": -6.4815,
      "longitude": 106.8540
    }
  ],
  "gap_factor": 0.75,
  "efficiency_factor": 0.65,
  "vulnerability_factor": 0.80,
  "composite_score": 0.73,
  "rank": 1
}
```

#### GET /api/v1/analysis/summary?regency_id={id}

Get a comprehensive analysis summary for a regency.

**Purpose**: Provides a high-level overview of health access in a regency including coverage metrics, average distances, and facility overview.

**Authentication**: Required

**Parameters**:
- `regency_id` (required): ID of the regency for summary analysis

**Response**:
```json
{
  "regency_name": "Kabupaten Bandung",
  "summary_metrics": {
    "coverage_percentage": 68.5,
    "average_distance_km": 4.7,
    "average_travel_time_hours": 1.2
  },
  "facility_overview": [
    {
      "id": "uuid-facility-1",
      "name": "RS. Borromeus",
      "type": "Hospital",
      "rating": 4.8
    },
    {
      "id": "uuid-facility-2",
      "name": "Klinik Medika",
      "type": "Clinic",
      "rating": 4.5
    }
  ]
}
```

### Simulation

#### POST /api/v1/simulation/run

Execute the "'What-If' Optimization Simulator".

**Purpose**: Most complex endpoint that takes a budget and a regency, runs the optimization algorithm, and returns the most cost-effective locations for new health facilities.

**Authentication**: Required

**Request Body**:
```json
{
  "regency_id": "3201",
  "budget": 10000000,
  "facility_type": "puskesmas",
  "optimization_criteria": [
    "population_coverage",
    "cost_efficiency"
  ]
}
```

**Response**:
```json
{
  "regency_id": "3201",
  "regency_name": "Kabupaten Bogor",
  "total_budget": 10000000,
  "budget_used": 8500000,
  "facilities_recommended": 2,
  "total_population_covered": 25000,
  "coverage_percentage": 50.0,
  "optimized_facilities": [
    {
      "latitude": -6.2088,
      "longitude": 106.8456,
      "sub_district_id": "320101",
      "sub_district_name": "Kecamatan Cibinong",
      "estimated_cost": 4250000,
      "population_covered": 12500,
      "coverage_radius_km": 5.0
    }
  ]
}
```

### Reports

#### POST /api/v1/reports/export

Generate a downloadable report (PDF/CSV) from analysis or simulation results.

**Purpose**: Creates formatted reports for budget proposals and stakeholder presentations.

**Authentication**: Required

**Request Body**:
```json
{
  "report_type": "simulation_results",
  "data": {
    "regency_id": "3201",
    "regency_name": "Kabupaten Bogor",
    "total_budget": 10000000,
    "budget_used": 8500000,
    "facilities_recommended": 2,
    "total_population_covered": 25000,
    "coverage_percentage": 50.0,
    "optimized_facilities": []
  },
  "format": "csv"
}
```

**Response**:
```json
{
  "filename": "simulation_results_20231201_143022.csv",
  "download_url": "/api/v1/reports/download/simulation_results_20231201_143022.csv",
  "file_size_bytes": 2048,
  "generated_at": "2023-12-01T14:30:22"
}
```

**Supported Report Types**:
- `simulation_results`: Results from optimization simulation
- `priority_ranking`: Sub-district priority rankings
- `heatmap_analysis`: Health access heatmap data
- `subdistrict_details`: Detailed sub-district statistics

**Supported Formats**:
- `pdf`: Portable Document Format
- `csv`: Comma-Separated Values

## Error Responses

All endpoints return consistent error responses:

### 401 Unauthorized
```json
{
  "detail": "Authentication required",
  "type": "authentication_error"
}
```

### 404 Not Found
```json
{
  "detail": "Regency with ID 9999 not found",
  "type": "not_found_error"
}
```

### 422 Validation Error
```json
{
  "detail": "Budget must be greater than 0",
  "type": "validation_error"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Database operation failed",
  "type": "database_error"
}
```

## Usage Examples

### Frontend Integration

```javascript
// Get provinces for dropdown
const response = await fetch('/api/v1/regions/provinces', {
  credentials: 'include'
});
const provinces = await response.json();

// Get regencies for selected province
const regenciesResponse = await fetch(`/api/v1/regions/regencies?province_id=${selectedProvinceId}`, {
  credentials: 'include'
});
const regencies = await regenciesResponse.json();

// Get sub-districts for selected regency
const subdistrictsResponse = await fetch(`/api/v1/regions/subdistricts?regency_id=${selectedRegencyId}`, {
  credentials: 'include'
});
const subdistricts = await subdistrictsResponse.json();

// Get facilities for selected regency
const facilitiesResponse = await fetch(`/api/v1/regions/facilities?regency_id=${selectedRegencyId}`, {
  credentials: 'include'
});
const facilities = await facilitiesResponse.json();

// Generate heatmap for selected regency
const heatmapResponse = await fetch(`/api/v1/analysis/heatmap?regency_id=${selectedRegencyId}`, {
  credentials: 'include'
});
const heatmapData = await heatmapResponse.json();

// Get priority scores for selected regency
const priorityResponse = await fetch(`/api/v1/analysis/priority-score?regency_id=${selectedRegencyId}`, {
  credentials: 'include'
});
const priorityData = await priorityResponse.json();

// Get detailed information for a specific sub-district
const detailsResponse = await fetch(`/api/v1/analysis/subdistrict-details?subdistrict_id=${selectedSubdistrictId}`, {
  credentials: 'include'
});
const subdistrictDetails = await detailsResponse.json();

// Run optimization simulation
const simulationResponse = await fetch('/api/v1/simulation/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include',
  body: JSON.stringify({
    regency_id: selectedRegencyId,
    budget: 10000000,
    facility_type: 'puskesmas',
    optimization_criteria: ['population_coverage', 'cost_efficiency']
  })
});
const simulationResult = await simulationResponse.json();

// Export simulation results as CSV
const exportResponse = await fetch('/api/v1/reports/export', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include',
  body: JSON.stringify({
    report_type: 'simulation_results',
    data: simulationResult,
    format: 'csv'
  })
});
const exportResult = await exportResponse.json();
```

## Implementation Notes

- All endpoints use Pydantic models for request/response validation
- Authentication is handled via cookie-based JWT tokens
- Database queries are currently mocked but structured for easy integration with real data
- Error handling is consistent across all endpoints
- The API follows RESTful conventions
- All endpoints are documented with OpenAPI/Swagger at `/docs`
- Report generation creates files in a `reports/` directory
- The API structure is now ready for:
  1. **Frontend Integration**: All endpoints are documented with examples
  2. **Database Integration**: Service layer is structured for easy database integration
  3. **Real Algorithm Implementation**: Placeholder methods are ready for actual optimization algorithms
  4. **Testing**: Basic test structure is in place
  5. **Report Generation**: CSV and PDF report generation is implemented 