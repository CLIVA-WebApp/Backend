from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.schemas.user_schema import UserSchema

from app.src.services.chatbot_service import ChatbotService
from app.src.schemas.chatbot_schema import (
    ChatbotRequest, ChatbotResponse, SessionContext, 
    SuggestedAction, StartChatResponse
)

# Create router
chatbot_router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# Initialize service
chatbot_service = ChatbotService()

@chatbot_router.post("/start_chat", response_model=StartChatResponse)
async def start_chat(current_user: UserSchema = Depends(get_current_user_required)):
    """
    Start a new chat session with the Ceeva chatbot.
    
    This endpoint initializes a chat session and returns recent simulation results
    for the authenticated user, along with an initial greeting and suggested actions.
    
    Args:
        current_user: Authenticated user (from access token)
        
    Returns:
        StartChatResponse with greeting, recent simulations, and suggested actions
    """
    try:
        return await chatbot_service.start_chat(user_id=str(current_user.id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start chat: {str(e)}")

@chatbot_router.post("/assist", response_model=ChatbotResponse)
async def assist_user(
    request: ChatbotRequest, 
    current_user: UserSchema = Depends(get_current_user_required)
):
    """
    Get assistance from the Ceeva chatbot.
    
    This endpoint processes user messages and returns intelligent responses
    based on simulation data and conversation context.
    
    Args:
        request: ChatbotRequest containing user message and session context
        current_user: Authenticated user (from access token)
        
    Returns:
        ChatbotResponse with bot response and suggested actions
    """
    try:
        return await chatbot_service.get_response(
            user_message=request.user_message,
            session_context=request.session_context,
            user_id=str(current_user.id)  # Pass user_id to get user-specific context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chatbot response: {str(e)}") 