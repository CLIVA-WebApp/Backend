#!/usr/bin/env python3
import os
import sys
import subprocess

def run_command(command, description=""):
    if description:
        print(f"🚀 {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ Command completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <command>")
        print("Commands: install, setup, test, run, migrate, format, lint, clean")
        return

    command = sys.argv[1]
    
    commands = {
        "install": ("pip install -r requirements.txt", "Installing dependencies..."),
        "setup": ("python setup.py", "Setting up environment..."),
        "test": ("python run_tests.py", "Running tests..."),
        "start": ("python start.py", "Starting development server..."),
        "migrate": ("alembic upgrade head", "Running database migrations..."),
        "format": ("black app/src/ app/tests/", "Formatting code..."),
        "lint": ("flake8 app/src/ app/tests/", "Running linter..."),
        "clean": ("find . -name '*.pyc' -delete", "Cleaning cache...")
    }
    
    if command in commands:
        cmd, desc = commands[command]
        run_command(cmd, desc)
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 