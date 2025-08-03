from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.schemas.user_schema import UserSchema

from app.src.services.simulation_service import SimulationService
from app.src.services.chatbot_service import ChatbotService
from app.src.schemas.simulation_schema import SimulationRequest, SimulationResponse, LegacySimulationResponse, GeographicLevel
from app.src.utils.exceptions import ValidationException
from app.src.models.regency import Regency
from app.src.models.province import Province
from app.src.config.database import get_db

# Create router
simulation_router = APIRouter(prefix="/simulation", tags=["Simulation"])

# Initialize services
simulation_service = SimulationService()
chatbot_service = ChatbotService()

@simulation_router.post("/run", response_model=SimulationResponse)
async def run_simulation(simulation_request: SimulationRequest, current_user: UserSchema = Depends(get_current_user_required)):
    """
    Run a simulation for healthcare facility placement optimization.
    
    This endpoint runs a greedy algorithm to optimize healthcare facility placement
    within specified areas, considering budget constraints and selected facility types.
    
    Args:
        simulation_request: SimulationRequest containing geographic_level, area_ids, budget, and facility_types
        current_user: Authenticated user (from access token)
        
    Returns:
        SimulationResponse with simulation summary and recommendations
    """
    try:
        # Validate input
        if simulation_request.budget <= 0:
            raise ValidationException("Budget must be greater than 0")
        
        if not simulation_request.area_ids:
            raise ValidationException("At least one area_id must be provided")
        
        if not simulation_request.facility_types:
            raise ValidationException("At least one facility_type must be provided")
        
        # Run simulation
        simulation_result = simulation_service.run_simulation(
            geographic_level=simulation_request.geographic_level,
            area_ids=simulation_request.area_ids,
            budget=simulation_request.budget,
            facility_types=simulation_request.facility_types
        )
        
        # Store simulation result for chatbot context
        try:
            # Convert simulation result to dict for storage
            simulation_data = {
                "user_id": str(current_user.id),  # Add user tracking
                "geographic_level": simulation_request.geographic_level.value,
                "area_ids": [str(area_id) for area_id in simulation_request.area_ids],
                "budget": simulation_request.budget,
                "facility_types": [ft.value for ft in simulation_request.facility_types],
                "simulation_summary": {
                    "initial_coverage": simulation_result.simulation_summary.initial_coverage,
                    "projected_coverage": simulation_result.simulation_summary.projected_coverage,
                    "coverage_increase_percent": simulation_result.simulation_summary.coverage_increase_percent,
                    "total_cost": simulation_result.simulation_summary.total_cost,
                    "budget_remaining": simulation_result.simulation_summary.budget_remaining
                },
                "recommendations": [
                    {
                        "type": rec.type.value,
                        "subdistrict_id": str(rec.subdistrict_id),
                        "location_name": rec.location_name,
                        "coordinates": {
                            "lat": rec.coordinates.lat,
                            "lon": rec.coordinates.lon
                        },
                        "estimated_cost": rec.estimated_cost
                    }
                    for rec in simulation_result.recommendations
                ],
                "automated_reasoning": simulation_result.automated_reasoning  # Add automated reasoning
            }
            
            # Get area name for storage (using first area)
            db = next(get_db())
            area_name = "Unknown"
            
            if simulation_request.geographic_level == GeographicLevel.SUBDISTRICT:
                subdistrict = db.query(simulation_service.get_subdistrict_by_id(simulation_request.area_ids[0])).first()
                area_name = subdistrict.name if subdistrict else "Unknown"
            elif simulation_request.geographic_level == GeographicLevel.REGENCY:
                regency = db.query(Regency).filter(Regency.id == simulation_request.area_ids[0]).first()
                area_name = regency.name if regency else "Unknown"
            elif simulation_request.geographic_level == GeographicLevel.PROVINCE:
                province = db.query(Province).filter(Province.id == simulation_request.area_ids[0]).first()
                area_name = province.name if province else "Unknown"
            
            await chatbot_service.store_simulation_result(
                simulation_result=simulation_data,
                regency_id=str(simulation_request.area_ids[0]),  # Use first area as regency_id for storage
                regency_name=area_name,
                user_id=str(current_user.id)  # Add user_id parameter
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

# Legacy endpoint for backward compatibility
@simulation_router.post("/run-legacy", response_model=LegacySimulationResponse)
async def run_legacy_simulation(
    budget: float,
    regency_id: str,
    current_user: UserSchema = Depends(get_current_user_required)
):
    """
    Legacy simulation endpoint for backward compatibility.
    
    This endpoint runs a greedy algorithm to optimize healthcare facility placement
    within a given regency, considering budget constraints and population coverage.
    
    Args:
        budget: Total budget available for facility construction
        regency_id: ID of the regency to analyze
        current_user: Authenticated user (from access token)
        
    Returns:
        LegacySimulationResponse with optimized facility recommendations and impact summary
    """
    try:
        # Validate input
        if budget <= 0:
            raise ValidationException("Budget must be greater than 0")
        
        # Run legacy simulation
        simulation_result = simulation_service.run_greedy_simulation(
            budget=budget,
            regency_id=regency_id
        )
        
        # Store simulation result for chatbot context
        try:
            # Convert simulation result to dict for storage
            simulation_data = {
                "user_id": str(current_user.id),  # Add user tracking
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
                        "subdistrict_id": str(facility.subdistrict_id),
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
                regency_name=simulation_result.regency_name,
                user_id=str(current_user.id)  # Add user_id parameter
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