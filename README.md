# CLIVA Health Planning Platform

## 🎯 Tentang CLIVA

**CLIVA** (Community-based Local Infrastructure Visualization and Analysis) adalah platform web untuk perencanaan kesehatan berbasis GIS yang membantu perencana kesehatan daerah mengatasi kesenjangan distribusi layanan kesehatan di Indonesia.

Platform ini dirancang untuk memberikan solusi komprehensif dalam analisis dan perencanaan distribusi fasilitas kesehatan, dengan fokus pada:

- **Visualisasi Peta Akses Kesehatan** - Heatmaps yang menunjukkan area dengan akses terbatas
- **Algoritma Prioritas Kecamatan** - Scoring system untuk menentukan prioritas pembangunan Puskesmas
- **Simulator "What-If"** - Simulasi dampak pembangunan Puskesmas baru
- **Manajemen Data Terpusat** - CRUD untuk data Puskesmas dan populasi
- **Ceeva Chatbot** - Asisten AI untuk analisis dan perencanaan kesehatan

## 🏗️ Arsitektur Teknis

### Tech Stack
- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL via Supabase (Cloud Database) dengan PostGIS extension
- **Architecture**: MVCS (Model-View-Controller-Service)
- **Authentication**: JWT (JSON Web Tokens) + Google OAuth
- **ORM**: SQLAlchemy
- **Database Migrations**: Alembic
- **API Documentation**: Auto-generated dengan FastAPI
- **Containerization**: Docker & Docker Compose
- **AI Assistant**: Groq API (Llama 3.1 8B)

### Struktur Direktori
```
Backend/
├── app/src/
│   ├── config/          # Database & settings
│   ├── models/          # SQLAlchemy models
│   ├── views/           # FastAPI routes/endpoints
│   ├── controllers/     # Data access layer
│   ├── services/        # Business logic
│   ├── middleware/      # Authentication, validation
│   ├── schemas/         # Pydantic models
│   └── utils/           # Helper functions
├── alembic/             # Database migrations
├── tests/               # Unit tests
├── raw_data/            # GDB files and data sources
├── data_scripts/        # Data processing scripts
├── requirements.txt     # Python dependencies
├── docker-compose.yaml  # Docker services
├── Dockerfile          # Container configuration
└── README.md           # This file
```

## 🚀 Fitur Utama

### 1. Health Access Heatmaps
Visualisasi peta yang menunjukkan:
- Area dengan akses kesehatan terbatas
- Radius coverage setiap Puskesmas
- Kepadatan populasi per kecamatan
- Indikator kemiskinan dan kebutuhan

### 2. Equity Prioritization Score
Algoritma scoring yang mempertimbangkan:
- Jarak ke Puskesmas terdekat
- Kepadatan populasi
- Tingkat kemiskinan
- Luas wilayah
- Akses transportasi

### 3. "What-If" Simulator
Simulasi dampak pembangunan Puskesmas baru:
- Analisis coverage area
- Perhitungan aksesibilitas
- Estimasi dampak pada populasi
- Rekomendasi lokasi optimal

### 4. Ceeva AI Assistant
Asisten AI untuk perencanaan kesehatan:
- Analisis pola akses kesehatan
- Interpretasi hasil simulasi
- Saran lokasi optimal fasilitas
- Penjelasan metrik kesehatan

### 5. Data Management
Sistem manajemen data terpusat untuk:
- Data Puskesmas (lokasi, kapasitas, coverage)
- Data populasi per kecamatan
- Indikator sosial-ekonomi
- Historical data tracking

## 📊 Model Data

### User (Perencana Kesehatan)
- Informasi profil perencana
- Role dan permissions
- Authentication credentials
- Activity tracking

### Puskesmas (Fasilitas Kesehatan)
- Nama dan kode Puskesmas
- Lokasi (latitude, longitude)
- Kapasitas dan radius coverage
- Status aktif/nonaktif
- Data administratif (kecamatan, kabupaten, provinsi)

### Population (Data Populasi)
- Jumlah penduduk per kecamatan
- Luas wilayah dan kepadatan
- Tingkat kemiskinan
- Koordinat pusat kecamatan
- Tahun data

### Simulation Results
- Hasil simulasi "what-if"
- Konteks untuk chatbot
- Automated reasoning
- Historical analysis

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Registrasi perencana kesehatan
- `POST /auth/login` - Login ke sistem
- `POST /auth/logout` - Logout dari sistem
- `GET /auth/google` - Google OAuth login
- `GET /auth/google/callback` - Google OAuth callback

### Region Management
- `GET /regions/provinces` - Daftar semua provinsi
- `GET /regions/provinces/{id}/regencies` - Regencies dalam provinsi
- `GET /regions/regencies/{id}/subdistricts` - Subdistricts dalam regency
- `GET /regions/regencies/{id}/facilities` - Fasilitas kesehatan dalam regency

### Analysis & Simulation
- `POST /analysis/heatmap` - Generate heatmap data
- `POST /analysis/priority-scores` - Calculate priority scores
- `POST /simulation/run` - Run "what-if" simulation
- `GET /simulation/results` - Get simulation results

### Chatbot
- `POST /chatbot/start_chat` - Start new chat session
- `POST /chatbot/assist` - Get AI assistance

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Status API

## 🐳 Docker Setup

### Quick Start with Docker

1. **Environment Setup**
```bash
cp env.example .env
# Edit .env with your Supabase credentials
```

2. **Production Deployment**
```bash
docker-compose up -d
```

3. **Development Setup**
```bash
docker-compose -f docker-compose.dev.yaml up -d
```

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
```

## 📁 Data Loading

### GDB Data Loading

The platform supports loading GDB (Geodatabase) files for administrative boundaries:

```bash
# Install required packages
pip install geopandas fiona shapely

# Run data loader
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

## 🚀 Quick Start

### Development Setup

#### 1. Setup Environment
```bash
cd Backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Setup Supabase
- Buat project di [Supabase](https://supabase.com)
- Enable PostGIS extension
- Dapatkan database credentials dari Settings > Database
- Copy connection string

#### 4. Configure Environment
```bash
cp env.example .env
# Edit .env dengan Supabase credentials Anda
```

#### 5. Load Data
```bash
# Load administrative boundaries
python load_gdb_data.py

# Run database migrations
alembic upgrade head
```

#### 6. Start Development Server
```bash
python start.py
```

#### 7. Access Application
- API: http://localhost:8000
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

### Production Deployment

#### Vercel Serverless Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
cd Backend
vercel login
vercel

# Deploy to production
vercel --prod
```

**For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**

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
python run.py install    # Install dependencies
python run.py setup      # Setup environment
python run.py test       # Run tests
python run.py run        # Start server
python run.py migrate    # Run migrations
```

## 🤝 Kontribusi

Kami mengundang kontribusi dari:
- **Perencana Kesehatan**: Feedback dan kebutuhan fungsional
- **Developer**: Pengembangan fitur dan perbaikan bug
- **Data Scientist**: Optimasi algoritma dan analisis
- **UI/UX Designer**: Peningkatan user experience

## 📄 License

MIT License - see LICENSE file for details

## 📞 Kontak

Untuk pertanyaan atau kolaborasi, silakan hubungi tim pengembang CLIVA.

---

**CLIVA - Empowering Health Planning Through Data-Driven Decisions**

> 📖 **For detailed technical documentation, see [TECHNICAL_README.md](./TECHNICAL_README.md)**