# CLIVA Health Planning Platform

## 🎯 Tentang CLIVA

**CLIVA** (Community-based Local Infrastructure Visualization and Analysis) adalah platform web untuk perencanaan kesehatan berbasis GIS yang membantu perencana kesehatan daerah mengatasi kesenjangan distribusi layanan kesehatan di Indonesia.

Platform ini dirancang untuk memberikan solusi komprehensif dalam analisis dan perencanaan distribusi fasilitas kesehatan, dengan fokus pada:

- **Visualisasi Peta Akses Kesehatan** - Heatmaps yang menunjukkan area dengan akses terbatas
- **Algoritma Prioritas Kecamatan** - Scoring system untuk menentukan prioritas pembangunan Puskesmas
- **Simulator "What-If"** - Simulasi dampak pembangunan Puskesmas baru
- **Manajemen Data Terpusat** - CRUD untuk data Puskesmas dan populasi

## 🏗️ Arsitektur Teknis

### Tech Stack
- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL via Supabase (Cloud Database)
- **Architecture**: MVCS (Model-View-Controller-Service)
- **Authentication**: JWT (JSON Web Tokens)
- **ORM**: SQLAlchemy
- **Database Migrations**: Alembic
- **API Documentation**: Auto-generated dengan FastAPI

### Struktur Direktori
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

### 4. Data Management
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

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Registrasi perencana kesehatan
- `POST /auth/login` - Login ke sistem
- `POST /auth/logout` - Logout dari sistem

### Puskesmas Management
- `GET /puskesmas/` - Daftar semua Puskesmas
- `POST /puskesmas/` - Tambah Puskesmas baru
- `GET /puskesmas/{id}` - Detail Puskesmas
- `PUT /puskesmas/{id}` - Update data Puskesmas
- `DELETE /puskesmas/{id}` - Hapus Puskesmas

### Population Management
- `GET /populations/` - Daftar data populasi
- `POST /populations/` - Tambah data populasi
- `GET /populations/{id}` - Detail data populasi
- `PUT /populations/{id}` - Update data populasi
- `DELETE /populations/{id}` - Hapus data populasi

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Status API

## 📅 Roadmap Implementasi

### ✅ Day 1: Foundation & Authentication (SELESAI)
- Setup Supabase database
- Create User model untuk perencana kesehatan
- Implement authentication (register/login)
- Create basic API endpoints
- Setup CORS untuk frontend

### ✅ Day 2: Data Models & CRUD (SELESAI)
- Create Puskesmas model
- Create Population model
- Implement CRUD operations
- Add data validation dengan Pydantic

### 🔄 Day 3: Health Access Heatmaps (DALAM PROSES)
- Implement geospatial calculations
- Create distance calculation API
- Add radius coverage logic
- Create heatmap data endpoint

### 📋 Day 4: Equity Prioritization Score (PLANNED)
- Implement scoring algorithm
- Create priority calculation API
- Add multiple factor calculations
- Create ranking system

### 🎯 Day 5: "What-If" Simulator & Polishing (PLANNED)
- Implement simulation logic
- Create virtual Puskesmas API
- Add impact calculation
- Create simulation results endpoint

## 🎯 Manfaat Platform

### Untuk Perencana Kesehatan
- **Data-Driven Decision Making**: Keputusan berbasis data yang akurat
- **Visualisasi Komprehensif**: Peta interaktif untuk analisis
- **Simulasi Dampak**: Prediksi hasil sebelum implementasi
- **Prioritasi Efektif**: Algoritma untuk menentukan prioritas

### Untuk Masyarakat
- **Akses Kesehatan Merata**: Distribusi fasilitas yang optimal
- **Transparansi Perencanaan**: Data terbuka untuk publik
- **Efisiensi Sumber Daya**: Penggunaan anggaran yang efektif
- **Peningkatan Kualitas Hidup**: Akses kesehatan yang lebih baik

### Untuk Pemerintah Daerah
- **Evidence-Based Policy**: Kebijakan berbasis bukti
- **Resource Optimization**: Optimasi penggunaan sumber daya
- **Monitoring & Evaluation**: Sistem monitoring yang terintegrasi
- **Stakeholder Collaboration**: Kolaborasi antar pemangku kepentingan

## 🔧 Quick Start untuk Development

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

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start Development Server
```bash
python start.py
```

### 7. Access Application
- API: http://localhost:8000
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

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