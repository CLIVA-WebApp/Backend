from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Union
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
from uuid import UUID

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
    province_id: Union[UUID, str] = Query(..., description="ID of the province to get regencies for (use 'mock' for testing)"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> RegencyListResponse:
    """
    Get all regencies within a specific province.
    
    This endpoint returns all regencies (Kabupaten/Kota) for a given province,
    allowing users to narrow down their area of interest for analysis.
    
    For development testing, use province_id="mock" to get mock data.
    """
    try:
        # Convert string to UUID if needed
        if isinstance(province_id, str) and province_id != "mock":
            try:
                province_id = UUID(province_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid UUID format"
                )
        
        # Validate that the province exists (skip for mock)
        if province_id != "mock":
            province = await region_service.get_province_by_id(province_id)
            if not province:
                raise NotFoundException(f"Province with ID {province_id} not found")
        
        regencies = await region_service.get_regencies_by_province(province_id)
        return RegencyListResponse(
            regencies=regencies,
            total=len(regencies),
            province_id=province_id if isinstance(province_id, UUID) else UUID("550e8400-e29b-41d4-a716-446655440001")
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
    regency_id: Union[UUID, str] = Query(..., description="ID of the regency to get sub-districts for (use 'mock' for testing)"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> SubDistrictListResponse:
    """
    Get all sub-districts within a specific regency.
    
    This endpoint returns all sub-districts (Kecamatan) for a given regency,
    providing detailed administrative boundaries for analysis and visualization.
    
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
        
        subdistricts = await region_service.get_subdistricts_by_regency(regency_id)
        return SubDistrictListResponse(
            sub_districts=subdistricts,
            total=len(subdistricts),
            regency_id=regency_id if isinstance(regency_id, UUID) else UUID("550e8400-e29b-41d4-a716-446655440002")
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
    regency_id: Union[UUID, str] = Query(..., description="ID of the regency to get facilities for (use 'mock' for testing)"),
    current_user: UserSchema = Depends(get_current_user_required)
) -> FacilityListResponse:
    """
    Get all health facilities within a specific regency.
    
    This endpoint returns all health facilities (Puskesmas, hospitals, clinics, etc.)
    for a given regency, providing the existing healthcare landscape for analysis
    and visualization.
    
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
        
        facilities = await region_service.get_facilities_by_regency(regency_id)
        return FacilityListResponse(
            facilities=facilities,
            total=len(facilities),
            regency_id=regency_id if isinstance(regency_id, UUID) else UUID("550e8400-e29b-41d4-a716-446655440002")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve facilities: {str(e)}"
        ) 