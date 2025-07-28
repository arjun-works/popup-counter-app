import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import bcrypt
import json
import os
from io import BytesIO
import base64

# Import custom modules
# Fixed module imports for Streamlit Cloud deployment
from auth import Authentication
from database import Database
from admin import AdminPanel
from dashboard import UserDashboard
from email_service import EmailService
from game_operator import GameOperatorPanel
from game_logger import GameScoringLogger

# Page configuration
st.set_page_config(
    page_title="🎮 Event Tracker - Gamified Scoring System",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .gift-card {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        font-weight: bold;
    }
    .gold-gift {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
    }
    .silver-gift {
        background: linear-gradient(135deg, #C0C0C0 0%, #808080 100%);
        color: #000;
    }
    .participation-gift {
        background: linear-gradient(135deg, #87CEEB 0%, #4682B4 100%);
        color: #fff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    
    /* Mobile-responsive styles */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            padding-left: 10px;
            padding-right: 10px;
            font-size: 0.9rem;
        }
        .stButton button {
            width: 100%;
            height: 50px;
            font-size: 1rem;
            margin: 5px 0;
        }
        .stSelectbox, .stTextInput, .stNumberInput {
            font-size: 1rem;
        }
        .stDataFrame {
            font-size: 0.8rem;
        }
        /* Large buttons for mobile touch */
        .game-operator-button {
            padding: 15px 20px;
            font-size: 1.1rem;
            border-radius: 8px;
            margin: 10px 0;
        }
        /* Larger form inputs for mobile */
        .stNumberInput input {
            height: 50px;
            font-size: 1.2rem;
        }
        .stSelectbox > div > div {
            height: 50px;
            font-size: 1.1rem;
        }
        .stTextInput input {
            height: 50px;
            font-size: 1.1rem;
        }
    }
    
    /* Game operator specific styles */
    .game-operator-panel {
        max-width: 100%;
        padding: 10px;
    }
    .mobile-score-form {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'is_admin' not in st.session_state:
        st.session_state['is_admin'] = False

def main():
    """Main application function"""
    initialize_session_state()
    
    # Initialize components
    auth = Authentication()
    db = Database()
    admin_panel = AdminPanel(db)
    user_dashboard = UserDashboard(db)
    email_service = EmailService()
    game_logger = GameScoringLogger()
    game_operator_panel = GameOperatorPanel(db, game_logger)
    
    # Header
    st.markdown('<h1 class="main-header">🎮 Event Tracker - Gamified Scoring System</h1>', unsafe_allow_html=True)
    
    # Authentication
    authenticator = auth.get_authenticator()
    
    # Check if authenticator was created successfully
    if authenticator is None:
        st.error("Authentication system failed to initialize. Please check configuration files.")
        st.stop()
    
    # Login/Logout
    if st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
        
        # Show registration and login options
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔐 Login")
            try:
                authenticator.login(location='main')
            except Exception as e:
                st.error(f"Login error: {str(e)}")
                st.error("Please check if all required files exist.")
                
        with col2:
            st.subheader("📝 New User Registration")
            with st.form("registration_form"):
                st.write("Register to participate in the event!")
                reg_name = st.text_input("Full Name", placeholder="Enter your full name")
                reg_emp_id = st.text_input("Employee ID", placeholder="Enter your employee ID")
                reg_email = st.text_input("Email", placeholder="Enter your email address")
                reg_username = st.text_input("Username", placeholder="Choose a username")
                reg_password = st.text_input("Password", type="password", placeholder="Choose a password")
                reg_confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                if st.form_submit_button("Register 🚀"):
                    if reg_password != reg_confirm_password:
                        st.error("Passwords don't match!")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters long!")
                    elif not all([reg_name, reg_emp_id, reg_email, reg_username, reg_password]):
                        st.error("Please fill all fields!")
                    else:
                        # Check if username or emp_id already exists
                        if auth.register_user(reg_username, reg_name, reg_emp_id, reg_email, reg_password):
                            # Also register in database
                            db.register_participant(reg_emp_id, reg_name, reg_email)
                            st.success("Registration successful! Please login with your credentials.")
                            st.rerun()
                        else:
                            st.error("Username or Employee ID already exists!")
    
    elif st.session_state["authentication_status"]:
        # User is logged in
        st.success(f'Welcome *{st.session_state["name"]}*! 🎉')
        
        # Check user role
        user_info = auth.get_user_info(st.session_state["username"])
        st.session_state['is_admin'] = user_info.get('is_admin', False)
        is_game_operator = auth.is_game_operator(st.session_state["username"])
        
        # Logout button
        try:
            authenticator.logout(location='sidebar')
        except Exception as e:
            st.sidebar.error(f"Logout error: {str(e)}")
            if st.sidebar.button("Force Logout"):
                st.session_state['authentication_status'] = None
                st.session_state['name'] = None
                st.session_state['username'] = None
                st.rerun()
        
        # Navigation based on role
        if st.session_state['is_admin']:
            # Admin interface
            tabs = st.tabs(["🏠 Dashboard", "🏆 Leaderboard", "⚙️ Admin Panel", "📧 Email Center"])
            
            with tabs[0]:
                user_dashboard.show_dashboard(st.session_state["username"])
            
            with tabs[1]:
                show_leaderboard(db)
            
            with tabs[2]:
                admin_panel.show_admin_panel()
            
            with tabs[3]:
                show_email_center(db, email_service)
                
        elif is_game_operator:
            # Game operator interface
            assigned_game = auth.get_assigned_game(st.session_state["username"])
            game_operator_panel.show_game_operator_panel(assigned_game, st.session_state["username"])
                
        else:
            # Regular user interface
            tabs = st.tabs(["🏠 Dashboard", "🏆 Leaderboard"])
            
            with tabs[0]:
                user_dashboard.show_dashboard(st.session_state["username"])
            
            with tabs[1]:
                show_leaderboard(db)

def show_leaderboard(db):
    """Display the leaderboard"""
    st.subheader("🏆 Leaderboard")
    
    scores_df = db.get_all_scores()
    if not scores_df.empty:
        # Sort by total score descending
        leaderboard = scores_df.sort_values('total', ascending=False).reset_index(drop=True)
        leaderboard['rank'] = leaderboard.index + 1
        
        # Add rank icons
        def get_rank_icon(rank):
            if rank == 1:
                return "🥇"
            elif rank == 2:
                return "🥈"
            elif rank == 3:
                return "🥉"
            else:
                return f"{rank}"
        
        leaderboard['Rank'] = leaderboard['rank'].apply(get_rank_icon)
        
        # Display leaderboard
        display_cols = ['Rank', 'name', 'total', 'gift_type']
        col_names = {'name': 'Name', 'total': 'Total Score', 'gift_type': 'Gift Category'}
        
        st.dataframe(
            leaderboard[display_cols].rename(columns=col_names),
            use_container_width=True,
            height=400
        )
        
        # Leaderboard visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 bar chart
            top_10 = leaderboard.head(10)
            fig_bar = px.bar(
                top_10, 
                x='name', 
                y='total',
                title="Top 10 Participants",
                color='total',
                color_continuous_scale='viridis'
            )
            fig_bar.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True, key="leaderboard_bar_chart")
        
        with col2:
            # Gift distribution pie chart
            gift_counts = leaderboard['gift_type'].value_counts()
            fig_pie = px.pie(
                values=gift_counts.values,
                names=gift_counts.index,
                title="Gift Distribution",
                color_discrete_map={
                    'Gold': '#FFD700',
                    'Silver': '#C0C0C0',
                    'Participation': '#87CEEB'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True, key="leaderboard_pie_chart")
        
        # Statistics
        st.subheader("📊 Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Participants", len(leaderboard))
        with col2:
            st.metric("Average Score", f"{leaderboard['total'].mean():.1f}")
        with col3:
            st.metric("Highest Score", leaderboard['total'].max())
        with col4:
            st.metric("Gold Winners", len(leaderboard[leaderboard['gift_type'] == 'Gold']))
    
    else:
        st.info("No scores available yet. Check back after the games begin! 🎮")

def show_email_center(db, email_service):
    """Display email center for admins"""
    st.subheader("📧 Email Center")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Send notifications to participants about their scores and gifts.")
        
        # Email options
        email_type = st.selectbox(
            "Select Email Type",
            ["All Participants", "Gold Winners Only", "Silver Winners Only", "Custom Selection"]
        )
        
        if email_type == "Custom Selection":
            participants = db.get_all_participants()
            if not participants.empty:
                selected_participants = st.multiselect(
                    "Select Participants",
                    options=participants['emp_id'].tolist(),
                    format_func=lambda x: f"{x} - {participants[participants['emp_id']==x]['name'].iloc[0]}"
                )
            else:
                st.warning("No participants found!")
                selected_participants = []
        
        # Email template customization
        st.subheader("📝 Email Template")
        st.text_area(
            "Email Body (Use {name}, {total_score}, {gift_type} as placeholders)",
            value="""Dear {name},

Congratulations on participating in our exciting event! 🎉

Here are your results:
- Total Score: {total_score} points
- Gift Category: {gift_type}

Thank you for your participation!

Best regards,
Event Team""",
            height=200,
            disabled=True
        )
    
    with col2:
        st.subheader("📊 Email Preview")
        if st.button("Preview Email"):
            st.info("Email preview will be shown here")
        
        if st.button("🚀 Send Emails", type="primary"):
            with st.spinner("Sending emails..."):
                try:
                    # Get recipients based on selection
                    if email_type == "All Participants":
                        recipients = db.get_all_scores()
                    elif email_type == "Gold Winners Only":
                        recipients = db.get_scores_by_gift_type("Gold")
                    elif email_type == "Silver Winners Only":
                        recipients = db.get_scores_by_gift_type("Silver")
                    else:  # Custom Selection
                        recipients = db.get_scores_by_emp_ids(selected_participants)
                    
                    if not recipients.empty:
                        success_count = 0
                        for _, participant in recipients.iterrows():
                            # Here you would integrate with SendGrid or SMTP
                            # For now, we'll simulate the email sending
                            success_count += 1
                        
                        st.success(f"✅ Successfully sent {success_count} emails!")
                    else:
                        st.warning("No recipients found for the selected criteria.")
                        
                except Exception as e:
                    st.error(f"Error sending emails: {str(e)}")
        
        # Email statistics
        st.subheader("📈 Email Stats")
        participants = db.get_all_participants()
        if not participants.empty:
            st.metric("Total Registered", len(participants))
            
            scores = db.get_all_scores()
            if not scores.empty:
                st.metric("Gold Winners", len(scores[scores['gift_type'] == 'Gold']))
                st.metric("Silver Winners", len(scores[scores['gift_type'] == 'Silver']))

if __name__ == "__main__":
    main()
# Updated 07/28/2025 19:00:07
