-- Enable PostGIS extension
-- Run this in your Supabase SQL editor

-- Enable the PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable additional PostGIS extensions if needed
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Verify PostGIS is installed
SELECT PostGIS_Version(); 