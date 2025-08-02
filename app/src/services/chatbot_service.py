import os
import json
from typing import List, Dict, Any, Optional
from groq import Groq
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.src.config.database import get_db
from app.src.models.simulation_result import SimulationResult
from app.src.schemas.chatbot_schema import ChatbotResponse, SuggestedAction, SessionContext, StartChatResponse

class ChatbotService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"  # Using Llama 3.1 8B model
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot"""
        return """You are Ceeva, an intelligent healthcare facility planning assistant. You help users analyze healthcare access patterns and optimize facility placement in Indonesia.

Your capabilities include:
- Analyzing healthcare access patterns
- Interpreting simulation results
- Suggesting optimal facility placements
- Explaining healthcare metrics and recommendations
- Providing insights on budget allocation and coverage optimization

Always be helpful, informative, and suggest relevant actions based on the user's queries and available simulation data.

Key metrics you can explain:
- Coverage percentage: Percentage of population with access to healthcare
- Average distance: Average distance to nearest healthcare facility
- Budget utilization: How effectively budget is being used
- Facility recommendations: Optimal locations for new facilities

When suggesting actions, consider:
- Explaining simulation results in detail
- Analyzing specific regions or metrics
- Providing insights on budget allocation
- Exploring different aspects of the simulation

Remember: You cannot run new simulations or generate heatmaps as these are costly operations. Focus on explaining existing data and results."""

    def _get_context_from_simulation(self, db: Session, regency_id: Optional[str] = None) -> str:
        """Get context from recent simulation results"""
        query = db.query(SimulationResult)
        
        if regency_id:
            query = query.filter(SimulationResult.regency_id == regency_id)
        
        recent_results = query.order_by(desc(SimulationResult.created_at)).limit(3).all()
        
        if not recent_results:
            return "No recent simulation results available."
        
        context = "Recent simulation results:\n"
        for result in recent_results:
            context += f"""
