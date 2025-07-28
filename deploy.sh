#!/bin/bash

# Deployment script for Event Tracker application

echo "🚀 Starting Event Tracker deployment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p .streamlit
mkdir -p data
mkdir -p logs

# Set up initial configuration
echo "⚙️ Setting up configuration..."

# Create default admin user if users.json doesn't exist
if [ ! -f "users.json" ]; then
    echo "👤 Creating default admin user..."
    python3 -c "
import json
import bcrypt

# Create default admin user
admin_password = 'admin123'
hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

users = {
    'admin': {
        'name': 'Administrator',
        'emp_id': 'ADMIN001',
        'email': 'admin@company.com',
        'department': 'IT',
        'password': hashed_password,
        'is_admin': True
    }
}

with open('users.json', 'w') as f:
    json.dump(users, f, indent=2)

print('✅ Default admin user created')
print('Username: admin')
print('Password: admin123')
print('⚠️  Please change the default password after first login!')
"
fi

# Create empty data files if they don't exist
if [ ! -f "participants.json" ]; then
    echo "{}" > participants.json
fi

if [ ! -f "scores.json" ]; then
    echo "{}" > scores.json
fi

# Check if Streamlit is working
echo "🧪 Testing Streamlit installation..."
if streamlit --version &> /dev/null; then
    echo "✅ Streamlit is installed correctly"
else
    echo "❌ Streamlit installation failed"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "🚀 To start the application, run:"
echo "   streamlit run app.py"
echo ""
echo "🌐 The app will be available at:"
echo "   Local: http://localhost:8501"
echo "   Network: http://your-ip:8501"
echo ""
echo "👤 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  Remember to:"
echo "   1. Change the default admin password"
echo "   2. Configure email settings in .streamlit/secrets.toml"
echo "   3. Backup your data regularly"
echo ""
echo "📚 For more information, check README.md"
