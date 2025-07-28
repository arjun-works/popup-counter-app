# 🎮 Event Tracker - Gamified Scoring System

A comprehensive Streamlit web application for managing gamified events with participant registration, score tracking, leaderboards, and automated email notifications.

## ✨ Features

### 🔐 Authentication & User Management
- **Streamlit-Authenticator** based login system
- User registration with employee ID validation
- Admin, game operator, and regular user roles
- Secure password hashing with bcrypt
- **Mobile-friendly interface** for game operators

### 👥 Participant Management
- Easy registration form (name, emp ID, email, department)
- Participant search and filtering
- Bulk operations support
- Data export capabilities

### 🎮 Score Management
- Individual game scoring (5 games, 10 points each)
- **Game-specific operators** for mobile score entry
- Real-time score logging with timestamps
- Automatic total calculation
- Gift tier assignment based on scores:
  - **Gold**: 40+ points 🏆
  - **Silver**: 30-39 points 🥈
  - **Participation**: <30 points 🎁

### 📊 Dashboard & Analytics
- **User Dashboard**: Personal scores, achievements, ranking
- **Admin Analytics**: Performance insights, department analysis
- **Leaderboard**: Real-time rankings with visual indicators
- **Interactive Charts**: Score distribution, game performance

### 📧 Email Notifications
- Customizable email templates
- Bulk email sending to winners
- Personalized score notifications
- HTML and plain text support

### 🎯 Advanced Features
- Achievement badges system
- Performance insights and tips
- Mobile-friendly responsive design
- Data backup and export
- Real-time statistics

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Authentication**: streamlit-authenticator
- **Data Visualization**: Plotly
- **Data Processing**: Pandas
- **Email**: SMTP/Gmail integration
- **Storage**: JSON-based local storage
- **Styling**: Custom CSS with gradients

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd event-tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional for email):
   ```bash
   # For email functionality
   export SENDER_EMAIL="your-email@gmail.com"
   export SENDER_PASSWORD="your-app-password"
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 🚀 Deployment on Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the main branch and `app.py`
   - Add secrets if using email functionality:
     ```toml
     [email]
     SENDER_EMAIL = "your-email@gmail.com"
     SENDER_PASSWORD = "your-app-password"
     ```

3. **Access your app**:
   - Your app will be available at `https://your-app-name.streamlit.app`

## 📁 Project Structure

```
event-tracker/
├── app.py                 # Main Streamlit application
├── auth.py               # Authentication management
├── database.py           # Data storage and retrieval
├── admin.py              # Admin panel functionality
├── dashboard.py          # User dashboard
├── email_service.py      # Email notification service
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── config.yaml          # Authentication configuration (auto-generated)
├── users.json           # User data (auto-generated)
├── participants.json    # Participant data (auto-generated)
└── scores.json          # Score data (auto-generated)
```

## 👤 Default Admin Access

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default admin password after first login!

## 🎮 Game Operator Access

**Mobile-Friendly Score Entry Interface**

Each game has a dedicated operator with mobile access:

| Game | Username | Password | Role |
|------|----------|----------|------|
| Game 1 | `game1_op` | `game123` | Game 1 Score Entry |
| Game 2 | `game2_op` | `game123` | Game 2 Score Entry |
| Game 3 | `game3_op` | `game123` | Game 3 Score Entry |
| Game 4 | `game4_op` | `game123` | Game 4 Score Entry |
| Game 5 | `game5_op` | `game123` | Game 5 Score Entry |

### 📱 Mobile Access Instructions

The 5 game operators will access the application through their mobile devices. Follow these steps:

#### 🔧 For the Admin (Setting up Network Access):
1. **Ensure Network Connection**: Make sure the computer running the Streamlit app is connected to the same WiFi network as the mobile devices
2. **Start App with Network Access**:
   ```bash
   streamlit run app.py --server.address 0.0.0.0
   ```
3. **Note the Network URL**: The terminal will display something like:
   ```
   Network URL: http://10.239.155.169:8505
   ```
4. **Share URL**: Provide this network URL to all 5 game operators

#### 📱 For Game Operators (Mobile Users):
1. **WiFi Connection**: Ensure your mobile device is connected to the same WiFi network as the admin's computer
2. **Open Mobile Browser**: Use Chrome, Safari, Firefox, or any mobile browser
3. **Enter Network URL**: Type the complete URL provided by admin
   - Example: `http://10.239.155.169:8505`
4. **Login Process**:
   - Enter your username (e.g., `game1_op`)
   - Enter password: `game123`
   - Tap "Login"
5. **Score Entry Interface**: You'll see a simplified interface showing only your assigned game

#### 🎯 Mobile Interface Features:
- **Touch-Optimized**: Large buttons designed for finger taps
- **Responsive Layout**: Automatically adjusts to your phone screen
- **Single Game View**: Only your assigned game is visible
- **Participant Search**: Easy dropdown to select participants
- **Score Entry Form**: Large input fields for easy typing
- **Instant Logging**: All entries are automatically timestamped
- **Success Feedback**: Clear confirmation when scores are saved

#### 🔧 Troubleshooting Mobile Access:

