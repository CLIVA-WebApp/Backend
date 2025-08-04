# API Endpoints Documentation

## Authentication Endpoints

### POST /api/v1/auth/signup
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "uuid"
}
```

### POST /api/v1/auth/signin
Sign in with existing credentials.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string"
  }
}
```

## Region Endpoints

### GET /api/v1/regions/provinces
Get all provinces in Indonesia.

**Response:**
```json
{
  "provinces": [
    {
      "id": "uuid",
      "name": "string",
      "pum_code": "string",
      "area_km2": 0.0
    }
  ],
  "total": 0
}
```

### GET /api/v1/regions/all-regencies
Get all regencies in Indonesia.

**Response:**
```json
{
  "regencies": [
    {
      "id": "uuid",
      "name": "string",
      "pum_code": "string",
      "province_id": "uuid",
      "province_name": "string",
      "area_km2": 0.0
    }
  ],
  "total": 0
}
```

### GET /api/v1/regions/all-subdistricts
Get all sub-districts in Indonesia.

**Response:**
```json
{
  "sub_districts": [
    {
      "id": "uuid",
      "name": "string",
      "pum_code": "string",
      "regency_id": "uuid",
      "regency_name": "string",
      "population_count": 0,
      "poverty_level": 0.0,
      "area_km2": 0.0
    }
  ],
  "total": 0
}
```

### GET /api/v1/regions/regencies
Get regencies by province ID.

**Query Parameters:**
- `province_id`: UUID or "mock" for testing

**Response:**
```json
{
  "regencies": [
    {
      "id": "uuid",
      "name": "string",
      "pum_code": "string",
      "province_id": "uuid",
      "province_name": "string",
      "area_km2": 0.0
    }
  ],
  "total": 0,
  "province_id": "uuid"
}
```

### GET /api/v1/regions/subdistricts
Get sub-districts by regency ID.

**Query Parameters:**
- `regency_id`: UUID or "mock" for testing

**Response:**
```json
{
  "sub_districts": [
    {
      "id": "uuid",
      "name": "string",
      "pum_code": "string",
      "regency_id": "uuid",
      "regency_name": "string",
      "population_count": 0,
      "poverty_level": 0.0,
      "area_km2": 0.0
    }
  ],
  "total": 0,
  "regency_id": "uuid"
}
```

### GET /api/v1/regions/facilities
Get health facilities by regency ID.

**Query Parameters:**
- `regency_id`: UUID or "mock" for testing

**Response:**
```json
{
  "facilities": [
    {
      "id": "uuid",
      "name": "string",
      "type": "string",
      "latitude": 0.0,
      "longitude": 0.0,
      "regency_id": "uuid",
      "regency_name": "string",
      "subdistrict_id": "uuid",
      "sub_district_name": "string"
    }
  ],
  "total": 0,
  "regency_id": "uuid"
}
```

### GET /api/v1/regions/search-by-bounding-box
Search for administrative regions that intersect with a bounding box.

**Query Parameters:**
- `north_east_lat`: North-east corner latitude (-90 to 90)
- `north_east_lng`: North-east corner longitude (-180 to 180)
- `south_west_lat`: South-west corner latitude (-90 to 90)
- `south_west_lng`: South-west corner longitude (-180 to 180)
- `min_coverage_percentage`: Minimum coverage percentage to include (default: 10.0)

**Example Request:**
```
GET /api/v1/regions/search-by-bounding-box?north_east_lat=6.2&north_east_lng=106.8&south_west_lat=6.1&south_west_lng=106.7&min_coverage_percentage=10.0
```

**Response:**
```json
{
  "primary_region": {
    "type": "regency",
    "id": "uuid",
    "name": "Kabupaten Bogor",
    "coverage_percentage": 85.5,
    "intersection_area_km2": 2547.8,
    "total_area_km2": 2985.43,
    "parent_region_id": "uuid",
    "parent_region_name": "Jawa Barat"
  },
  "intersecting_regions": [
    {
      "type": "regency",
      "id": "uuid",
      "name": "Kabupaten Bogor",
      "coverage_percentage": 85.5,
      "intersection_area_km2": 2547.8,
      "total_area_km2": 2985.43,
      "parent_region_id": "uuid",
      "parent_region_name": "Jawa Barat"
    },
    {
      "type": "province",
      "id": "uuid",
      "name": "Jawa Barat",
      "coverage_percentage": 45.2,
      "intersection_area_km2": 16000.0,
      "total_area_km2": 35377.76,
      "parent_region_id": null,
      "parent_region_name": null
    },
    {
      "type": "subdistrict",
      "id": "uuid",
      "name": "Kecamatan Cibinong",
      "coverage_percentage": 92.3,
      "intersection_area_km2": 41.7,
      "total_area_km2": 45.2,
      "parent_region_id": "uuid",
      "parent_region_name": "Kabupaten Bogor"
    }
  ],
  "bounding_box": {
    "north_east": {
      "lat": 6.2,
      "lng": 106.8
    },
    "south_west": {
      "lat": 6.1,
      "lng": 106.7
    }
  },
  "total_regions_found": 3
}
```

