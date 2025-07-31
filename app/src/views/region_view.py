from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from app.src.schemas.region_schema import (
    ProvinceListResponse,
    RegencyListResponse,
    SubDistrictListResponse,
    FacilityListResponse
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
    
    This endpoint returns a list of all provinces that can be used to populate
    dropdown menus in the frontend, allowing users to begin their analysis by
    selecting a province.
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
    
    This endpoint returns all regencies (Kabupaten/Kota) for a given province,
    allowing users to narrow down their area of interest for analysis.
    """
    try:
        # Validate that the province exists
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

@region_router.get(
    "/subdistricts",
    response_model=SubDistrictListResponse,
    summary="Get Sub-districts by Regency",
    description="Retrieve all sub-districts (Kecamatan) within a specific regency. This provides detailed administrative boundaries for analysis."
)
async def get_subdistricts(
    regency_id: str = Query(..., description="ID of the regency to get sub-districts for"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> SubDistrictListResponse:
    """
    Get all sub-districts within a specific regency.
    
    This endpoint returns all sub-districts (Kecamatan) for a given regency,
    providing detailed administrative boundaries that can be used for filtering
    or detailed analysis.
    """
    try:
        # Validate that the regency exists (by checking if it has any sub-districts)
        subdistricts = await region_service.get_subdistricts_by_regency(regency_id)
        
        return SubDistrictListResponse(
            sub_districts=subdistricts,
            total=len(subdistricts),
            regency_id=regency_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sub-districts: {str(e)}"
        )

@region_router.get(
    "/facilities",
    response_model=FacilityListResponse,
    summary="Get Facilities by Regency",
    description="Retrieve all health facilities within a specific regency. This provides the existing healthcare landscape for analysis and visualization."
)
async def get_facilities(
    regency_id: str = Query(..., description="ID of the regency to get facilities for"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> FacilityListResponse:
    """
    Get all health facilities within a specific regency.
    
    This endpoint returns all health facilities (Puskesmas, hospitals, clinics, etc.)
    for a given regency, providing the existing healthcare landscape that is essential
    for heatmap analysis and simulation algorithms.
    """
    try:
        # Validate that the regency exists (by checking if it has any facilities)
        facilities = await region_service.get_facilities_by_regency(regency_id)
        
        return FacilityListResponse(
            facilities=facilities,
            total=len(facilities),
            regency_id=regency_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve facilities: {str(e)}"
        ) 