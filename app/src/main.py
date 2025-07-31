from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.src.config.settings import settings
from app.src.views.auth_view import auth_router
from app.src.views.region_view import region_router
from app.src.views.analysis_view import analysis_router
from app.src.views.simulation_view import simulation_router
from app.src.utils.exceptions import (
    AuthenticationException, 
    DatabaseException, 
    ValidationException, 
    NotFoundException
)

# Create FastAPI application
app = FastAPI(
    title="Google OAuth with Supabase API",
    description="FastAPI application with Google OAuth authentication using Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(region_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(simulation_router, prefix="/api/v1")

# Global exception handlers
@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc), "type": "authentication_error"}
    )

@app.exception_handler(DatabaseException)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed", "type": "database_error"}
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "type": "validation_error"}
    )

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "type": "not_found_error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Google OAuth API"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Google OAuth with Supabase API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development"
    )