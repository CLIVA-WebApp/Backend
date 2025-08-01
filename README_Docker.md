# Docker Setup for Health Access Analysis Backend

This document explains how to run the FastAPI backend application using Docker and Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- Environment variables configured (see `.env` file)

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure your variables:

```bash
cp env.example .env
```

Edit `.env` file with your actual values:

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

# App URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 2. Production Deployment

Build and run the production stack:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### 3. Development Setup

For development with hot reload and additional tools:

```bash
# Build and start development stack
docker-compose -f docker-compose.dev.yaml up -d

# View logs
docker-compose -f docker-compose.dev.yaml logs -f backend

# Stop development services
docker-compose -f docker-compose.dev.yaml down
```

## Services

### Production Stack (`docker-compose.yaml`)

- **backend**: FastAPI application (port 8000)
- **postgres**: PostgreSQL with PostGIS extension (port 5432)
- **redis**: Redis cache (port 6379)

### Development Stack (`docker-compose.dev.yaml`)

- **backend**: FastAPI application with hot reload (port 8000)
- **postgres**: PostgreSQL with PostGIS extension (port 5432)
- **redis**: Redis cache (port 6379)
- **pgadmin**: Database management interface (port 5050)

## Access Points

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **pgAdmin** (dev only): http://localhost:5050
  - Email: admin@healthaccess.com
  - Password: admin

## Database Management

### Connect to PostgreSQL

```bash
# Connect to database container
docker exec -it health-access-db psql -U postgres -d health_access

# Or connect from host
psql -h localhost -p 5432 -U postgres -d health_access
```

### Run Migrations

```bash
# Run migrations in container
docker exec -it health-access-backend alembic upgrade head

# Or run from host
docker-compose exec backend alembic upgrade head
```

## Useful Commands

### Build and Deploy

```bash
# Build images
docker-compose build

# Build specific service
docker-compose build backend

# Force rebuild
docker-compose build --no-cache
```

### Container Management

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec backend python -c "print('Hello from container')"

# Access container shell
docker-compose exec backend bash
```

### Data Management

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres health_access > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres health_access < backup.sql

# View volume data
docker volume ls
docker volume inspect health-access_postgres_data
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove all related images
docker-compose down --rmi all

# Clean up unused resources
docker system prune -a
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8000
   
   # Kill the process or change port in docker-compose.yaml
   ```

2. **Permission issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Database connection issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Test connection
   docker-compose exec backend python -c "from app.src.config.database import engine; print(engine.connect())"
   ```

4. **Environment variables not loaded**
   ```bash
   # Check environment in container
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

## Production Considerations

1. **Security**
   - Use strong passwords and secrets
   - Enable HTTPS in production
   - Configure proper CORS settings
   - Use secrets management

2. **Performance**
   - Configure proper resource limits
   - Use multi-stage builds for smaller images
   - Implement caching strategies

3. **Monitoring**
   - Add logging configuration
   - Set up health checks
   - Monitor resource usage

4. **Backup**
   - Regular database backups
   - Volume backups
   - Configuration backups

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_USER` | Supabase database user | Yes |
| `SUPABASE_PASSWORD` | Supabase database password | Yes |
| `SUPABASE_HOST` | Supabase database host | Yes |
| `SUPABASE_PORT` | Supabase database port | Yes |
| `SUPABASE_DBNAME` | Supabase database name | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon key | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service key | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `FRONTEND_URL` | Frontend application URL | No |
| `BACKEND_URL` | Backend application URL | No |
| `ALLOWED_ORIGINS` | CORS allowed origins | No | 