**Problem: Cannot access the URL**
- ✅ **Solution**: Verify both devices are on the same WiFi network
- ✅ **Check**: Try opening any website to confirm internet connectivity
- ✅ **Alternative**: Ask admin to restart the app and get a new URL

**Problem: Page won't load or looks broken**
- ✅ **Solution**: Clear your browser cache and refresh
- ✅ **Try**: Force refresh by pulling down on the page
- ✅ **Alternative**: Close browser completely and reopen

**Problem: Login credentials not working**
- ✅ **Solution**: Double-check username and password with admin
- ✅ **Check**: Ensure you're using the correct game operator account
- ✅ **Try**: Type credentials manually instead of copy-pasting

**Problem: Screen elements too small**
- ✅ **Solution**: Rotate phone to landscape mode
- ✅ **Try**: Zoom in using browser zoom (pinch gesture)
- ✅ **Settings**: Increase font size in browser settings

**Problem: Network IP changed**
- ✅ **Solution**: Ask admin to provide updated IP address
- ✅ **Reason**: IP addresses can change when router restarts
- ✅ **Prevention**: Admin can set static IP for consistency

### 🔍 Finding Your Server IP

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

**Mac/Linux:**
```bash
ifconfig
```
Look for "inet" address under your active network interface.

**Alternative:** When you run `streamlit run app.py`, check the terminal output for "Network URL"

#### 📋 Mobile Deployment Checklist:

**Before Event Day:**
- [ ] Test the network URL from at least one mobile device
- [ ] Verify all 5 game operator accounts can login
- [ ] Confirm score entry works on mobile interface
- [ ] Test with different phone screen sizes if possible
- [ ] Ensure WiFi network is stable and reliable
- [ ] Have backup internet connection if needed

**On Event Day:**
- [ ] Start app with network access: `streamlit run app.py --server.address 0.0.0.0`
- [ ] Share network URL with all game operators
- [ ] Keep terminal window open (don't close it)
- [ ] Monitor for any connection issues
- [ ] Have admin credentials ready for troubleshooting

**Emergency Backup Plan:**
- [ ] Have admin device ready to enter scores manually if needed
- [ ] Keep game operator credentials written down
- [ ] Know how to restart the app quickly if needed

## 🎯 Usage Guide

### For Participants:
1. **Register**: Create account with emp ID and email
2. **Login**: Use your credentials to access dashboard
3. **View Scores**: Check your game scores and total
4. **Track Progress**: See your ranking on the leaderboard
5. **Achievements**: Earn badges based on performance

### For Game Operators (Mobile Users):
1. **Connect**: Ensure mobile is on same network as server
2. **Access**: Open browser and go to network URL
3. **Login**: Use your assigned game credentials (`game1_op`, `game2_op`, etc.)
4. **Score Entry**: Enter scores only for your assigned game
5. **Real-time Logging**: All entries are timestamped and logged
6. **Search Participants**: Quick search by name or employee ID

### For Admins:
1. **Login**: Use admin credentials
2. **Score Entry**: Input scores for each participant
3. **Manage Users**: View, search, and manage participants
4. **Analytics**: Access detailed performance insights
5. **Email Center**: Send notifications to winners
6. **Export Data**: Download Excel reports
7. **View Logs**: Monitor all game operator activities

## 🎮 Scoring System

| Score Range | Gift Type | Description |
|-------------|-----------|-------------|
| 40-50 points | 🏆 Gold | Top performers |
| 30-39 points | 🥈 Silver | Great performance |
| 0-29 points | 🎁 Participation | Thank you gift |

## 📧 Email Configuration

To enable email notifications:

1. **Gmail Setup**:
   - Enable 2-factor authentication
   - Generate app password
   - Use app password in configuration

2. **Environment Variables**:
   ```bash
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   ```

3. **Streamlit Secrets** (for cloud deployment):
   ```toml
   [email]
   SENDER_EMAIL = "your-email@gmail.com"
   SENDER_PASSWORD = "your-app-password"
   ```

## 🎨 Customization

### Themes and Colors:
- Modify CSS in `app.py` for custom styling
- Update color schemes in plotly charts
- Customize achievement badges and gift cards

### Scoring Rules:
- Adjust gift thresholds in `database.py`
- Modify number of games in admin panel
- Change maximum scores per game

### Email Templates:
- Edit templates in `email_service.py`
- Add custom placeholders
- Modify HTML styling

## 🔧 Troubleshooting

### Common Issues:

1. **Authentication not working**:
   - Check if `config.yaml` exists
   - Verify user credentials in `users.json`

2. **Data not saving**:
   - Ensure write permissions in directory
   - Check JSON file formats

3. **Email not sending**:
   - Verify email credentials
   - Check Gmail security settings
   - Ensure app password is used

4. **Charts not displaying**:
   - Update plotly version
   - Clear browser cache
   - Check data format

## 📊 Data Management

### Backup:
- Use admin panel export feature
- Regular JSON file backups
- Excel export for analysis

### Migration:
- Export data before updates
- Maintain JSON structure
- Test with sample data

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check documentation and FAQ

## 🎉 Acknowledgments

- Streamlit team for the amazing framework
- Plotly for beautiful visualizations
- Contributors and testers

---

**Happy Gaming! 🎮🏆**
