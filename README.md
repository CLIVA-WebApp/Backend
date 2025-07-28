# CLIVA Health Planning Platform Backend

Backend API untuk platform perencanaan kesehatan CLIVA - TIC 2025

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL via Supabase
- **Architecture**: MVCS (Model-View-Controller-Service)
- **Authentication**: JWT
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

## Struktur Direktori

```
Backend/
├── src/
│   ├── config/          # Database & settings
│   ├── models/          # SQLAlchemy models (User, Puskesmas, Population)
│   ├── views/           # FastAPI routes/endpoints
│   ├── controllers/     # Business logic
│   ├── services/        # External services, utilities
│   ├── middleware/      # Authentication, validation
│   ├── schemas/         # Pydantic models
│   └── utils/           # Helper functions
├── alembic/             # Database migrations
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
├── setup.py            # Setup script
├── start.py            # Development server
└── README.md           # This file
```

## Fitur Utama

- **Health Access Heatmaps** - Visualisasi peta akses kesehatan
- **Equity Prioritization Score** - Algoritma prioritas kecamatan
- **"What-If" Simulator** - Simulasi Puskesmas virtual
- **Data Management** - CRUD untuk data Puskesmas & populasi

## Roadmap Implementasi

### Phase 1: Setup & Foundation (Week 1)
1. **Environment Setup**
   - Install dependencies: `pip install -r requirements.txt`
   - Setup virtual environment
   - Configure `.env` file dengan Supabase credentials

2. **Database Setup**
   - Setup Supabase project
   - Configure database connection
   - Run initial migrations dengan Alembic

3. **Basic Authentication**
   - Implement user registration/login
   - JWT token generation/validation
   - Password hashing dengan bcrypt

### Phase 2: Core Features (Week 2)
1. **Git Repository Management**
   - Upload repository files
   - Clone repositories from Git URLs
   - Repository validation

2. **Merge Conflict Detection**
   - Parse Git merge conflicts
   - Extract conflict markers
   - Store conflict data

3. **Conflict Resolution Interface**
   - API endpoints untuk conflict data
   - Conflict visualization
   - Resolution tracking

### Phase 3: Advanced Features (Week 3)
1. **Conflict Resolution Engine**
   - Automatic conflict resolution suggestions
   - Manual resolution interface
   - Conflict resolution history

2. **Real-time Features**
   - WebSocket untuk real-time updates
   - Collaborative conflict resolution
   - Live conflict status

3. **Security & Validation**
   - Input validation
   - File upload security
   - Rate limiting

### Phase 4: Testing & Deployment (Week 4)
1. **Testing**
   - Unit tests untuk semua modules
   - Integration tests
   - API endpoint testing

2. **Documentation**
   - API documentation dengan FastAPI docs
   - Code documentation
   - Deployment guide

3. **Deployment**
   - Docker containerization
   - Production environment setup
   - CI/CD pipeline

## Quick Start

1. **Setup virtual environment**
   ```bash
   cd Backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Supabase project**
   - Buat project di [Supabase](https://supabase.com)
   - Dapatkan database credentials dari Settings > Database
   - Copy connection string

4. **Setup environment variables**
   ```bash
   cp env.example .env
   # Edit .env dengan Supabase credentials Anda
   ```

5. **Initialize Alembic (first time only)**
   ```bash
   alembic init alembic  # Skip if already done
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

6. **Start development server**
   ```bash
   # Option 1: Using start script
   python start.py
   
   # Option 2: Using uvicorn directly
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the application**
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/health
   - API Documentation: http://localhost:8000/docs

## API Endpoints

- `GET /` - Health check
- `GET /health` - API status
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

## Development Guidelines

1. **Code Style**: Use Black for formatting, isort for imports
2. **Type Hints**: Always use type hints
3. **Documentation**: Docstrings for all functions
4. **Testing**: Write tests for new features
5. **Git Flow**: Feature branches, PR reviews

## Next Steps

1. Setup Supabase project dan dapatkan credentials
2. Configure database connection
3. Implement basic authentication
4. Create first API endpoints
5. Setup testing framework