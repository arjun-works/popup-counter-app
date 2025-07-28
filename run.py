#!/usr/bin/env python3
"""
Event Tracker Application Runner
Utility script to run the Streamlit application with proper configuration
"""

import subprocess
import sys
import os
import json
import bcrypt
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'plotly',
        'streamlit_authenticator',
        'bcrypt',
        'PyYAML'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def initialize_data_files():
    """Initialize data files if they don't exist"""
    # Create users.json with default admin
    if not os.path.exists('users.json'):
        print("👤 Creating default admin user...")
        admin_password = "admin123"
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        users = {
            "admin": {
                "name": "Administrator",
                "emp_id": "ADMIN001",
                "email": "admin@company.com",
                "department": "IT",
                "password": hashed_password,
                "is_admin": True
            }
        }
        
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=2)
        
        print("✅ Default admin user created")
        print("   Username: admin")
        print("   Password: admin123")
    
    # Create empty participants.json
    if not os.path.exists('participants.json'):
        with open('participants.json', 'w') as f:
            json.dump({}, f)
    
    # Create empty scores.json
    if not os.path.exists('scores.json'):
        with open('scores.json', 'w') as f:
            json.dump({}, f)

def create_directories():
    """Create necessary directories"""
    directories = ['.streamlit', 'data', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def run_application():
    """Run the Streamlit application"""
    print("🚀 Starting Event Tracker...")
    print("🌐 The application will open in your default browser")
    print("📱 Mobile-friendly interface available")
    print("👤 Default admin login: admin / admin123")
    print("⚠️  Remember to change the default password!")
    print("-" * 50)
    
    try:
        # Run Streamlit with custom configuration
        cmd = [
            'streamlit', 'run', 'app.py',
            '--server.port', '8501',
            '--server.headless', 'false',
            '--browser.gatherUsageStats', 'false'
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {str(e)}")

def main():
    """Main function"""
    print("🎮 Event Tracker - Gamified Scoring System")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize application
    create_directories()
    initialize_data_files()
    
    # Run application
    run_application()

if __name__ == "__main__":
    main()
