# API Endpoints Documentation

## Authentication Endpoints

### Login

**Endpoint**: `POST /api/v1/auth/login`

**Description**: Authenticate user and get access token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

## Region Endpoints

### Get All Provinces

**Endpoint**: `GET /api/v1/regions/provinces`

**Description**: Get all provinces in Indonesia.

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "DKI Jakarta",
    "code": "31"
  }
]
```

### Get Regencies by Province

**Endpoint**: `GET /api/v1/regions/provinces/{province_id}/regencies`

**Description**: Get all regencies within a specific province.

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Jakarta Selatan",
    "code": "31.74"
  }
]
```

### Get Subdistricts by Regency

**Endpoint**: `GET /api/v1/regions/regencies/{regency_id}/subdistricts`

**Description**: Get all subdistricts within a specific regency.

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "name": "Kecamatan Kebayoran Baru",
    "code": "31.74.01"
  }
]
```

### Get Health Facilities by Regency

**Endpoint**: `GET /api/v1/regions/regencies/{regency_id}/facilities`

**Description**: Get all health facilities within a specific regency.

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "name": "Puskesmas Kebayoran Baru",
    "type": "Puskesmas",
    "latitude": -6.2088,
    "longitude": 106.8456,
    "subdistrict_id": "550e8400-e29b-41d4-a716-446655440003",
    "subdistrict_name": "Kecamatan Kebayoran Baru"
  }
]
```

## Analysis Endpoints

### Get Priority Scores

**Endpoint**: `GET /api/v1/analysis/priority-scores?regency_id={id}&radius={km}&gap_weight={0-1}&efficiency_weight={0-1}&vulnerability_weight={0-1}`

**Description**: Get priority scores for subdistricts within a regency based on gap, efficiency, and vulnerability factors.

**Parameters**:
- `regency_id` (required): UUID of the regency
- `radius` (optional): Coverage radius in kilometers (default: 5)
- `gap_weight` (optional): Weight for gap factor (default: 0.4)
- `efficiency_weight` (optional): Weight for efficiency factor (default: 0.3)
- `vulnerability_weight` (optional): Weight for vulnerability factor (default: 0.3)

**Response**:
```json
[
  {
    "subdistrict_id": "550e8400-e29b-41d4-a716-446655440003",
    "subdistrict_name": "Kecamatan Kebayoran Baru",
    "gap_factor": 0.75,
    "efficiency_factor": 0.85,
    "vulnerability_factor": 0.60,
    "composite_score": 0.73,
    "rank": 1
  }
]
```

### Generate Heatmap Data

**Endpoint**: `GET /api/v1/analysis/heatmap?regency_id={id}&grid_size={km}&search_radius={km}`

**Description**: Generate heatmap data showing population density and healthcare access patterns.

**Parameters**:
- `regency_id` (required): UUID of the regency
- `grid_size` (optional): Size of grid cells in kilometers (default: 2)
- `search_radius` (optional): Search radius for population density calculation (default: 4)

**Response**:
```json
{
  "total_population": 150000,
  "population_outside_radius": 45000,
  "heatmap_points": [
    {
      "latitude": -6.2088,
      "longitude": 106.8456,
      "population_density": 0.75,
      "access_score": 0.45,
      "distance_to_facility": 2.3
    }
  ]
}
```

### Get Analysis Summary

**Endpoint**: `GET /api/v1/analysis/summary?regency_id={id}`

**Description**: Get a comprehensive summary of healthcare access metrics for a regency.

**Parameters**:
- `regency_id` (required): UUID of the regency

**Response**:
```json
{
  "regency_name": "Jakarta Selatan",
  "summary_metrics": {
    "coverage_percentage": 75.5,
    "average_distance_km": 3.2,
    "average_travel_time_hours": 0.064
  },
  "facility_overview": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "name": "Puskesmas Kebayoran Baru",
      "type": "Puskesmas",
      "rating": 4.2
    }
  ]
}
```

## Simulation Endpoints

### Run Simulation

**Endpoint**: `POST /api/v1/simulation/run`

**Description**: Run a greedy simulation for healthcare facility placement optimization.

