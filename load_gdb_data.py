#!/usr/bin/env python3
"""
Main script to load GDB (Geodatabase) data into PostGIS database.
This script handles the complete data loading pipeline.
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app" / "src"))

from utils.create_tables import create_all_tables
from utils.data_loader import GDBDataLoader

def main():
    """Main function to run the complete data loading process"""
    
    print("🚀 Starting GDB Data Loading Process...")
    print("=" * 50)
    
    # Step 1: Create tables
    print("\n📋 Step 1: Creating database tables...")
    try:
        create_all_tables()
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return
    
    # Step 2: Load GDB data
    print("\n🗺️  Step 2: Loading GDB data...")
    
    # Update this path to your GDB file location
    gdb_path = "../raw_data/RBI10K_ADMINISTRASI_DESA_20230928.gdb"
    
    if not os.path.exists(gdb_path):
        print(f"❌ GDB file not found at: {gdb_path}")
        print("Please update the gdb_path variable in this script")
        return
    
    try:
        loader = GDBDataLoader(gdb_path)
        loader.load_all_data()
        print("\n✅ Data loading completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    print("\n🎉 All done! Your PostGIS database is now populated with administrative boundaries.")

if __name__ == "__main__":
    main() 