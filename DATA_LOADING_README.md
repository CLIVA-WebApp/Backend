# GDB Data Loading Guide

This guide explains how to load GDB (Geodatabase) files into your PostGIS-extended Supabase database.

## Prerequisites

1. **Install required packages:**
   ```bash
   pip install geopandas fiona shapely
   ```

2. **Ensure your Supabase database has PostGIS extension enabled**

3. **Configure your environment variables** in `.env`:
   ```
   SUPABASE_USER=your_user
   SUPABASE_PASSWORD=your_password
   SUPABASE_HOST=your_host
   SUPABASE_PORT=5432
   SUPABASE_DBNAME=postgres
   ```

## Data Loading Process

### Step 1: Prepare Your GDB File

Place your GDB file in the `raw_data/` directory. The script expects:
- File: `RBI10K_ADMINISTRASI_DESA_20230928.gdb`
- Layer: `ADMINISTRASI_AR_DESAKEL`

### Step 2: Run the Data Loader

```bash
cd Backend
python load_gdb_data.py
```

This script will:
1. Create all necessary database tables
2. Load provinces, regencies, and subdistricts from the GDB
3. Calculate areas for each administrative unit
4. Establish proper foreign key relationships

## What Gets Loaded

### Administrative Hierarchy
- **Provinces** (Provinsi) - Top-level administrative units
- **Regencies** (Kabupaten/Kota) - Second-level administrative units
- **Subdistricts** (Kecamatan) - Third-level administrative units

### Data Fields
For each administrative unit, the following data is loaded:
- **Name** - Administrative name in Indonesian
- **Geometry** - MultiPolygon boundary in WGS84 (EPSG:4326)
- **Area** - Calculated area in square kilometers
- **Relationships** - Proper foreign key relationships

### Columns Used from GDB
- `KDPPUM` - Province PUM code
- `KDPKAB` - Regency PUM code  
- `KDCPUM` - Subdistrict PUM code
- `WADMPR` - Province name
- `WADMKK` - Regency name
- `WADMKC` - Subdistrict name
- `geometry` - Spatial boundaries

## Database Schema

### Tables Created
1. **provinces** - Province boundaries and metadata
2. **regencies** - Regency boundaries with province relationships
3. **subdistricts** - Subdistrict boundaries with regency relationships
4. **population_points** - Population distribution points
5. **health_facilities** - Health facility locations
6. **users** - User management

### Geometry Types
- All administrative boundaries use `MULTIPOLYGON` geometry type
- Population points use `POINT` geometry type
- Health facilities use `POINT` geometry type
- All geometries use SRID 4326 (WGS84)

## Troubleshooting

### Common Issues

1. **GDB file not found**
   - Ensure the file path in `load_gdb_data.py` is correct
   - Check that the GDB file exists in the specified location

2. **Database connection errors**
   - Verify your `.env` file has correct Supabase credentials
   - Ensure PostGIS extension is enabled in your Supabase database

3. **Memory issues with large datasets**
   - The script processes data in chunks to handle large GDB files
   - If you encounter memory issues, consider processing smaller regions

4. **Geometry conversion errors**
   - The script automatically converts CRS to WGS84 (EPSG:4326)
   - Complex geometries are handled as MultiPolygons

### Verification

After loading, you can verify the data:

```sql
-- Check province count
SELECT COUNT(*) FROM provinces;

-- Check regency count  
SELECT COUNT(*) FROM regencies;

-- Check subdistrict count
SELECT COUNT(*) FROM subdistricts;

-- Verify geometry types
SELECT DISTINCT ST_GeometryType(geom) FROM provinces;
```

## Next Steps

After loading the administrative boundaries:

1. **Load population data** - Add population points for coverage analysis
2. **Load health facility data** - Add Puskesmas and other health facilities
3. **Calculate priority scores** - Use the loaded data for priority calculations
4. **Create spatial indexes** - Optimize for spatial queries

## Performance Notes

- The script includes duplicate checking to avoid re-loading existing data
- Large GDB files may take several minutes to process
- Progress logging shows the current status during loading
- Database transactions ensure data consistency 