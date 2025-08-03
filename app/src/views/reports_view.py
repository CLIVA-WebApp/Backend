from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.src.schemas.analysis_schema import (
    ReportExportRequest,
    ReportExportResponse
)
from app.src.schemas.user_schema import UserSchema
from app.src.middleware.auth_middleware import get_current_user_required
from app.src.services.report_service import ReportService
from app.src.utils.exceptions import ValidationException

reports_router = APIRouter(prefix="/reports", tags=["Reports"])
report_service = ReportService()

@reports_router.post(
    "/export",
    response_model=ReportExportResponse,
    summary="Export Report",
    description="Generate a downloadable report (PDF/CSV) from analysis or simulation results. This endpoint takes the JSON output from a simulation or analysis endpoint and creates a formatted report."
)
async def export_report(
    request: ReportExportRequest,
    current_user: UserSchema = Depends(get_current_user_required)
) -> ReportExportResponse:
    """
    Generate a downloadable report from analysis or simulation results.
    
    This endpoint takes the results from analysis or simulation endpoints and
    generates a formatted report in either PDF or CSV format. This is crucial
    for users who need to justify budget proposals and share findings with
    stakeholders.
    
    Supported report types:
    - simulation_results: Results from optimization simulation
    - priority_ranking: Sub-district priority rankings
    - heatmap_analysis: Health access heatmap data
    - subdistrict_details: Detailed sub-district statistics
    
    Supported formats:
    - pdf: Portable Document Format
    - csv: Comma-Separated Values
    """
    try:
        # Validate the request data structure based on report type
        await _validate_report_data(request)
        
        # Generate the report
        report_response = await report_service.generate_report(request)
        return report_response
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

async def _validate_report_data(request: ReportExportRequest) -> None:
    """
    Validate the report data structure based on the report type.
    """
    data = request.data
    
    if request.report_type == "simulation_results":
        required_fields = [
            "regency_id", "regency_name", "total_budget", "budget_used",
            "facilities_recommended", "total_population_covered", "coverage_percentage",
            "optimized_facilities"
        ]
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required field '{field}' for simulation results report")
        
        # Validate optimized_facilities is a list
        if not isinstance(data.get("optimized_facilities"), list):
            raise ValidationException("optimized_facilities must be a list")
    
    elif request.report_type == "priority_ranking":
        required_fields = [
            "regency_id", "regency_name", "total_sub_districts", "sub_districts"
        ]
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required field '{field}' for priority ranking report")
        
        # Validate sub_districts is a list
        if not isinstance(data.get("sub_districts"), list):
            raise ValidationException("sub_districts must be a list")
    
    elif request.report_type == "heatmap_analysis":
        required_fields = [
            "regency_id", "regency_name", "total_population",
            "population_outside_radius", "service_radius_km", "heatmap_points"
        ]
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required field '{field}' for heatmap analysis report")
        
        # Validate heatmap_points is a list
        if not isinstance(data.get("heatmap_points"), list):
            raise ValidationException("heatmap_points must be a list")
    
    elif request.report_type == "subdistrict_details":
        required_fields = [
            "subdistrict_id", "sub_district_name", "regency_id", "regency_name",
            "population", "area_km2", "population_density", "poverty_rate",
            "existing_facilities_count", "existing_facilities", "gap_factor",
            "efficiency_factor", "vulnerability_factor", "composite_score", "rank"
        ]
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required field '{field}' for sub-district details report")
        
        # Validate existing_facilities is a list
        if not isinstance(data.get("existing_facilities"), list):
            raise ValidationException("existing_facilities must be a list")
    
    else:
        raise ValidationException(f"Unsupported report type: {request.report_type}") 