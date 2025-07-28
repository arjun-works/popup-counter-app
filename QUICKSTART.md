# 🚀 Quick Start Guide

## Getting Started in 5 Minutes

### 1. **Installation**
Run the deployment script for your operating system:

**Windows:**
```bash
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 2. **Start the Application**
```bash
streamlit run app.py
```

### 3. **Access the App**
Open your browser and go to: `http://localhost:8501`

### 4. **Login as Admin**
- **Username:** `admin`
- **Password:** `admin123`

### 5. **First Steps**
1. **Change Admin Password** (recommended)
2. **Register Test Participants** or use the registration form
3. **Add Sample Scores** through the admin panel
4. **Explore Features** - dashboard, leaderboard, analytics

---

## 📋 Sample Data

### Test Participants:
| Name | Emp ID | Email | Department |
|------|--------|--------|------------|
| John Doe | EMP001 | john@company.com | IT |
| Jane Smith | EMP002 | jane@company.com | HR |
| Mike Johnson | EMP003 | mike@company.com | Finance |
| Sarah Wilson | EMP004 | sarah@company.com | Marketing |
| David Brown | EMP005 | david@company.com | Operations |

### Sample Scores:
| Emp ID | Game1 | Game2 | Game3 | Game4 | Game5 | Total | Gift |
|--------|-------|-------|-------|-------|-------|-------|------|
| EMP001 | 9 | 8 | 9 | 8 | 9 | 43 | Gold |
| EMP002 | 7 | 8 | 6 | 9 | 7 | 37 | Silver |
| EMP003 | 6 | 5 | 7 | 6 | 8 | 32 | Silver |
| EMP004 | 5 | 6 | 4 | 7 | 5 | 27 | Participation |
| EMP005 | 8 | 9 | 8 | 9 | 8 | 42 | Gold |

---

## 🔧 Configuration

### Email Setup (Optional):
1. Edit `.streamlit/secrets.toml`
2. Add your Gmail credentials:
   ```toml
   [email]
   SENDER_EMAIL = "your-email@gmail.com"
   SENDER_PASSWORD = "your-app-password"
   ```

### Customization:
- **Colors**: Edit CSS in `app.py`
- **Scoring**: Modify thresholds in `database.py`
- **Games**: Update number of games in admin settings

---

## 🎯 Key Features to Explore

### For Participants:
- ✅ Register with employee details
- ✅ View personal dashboard
- ✅ Check leaderboard position
- ✅ Earn achievement badges

### For Admins:
- ✅ Add/edit participant scores
- ✅ View comprehensive analytics
- ✅ Send email notifications
- ✅ Export data to Excel
- ✅ Manage users and settings

---

## 📱 Mobile Support
The app is fully responsive and works great on:
- 📱 Mobile phones
- 📟 Tablets
- 💻 Desktops
- 🖥️ Large screens

---

## 🆘 Need Help?

1. **Check the README.md** for detailed documentation
2. **View the troubleshooting section** for common issues
3. **Contact support** or create an issue

---

**Happy Gaming! 🎮🏆**
