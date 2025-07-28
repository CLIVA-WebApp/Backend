# CLIVA Health Planning Platform Backend

Backend API untuk platform perencanaan kesehatan CLIVA - TIC 2025

## 🎯 Tujuan Proyek

CLIVA adalah platform web untuk perencanaan kesehatan berbasis GIS yang membantu perencana kesehatan daerah mengatasi kesenjangan distribusi layanan kesehatan di Indonesia.

## 🏗️ Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL via Supabase
- **Architecture**: MVCS (Model-View-Controller-Service)
- **Authentication**: JWT
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

## 📁 Struktur Direktori

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

## 🚀 Fitur Utama

- **Health Access Heatmaps** - Visualisasi peta akses kesehatan
- **Equity Prioritization Score** - Algoritma prioritas kecamatan
- **"What-If" Simulator** - Simulasi Puskesmas virtual
- **Data Management** - CRUD untuk data Puskesmas & populasi

## 📅 Roadmap Implementasi (5 Hari)

### Day 1: Foundation & Authentication ✅
**Target:** Setup database dan sistem autentikasi
- [x] Setup Supabase database
- [x] Create User model (perencana kesehatan)
- [x] Implement authentication (register/login)
- [x] Create basic API endpoints
- [x] Setup CORS untuk frontend

### Day 2: Data Models & CRUD ✅
**Target:** Sistem manajemen data Puskesmas dan populasi
- [x] Create Puskesmas model
- [x] Create Population model
- [x] Implement CRUD operations
- [x] Add data validation

### Day 3: Health Access Heatmaps 🔄
**Target:** Visualisasi peta akses kesehatan
- [ ] Implement geospatial calculations
- [ ] Create distance calculation API
- [ ] Add radius coverage logic
- [ ] Create heatmap data endpoint

### Day 4: Equity Prioritization Score 📋
**Target:** Algoritma prioritas kecamatan
- [ ] Implement scoring algorithm
- [ ] Create priority calculation API
- [ ] Add multiple factor calculations
- [ ] Create ranking system

### Day 5: "What-If" Simulator & Polishing 🎯
**Target:** Simulasi dan finishing touches
- [ ] Implement simulation logic
- [ ] Create virtual Puskesmas API
- [ ] Add impact calculation
- [ ] Create simulation results endpoint

## ⚡ Quick Start

### 1. Setup Environment
```bash
cd Backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Supabase
- Buat project di [Supabase](https://supabase.com)
- Dapatkan database credentials dari Settings > Database
- Copy connection string

### 4. Configure Environment
```bash
cp env.example .env
# Edit .env dengan Supabase credentials Anda
```

### 5. Run Setup Script
```bash
python setup.py
```

### 6. Start Development Server
```bash
python start.py
```

### 7. Access Application
- API: http://localhost:8000
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Puskesmas Management
- `GET /puskesmas/` - Get all Puskesmas
- `POST /puskesmas/` - Create new Puskesmas
- `GET /puskesmas/{id}` - Get Puskesmas by ID
- `PUT /puskesmas/{id}` - Update Puskesmas
- `DELETE /puskesmas/{id}` - Delete Puskesmas

### Health Check
- `GET /` - Root endpoint
- `GET /health` - API status

## 🧪 Testing

```bash
# Run all tests
python run_tests.py

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🛠️ Development Commands

```bash
# Windows
run.bat install    # Install dependencies
run.bat setup      # Setup environment
run.bat test       # Run tests
run.bat run        # Start server
run.bat migrate    # Run migrations

# Linux/Mac
make install       # Install dependencies
make setup         # Setup environment
make test          # Run tests
make run           # Start server
make migrate       # Run migrations
```

## 📊 Database Models

### User
- Perencana kesehatan yang menggunakan sistem
- Authentication dan authorization

### Puskesmas
- Data fasilitas kesehatan
- Lokasi (latitude, longitude)
- Kapasitas dan radius coverage

### Population
- Data populasi per kecamatan
- Indikator kemiskinan dan kepadatan
- Koordinat pusat kecamatan

## 🎯 Next Steps

1. **Day 3**: Implement geospatial calculations untuk heatmaps
2. **Day 4**: Build equity prioritization algorithm
3. **Day 5**: Create "What-If" simulation engine
4. **Frontend**: Integrate dengan React untuk UI
5. **Deployment**: Setup production environment

## 📝 Development Guidelines

1. **Code Style**: Use Black for formatting, isort for imports
2. **Type Hints**: Always use type hints
3. **Documentation**: Docstrings for all functions
4. **Testing**: Write tests for new features
5. **Git Flow**: Feature branches, PR reviews

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details 