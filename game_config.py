import json
import os
import streamlit as st
from datetime import datetime
import secrets
import string

class GameConfigManager:
    """Manages game configurations and settings"""
    
    def __init__(self):
        self.config_file = 'games_config.json'
        self.ensure_config_exists()
    
    def ensure_config_exists(self):
        """Ensure game configuration file exists"""
        if not os.path.exists(self.config_file):
            self.create_default_config()
    
    def create_default_config(self):
        """Create default game configuration"""
        default_config = {
            "total_games": 5,
            "games": {
                "1": {
                    "name": "Game 1",
                    "scoring_type": "points",  # "points" or "win_lose"
                    "max_points": 10,
                    "win_points": 10,
                    "lose_points": 0,
                    "description": "First game activity",
                    "active": True
                },
                "2": {
                    "name": "Game 2", 
                    "scoring_type": "points",
                    "max_points": 10,
                    "win_points": 10,
                    "lose_points": 0,
                    "description": "Second game activity",
                    "active": True
                },
                "3": {
                    "name": "Game 3",
                    "scoring_type": "points", 
                    "max_points": 10,
                    "win_points": 10,
                    "lose_points": 0,
                    "description": "Third game activity",
                    "active": True
                },
                "4": {
                    "name": "Game 4",
                    "scoring_type": "points",
                    "max_points": 10, 
                    "win_points": 10,
                    "lose_points": 0,
                    "description": "Fourth game activity",
                    "active": True
                },
                "5": {
                    "name": "Game 5",
                    "scoring_type": "points",
                    "max_points": 10,
                    "win_points": 10,
                    "lose_points": 0,
                    "description": "Fifth game activity", 
                    "active": True
                }
            },
            "gift_thresholds": {
                "gold": 40,
                "silver": 30,
                "participation": 0
            },
            "last_updated": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
    
    def load_config(self):
        """Load game configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading game config: {str(e)}")
            return self.create_default_config()
    
    def save_config(self, config):
        """Save game configuration"""
        try:
            config['last_updated'] = datetime.now().isoformat()
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving game config: {str(e)}")
            return False
    
    def get_game_config(self, game_number):
        """Get configuration for a specific game"""
        config = self.load_config()
        return config['games'].get(str(game_number))
    
    def update_game_config(self, game_number, game_config):
        """Update configuration for a specific game"""
        config = self.load_config()
        config['games'][str(game_number)] = game_config
        return self.save_config(config)
    
    def add_new_game(self, game_number, name, scoring_type, max_points=10, win_points=10, lose_points=0, description=""):
        """Add a new game configuration"""
        config = self.load_config()
        
        config['games'][str(game_number)] = {
            "name": name,
            "scoring_type": scoring_type,
            "max_points": max_points,
            "win_points": win_points,
            "lose_points": lose_points,
            "description": description,
            "active": True
        }
        
        # Update total games count
        config['total_games'] = max(config['total_games'], game_number)
        
        return self.save_config(config)
    
    def remove_game(self, game_number):
        """Remove a game configuration"""
        config = self.load_config()
        
        if str(game_number) in config['games']:
            del config['games'][str(game_number)]
            
            # Update total games count
            if config['games']:
                config['total_games'] = max([int(k) for k in config['games'].keys()])
            else:
                config['total_games'] = 0
                
            return self.save_config(config)
        return False
    
    def update_gift_thresholds(self, gold_threshold, silver_threshold):
        """Update gift thresholds"""
        config = self.load_config()
        config['gift_thresholds'] = {
            "gold": gold_threshold,
            "silver": silver_threshold,
            "participation": 0
        }
        return self.save_config(config)
    
    def get_active_games(self):
        """Get list of active games"""
        config = self.load_config()
        return {k: v for k, v in config['games'].items() if v.get('active', True)}
    
    def toggle_game_status(self, game_number):
        """Toggle active/inactive status of a game"""
        config = self.load_config()
        game_key = str(game_number)
        
        if game_key in config['games']:
            config['games'][game_key]['active'] = not config['games'][game_key].get('active', True)
            return self.save_config(config)
        return False

class GameOperatorManager:
    """Manages game operators and their assignments"""
    
    def __init__(self, auth_system):
        self.auth = auth_system
    
    def generate_secure_password(self, length=8):
        """Generate a secure password for game operators"""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def create_game_operator(self, game_number, operator_name=None, custom_password=None):
        """Create a new game operator"""
        users = self.auth.load_users()
        
        # Generate username
        username = f"game{game_number}_op"
        
        # Check if operator already exists
        if username in users:
            return False, f"Game operator for Game {game_number} already exists"
        
        # Generate operator details
        if not operator_name:
            operator_name = f"Game {game_number} Operator"
        
        password = custom_password if custom_password else self.generate_secure_password()
        
        # Hash password
        import bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Add operator to users
        users[username] = {
            "name": operator_name,
            "emp_id": f"GAME{game_number:03d}",
            "email": f"game{game_number}@company.com",
            "department": "Game Operations",
            "password": hashed_password,
            "is_admin": False,
            "role": "game_operator",
            "assigned_game": game_number,
            "created_date": datetime.now().isoformat()
        }
        
        # Save users
        if self.auth.save_users(users):
            return True, {"username": username, "password": password, "name": operator_name}
        
        return False, "Failed to create game operator"
    
    def remove_game_operator(self, game_number):
        """Remove a game operator"""
        users = self.auth.load_users()
        username = f"game{game_number}_op"
        
        if username in users:
            del users[username]
            return self.auth.save_users(users)
        
        return False
    
    def update_operator_password(self, game_number, new_password):
        """Update game operator password"""
        users = self.auth.load_users()
        username = f"game{game_number}_op"
        
        if username in users:
            import bcrypt
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            users[username]['password'] = hashed_password
            return self.auth.save_users(users)
        
        return False
    
    def get_all_game_operators(self):
        """Get all game operators"""
        users = self.auth.load_users()
        operators = {}
        
        for username, user_data in users.items():
            if user_data.get('role') == 'game_operator':
                operators[username] = user_data
        
        return operators
    
    def get_operator_by_game(self, game_number):
        """Get operator assigned to specific game"""
        users = self.auth.load_users()
        username = f"game{game_number}_op"
        return users.get(username)
    
    def bulk_create_operators(self, game_numbers, custom_passwords=None):
        """Create multiple game operators at once"""
        results = []
        custom_passwords = custom_passwords or {}
        
        for game_num in game_numbers:
            password = custom_passwords.get(game_num)
            success, data = self.create_game_operator(game_num, custom_password=password)
            
            if success:
                results.append({
                    "game": game_num,
                    "success": True,
                    "username": data["username"],
                    "password": data["password"],
                    "name": data["name"]
                })
            else:
                results.append({
                    "game": game_num,
                    "success": False,
                    "error": data
                })
        
        return results
    
    def reset_all_operator_passwords(self):
        """Reset passwords for all game operators"""
        operators = self.get_all_game_operators()
        results = []
        
        for username, operator_data in operators.items():
            game_number = operator_data.get('assigned_game')
            if game_number:
                new_password = self.generate_secure_password()
                if self.update_operator_password(game_number, new_password):
                    results.append({
                        "username": username,
                        "game": game_number,
                        "new_password": new_password,
                        "success": True
                    })
                else:
                    results.append({
                        "username": username, 
                        "game": game_number,
                        "success": False
                    })
        
        return results
