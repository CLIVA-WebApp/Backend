
# CLIVA Platform Perencanaan Kesehatan

## 🎯 Tentang CLIVA

**CLIVA** (Community-based Local Infrastructure Visualization and Analysis) adalah platform web untuk perencanaan kesehatan berbasis GIS yang membantu perencana kesehatan daerah mengatasi kesenjangan distribusi layanan kesehatan di Indonesia.

Platform ini dirancang untuk memberikan solusi komprehensif dalam analisis dan perencanaan distribusi fasilitas kesehatan, dengan fokus pada:

- **Visualisasi Peta Akses Kesehatan** - Heatmap yang menunjukkan area dengan akses terbatas
- **Algoritma Prioritas Kecamatan** - Sistem skor untuk menentukan prioritas pembangunan Puskesmas
- **Simulator "What-If"** - Simulasi dampak pembangunan Puskesmas baru
- **Manajemen Data Terpusat** - CRUD untuk data Puskesmas dan populasi
- **Ceeva Chatbot** - Asisten AI untuk analisis dan perencanaan kesehatan

## 🏗️ Arsitektur Teknis

### Teknologi yang Digunakan
- **Kerangka Backend**: FastAPI (Python)
- **Basis Data**: PostgreSQL melalui Supabase (Basis data di cloud) dengan ekstensi PostGIS
- **Arsitektur**: MVCS (Model-View-Controller-Service)
- **Autentikasi**: JWT (JSON Web Tokens) + Google OAuth
- **ORM**: SQLAlchemy
- **Migrasi Basis Data**: Alembic
- **Dokumentasi API**: Otomatis dari FastAPI
- **Kontainerisasi**: Docker & Docker Compose
- **Asisten AI**: Groq API (Llama 3.1 8B)

### Struktur Direktori
```
Backend/
├── app/src/
│   ├── config/          # Konfigurasi basis data & pengaturan
│   ├── models/          # Model SQLAlchemy
│   ├── views/           # Rute/endpoints FastAPI
│   ├── controllers/     # Lapisan akses data
│   ├── services/        # Logika bisnis
│   ├── middleware/      # Autentikasi, validasi
│   ├── schemas/         # Model Pydantic
│   └── utils/           # Fungsi bantu
├── alembic/             # Migrasi basis data
├── tests/               # Unit test
├── raw_data/            # File GDB dan sumber data
├── data_scripts/        # Skrip pengolahan data
├── requirements.txt     # Dependensi Python
├── docker-compose.yaml  # Layanan Docker
├── Dockerfile           # Konfigurasi kontainer
└── README.md            # File ini
```

## 🚀 Fitur Utama

### 1. Heatmap Akses Kesehatan
Visualisasi peta yang menunjukkan:
- Area dengan akses kesehatan terbatas
- Radius jangkauan setiap Puskesmas
- Kepadatan populasi per kecamatan
- Indikator kemiskinan dan kebutuhan

### 2. Skor Prioritas Keadilan
Algoritma skor yang mempertimbangkan:
- Jarak ke Puskesmas terdekat
- Kepadatan populasi
- Tingkat kemiskinan
- Luas wilayah
- Akses transportasi

### 3. Simulator "What-If"
Simulasi dampak pembangunan Puskesmas baru:
- Analisis area cakupan
- Perhitungan aksesibilitas
- Estimasi dampak pada populasi
- Rekomendasi lokasi optimal

### 4. Ceeva AI Assistant
Asisten AI untuk perencanaan kesehatan:
- Analisis pola akses kesehatan
- Interpretasi hasil simulasi
- Saran lokasi optimal fasilitas
- Penjelasan metrik kesehatan

### 5. Manajemen Data
Sistem manajemen data terpusat untuk:
- Data Puskesmas (lokasi, kapasitas, cakupan)
- Data populasi per kecamatan
- Indikator sosial-ekonomi
- Pelacakan data historis

## 📊 Model Data

### Pengguna (Perencana Kesehatan)
- Informasi profil
- Peran dan izin
- Kredensial autentikasi
- Pelacakan aktivitas

### Puskesmas
- Nama dan kode
- Lokasi (latitude, longitude)
- Kapasitas dan radius cakupan
- Status aktif/nonaktif
- Data administratif (kecamatan, kabupaten, provinsi)

### Populasi
- Jumlah penduduk per kecamatan
- Luas wilayah dan kepadatan
- Tingkat kemiskinan
- Koordinat pusat kecamatan
- Tahun data

