from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.src.config.settings import settings
from app.src.config.cache import init_cache
from app.src.views.auth_view import auth_router
from app.src.views.region_view import region_router
from app.src.views.analysis_view import analysis_router
from app.src.views.simulation_view import simulation_router
from app.src.views.reports_view import reports_router
from app.src.views.chatbot_view import chatbot_router
from app.src.utils.exceptions import (
    AuthenticationException, 
    DatabaseException, 
    ValidationException,
    NotFoundException
)

# Create FastAPI app instance
app = FastAPI(
    title="Health Access Analysis and Optimization API",
    description="API for analyzing health access patterns and optimizing facility placement in Indonesia",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(region_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(simulation_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(chatbot_router, prefix="/api/v1")

# Initialize cache on startup
@app.on_event("startup")
async def startup_event():
    await init_cache()

# Global exception handlers
@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc), "type": "authentication_error"}
    )

@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": "database_error"}
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "type": "validation_error"}
    )

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "type": "not_found_error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Health Access Analysis and Optimization API",
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