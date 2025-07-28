from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CLIVA Health Planning Platform API",
    description="Backend API untuk platform perencanaan kesehatan CLIVA - TIC 2025",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from src.views.auth import router as auth_router
from src.views.puskesmas import router as puskesmas_router

# Include routers
app.include_router(auth_router)
app.include_router(puskesmas_router)

@app.get("/")
async def root():
    return {
        "message": "CLIVA Health Planning Platform API",
        "version": "1.0.0",
        "description": "Platform perencanaan kesehatan berbasis GIS"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "cliva-health-platform",
        "features": [
            "Health Access Heatmaps",
            "Equity Prioritization Score", 
            "What-If Simulator"
        ]
    } 