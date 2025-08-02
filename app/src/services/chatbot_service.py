import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import groq

from app.src.config.database import get_db
from app.src.models.simulation_result import SimulationResult
from app.src.schemas.chatbot_schema import (
    ChatbotRequest, ChatbotResponse, SessionContext, 
    SuggestedAction, StartChatResponse
)

class ChatbotService:
    def __init__(self):
        self.client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
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

    def _get_context_from_simulation(self, user_id: str) -> str:
        """Get context from recent simulation results for the user"""
        try:
            db = next(get_db())
            
            # Get recent simulation results for the specific user
            query = text("""
                SELECT simulation_data, created_at 
                FROM simulation_results 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            results = db.execute(query, {"user_id": user_id}).fetchall()
            
            if not results:
                return "No recent simulation data available."
            
            context = "Recent simulation results:\n"
            for result in results:
                data = json.loads(result.simulation_data)
                context += f"- {data.get('regency_name', 'Unknown area')}: "
                if 'simulation_summary' in data:
                    summary = data['simulation_summary']
                    context += f"Budget: {summary.get('total_cost', 0):,.0f} IDR, "
                    context += f"Coverage: {summary.get('projected_coverage', 0):.1f}%, "
                    context += f"Facilities: {len(data.get('recommendations', []))}\n"
                    # Add automated reasoning if available
                    if data.get('automated_reasoning'):
                        context += f"  Reasoning: {data['automated_reasoning']}\n"
                else:
                    context += f"Budget: {data.get('budget_used', 0):,.0f} IDR, "
                    context += f"Coverage: {data.get('coverage_percentage', 0):.1f}%, "
                    context += f"Facilities: {data.get('facilities_recommended', 0)}\n"
                    # Add automated reasoning if available
                    if data.get('automated_reasoning'):
                        context += f"  Reasoning: {data['automated_reasoning']}\n"
            
            return context
        except Exception as e:
            print(f"Error getting simulation context: {e}")
            return "Unable to retrieve recent simulation data."

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

    async def get_response(self, user_message: str, session_context: Optional[SessionContext] = None, user_id: str = None) -> ChatbotResponse:
        """Get response from the chatbot"""
        try:
            # Build the prompt
            system_prompt = self._get_system_prompt()
            
            # Add simulation context if user_id is provided
            simulation_context = ""
            if user_id:
                simulation_context = self._get_context_from_simulation(user_id)
            
            # Add session context if available
            session_info = ""
            if session_context and session_context.last_simulation_result:
                session_info = f"\nLast simulation: {session_context.last_simulation_result}\n"
            
            # Add previous messages if available
            previous_messages = ""
            if session_context and session_context.previous_messages:
                previous_messages = "\nPrevious conversation:\n"
                for msg in session_context.previous_messages:
                    role = "Assistant" if msg.get('role') == 'bot' else "User"
                    previous_messages += f"{role}: {msg.get('content', '')}\n"
            
            prompt = f"{system_prompt}\n\n{simulation_context}\n{session_info}\n{previous_messages}\nUser: {user_message}\nAssistant:"
            
            # Get response from Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content.strip()
            
            # Extract suggested actions
            suggested_actions = self._extract_suggested_actions(bot_response)
            
            return ChatbotResponse(
                bot_response=bot_response,
                suggested_actions=suggested_actions
            )
            
        except Exception as e:
            print(f"Error getting chatbot response: {e}")
            return ChatbotResponse(
                bot_response="I apologize, but I'm having trouble processing your request right now. Please try again later.",
                suggested_actions=[
                    SuggestedAction(
                        action_type="explain_simulation",
                        description="Explain simulation results in detail"
                    )
                ]
            )

    async def store_simulation_result(self, simulation_result: Dict[str, Any], regency_id: str, regency_name: str, user_id: str) -> None:
        """Store simulation result for chatbot context"""
        try:
            db = next(get_db())
            
            # Create new simulation result record
            simulation_record = SimulationResult(
                regency_id=regency_id,
                regency_name=regency_name,
                user_id=user_id,  # Add user_id
                budget=simulation_result.get('budget', 0),
                facilities_recommended=len(simulation_result.get('recommendations', [])),
                total_population_covered=0,  # Would need to calculate this
                coverage_percentage=simulation_result.get('simulation_summary', {}).get('projected_coverage', 0),
                automated_reasoning=simulation_result.get('automated_reasoning', ''),  # Add automated reasoning
                simulation_data=json.dumps(simulation_result),
                created_at=datetime.utcnow()
            )
            
            db.add(simulation_record)
            db.commit()
            
            print(f"Stored simulation result for user {user_id}")
            
        except Exception as e:
            print(f"Error storing simulation result: {e}")
            db.rollback()

    async def get_recent_simulations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent simulation results for a specific user"""
        try:
            db = next(get_db())
            
            query = text("""
                SELECT id, regency_id, regency_name, budget, facilities_recommended, 
                       total_population_covered, coverage_percentage, automated_reasoning, created_at
                FROM simulation_results 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            
            results = db.execute(query, {"user_id": user_id}).fetchall()
            
            return [
                {
                    "id": str(result.id),
                    "regency_id": str(result.regency_id),
                    "regency_name": result.regency_name,
                    "budget": result.budget,
                    "facilities_recommended": result.facilities_recommended,
                    "total_population_covered": result.total_population_covered,
                    "coverage_percentage": result.coverage_percentage,
                    "automated_reasoning": result.automated_reasoning,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error getting recent simulations: {e}")
            return []

    async def start_chat(self, user_id: str) -> StartChatResponse:
        """Start a new chat session with recent simulations for context"""
        try:
            # Get recent simulations for the user
            recent_simulations = await self.get_recent_simulations(user_id)
            
            # Generate initial greeting
            greeting = "Hello! I'm Ceeva, your healthcare facility planning assistant. I can help you analyze healthcare access patterns, interpret simulation results, and provide insights on facility placement optimization. How can I assist you today?"
            
            # Generate suggested actions
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
            print(f"Error starting chat: {e}")
            return StartChatResponse(
                bot_response="Hello! I'm Ceeva, your healthcare facility planning assistant. How can I help you today?",
                recent_simulations=[],
                suggested_actions=[
                    SuggestedAction(
                        action_type="explain_simulation",
                        description="Explain simulation results in detail"
                    )
                ]
            ) 