- Regency: {result.regency_name}
- Budget used: {result.budget:,.0f} IDR
- Facilities recommended: {result.facilities_recommended}
- Population covered: {result.total_population_covered:,}
- Coverage percentage: {result.coverage_percentage:.1f}%
- Date: {result.created_at.strftime('%Y-%m-%d %H:%M')}
"""
        
        return context

    def _extract_suggested_actions(self, response: str) -> List[SuggestedAction]:
        """Extract suggested actions from the LLM response"""
        actions = []
        
        # Updated action patterns focused on explanation and analysis
        action_patterns = [
            ("explain_simulation", "Explain simulation results in detail"),
            ("analyze_budget", "Analyze budget allocation and efficiency"),
            ("explain_coverage", "Explain coverage patterns and gaps"),
            ("analyze_facilities", "Analyze recommended facility locations"),
            ("explain_algorithm", "Explain the greedy algorithm's reasoning"),
            ("compare_scenarios", "Compare different simulation scenarios"),
            ("explain_metrics", "Explain key healthcare metrics"),
            ("analyze_regions", "Analyze specific regions or subdistricts"),
            ("explain_factors", "Explain gap, efficiency, and vulnerability factors"),
            ("suggest_improvements", "Suggest improvements based on results")
        ]
        
        response_lower = response.lower()
        
        for action_type, description in action_patterns:
            if any(keyword in response_lower for keyword in [action_type.replace("_", " "), description.lower()]):
                actions.append(SuggestedAction(
                    action_type=action_type,
                    description=description
                ))
        
        # Add default actions if none found
        if not actions:
            actions = [
                SuggestedAction(
                    action_type="explain_simulation",
                    description="Explain simulation results in detail"
                ),
                SuggestedAction(
                    action_type="analyze_budget",
                    description="Analyze budget allocation and efficiency"
                ),
                SuggestedAction(
                    action_type="explain_coverage",
                    description="Explain coverage patterns and gaps"
                )
            ]
        
        return actions

    async def start_chat(self) -> StartChatResponse:
        """Start a new chat session and return initial greeting with recent simulations"""
        try:
            # Get database session
            db = next(get_db())
            
            # Get recent simulations
            recent_simulations = await self.get_recent_simulations(limit=5)
            
            # Generate initial greeting
            greeting = "Hello! I'm Ceeva, your healthcare facility planning assistant. I can help you analyze healthcare access patterns, interpret simulation results, and provide insights on facility placement optimization. How can I assist you today?"
            
            # Generate suggested actions focused on explanation and analysis
            suggested_actions = [
                SuggestedAction(
                    action_type="explain_simulation",
                    description="Explain simulation results in detail"
                ),
                SuggestedAction(
                    action_type="analyze_budget",
                    description="Analyze budget allocation and efficiency"
                ),
                SuggestedAction(
                    action_type="explain_coverage",
                    description="Explain coverage patterns and gaps"
                ),
                SuggestedAction(
                    action_type="analyze_facilities",
                    description="Analyze recommended facility locations"
                ),
                SuggestedAction(
                    action_type="explain_algorithm",
                    description="Explain the greedy algorithm's reasoning"
                )
            ]
            
            return StartChatResponse(
                bot_response=greeting,
                recent_simulations=recent_simulations,
                suggested_actions=suggested_actions
            )
            
        except Exception as e:
            # Fallback response in case of errors
            return StartChatResponse(
                bot_response="Hello! I'm Ceeva, your healthcare facility planning assistant. I'm experiencing some technical difficulties, but I'm here to help!",
                recent_simulations=[],
                suggested_actions=[
                    SuggestedAction(
                        action_type="explain_simulation",
                        description="Explain simulation results in detail"
                    )
                ]
            )

    async def get_response(self, user_message: str, session_context: Optional[SessionContext] = None) -> ChatbotResponse:
        """Get a response from the chatbot"""
        try:
            # Get database session
            db = next(get_db())
            
            # Build context
            context = self._get_context_from_simulation(db)
            
            # Add session context if available
            if session_context:
                if session_context.last_simulation_result:
                    context += f"\nLast simulation context: {json.dumps(session_context.last_simulation_result, indent=2)}"
                
                # Add previous messages for chatroom context
                if session_context.previous_messages:
                    context += "\n\nPrevious conversation:\n"
                    for msg in session_context.previous_messages[-5:]:  # Last 5 messages
                        role = msg.get('role', 'user')
                        content = msg.get('content', '')
                        context += f"{role.capitalize()}: {content}\n"
            
            # Build the prompt
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Context: {context}\n\nUser message: {user_message}"}
            ]
            
            # Get response from Groq
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            bot_response = completion.choices[0].message.content
            
            # Extract suggested actions
            suggested_actions = self._extract_suggested_actions(bot_response)
            
            return ChatbotResponse(
                bot_response=bot_response,
                suggested_actions=suggested_actions
            )
            
        except Exception as e:
            # Fallback response in case of API errors
            return ChatbotResponse(
                bot_response=f"I apologize, but I'm experiencing some technical difficulties. Please try again later. Error: {str(e)}",
                suggested_actions=[
                    SuggestedAction(
                        action_type="explain_simulation",
                        description="Explain simulation results in detail"
                    )
                ]
            )

    async def store_simulation_result(self, simulation_result: Dict[str, Any], regency_id: str, regency_name: str) -> str:
        """Store a simulation result for future context"""
        try:
            db = next(get_db())
            
            # Create simulation result record
            simulation_record = SimulationResult.from_simulation_result(
                simulation_result, regency_id, regency_name
            )
            
            db.add(simulation_record)
            db.commit()
            db.refresh(simulation_record)
            
            return str(simulation_record.id)
            
        except Exception as e:
            print(f"Error storing simulation result: {e}")
            return None

    async def get_recent_simulations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent simulation results for context"""
        try:
            db = next(get_db())
            
            recent_results = db.query(SimulationResult).order_by(
                desc(SimulationResult.created_at)
            ).limit(limit).all()
            
            return [result.to_dict() for result in recent_results]
            
        except Exception as e:
            print(f"Error getting recent simulations: {e}")
            return [] 