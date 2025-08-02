from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class SessionContext(BaseModel):
    last_simulation_result: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Last simulation result for context"
    )
    previous_messages: Optional[List[Dict[str, str]]] = Field(
        default=[],
        description="Previous user and bot messages for chatroom context"
    )
    
    class Config:
        from_attributes = True

class ChatbotRequest(BaseModel):
    user_message: str = Field(..., description="User's message to the chatbot")
    session_context: Optional[SessionContext] = Field(
        default=None,
        description="Optional session context including previous messages and simulation results"
    )
    
    class Config:
        from_attributes = True

class SuggestedAction(BaseModel):
    action_type: str = Field(..., description="Type of suggested action")
    description: str = Field(..., description="Description of the action")
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parameters for the action"
    )
    
    class Config:
        from_attributes = True

class ChatbotResponse(BaseModel):
    bot_response: str = Field(..., description="Chatbot's response to the user")
    suggested_actions: List[SuggestedAction] = Field(
        default=[],
        description="List of suggested actions for the user"
    )
    
    class Config:
        from_attributes = True

class StartChatResponse(BaseModel):
    bot_response: str = Field(..., description="Initial chatbot greeting")
    recent_simulations: List[Dict[str, Any]] = Field(
        default=[],
        description="Recent simulation results for context"
    )
    suggested_actions: List[SuggestedAction] = Field(
        default=[],
        description="List of suggested actions for the user"
    )
    
    class Config:
        from_attributes = True

class SimulationResult(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the simulation result")
    regency_id: UUID = Field(..., description="ID of the regency")
    regency_name: str = Field(..., description="Name of the regency")
    budget: float = Field(..., description="Budget used in the simulation")
    facilities_recommended: int = Field(..., description="Number of facilities recommended")
    total_population_covered: int = Field(..., description="Total population covered")
    coverage_percentage: float = Field(..., description="Percentage of population covered")
    created_at: datetime = Field(..., description="When the simulation was run")
    
    class Config:
        from_attributes = True 