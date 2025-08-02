from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.schemas.user_schema import UserSchema

from app.src.services.simulation_service import SimulationService
from app.src.services.chatbot_service import ChatbotService
from app.src.schemas.simulation_schema import SimulationRequest, SimulationResponse
from app.src.utils.exceptions import ValidationException

# Create router
simulation_router = APIRouter(prefix="/simulation", tags=["Simulation"])

# Initialize services
simulation_service = SimulationService()
chatbot_service = ChatbotService()

@simulation_router.post("/run", response_model=SimulationResponse)
async def run_simulation(simulation_request: SimulationRequest, current_user: UserSchema = Depends(get_current_user_required)):
    """
    Run a greedy simulation for healthcare facility placement optimization.
    
    This endpoint runs a greedy algorithm to optimize healthcare facility placement
    within a given regency, considering budget constraints and population coverage.
    
    Args:
        simulation_request: SimulationRequest containing budget and regency_id
        current_user: Authenticated user (from access token)
        
    Returns:
        SimulationResponse with optimized facility recommendations and impact summary
    """
    try:
        # Validate input
        if simulation_request.budget <= 0:
            raise ValidationException("Budget must be greater than 0")
        
        # Run simulation
        simulation_result = simulation_service.run_greedy_simulation(
            budget=simulation_request.budget,
            regency_id=simulation_request.regency_id
        )
        
        # Store simulation result for chatbot context (only for real simulations, not mock)
        if str(simulation_request.regency_id) != "550e8400-e29b-41d4-a716-446655440002":  # Not mock
            try:
                # Convert simulation result to dict for storage
                simulation_data = {
                    "regency_id": str(simulation_result.regency_id),
                    "regency_name": simulation_result.regency_name,
                    "total_budget": simulation_result.total_budget,
                    "budget_used": simulation_result.budget_used,
                    "facilities_recommended": simulation_result.facilities_recommended,
                    "total_population_covered": simulation_result.total_population_covered,
                    "coverage_percentage": simulation_result.coverage_percentage,
                    "automated_reasoning": simulation_result.automated_reasoning,
                    "optimized_facilities": [
                        {
                            "latitude": facility.latitude,
                            "longitude": facility.longitude,
                            "sub_district_id": str(facility.sub_district_id),
                            "sub_district_name": facility.sub_district_name,
                            "estimated_cost": facility.estimated_cost,
                            "population_covered": facility.population_covered,
                            "coverage_radius_km": facility.coverage_radius_km,
                            "facility_type": facility.facility_type.value
                        }
                        for facility in simulation_result.optimized_facilities
                    ]
                }
                
                await chatbot_service.store_simulation_result(
                    simulation_result=simulation_data,
                    regency_id=str(simulation_result.regency_id),
                    regency_name=simulation_result.regency_name
                )
            except Exception as e:
                # Log error but don't fail the simulation
                print(f"Failed to store simulation result for chatbot: {e}")
        
        return simulation_result
        
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}") 