**Use Cases:**
- **Map-based region selection**: Frontend sends map viewport coordinates
- **Automatic region detection**: Identify which regions are visible on the map
- **Multi-region analysis**: Handle border areas where multiple regions intersect
- **Coverage-based filtering**: Only include regions with significant coverage

**Frontend Integration:**
1. Capture map viewport coordinates (4 corners)
2. Send coordinates to this endpoint
3. Use `primary_region` for auto-selection
4. Show coverage percentages in UI
5. Allow user to switch between intersecting regions if needed

## Analysis Endpoints

### POST /api/v1/analysis/priority-scores
Calculate priority scores for healthcare facility placement.

**Request Body:**
```json
{
  "regency_id": "uuid",
  "service_radius_km": 5.0,
  "facility_types": ["puskesmas", "hospital"],
  "weights": {
    "population_coverage": 0.4,
    "poverty_level": 0.3,
    "existing_facility_distance": 0.3
  }
}
```

**Response:**
```json
{
  "regency_id": "uuid",
  "regency_name": "string",
  "service_radius_km": 5.0,
  "subdistricts": [
    {
      "id": "uuid",
      "name": "string",
      "priority_score": 0.85,
      "population_coverage": 0.9,
      "poverty_level": 0.8,
      "existing_facility_distance": 0.85,
      "recommended_facility_count": 2
    }
  ],
  "total_subdistricts": 0,
  "average_priority_score": 0.0
}
```

### GET /api/v1/analysis/heatmap/{regency_id}
Generate heatmap data for a specific regency.

**Path Parameters:**
- `regency_id`: UUID of the regency

**Query Parameters:**
- `service_radius_km`: Service radius in kilometers (default: 5.0)

**Response:**
```json
{
  "regency_id": "uuid",
  "regency_name": "string",
  "service_radius_km": 5.0,
  "heatmap_data": [
    {
      "latitude": 0.0,
      "longitude": 0.0,
      "intensity": 0.85,
      "population_count": 1000,
      "facility_count": 2
    }
  ],
  "total_points": 0
}
```

## Simulation Endpoints

### POST /api/v1/simulation/run
Run a healthcare facility placement simulation.

**Request Body:**
```json
{
  "regency_id": "uuid",
  "facility_types": ["puskesmas", "hospital"],
  "facility_counts": {
    "puskesmas": 5,
    "hospital": 2
  },
  "service_radius_km": 5.0,
  "optimization_criteria": ["population_coverage", "poverty_level"]
}
```

**Response:**
```json
{
  "simulation_id": "uuid",
  "status": "completed",
  "results": {
    "total_population_covered": 500000,
    "coverage_percentage": 85.5,
    "average_distance_to_facility": 2.3,
    "facility_placements": [
      {
        "facility_type": "puskesmas",
        "latitude": 0.0,
        "longitude": 0.0,
        "subdistrict_id": "uuid",
        "population_served": 50000
      }
    ]
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/v1/simulation/results/{simulation_id}
Get simulation results by ID.

**Path Parameters:**
- `simulation_id`: UUID of the simulation

**Response:**
```json
{
  "simulation_id": "uuid",
  "status": "completed",
  "regency_id": "uuid",
  "regency_name": "string",
  "results": {
    "total_population_covered": 500000,
    "coverage_percentage": 85.5,
    "average_distance_to_facility": 2.3,
    "facility_placements": [
      {
        "facility_type": "puskesmas",
        "latitude": 0.0,
        "longitude": 0.0,
        "subdistrict_id": "uuid",
        "population_served": 50000
      }
    ]
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": "Validation error"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
``` 