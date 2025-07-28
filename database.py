import pandas as pd
import json
import os
from datetime import datetime
import streamlit as st
from io import BytesIO

class Database:
    def __init__(self):
        self.participants_file = 'participants.json'
        self.scores_file = 'scores.json'
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Ensure database files exist"""
        if not os.path.exists(self.participants_file):
            with open(self.participants_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.scores_file):
            with open(self.scores_file, 'w') as f:
                json.dump({}, f)
    
    def load_participants(self):
        """Load participants from file"""
        try:
            with open(self.participants_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading participants: {str(e)}")
            return {}
    
    def save_participants(self, participants):
        """Save participants to file"""
        try:
            with open(self.participants_file, 'w') as f:
                json.dump(participants, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving participants: {str(e)}")
            return False
    
    def load_scores(self):
        """Load scores from file"""
        try:
            with open(self.scores_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading scores: {str(e)}")
            return {}
    
    def save_scores(self, scores):
        """Save scores to file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(scores, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving scores: {str(e)}")
            return False
    
    def register_participant(self, emp_id, name, email):
        """Register a new participant"""
        participants = self.load_participants()
        
        # Check if participant already exists
        if emp_id in participants:
            return False
        
        participants[emp_id] = {
            'name': name,
            'email': email,
            'registration_date': datetime.now().isoformat()
        }
        
        return self.save_participants(participants)
    
    def get_participant(self, emp_id):
        """Get participant by emp_id"""
        participants = self.load_participants()
        return participants.get(emp_id)
    
    def get_all_participants(self):
        """Get all participants as DataFrame"""
        participants = self.load_participants()
        if participants:
            df = pd.DataFrame.from_dict(participants, orient='index')
            df['emp_id'] = df.index
            df = df.reset_index(drop=True)
            return df
        return pd.DataFrame()
    
    def update_scores(self, emp_id, game1=0, game2=0, game3=0, game4=0, game5=0):
        """Update scores for a participant"""
        # Get participant info
        participant = self.get_participant(emp_id)
        if not participant:
            return False
        
        scores = self.load_scores()
        
        # Calculate total and gift type
        total = game1 + game2 + game3 + game4 + game5
        gift_type = self.calculate_gift_type(total)
        
        scores[emp_id] = {
            'name': participant['name'],
            'email': participant['email'],
            'game1': game1,
            'game2': game2,
            'game3': game3,
            'game4': game4,
            'game5': game5,
            'total': total,
            'gift_type': gift_type,
            'last_updated': datetime.now().isoformat()
        }
        
        return self.save_scores(scores)
    
    def calculate_gift_type(self, total_score):
        """Calculate gift type based on total score"""
        if total_score >= 40:
            return "Gold"
        elif total_score >= 30:
            return "Silver"
        else:
            return "Participation"
    
    def get_user_scores(self, emp_id):
        """Get scores for a specific user"""
        scores = self.load_scores()
        return scores.get(emp_id)
    
    def get_all_scores(self):
        """Get all scores as DataFrame"""
        scores = self.load_scores()
        if scores:
            df = pd.DataFrame.from_dict(scores, orient='index')
            df['emp_id'] = df.index
            df = df.reset_index(drop=True)
            return df
        return pd.DataFrame()
    
    def get_scores_by_gift_type(self, gift_type):
        """Get scores filtered by gift type"""
        all_scores = self.get_all_scores()
        if not all_scores.empty:
            return all_scores[all_scores['gift_type'] == gift_type]
        return pd.DataFrame()
    
    def get_scores_by_emp_ids(self, emp_ids):
        """Get scores for specific employee IDs"""
        all_scores = self.get_all_scores()
        if not all_scores.empty:
            return all_scores[all_scores['emp_id'].isin(emp_ids)]
        return pd.DataFrame()
    
    def delete_participant(self, emp_id):
        """Delete a participant and their scores"""
        # Delete from participants
        participants = self.load_participants()
        if emp_id in participants:
            del participants[emp_id]
            self.save_participants(participants)
        
        # Delete from scores
        scores = self.load_scores()
        if emp_id in scores:
            del scores[emp_id]
            self.save_scores(scores)
        
        return True
    
    def export_data_to_excel(self):
        """Export all data to Excel format"""
        try:
            # Get all data
            participants_df = self.get_all_participants()
            scores_df = self.get_all_scores()
            
            # Create Excel buffer
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if not participants_df.empty:
                    participants_df.to_excel(writer, sheet_name='Participants', index=False)
                
                if not scores_df.empty:
                    scores_df.to_excel(writer, sheet_name='Scores', index=False)
                
                # Create summary sheet
                if not scores_df.empty:
                    summary_data = {
                        'Metric': [
                            'Total Participants',
                            'Average Score',
                            'Highest Score',
                            'Lowest Score',
                            'Gold Winners',
                            'Silver Winners',
                            'Participation Gifts'
                        ],
                        'Value': [
                            len(scores_df),
                            round(scores_df['total'].mean(), 2),
                            scores_df['total'].max(),
                            scores_df['total'].min(),
                            len(scores_df[scores_df['gift_type'] == 'Gold']),
                            len(scores_df[scores_df['gift_type'] == 'Silver']),
                            len(scores_df[scores_df['gift_type'] == 'Participation'])
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            output.seek(0)
            return output
            
        except Exception as e:
            st.error(f"Error exporting data: {str(e)}")
            return None
    
    def get_statistics(self):
        """Get database statistics"""
        participants = self.get_all_participants()
        scores = self.get_all_scores()
        
        stats = {
            'total_participants': len(participants) if not participants.empty else 0,
            'total_scored': len(scores) if not scores.empty else 0,
            'average_score': round(scores['total'].mean(), 2) if not scores.empty else 0,
            'highest_score': scores['total'].max() if not scores.empty else 0,
            'gold_winners': len(scores[scores['gift_type'] == 'Gold']) if not scores.empty else 0,
            'silver_winners': len(scores[scores['gift_type'] == 'Silver']) if not scores.empty else 0,
            'participation_gifts': len(scores[scores['gift_type'] == 'Participation']) if not scores.empty else 0
        }
        
        return stats
