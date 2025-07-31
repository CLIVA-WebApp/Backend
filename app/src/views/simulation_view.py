from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.src.schemas.analysis_schema import (
    SimulationRequest,
    SimulationResult
)
from app.src.schemas.user_schema import UserSchema
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.services.simulation_service import SimulationService
from app.src.utils.exceptions import NotFoundException, ValidationException

# Create router with prefix and tags
simulation_router = APIRouter(prefix="/simulation", tags=["Simulation"])

# Initialize service
simulation_service = SimulationService()

@simulation_router.post(
    "/run",
    response_model=SimulationResult,
    summary="Run Optimization Simulation",
    description="Execute the 'What-If' Optimization Simulator. This endpoint takes a budget and a regency, runs the optimization algorithm, and returns the most cost-effective locations for new health facilities."
)
async def run_simulation(
    simulation_request: SimulationRequest,
    current_user: UserSchema = Depends(get_current_user_required)
) -> SimulationResult:
    """
    Run optimization simulation for health facility placement.
    
    This endpoint executes the "'What-If' Optimization Simulator" which is the most
    complex feature of the system. It takes a budget and a regency, runs sophisticated
    optimization algorithms, and returns the most cost-effective locations for new
    health facilities.
    
    The simulation considers multiple factors including:
    - Population distribution and density
    - Existing health facility locations
    - Transportation infrastructure
    - Cost constraints and budget allocation
    - Coverage optimization
    
    The result provides actionable insights for health infrastructure planning
    and resource allocation decisions.
    
    Args:
        simulation_request: Contains regency_id, budget, facility_type, and optimization criteria
    """
    try:
        # Validate regency exists
        regency = await simulation_service.get_regency_by_id(simulation_request.regency_id)
        if not regency:
            raise NotFoundException(f"Regency with ID {simulation_request.regency_id} not found")
        
        # Validate budget constraints
        if simulation_request.budget <= 0:
            raise ValidationException("Budget must be greater than 0")
        
        # Run the optimization simulation
        simulation_result = await simulation_service.run_optimization_simulation(
            regency_id=simulation_request.regency_id,
            budget=simulation_request.budget,
            facility_type=simulation_request.facility_type,
            optimization_criteria=simulation_request.optimization_criteria
        )
        
        return simulation_result
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run simulation: {str(e)}"
        ) 