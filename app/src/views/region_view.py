from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from app.src.schemas.region_schema import (
    ProvinceListResponse,
    RegencyListResponse
)
from app.src.schemas.user_schema import UserSchema
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.services.region_service import RegionService
from app.src.utils.exceptions import NotFoundException

# Create router with prefix and tags
region_router = APIRouter(prefix="/regions", tags=["Regions"])

# Initialize service
region_service = RegionService()

@region_router.get(
    "/provinces",
    response_model=ProvinceListResponse,
    summary="Get All Provinces",
    description="Retrieve a list of all provinces in Indonesia. This endpoint provides foundational data for the frontend dropdown selection."
)
async def get_provinces(
    current_user: UserSchema = Depends(get_current_user_required)
) -> ProvinceListResponse:
    """
    Get all provinces in Indonesia.
    
    This endpoint returns a comprehensive list of all provinces, typically used
    to populate dropdown menus in the frontend interface. Users can select a
    province to begin their analysis journey.
    """
    try:
        provinces = await region_service.get_all_provinces()
        return ProvinceListResponse(
            provinces=provinces,
            total=len(provinces)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve provinces: {str(e)}"
        )

@region_router.get(
    "/regencies",
    response_model=RegencyListResponse,
    summary="Get Regencies by Province",
    description="Retrieve all regencies (Kabupaten/Kota) within a specific province. This is the next step in the user's journey, narrowing down the area of interest."
)
async def get_regencies(
    province_id: str = Query(..., description="ID of the province to get regencies for"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> RegencyListResponse:
    """
    Get all regencies within a specific province.
    
    This endpoint returns all regencies (Kabupaten/Kota) that belong to the
    specified province. This is typically called after a user selects a province
    to narrow down their area of interest for analysis.
    
    Args:
        province_id: The unique identifier of the province
    """
    try:
        # Validate province exists
        province = await region_service.get_province_by_id(province_id)
        if not province:
            raise NotFoundException(f"Province with ID {province_id} not found")
        
        regencies = await region_service.get_regencies_by_province(province_id)
        return RegencyListResponse(
            regencies=regencies,
            total=len(regencies),
            province_id=province_id
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve regencies: {str(e)}"
        ) 