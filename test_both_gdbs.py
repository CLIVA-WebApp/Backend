import fiona
import os

# Test both geodatabase files
gdb_paths = [
    '../raw_data/RBI10K_ADMINISTRASI_DESA_20230928.gdb',
    '../raw_data/RBI50K_ADMINISTRASI_KABKOTA_20230907.gdb'
]

for gdb_path in gdb_paths:
    print(f"\n{'='*60}")
    print(f"Testing: {gdb_path}")
    print(f"Absolute path: {os.path.abspath(gdb_path)}")
    print(f"File exists: {os.path.exists(gdb_path)}")
    
    if os.path.exists(gdb_path):
        try:
            available_layers = fiona.listlayers(gdb_path)
            print(f'✅ Successfully connected to the Geodatabase.')
            print('Available layers:')
            for layer in available_layers:
                print(f'  - {layer}')
        except Exception as e:
            print(f'❌ Error connecting to Geodatabase: {e}')
            print('Please ensure the path is correct and you have the necessary drivers installed.')
    else:
        print("❌ The geodatabase file does not exist at the specified path.") 