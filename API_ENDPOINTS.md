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
      "sub_district_name": "Kecamatan 1",
      "gap_factor": 0.8,
      "efficiency_factor": 0.6,
      "vulnerability_factor": 0.7,
      "composite_score": 0.71,
      "rank": 1
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
      "sub_district_name": "Kecamatan 1",
      "estimated_cost": 4250000,
      "population_covered": 12500,
      "coverage_radius_km": 5.0
    }
  ]
}
```

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

// Generate heatmap for selected regency
const heatmapResponse = await fetch(`/api/v1/analysis/heatmap?regency_id=${selectedRegencyId}`, {
  credentials: 'include'
});
const heatmapData = await heatmapResponse.json();

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
```

## Implementation Notes

- All endpoints use Pydantic models for request/response validation
- Authentication is handled via cookie-based JWT tokens
- Database queries are currently mocked but structured for easy integration with real data
- Error handling is consistent across all endpoints
- The API follows RESTful conventions
- All endpoints are documented with OpenAPI/Swagger at `/docs` 