**Request Body**:
```json
{
  "budget": 5000000000,
  "regency_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Response**:
```json
{
  "regency_id": "550e8400-e29b-41d4-a716-446655440002",
  "regency_name": "Jakarta Selatan",
  "total_budget": 5000000000,
  "budget_used": 4500000000,
  "facilities_recommended": 3,
  "total_population_covered": 150000,
  "coverage_percentage": 75.5,
  "automated_reasoning": "The greedy algorithm analyzed Jakarta Selatan and allocated 4,500,000,000 IDR (90.0% of total budget) to recommend 3 facilities, achieving 75.5% population coverage for 150,000 people. The algorithm prioritized cost-effectiveness by recommending 2 Puskesmas and 1 Pustu facilities based on population density and coverage gaps in underserved areas.",
  "optimized_facilities": [
    {
      "latitude": -6.2088,
      "longitude": 106.8456,
      "sub_district_id": "550e8400-e29b-41d4-a716-446655440003",
      "sub_district_name": "Kecamatan Kebayoran Baru",
      "estimated_cost": 2000000000,
      "population_covered": 50000,
      "coverage_radius_km": 5.0,
      "facility_type": "Puskesmas"
    }
  ]
}
```

## Chatbot Endpoints

### Start Chat Session

**Endpoint**: `POST /api/v1/chatbot/start_chat`

**Description**: Start a new chat session with Ceeva chatbot. This endpoint initializes a new chat session and returns an initial greeting along with recent simulation results for context.

**Headers**: 
- `Authorization: Bearer {access_token}` (required)

**Response**:
```json
{
  "bot_response": "Hello! I'm Ceeva, your healthcare facility planning assistant. I can help you analyze healthcare access patterns, interpret simulation results, and provide insights on facility placement optimization. How can I assist you today?",
  "recent_simulations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "regency_id": "550e8400-e29b-41d4-a716-446655440002",
      "regency_name": "Jakarta Selatan",
      "budget": 5000000000,
      "facilities_recommended": 3,
      "total_population_covered": 150000,
      "coverage_percentage": 75.5,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "suggested_actions": [
    {
      "action_type": "explain_simulation",
      "description": "Explain simulation results in detail"
    },
    {
      "action_type": "analyze_budget",
      "description": "Analyze budget allocation and efficiency"
    },
    {
      "action_type": "explain_coverage",
      "description": "Explain coverage patterns and gaps"
    },
    {
      "action_type": "analyze_facilities",
      "description": "Analyze recommended facility locations"
    },
    {
      "action_type": "explain_algorithm",
      "description": "Explain the greedy algorithm's reasoning"
    }
  ]
}
```

### Assist User

**Endpoint**: `POST /api/v1/chatbot/assist`

**Description**: Get intelligent assistance from Ceeva, the healthcare facility planning chatbot. The chatbot can analyze simulation results, provide insights, and suggest relevant actions.

**Headers**: 
- `Authorization: Bearer {access_token}` (required)

**Request Body**:
```json
{
  "user_message": "Can you help me understand the simulation results?",
  "session_context": {
    "last_simulation_result": {
      "regency_name": "Jakarta Selatan",
      "budget_used": 5000000000,
      "facilities_recommended": 3,
      "coverage_percentage": 75.5
    },
    "previous_messages": [
      {
        "role": "user",
        "content": "Hello Ceeva"
      },
      {
        "role": "bot",
        "content": "Hello! How can I help you with healthcare facility planning?"
      }
    ]
  }
}
```

**Response**:
```json
{
  "bot_response": "Based on your simulation results for Jakarta Selatan, I can see that you've allocated 5 billion IDR and achieved 75.5% population coverage with 3 recommended facilities. This is a good coverage rate, but there might be room for optimization. Let me suggest some actions to help you understand the results better.",
  "suggested_actions": [
    {
      "action_type": "explain_simulation",
      "description": "Explain simulation results in detail",
      "parameters": null
    },
    {
      "action_type": "analyze_budget",
      "description": "Analyze budget allocation and efficiency",
      "parameters": null
    },
    {
      "action_type": "explain_coverage",
      "description": "Explain coverage patterns and gaps",
      "parameters": null
    },
    {
      "action_type": "analyze_facilities",
      "description": "Analyze recommended facility locations",
      "parameters": null
    },
    {
      "action_type": "explain_algorithm",
      "description": "Explain the greedy algorithm's reasoning",
      "parameters": null
    }
  ]
}
```

### Get Recent Simulations

**Endpoint**: `GET /api/v1/chatbot/recent-simulations`

**Description**: Get recent simulation results that can be used as context for chatbot conversations.

**Headers**: 
- `Authorization: Bearer {access_token}` (required)

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "regency_id": "550e8400-e29b-41d4-a716-446655440002",
    "regency_name": "Jakarta Selatan",
    "budget": 5000000000,
    "facilities_recommended": 3,
    "total_population_covered": 150000,
    "coverage_percentage": 75.5,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

## Reports Endpoints

### Generate Report

**Endpoint**: `POST /api/v1/reports/generate`

**Description**: Generate comprehensive reports for healthcare facility planning.

**Request Body**:
```json
{
  "report_type": "comprehensive",
  "regency_id": "550e8400-e29b-41d4-a716-446655440002",
  "include_analysis": true,
  "include_simulation": true
}
```

**Response**:
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440005",
  "download_url": "/api/v1/reports/download/550e8400-e29b-41d4-a716-446655440005",
  "generated_at": "2024-01-15T10:30:00"
}
```

## Frontend Integration Examples

### Starting a Chat Session

```javascript
// Start a new chat session
const startChat = async () => {
  try {
    const response = await fetch('/api/v1/chatbot/start_chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    
    // Display initial greeting
    displayMessage('bot', data.bot_response);
    
    // Show recent simulations
    if (data.recent_simulations.length > 0) {
      displayRecentSimulations(data.recent_simulations);
    }
    
    // Show suggested actions
    displaySuggestedActions(data.suggested_actions);
    
  } catch (error) {
    console.error('Error starting chat:', error);
  }
};
```

### Sending a Message to Chatbot

```javascript
// Send a message to the chatbot
const sendMessage = async (message, sessionContext = null) => {
  try {
    const response = await fetch('/api/v1/chatbot/assist', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_message: message,
        session_context: sessionContext
      })
    });
    
    const data = await response.json();
    
    // Display bot response
    displayMessage('bot', data.bot_response);
    
    // Show suggested actions
    displaySuggestedActions(data.suggested_actions);
    
  } catch (error) {
    console.error('Error sending message:', error);
  }
};
```

### Running a Simulation

```javascript
// Run a simulation and automatically store for chatbot context
const runSimulation = async (budget, regencyId) => {
  try {
    const response = await fetch('/api/v1/simulation/run', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        budget: budget,
        regency_id: regencyId
      })
    });
    
    const data = await response.json();
    
    // Display simulation results
    displaySimulationResults(data);
    
    // The simulation result is automatically stored for chatbot context
    // You can now ask the chatbot about this simulation
    
  } catch (error) {
    console.error('Error running simulation:', error);
  }
};
```

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 422 Validation Error
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Authentication

Most endpoints require authentication. Include the access token in the Authorization header:

```
Authorization: Bearer {access_token}
```

The access token is obtained from the login endpoint and should be included in all subsequent requests. 