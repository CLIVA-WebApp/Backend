from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.schemas.user_schema import UserSchema

from app.src.services.chatbot_service import ChatbotService
from app.src.schemas.chatbot_schema import ChatbotRequest, ChatbotResponse, StartChatResponse, SimulationResult
from app.src.utils.exceptions import ValidationException

# Create router
chatbot_router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# Initialize service
chatbot_service = ChatbotService()

@chatbot_router.post("/start_chat", response_model=StartChatResponse)
async def start_chat(current_user: UserSchema = Depends(get_current_user_required)):
    """
    Start a new chat session with Ceeva chatbot.
    
    This endpoint initializes a new chat session and returns an initial greeting
    along with recent simulation results for context.
    
    Args:
        current_user: Authenticated user (from access token)
        
    Returns:
        StartChatResponse with initial greeting, recent simulations, and suggested actions
    """
    try:
        response = await chatbot_service.start_chat()
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot service error: {str(e)}")

@chatbot_router.post("/assist", response_model=ChatbotResponse)
async def assist_user(request: ChatbotRequest, current_user: UserSchema = Depends(get_current_user_required)):
    """
    Get assistance from Ceeva chatbot.
    
    This endpoint allows users to interact with the Ceeva chatbot for healthcare facility planning assistance.
    The chatbot can provide insights, answer questions, and suggest relevant actions based on simulation results.
    
    Args:
        request: ChatbotRequest containing user message and optional session context
        current_user: Authenticated user (from access token)
        
    Returns:
        ChatbotResponse with bot response and suggested actions
    """
    try:
        # Validate input
        if not request.user_message or request.user_message.strip() == "":
            raise ValidationException("User message cannot be empty")
        
        # Get response from chatbot
        response = await chatbot_service.get_response(
            user_message=request.user_message,
            session_context=request.session_context
        )
        
        return response
        
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot service error: {str(e)}")

@chatbot_router.get("/recent-simulations", response_model=List[SimulationResult])
async def get_recent_simulations(current_user: UserSchema = Depends(get_current_user_required)):
    """
    Get recent simulation results for context.
    
    This endpoint returns recent simulation results that can be used as context
    for the chatbot conversations.
    
    Args:
        current_user: Authenticated user (from access token)
        
    Returns:
        List of recent simulation results
    """
    try:
        recent_simulations = await chatbot_service.get_recent_simulations(limit=10)
        return recent_simulations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recent simulations: {str(e)}") 