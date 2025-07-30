import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Git Merge Conflict Resolver API" in response.json()["message"]

def test_api_docs_available(client: TestClient):
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema_available(client: TestClient):
    """Test that OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200 