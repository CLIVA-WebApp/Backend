# Ceeva Chatbot - Healthcare Facility Planning Assistant

## Overview

Ceeva is an intelligent chatbot assistant designed to help users analyze healthcare access patterns and optimize facility placement in Indonesia. The chatbot integrates with the Groq API to provide intelligent responses and suggested actions based on simulation results and user queries.

## Features

- **Intelligent Analysis**: Analyzes healthcare access patterns and simulation results
- **Context-Aware Responses**: Uses previous simulation results for better context
- **Actionable Suggestions**: Provides relevant action suggestions based on user queries
- **Simulation Integration**: Automatically stores simulation results for future reference
- **Real-time Assistance**: Provides immediate help for healthcare planning decisions

## Setup

### 1. Install Dependencies

Add the required dependency to your environment:

```bash
pip install groq
```

Or update your `requirements.txt`:

```
groq
```

### 2. Environment Variables

Set up the Groq API key in your environment:

```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

Or add it to your `.env` file:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Database Migration

Run the database migration to create the simulation_results table:

```bash
cd Backend
alembic upgrade head
```

## API Endpoints

### 1. Assist User

**Endpoint**: `POST /api/v1/chatbot/assist`

Get intelligent assistance from Ceeva.

**Request**:
```json
{
  "user_message": "Can you help me understand the simulation results?",
  "session_context": {
    "last_simulation_result": {
      "regency_name": "Jakarta Selatan",
      "budget_used": 5000000000,
      "facilities_recommended": 3,
      "coverage_percentage": 75.5
    }
  }
}
```

**Response**:
```json
{
  "bot_response": "Based on your simulation results for Jakarta Selatan...",
  "suggested_actions": [
    {
      "action_type": "run_simulation",
      "description": "Run a new simulation with different parameters"
    }
  ]
}
```

### 2. Get Recent Simulations

**Endpoint**: `GET /api/v1/chatbot/recent-simulations`

Get recent simulation results for context.

### 3. Store Simulation Result

**Endpoint**: `POST /api/v1/chatbot/store-simulation`

Store a simulation result for future chatbot context.

## Usage Examples

### Frontend Integration

```javascript
// Get assistance from Ceeva
const response = await fetch('/api/v1/chatbot/assist', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_message: "Can you help me understand the simulation results?",
    session_context: {
      last_simulation_result: simulationResult
    }
  })
});

const chatbotResult = await response.json();
console.log(chatbotResult.bot_response);
console.log(chatbotResult.suggested_actions);
```

### Python Integration

```python
import requests

# Test the chatbot
response = requests.post(
    "http://localhost:8000/api/v1/chatbot/assist",
    json={
        "user_message": "What are the key metrics I should focus on?",
        "session_context": {
            "last_simulation_result": {
                "regency_name": "Jakarta Selatan",
                "coverage_percentage": 75.5
            }
        }
    }
)

result = response.json()
print(result["bot_response"])
```

## Testing

Run the test script to verify the chatbot functionality:

```bash
cd Backend
python test_chatbot.py
```

## Architecture

### Components

1. **ChatbotService** (`app/src/services/chatbot_service.py`)
   - Handles communication with Groq API
   - Manages simulation result storage and retrieval
   - Extracts suggested actions from responses

2. **ChatbotView** (`app/src/views/chatbot_view.py`)
   - Exposes REST API endpoints
   - Handles request validation and response formatting

3. **ChatbotSchema** (`app/src/schemas/chatbot_schema.py`)
   - Defines Pydantic models for request/response validation

4. **SimulationResult Model** (`app/src/models/simulation_result.py`)
   - Database model for storing simulation results
   - Provides context for chatbot conversations

### Data Flow

1. User sends message to `/api/v1/chatbot/assist`
2. ChatbotService retrieves recent simulation results from database
3. Context is built from simulation data and session context
4. Message is sent to Groq API with system prompt and context
5. Response is processed to extract suggested actions
6. Formatted response is returned to user

## Configuration

### Groq API Settings

The chatbot uses the Llama 3.1 8B model by default. You can modify the model in `ChatbotService`:

```python
self.model = "llama3-8b-8192"  # Change to other available models
```

### System Prompt

The system prompt can be customized in `ChatbotService._get_system_prompt()` to change the chatbot's behavior and capabilities.

### Suggested Actions

The action extraction logic can be modified in `ChatbotService._extract_suggested_actions()` to add new action types or change the detection logic.

## Error Handling

The chatbot includes comprehensive error handling:

- **API Errors**: Fallback responses when Groq API is unavailable
- **Database Errors**: Graceful handling of database connection issues
- **Validation Errors**: Proper validation of input data
- **Network Errors**: Timeout and connection error handling

## Security Considerations

- API keys are stored in environment variables
- Input validation prevents injection attacks
- Database queries use parameterized statements
- Error messages don't expose sensitive information

## Performance

- Database queries are optimized with indexes
- Caching can be added for frequently accessed data
- Async operations for better concurrency
- Efficient context building from simulation results

## Troubleshooting

### Common Issues

1. **Groq API Key Not Set**
   ```
   Error: GROQ_API_KEY environment variable not found
   ```
   Solution: Set the GROQ_API_KEY environment variable

2. **Database Migration Failed**
   ```
   Error: Table 'simulation_results' already exists
   ```
   Solution: Check if migration has already been run

3. **Import Error**
   ```
   Error: No module named 'groq'
   ```
   Solution: Install the groq package: `pip install groq`

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Multi-language Support**: Add support for Indonesian language
- **Advanced Context**: Include more detailed simulation analysis
- **Action Execution**: Automatically execute suggested actions
- **Conversation History**: Store and retrieve conversation history
- **Custom Models**: Support for different LLM providers
- **Analytics**: Track chatbot usage and effectiveness

## Support

For issues or questions about the Ceeva chatbot:

1. Check the troubleshooting section above
2. Review the API documentation
3. Run the test script to verify functionality
4. Check server logs for detailed error messages 