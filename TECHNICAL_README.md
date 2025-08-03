# CLIVA Technical Documentation

This document contains detailed technical information for developers working on the CLIVA Health Planning Platform.

## Table of Contents

1. [Docker Setup](#docker-setup)
2. [Data Loading Guide](#data-loading-guide)
3. [Chatbot Implementation](#chatbot-implementation)
4. [API Endpoints Reference](#api-endpoints-reference)
5. [Database Schema](#database-schema)
6. [Architecture Details](#architecture-details)
7. [Environment Configuration](#environment-configuration)
8. [Troubleshooting](#troubleshooting)

## Docker Setup

### Prerequisites
- Docker and Docker Compose installed
- Environment variables configured (see `.env` file)

### Environment Variables
```env
# Supabase Configuration
SUPABASE_USER=your-supabase-user
SUPABASE_PASSWORD=your-supabase-password
SUPABASE_HOST=your-project.supabase.co
SUPABASE_PORT=5432
SUPABASE_DBNAME=postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Groq AI API
GROQ_API_KEY=your-groq-api-key

# App URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Quick Start
```bash
# Production
docker-compose up -d

# Development
docker-compose -f docker-compose.dev.yaml up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Services
- **backend**: FastAPI application (port 8000)
- **postgres**: PostgreSQL with PostGIS extension (port 5432)
- **redis**: Redis cache (port 6379)
- **pgadmin**: Database management interface (port 5050, dev only)

### Access Points
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **pgAdmin** (dev only): http://localhost:5050

### Database Management
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Connect to database
docker exec -it health-access-db psql -U postgres -d health_access

# Backup database
docker-compose exec postgres pg_dump -U postgres health_access > backup.sql
```

## Data Loading Guide

### Prerequisites
```bash
pip install geopandas fiona shapely
```

### GDB Data Loading
```bash
cd Backend
python load_gdb_data.py
```

### What Gets Loaded
- **Provinces** (Provinsi) - Top-level administrative units
- **Regencies** (Kabupaten/Kota) - Second-level administrative units
- **Subdistricts** (Kecamatan) - Third-level administrative units
- **Population Points** - Population distribution data
- **Health Facilities** - Puskesmas and other health facilities

### Data Sources
- **Administrative Boundaries**: RBI10K_ADMINISTRASI_DESA_20230928.gdb
- **Population Data**: CSV files from BPS
- **Health Facilities**: Geocoded health center data

### Database Schema
```sql
-- Core tables with PostGIS geometry
CREATE TABLE provinces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    pum_code VARCHAR(10) UNIQUE NOT NULL,
    area_km2 DECIMAL(10,2),
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

CREATE TABLE regencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    pum_code VARCHAR(10) UNIQUE NOT NULL,
    province_id UUID REFERENCES provinces(id),
    area_km2 DECIMAL(10,2),
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

CREATE TABLE subdistricts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    pum_code VARCHAR(10) UNIQUE NOT NULL,
    regency_id UUID REFERENCES regencies(id),
    population_count INTEGER,
    poverty_level DECIMAL(5,2),
    area_km2 DECIMAL(10,2),
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

CREATE TABLE health_facilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    subdistrict_id UUID REFERENCES subdistricts(id),
    geom GEOMETRY(POINT, 4326)
);

CREATE TABLE population_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    population_count INTEGER NOT NULL,
    subdistrict_id UUID REFERENCES subdistricts(id),
    geom GEOMETRY(POINT, 4326)
);

CREATE TABLE simulation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    regency_id UUID NOT NULL,
    regency_name VARCHAR(255) NOT NULL,
    budget DECIMAL(15,2),
    facilities_recommended INTEGER,
    total_population_covered INTEGER,
    coverage_percentage DECIMAL(5,2),
    automated_reasoning TEXT,
    simulation_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Chatbot Implementation

### Overview
Ceeva is an intelligent chatbot assistant that integrates with Groq API to provide healthcare planning assistance.

### Setup
```bash
# Install dependency
pip install groq

# Set environment variable
export GROQ_API_KEY="your_groq_api_key_here"

# Run migration
alembic upgrade head
```

### API Endpoints
- `POST /chatbot/start_chat` - Start new chat session
- `POST /chatbot/assist` - Get AI assistance

### Features
- **Intelligent Analysis**: Analyzes healthcare access patterns
- **Context-Aware Responses**: Uses simulation results for context
- **Actionable Suggestions**: Provides relevant action suggestions
- **Simulation Integration**: Stores results for future reference

### Architecture
1. **ChatbotService** - Handles Groq API communication
2. **ChatbotView** - Exposes REST API endpoints
3. **ChatbotSchema** - Request/response validation
4. **SimulationResult Model** - Database context storage

## API Endpoints Reference

### Authentication
- `POST /auth/login` - Authenticate user
- `POST /auth/register` - Register new user
- `GET /auth/google` - Google OAuth login
- `GET /auth/google/callback` - Google OAuth callback

### Regions
- `GET /regions/provinces` - Get all provinces
- `GET /regions/provinces/{id}/regencies` - Get regencies by province
- `GET /regions/regencies/{id}/subdistricts` - Get subdistricts by regency
- `GET /regions/regencies/{id}/facilities` - Get facilities by regency

### Analysis
- `POST /analysis/heatmap` - Generate heatmap data
- `POST /analysis/priority-scores` - Calculate priority scores

### Simulation
- `POST /simulation/run` - Run "what-if" simulation
- `GET /simulation/results` - Get simulation results

### Chatbot
- `POST /chatbot/start_chat` - Start new chat session
- `POST /chatbot/assist` - Get AI assistance

## Architecture Details

### MVCS Architecture
```
View (HTTP) → Service (Business Logic) → Controller (Data Access) → Database
```

### Layers
1. **Views** - Handle HTTP requests/responses
2. **Services** - Business logic implementation
3. **Controllers** - Database access operations
4. **Models** - SQLAlchemy ORM models
5. **Middleware** - Authentication and validation
6. **Schemas** - Pydantic validation models

### Key Components
- **Authentication**: JWT + Google OAuth
- **Geospatial**: PostGIS for spatial operations
- **AI Integration**: Groq API for chatbot
- **Caching**: Redis for session storage

## Environment Configuration

### Required Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_USER` | Supabase database user | Yes |
| `SUPABASE_PASSWORD` | Supabase database password | Yes |
| `SUPABASE_HOST` | Supabase database host | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon key | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service key | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `GROQ_API_KEY` | Groq AI API key | Yes |

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   netstat -tulpn | grep :8000
   ```

2. **Database connection errors**
   ```bash
   docker-compose logs postgres
   ```

3. **PostGIS extension not enabled**
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

4. **Environment variables not loaded**
   ```bash
   docker-compose exec backend env | grep SUPABASE
   ```

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check container health
docker-compose ps

# Check resource usage
docker stats
```

### Performance Optimization
- Use spatial indexes for geospatial queries
- Implement caching for analysis results
- Use async operations for better concurrency
- Optimize Docker image sizes

### Security Considerations
- Use strong passwords and secrets
- Enable HTTPS in production
- Configure proper CORS settings
- Implement input validation
- Use parameterized queries

---

**For more information, see the main [README.md](./README.md)** 