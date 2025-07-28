import json
import os
from datetime import datetime
import streamlit as st

class GameScoringLogger:
    def __init__(self):
        self.log_file = 'game_scoring_log.json'
        self.ensure_log_exists()
    
    def ensure_log_exists(self):
        """Ensure log file exists"""
        if not os.path.exists(self.log_file):
            log_data = {
                "entries": [],
                "created": datetime.now().isoformat()
            }
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
    
    def log_score_entry(self, game_number, operator_username, participant_emp_id, participant_name, score, old_score=None):
        """Log a score entry"""
        try:
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "game_number": game_number,
                "operator": operator_username,
                "participant_emp_id": participant_emp_id,
                "participant_name": participant_name,
                "new_score": score,
                "old_score": old_score,
                "action": "update" if old_score is not None else "create"
            }
            
            log_data["entries"].append(entry)
            
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error logging score entry: {str(e)}")
            return False
    
    def get_recent_entries(self, limit=50):
        """Get recent log entries"""
        try:
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
            
            # Sort by timestamp descending and limit
            entries = sorted(log_data["entries"], key=lambda x: x["timestamp"], reverse=True)
            return entries[:limit]
        except Exception as e:
            st.error(f"Error reading log entries: {str(e)}")
            return []
    
    def get_entries_by_game(self, game_number):
        """Get log entries for a specific game"""
        try:
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
            
            game_entries = [entry for entry in log_data["entries"] if entry["game_number"] == game_number]
            return sorted(game_entries, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            st.error(f"Error reading game entries: {str(e)}")
            return []
    
    def get_entries_by_operator(self, operator_username):
        """Get log entries for a specific operator"""
        try:
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
            
            operator_entries = [entry for entry in log_data["entries"] if entry["operator"] == operator_username]
            return sorted(operator_entries, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            st.error(f"Error reading operator entries: {str(e)}")
            return []
