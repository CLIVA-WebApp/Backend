import pytest
from fastapi.testclient import TestClient
from app.src.main import app

client = TestClient(app)

class TestRegionRoutes:
    """Test cases for region-related endpoints"""
    
    def test_get_provinces_unauthorized(self):
        """Test that provinces endpoint requires authentication"""
        response = client.get("/api/v1/regions/provinces")
        assert response.status_code == 401
    
    def test_get_regencies_unauthorized(self):
        """Test that regencies endpoint requires authentication"""
        response = client.get("/api/v1/regions/regencies?province_id=32")
        assert response.status_code == 401

class TestAnalysisRoutes:
    """Test cases for analysis-related endpoints"""
    
    def test_get_heatmap_unauthorized(self):
        """Test that heatmap endpoint requires authentication"""
        response = client.get("/api/v1/analysis/heatmap?regency_id=3201")
        assert response.status_code == 401
    
    def test_get_priority_score_unauthorized(self):
        """Test that priority score endpoint requires authentication"""
        response = client.get("/api/v1/analysis/priority-score?regency_id=3201")
        assert response.status_code == 401

class TestSimulationRoutes:
    """Test cases for simulation-related endpoints"""
    
    def test_run_simulation_unauthorized(self):
        """Test that simulation endpoint requires authentication"""
        simulation_data = {
            "regency_id": "3201",
            "budget": 10000000,
            "facility_type": "puskesmas",
            "optimization_criteria": ["population_coverage", "cost_efficiency"]
        }
        response = client.post("/api/v1/simulation/run", json=simulation_data)
        assert response.status_code == 401

class TestAPIStructure:
    """Test cases for API structure and documentation"""
    
    def test_api_docs_accessible(self):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_health_check(self):
        """Test that health check endpoint works"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test that root endpoint works"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json() 