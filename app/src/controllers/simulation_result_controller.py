from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.src.config.database import SessionLocal
from app.src.models.simulation_result import SimulationResult
from app.src.utils.exceptions import DatabaseException
import json
import logging

logger = logging.getLogger(__name__)

class SimulationResultController:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def _get_db_session(self) -> Session:
        """Get a fresh database session."""
        return self.db
    
    async def get_simulation_context_for_user(self, user_id: str) -> str:
        """Get context from recent simulation results for the user"""
        try:
            def execute_query(db):
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
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error getting simulation context: {e}")
            raise DatabaseException(f"Error getting simulation context: {str(e)}")
    
    async def get_recent_simulations_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent simulation results for a specific user"""
        try:
            def execute_query(db):
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
            
            return execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error getting recent simulations: {e}")
            raise DatabaseException(f"Error getting recent simulations: {str(e)}")
    
    async def store_simulation_result(self, simulation_result: Dict[str, Any], regency_id: str, regency_name: str, user_id: str) -> None:
        """Store simulation result for chatbot context"""
        try:
            def execute_query(db):
                # Create new simulation result record
                simulation_record = SimulationResult(
                    regency_id=regency_id,
                    regency_name=regency_name,
                    user_id=user_id,
                    budget=simulation_result.get('budget', 0),
                    facilities_recommended=len(simulation_result.get('recommendations', [])),
                    total_population_covered=0,  # Would need to calculate this
                    coverage_percentage=simulation_result.get('simulation_summary', {}).get('projected_coverage', 0),
                    automated_reasoning=simulation_result.get('automated_reasoning', ''),
                    simulation_data=json.dumps(simulation_result),
                    created_at=datetime.utcnow()
                )
                
                db.add(simulation_record)
                db.commit()
                
                logger.info(f"Stored simulation result for user {user_id}")
            
            execute_query(self._get_db_session())
        except Exception as e:
            logger.error(f"Error storing simulation result: {e}")
            self._get_db_session().rollback()
            raise DatabaseException(f"Error storing simulation result: {str(e)}")

# Create controller instance
simulation_result_controller = SimulationResultController()
