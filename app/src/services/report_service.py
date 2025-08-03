from typing import Dict, Any, Optional
from app.src.schemas.analysis_schema import ReportExportRequest, ReportExportResponse
from app.src.config.database import SessionLocal
from sqlalchemy.orm import Session
import logging
import json
import csv
import io
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.db: Session = SessionLocal()
        self.reports_dir = "reports"
        self._ensure_reports_directory()
    
    def _ensure_reports_directory(self):
        """Ensure the reports directory exists."""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
            logger.info(f"Created reports directory: {self.reports_dir}")
    
    async def generate_report(self, request: ReportExportRequest) -> ReportExportResponse:
        """
        Generate a report based on the request type and data.
        Currently supports CSV format with mock PDF generation.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{request.report_type}_{timestamp}.{request.format}"
            filepath = os.path.join(self.reports_dir, filename)
            
            if request.format == "csv":
                file_size = await self._generate_csv_report(request, filepath)
            elif request.format == "pdf":
                file_size = await self._generate_pdf_report(request, filepath)
            else:
                raise ValueError(f"Unsupported format: {request.format}")
            
            # Generate download URL (in production, this would be a proper file serving endpoint)
            download_url = f"/api/v1/reports/download/{filename}"
            
            response = ReportExportResponse(
                filename=filename,
                download_url=download_url,
                file_size_bytes=file_size,
                generated_at=datetime.now()
            )
            
            logger.info(f"Generated {request.format.upper()} report: {filename} ({file_size} bytes)")
            return response
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise
    
    async def _generate_csv_report(self, request: ReportExportRequest, filepath: str) -> int:
        """
        Generate a CSV report based on the report type.
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if request.report_type == "simulation_results":
                    await self._generate_simulation_csv(request.data, csvfile)
                elif request.report_type == "priority_ranking":
                    await self._generate_priority_csv(request.data, csvfile)
                elif request.report_type == "heatmap_analysis":
                    await self._generate_heatmap_csv(request.data, csvfile)
                elif request.report_type == "subdistrict_details":
                    await self._generate_subdistrict_csv(request.data, csvfile)
                else:
                    raise ValueError(f"Unsupported report type: {request.report_type}")
            
            return os.path.getsize(filepath)
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {str(e)}")
            raise
    
    async def _generate_pdf_report(self, request: ReportExportRequest, filepath: str) -> int:
        """
        Generate a PDF report based on the report type.
        Currently creates a placeholder file.
        """
        try:
            # Mock PDF generation - in production, you would use a library like reportlab
            report_content = f"""
            Report Type: {request.report_type}
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Format: PDF
            
            Data Summary:
            {json.dumps(request.data, indent=2)}
            """
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return os.path.getsize(filepath)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise
    
    async def _generate_simulation_csv(self, data: Dict[str, Any], csvfile) -> None:
        """Generate CSV for simulation results."""
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            "Regency ID", "Regency Name", "Total Budget", "Budget Used",
            "Facilities Recommended", "Total Population Covered", "Coverage Percentage"
        ])
        
        # Write summary row
        writer.writerow([
            data.get("regency_id", ""),
            data.get("regency_name", ""),
            data.get("total_budget", 0),
            data.get("budget_used", 0),
            data.get("facilities_recommended", 0),
            data.get("total_population_covered", 0),
            data.get("coverage_percentage", 0)
        ])
        
        # Write facilities details
        writer.writerow([])  # Empty row
        writer.writerow(["Optimized Facilities Details"])
        writer.writerow([
            "Latitude", "Longitude", "Sub-district ID", "Sub-district Name",
            "Estimated Cost", "Population Covered", "Coverage Radius (km)"
        ])
        
        for facility in data.get("optimized_facilities", []):
            writer.writerow([
                facility.get("latitude", 0),
                facility.get("longitude", 0),
                facility.get("subdistrict_id", ""),
                facility.get("sub_district_name", ""),
                facility.get("estimated_cost", 0),
                facility.get("population_covered", 0),
                facility.get("coverage_radius_km", 0)
            ])
    
    async def _generate_priority_csv(self, data: Dict[str, Any], csvfile) -> None:
        """Generate CSV for priority ranking results."""
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            "Regency ID", "Regency Name", "Total Sub-districts"
        ])
        
        # Write summary row
        writer.writerow([
            data.get("regency_id", ""),
            data.get("regency_name", ""),
            data.get("total_sub_districts", 0)
        ])
        
        # Write sub-district rankings
        writer.writerow([])  # Empty row
        writer.writerow(["Sub-district Rankings"])
        writer.writerow([
            "Rank", "Sub-district ID", "Sub-district Name", "Gap Factor",
            "Efficiency Factor", "Vulnerability Factor", "Composite Score"
        ])
        
        for subdistrict in data.get("sub_districts", []):
            writer.writerow([
                subdistrict.get("rank", 0),
                subdistrict.get("subdistrict_id", ""),
                subdistrict.get("sub_district_name", ""),
                subdistrict.get("gap_factor", 0),
                subdistrict.get("efficiency_factor", 0),
                subdistrict.get("vulnerability_factor", 0),
                subdistrict.get("composite_score", 0)
            ])
    
    async def _generate_heatmap_csv(self, data: Dict[str, Any], csvfile) -> None:
        """Generate CSV for heatmap analysis results."""
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            "Regency ID", "Regency Name", "Total Population",
            "Population Outside Radius", "Service Radius (km)"
        ])
        
        # Write summary row
        writer.writerow([
            data.get("regency_id", ""),
            data.get("regency_name", ""),
            data.get("total_population", 0),
            data.get("population_outside_radius", 0),
            data.get("service_radius_km", 0)
        ])
        
        # Write heatmap points
        writer.writerow([])  # Empty row
        writer.writerow(["Heatmap Points"])
        writer.writerow([
            "Latitude", "Longitude", "Population Density",
            "Access Score", "Distance to Facility (km)"
        ])
        
        for point in data.get("heatmap_points", []):
            writer.writerow([
                point.get("latitude", 0),
                point.get("longitude", 0),
                point.get("population_density", 0),
                point.get("access_score", 0),
                point.get("distance_to_facility", 0)
            ])
    
    async def _generate_subdistrict_csv(self, data: Dict[str, Any], csvfile) -> None:
        """Generate CSV for sub-district details."""
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            "Sub-district ID", "Sub-district Name", "Regency ID", "Regency Name",
            "Population", "Area (km²)", "Population Density", "Poverty Rate (%)",
            "Existing Facilities Count", "Gap Factor", "Efficiency Factor",
            "Vulnerability Factor", "Composite Score", "Rank"
        ])
        
        # Write sub-district details
        writer.writerow([
            data.get("subdistrict_id", ""),
            data.get("sub_district_name", ""),
            data.get("regency_id", ""),
            data.get("regency_name", ""),
            data.get("population", 0),
            data.get("area_km2", 0),
            data.get("population_density", 0),
            data.get("poverty_rate", 0),
            data.get("existing_facilities_count", 0),
            data.get("gap_factor", 0),
            data.get("efficiency_factor", 0),
            data.get("vulnerability_factor", 0),
            data.get("composite_score", 0),
            data.get("rank", 0)
        ])
        
        # Write existing facilities
        writer.writerow([])  # Empty row
        writer.writerow(["Existing Facilities"])
        writer.writerow([
            "Facility ID", "Facility Name", "Type", "Latitude", "Longitude"
        ])
        
        for facility in data.get("existing_facilities", []):
            writer.writerow([
                facility.get("id", ""),
                facility.get("name", ""),
                facility.get("type", ""),
                facility.get("latitude", 0),
                facility.get("longitude", 0)
            ]) 