import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import bcrypt
import json
import os

class Authentication:
    def __init__(self):
        self.config_file = 'config.yaml'
        self.users_file = 'users.json'
        self.ensure_config_exists()
    
    def ensure_config_exists(self):
        """Ensure configuration files exist"""
        if not os.path.exists(self.config_file):
            self.create_default_config()
        if not os.path.exists(self.users_file):
            self.create_default_users()
    
    def create_default_config(self):
        """Create default configuration file"""
        config = {
            'credentials': {
                'usernames': {}
            },
            'cookie': {
                'name': 'event_tracker_cookie',
                'key': 'event_tracker_key_123',
                'expiry_days': 30,
                'same_site': 'strict'
            },
            'preauthorized': {
                'emails': []
            }
        }
        
        with open(self.config_file, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
    
    def create_default_users(self):
        """Create default users file with admin user and game operators"""
        # Create default admin user
        admin_password = "admin123"
        admin_hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create game operator password
        game_password = "game123"
        game_hashed = bcrypt.hashpw(game_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        users = {
            "admin": {
                "name": "Administrator",
                "emp_id": "ADMIN001",
                "email": "admin@company.com",
                "password": admin_hashed,
                "is_admin": True
            },
            "game1_op": {
                "name": "Game 1 Operator",
                "emp_id": "GAME001",
                "email": "game1@company.com",
                "password": game_hashed,
                "is_admin": False,
                "role": "game_operator",
                "assigned_game": 1
            },
            "game2_op": {
                "name": "Game 2 Operator",
                "emp_id": "GAME002",
                "email": "game2@company.com",
                "password": game_hashed,
                "is_admin": False,
                "role": "game_operator",
                "assigned_game": 2
            },
            "game3_op": {
                "name": "Game 3 Operator",
                "emp_id": "GAME003",
                "email": "game3@company.com",
                "password": game_hashed,
                "is_admin": False,
                "role": "game_operator",
                "assigned_game": 3
            },
            "game4_op": {
                "name": "Game 4 Operator",
                "emp_id": "GAME004",
                "email": "game4@company.com",
                "password": game_hashed,
                "is_admin": False,
                "role": "game_operator",
                "assigned_game": 4
            },
            "game5_op": {
                "name": "Game 5 Operator",
                "emp_id": "GAME005",
                "email": "game5@company.com",
                "password": game_hashed,
                "is_admin": False,
                "role": "game_operator",
                "assigned_game": 5
            }
        }
        
        with open(self.users_file, 'w') as file:
            json.dump(users, file, indent=2)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as file:
                config = yaml.load(file, Loader=SafeLoader)
            return config
        except Exception as e:
            st.error(f"Error loading config: {str(e)}")
            return None
    
    def load_users(self):
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as file:
                users = json.load(file)
            return users
        except Exception as e:
            st.error(f"Error loading users: {str(e)}")
            return {}
    
    def save_users(self, users):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as file:
                json.dump(users, file, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving users: {str(e)}")
            return False
    
    def update_config_with_users(self):
        """Update config file with current users"""
        config = self.load_config()
        users = self.load_users()
        
        if config and users:
            config['credentials']['usernames'] = {}
            
            for username, user_data in users.items():
                config['credentials']['usernames'][username] = {
                    'name': user_data['name'],
                    'password': user_data['password']
                }
            
            with open(self.config_file, 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    
    def get_authenticator(self):
        """Get streamlit authenticator instance"""
        self.update_config_with_users()
        config = self.load_config()
        
        if config:
            try:
                # Try newer streamlit-authenticator API with additional parameters
                authenticator = stauth.Authenticate(
                    config['credentials'],
                    config['cookie']['name'],
                    config['cookie']['key'],
                    config['cookie']['expiry_days'],
                    preauthorized=None
                )
                
                # Force cookie configuration for Streamlit Cloud
                if hasattr(authenticator, 'cookie_manager'):
                    authenticator.cookie_manager.set_config(
                        name=config['cookie']['name'],
                        key=config['cookie']['key'],
                        expiry_days=config['cookie']['expiry_days']
                    )
                    
            except (TypeError, AttributeError):
                # Fallback to older API
                authenticator = stauth.Authenticate(
                    config['credentials'],
                    config['cookie']['name'],
                    config['cookie']['key'],
                    config['cookie']['expiry_days']
                )
            return authenticator
        return None
    
    def register_user(self, username, name, emp_id, email, password):
        """Register a new user"""
        users = self.load_users()
        
        # Check if username or emp_id already exists
        for existing_username, user_data in users.items():
            if existing_username == username or user_data.get('emp_id') == emp_id:
                return False
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Add new user
        users[username] = {
            'name': name,
            'emp_id': emp_id,
            'email': email,
            'password': hashed_password,
            'is_admin': False
        }
        
        return self.save_users(users)
    
    def get_user_info(self, username):
        """Get user information"""
        users = self.load_users()
        return users.get(username, {})
    
    def make_admin(self, username):
        """Make a user admin"""
        users = self.load_users()
        if username in users:
            users[username]['is_admin'] = True
            return self.save_users(users)
        return False
    
    def remove_admin(self, username):
        """Remove admin privileges from a user"""
        users = self.load_users()
        if username in users and username != 'admin':  # Protect default admin
            users[username]['is_admin'] = False
            return self.save_users(users)
        return False
    
    def get_all_users(self):
        """Get all users"""
        return self.load_users()
    
    def delete_user(self, username):
        """Delete a user"""
        if username == 'admin':  # Protect default admin
            return False
        
        users = self.load_users()
        if username in users:
            del users[username]
            return self.save_users(users)
        return False
    
    def is_game_operator(self, username):
        """Check if user is a game operator"""
        user_info = self.get_user_info(username)
        return user_info.get('role') == 'game_operator'
    
    def get_assigned_game(self, username):
        """Get the assigned game number for a game operator"""
        user_info = self.get_user_info(username)
        return user_info.get('assigned_game')
