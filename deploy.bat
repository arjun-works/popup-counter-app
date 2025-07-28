@echo off
REM Deployment script for Event Tracker application on Windows

echo 🚀 Starting Event Tracker deployment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
pip install --upgrade pip

REM Install requirements
echo 📚 Installing requirements...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist ".streamlit" mkdir .streamlit
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Set up initial configuration
echo ⚙️ Setting up configuration...

REM Create default admin user if users.json doesn't exist
if not exist "users.json" (
    echo 👤 Creating default admin user...
    python -c "import json; import bcrypt; admin_password = 'admin123'; hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'); users = {'admin': {'name': 'Administrator', 'emp_id': 'ADMIN001', 'email': 'admin@company.com', 'department': 'IT', 'password': hashed_password, 'is_admin': True}}; json.dump(users, open('users.json', 'w'), indent=2); print('✅ Default admin user created'); print('Username: admin'); print('Password: admin123'); print('⚠️  Please change the default password after first login!')"
)

REM Create empty data files if they don't exist
if not exist "participants.json" (
    echo {} > participants.json
)

if not exist "scores.json" (
    echo {} > scores.json
)

REM Check if Streamlit is working
echo 🧪 Testing Streamlit installation...
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit installation failed
    pause
    exit /b 1
) else (
    echo ✅ Streamlit is installed correctly
)

echo.
echo 🎉 Deployment completed successfully!
echo.
echo 🚀 To start the application, run:
echo    streamlit run app.py
echo.
echo 🌐 The app will be available at:
echo    Local: http://localhost:8501
echo    Network: http://your-ip:8501
echo.
echo 👤 Default admin credentials:
echo    Username: admin
echo    Password: admin123
echo.
echo ⚠️  Remember to:
echo    1. Change the default admin password
echo    2. Configure email settings in .streamlit/secrets.toml
echo    3. Backup your data regularly
echo.
echo 📚 For more information, check README.md
pause
