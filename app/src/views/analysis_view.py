from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from app.src.schemas.analysis_schema import (
    HeatmapData,
    PriorityScoreData,
    SubDistrictDetails
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
    
    This endpoint calculates health access scores based on the proportion of the
    population living outside a defined service radius of the nearest health facility.
    The data can be used to generate a heatmap visualization showing areas with
    poor health access.
    """
    try:
        # Validate that the regency exists
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
    Get equity prioritization score data for a specific regency.
    
    This endpoint returns a ranked list of sub-districts based on a composite score
    that considers three factors:
    - Gap Factor: Measures the gap in health service access
    - Efficiency Factor: Evaluates the efficiency of current health infrastructure
    - Vulnerability Factor: Assesses the vulnerability of the population
    
    The results help prioritize areas for health infrastructure investment.
    """
    try:
        # Validate that the regency exists
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

@analysis_router.get(
    "/subdistrict-details",
    response_model=SubDistrictDetails,
    summary="Get Sub-district Details",
    description="Retrieve detailed statistics for a specific sub-district including population, area, poverty rate, existing facilities, and calculated scores."
)
async def get_subdistrict_details(
    subdistrict_id: str = Query(..., description="ID of the sub-district for detailed analysis"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> SubDistrictDetails:
    """
    Get detailed statistics for a specific sub-district.
    
    This endpoint provides comprehensive information about a sub-district including:
    - Population and demographic data
    - Geographic information (area, population density)
    - Socioeconomic indicators (poverty rate)
    - Existing health facilities
    - Calculated priority scores
    
    This data is useful when users click on a specific sub-district on the map
    or in the priority list to get detailed information.
    """
    try:
        # Validate that the sub-district exists
        subdistrict = await analysis_service.get_subdistrict_by_id(subdistrict_id)
        if not subdistrict:
            raise NotFoundException(f"Sub-district with ID {subdistrict_id} not found")
        
        details = await analysis_service.get_subdistrict_details(subdistrict_id)
        return details
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sub-district details: {str(e)}"
        ) 