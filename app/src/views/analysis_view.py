from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Union
from app.src.schemas.analysis_schema import (
    HeatmapData,
    PriorityScoreData,
    SubDistrictDetails,
    AnalysisSummary
)
from app.src.schemas.user_schema import UserSchema
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.services.analysis_service import AnalysisService
from app.src.utils.exceptions import NotFoundException
from app.src.utils.cache_manager import CacheManager
from uuid import UUID

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
    regency_id: Union[UUID, str] = Query(..., description="ID of the regency for heatmap analysis (use 'mock' for testing)"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> HeatmapData:
    """
    Get health access heatmap data for a specific regency.
    
    This endpoint calculates health access scores based on the proportion of the
    population living outside a defined service radius of the nearest health facility.
    The data can be used to generate a heatmap visualization showing areas with
    poor health access.
    
    For development testing, use regency_id="mock" to get mock data.
    """
    try:
        # Convert string to UUID if needed
        if isinstance(regency_id, str) and regency_id != "mock":
            try:
                regency_id = UUID(regency_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid UUID format"
                )
        
        # Validate that the regency exists (skip for mock)
        if regency_id != "mock":
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
    regency_id: Union[UUID, str] = Query(..., description="ID of the regency for priority score analysis (use 'mock' for testing)"),
    service_radius_km: float = Query(5.0, ge=0.1, le=50.0, description="Service radius in kilometers (0.1-50.0)"),
    gap_weight: float = Query(0.4, ge=0.0, le=1.0, description="Weight for gap factor (0.0-1.0)"),
    efficiency_weight: float = Query(0.3, ge=0.0, le=1.0, description="Weight for efficiency factor (0.0-1.0)"),
    vulnerability_weight: float = Query(0.3, ge=0.0, le=1.0, description="Weight for vulnerability factor (0.0-1.0)"),
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
    
    For development testing, use regency_id="mock" to get mock data.
    """
    try:
        # Convert string to UUID if needed
        if isinstance(regency_id, str) and regency_id != "mock":
            try:
                regency_id = UUID(regency_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid UUID format"
                )
        
        # Validate that the regency exists (skip for mock)
        if regency_id != "mock":
            regency = await analysis_service.get_regency_by_id(regency_id)
            if not regency:
                raise NotFoundException(f"Regency with ID {regency_id} not found")
        
        # Validate that weights sum to 1.0
        total_weight = gap_weight + efficiency_weight + vulnerability_weight
        if abs(total_weight - 1.0) > 0.001:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Weights must sum to 1.0. Current sum: {total_weight}"
            )
        
        # For mock requests, use the existing method
        if regency_id == "mock":
            priority_data = await analysis_service.generate_priority_score_data(regency_id)
        else:
            # Use the new calculate_priority_scores method with custom parameters
            sub_district_scores = await analysis_service.calculate_priority_scores(
                regency_id=regency_id,
                service_radius_km=service_radius_km,
                gap_weight=gap_weight,
                efficiency_weight=efficiency_weight,
                vulnerability_weight=vulnerability_weight
            )
            
            # Get regency info
            regency = await analysis_service.get_regency_by_id(regency_id)
            
            priority_data = PriorityScoreData(
                regency_id=regency_id,
                regency_name=regency.name,
                total_sub_districts=len(sub_district_scores),
                sub_districts=sub_district_scores
            )
        
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
    subdistrict_id: Union[UUID, str] = Query(..., description="ID of the sub-district for detailed analysis (use 'mock' for testing)"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> SubDistrictDetails:
    """
    Get detailed statistics for a specific sub-district.
    
    This endpoint returns comprehensive information about a sub-district including:
    - Basic information (name, parent regency)
    - Demographic data (population, area, poverty rate)
    - Health infrastructure (existing facilities)
    - Calculated scores (health access, priority scores)
    
    This data is useful for detailed analysis and decision-making.
    
    For development testing, use subdistrict_id="mock" to get mock data.
    """
    try:
        # Convert string to UUID if needed
        if isinstance(subdistrict_id, str) and subdistrict_id != "mock":
            try:
                subdistrict_id = UUID(subdistrict_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid UUID format"
                )
        
        # Validate that the sub-district exists (skip for mock)
        if subdistrict_id != "mock":
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

@analysis_router.get(
    "/summary",
    response_model=AnalysisSummary,
    summary="Get Analysis Summary",
    description="Get a comprehensive analysis summary for a regency including coverage metrics, average distances, and facility overview."
)
async def get_analysis_summary(
    regency_id: Union[UUID, str] = Query(..., description="ID of the regency for summary analysis (use 'mock' for testing)"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> AnalysisSummary:
    """
    Get a comprehensive analysis summary for a specific regency.
    
    This endpoint provides a high-level overview of health access in a regency including:
    - Coverage percentage: Proportion of population covered by health facilities
    - Average distance: Average distance to the nearest health facility
    - Average travel time: Estimated travel time to the nearest facility
    - Facility overview: List of health facilities with ratings
    
    This summary is useful for quick assessment and decision-making.
    
    For development testing, use regency_id="mock" to get mock data.
    """
    try:
        # Convert string to UUID if needed
        if isinstance(regency_id, str) and regency_id != "mock":
            try:
                regency_id = UUID(regency_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid UUID format"
                )
        
        # Validate that the regency exists (skip for mock)
        if regency_id != "mock":
            regency = await analysis_service.get_regency_by_id(regency_id)
            if not regency:
                raise NotFoundException(f"Regency with ID {regency_id} not found")
        
        summary = await analysis_service.generate_analysis_summary(regency_id)
        return summary
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analysis summary: {str(e)}"
        )

@analysis_router.delete(
    "/cache/clear",
    summary="Clear Analysis Cache",
    description="Clear all analysis cache or cache for a specific regency."
)
async def clear_analysis_cache(
    regency_id: Optional[str] = Query(None, description="Optional regency ID to clear cache for specific regency"),
    current_user: UserSchema = Depends(get_current_user_required)
):
    """
    Clear analysis cache.
    
    This endpoint allows clearing the cache for expensive analysis operations.
    If regency_id is provided, only cache for that regency is cleared.
    Otherwise, all analysis cache is cleared.
    """
    try:
        await CacheManager.clear_analysis_cache(regency_id)
        return {
            "message": "Cache cleared successfully",
            "regency_id": regency_id,
            "cleared_all": regency_id is None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

@analysis_router.get(
    "/cache/stats",
    summary="Get Cache Statistics",
    description="Get cache statistics and status."
)
async def get_cache_stats(
    current_user: UserSchema = Depends(get_current_user_required)
):
    """
    Get cache statistics.
    
    This endpoint returns information about the cache status and performance.
    """
    try:
        stats = await CacheManager.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        ) 