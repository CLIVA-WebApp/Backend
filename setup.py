#!/usr/bin/env python3
"""
Setup script untuk CLIVA Health Planning Platform
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} berhasil!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} gagal: {e}")
        print(f"Error: {e.stderr}")
        return False

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  File .env tidak ditemukan!")
        print("📝 Copy env.example ke .env dan edit dengan credentials Supabase Anda")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment tidak aktif!")
        print("💡 Aktifkan dengan: venv\\Scripts\\activate (Windows) atau source venv/bin/activate (Linux/Mac)")
        return False
    
    print("✅ Environment check passed!")
    return True

def setup_database():
    """Setup database and run migrations"""
    print("🗄️  Setting up database...")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Run migrations
    if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration"):
        return False
    
    if not run_command("alembic upgrade head", "Running database migrations"):
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def run_tests():
    """Run basic tests"""
    return run_command("python run_tests.py", "Running tests")

def main():
    """Main setup function"""
    print("🚀 CLIVA Health Planning Platform - Setup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Setup dibatalkan karena environment tidak siap")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup dibatalkan karena gagal install dependencies")
        return False
    
    # Setup database
    if not setup_database():
        print("\n❌ Setup dibatalkan karena gagal setup database")
        return False
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Setup selesai tapi ada test yang gagal")
    else:
        print("\n✅ Setup selesai dengan sukses!")
    
    print("\n🎉 CLIVA Health Planning Platform siap digunakan!")
    print("\n📋 Next steps:")
    print("1. Start server: python start.py")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Test endpoints: http://localhost:8000/health")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 