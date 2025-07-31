from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from app.src.schemas.analysis_schema import (
    HeatmapData,
    PriorityScoreData
)
from app.src.schemas.user_schema import UserSchema
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.services.analysis_service import AnalysisService
from app.src.utils.exceptions import NotFoundException

# Create router with prefix and tags
analysis_router = APIRouter(prefix="/analysis", tags=["Analysis"])

# Initialize service
analysis_service = AnalysisService()

@analysis_router.get(
    "/heatmap",
    response_model=HeatmapData,
    summary="Get Health Access Heatmap",
    description="Calculate and return data needed to generate the Health Access Heatmap for a chosen regency. The calculation is based on the proportion of the population living outside a defined service radius of the nearest health facility."
)
async def get_heatmap(
    regency_id: str = Query(..., description="ID of the regency for heatmap analysis"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> HeatmapData:
    """
    Get health access heatmap data for a specific regency.
    
    This endpoint calculates and returns the data needed to generate a "Health Access Heatmap"
    for the chosen regency. The calculation is based on the proportion of the population
    living outside a defined service radius of the nearest health facility.
    
    The heatmap visualization helps identify areas with poor health facility access,
    enabling targeted interventions to improve healthcare accessibility.
    
    Args:
        regency_id: The unique identifier of the regency
    """
    try:
        # Validate regency exists
        regency = await analysis_service.get_regency_by_id(regency_id)
        if not regency:
            raise NotFoundException(f"Regency with ID {regency_id} not found")
        
        heatmap_data = await analysis_service.generate_heatmap_data(regency_id)
        return heatmap_data
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate heatmap data: {str(e)}"
        )

@analysis_router.get(
    "/priority-score",
    response_model=PriorityScoreData,
    summary="Get Equity Prioritization Score",
    description="Deliver the Equity Prioritization Score. This endpoint returns a ranked list of sub-districts based on the composite score defined in the project brief (Gap Factor, Efficiency Factor, Vulnerability Factor)."
)
async def get_priority_score(
    regency_id: str = Query(..., description="ID of the regency for priority score analysis"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> PriorityScoreData:
    """
    Get equity prioritization score for a specific regency.
    
    This endpoint delivers the "Equity Prioritization Score" by returning a ranked
    list of sub-districts based on a composite score that considers:
    
    - Gap Factor: Measures the gap in health service access
    - Efficiency Factor: Evaluates the efficiency of current health infrastructure
    - Vulnerability Factor: Assesses the vulnerability of the population
    
    The composite score helps prioritize areas that need the most attention
    for health infrastructure development and improvement.
    
    Args:
        regency_id: The unique identifier of the regency
    """
    try:
        # Validate regency exists
        regency = await analysis_service.get_regency_by_id(regency_id)
        if not regency:
            raise NotFoundException(f"Regency with ID {regency_id} not found")
        
        priority_data = await analysis_service.generate_priority_score_data(regency_id)
        return priority_data
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate priority score data: {str(e)}"
        ) 