### Hasil Simulasi
- Hasil simulasi "what-if"
- Konteks untuk chatbot
- Penalaran otomatis
- Analisis historis

## 🔌 API Endpoint

### Autentikasi
- `POST /auth/register` - Registrasi pengguna
- `POST /auth/login` - Masuk ke sistem
- `POST /auth/logout` - Keluar dari sistem
- `GET /auth/google` - Login dengan Google
- `GET /auth/google/callback` - Callback Google OAuth

### Manajemen Wilayah
- `GET /regions/provinces` - Daftar provinsi
- `GET /regions/provinces/{id}/regencies` - Kabupaten dalam provinsi
- `GET /regions/regencies/{id}/subdistricts` - Kecamatan dalam kabupaten
- `GET /regions/regencies/{id}/facilities` - Fasilitas kesehatan dalam kabupaten

### Analisis & Simulasi
- `POST /analysis/heatmap` - Hasil heatmap
- `POST /analysis/priority-scores` - Hitung skor prioritas
- `POST /simulation/run` - Jalankan simulasi "what-if"
- `GET /simulation/results` - Ambil hasil simulasi

### Chatbot
- `POST /chatbot/start_chat` - Mulai sesi chat
- `POST /chatbot/assist` - Dapatkan bantuan AI

### Pemeriksaan Sistem
- `GET /` - Endpoint root
- `GET /health` - Status API

## 🐳 Docker Setup

### Jalankan Cepat dengan Docker

1. **Persiapan Lingkungan**
```bash
cp env.example .env
# Edit .env dengan kredensial Supabase Anda
```

2. **Deploy Produksi**
```bash
docker-compose up -d
```

3. **Setup untuk Pengembangan**
```bash
docker-compose -f docker-compose.dev.yaml up -d
```

### Titik Akses
- **Dokumentasi API**: http://localhost:8000/docs
- **Pemeriksaan Sistem**: http://localhost:8000/health
- **pgAdmin (dev)**: http://localhost:5050

### Manajemen Basis Data
```bash
# Jalankan migrasi
docker-compose exec backend alembic upgrade head

# Koneksi ke basis data
docker exec -it health-access-db psql -U postgres -d health_access
```

## 📁 Pemuatan Data

### Pemuatan Data GDB

Platform ini mendukung pemuatan file GDB (Geodatabase):

```bash
# Instalasi dependensi
pip install geopandas fiona shapely

# Jalankan loader
python load_gdb_data.py
```

### Data yang Dimuat
- **Provinsi**
- **Kabupaten/Kota**
- **Kecamatan**
- **Titik Populasi**
- **Fasilitas Kesehatan**

### Sumber Data
- **Batas Administratif**: RBI10K_ADMINISTRASI_DESA_20230928.gdb
- **Data Populasi**: CSV dari BPS
- **Fasilitas Kesehatan**: Data lokasi [Puskesmas Jawa Barat](https://rsmatacicendo.go.id/images/M_images/Daftar_Nama_Puskesmas_di_Propinsi_Jawa_Barat.pdf)

## 🚀 Quickstart

### Setup untuk Pengembangan

#### 1. Persiapkan Lingkungan
```bash
cd Backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 2. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

#### 3. Setup Supabase
- Buat project di [Supabase](https://supabase.com)
- Aktifkan ekstensi PostGIS
- Dapatkan kredensial basis data dari menu Settings
- Salin connection string

#### 4. Konfigurasi Lingkungan
```bash
cp env.example .env
# Edit .env dengan kredensial Supabase Anda
```

#### 5. Muat Data
```bash
# Muat batas administratif
python load_gdb_data.py

# Jalankan migrasi
alembic upgrade head
```

#### 6. Jalankan Server
```bash
python start.py
```

#### 7. Akses Aplikasi
- API: http://localhost:8000
- Pemeriksaan Sistem: http://localhost:8000/health
- Dokumentasi API: http://localhost:8000/docs

## 🛠️ Perintah Pengembangan

```bash
python run.py install    # Instalasi dependensi
python run.py setup      # Setup lingkungan
python run.py test       # Jalankan tes
python run.py run        # Jalankan server
python run.py migrate    # Jalankan migrasi
```

---

**CLIVA - Memberdayakan Perencanaan Kesehatan Melalui Pengambilan Keputusan Berbasis Data**

> 📖 **Untuk dokumentasi teknis lengkap, lihat [TECHNICAL_README.md](./TECHNICAL_README.md)**
