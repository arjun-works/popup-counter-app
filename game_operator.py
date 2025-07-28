import streamlit as st
import pandas as pd
from database import Database
from game_logger import GameScoringLogger

class GameOperatorPanel:
    def __init__(self, database, game_logger):
        self.db = database
        self.logger = game_logger
    
    def show_game_operator_panel(self, assigned_game, operator_username):
        """Show the game operator panel for score entry"""
        st.title(f"🎮 Game {assigned_game} Score Entry")
        
        # Game operator info
        st.info(f"Logged in as: **{operator_username}** - Game {assigned_game} Operator")
        
        # Get all participants
        participants_df = self.db.get_all_participants()
        
        if participants_df.empty:
            st.warning("No participants registered yet!")
            return
        
        # Tabs for different sections
        tab1, tab2, tab3 = st.tabs(["📝 Score Entry", "📊 Current Scores", "📋 Entry Log"])
        
        with tab1:
            self.show_score_entry_form(assigned_game, operator_username, participants_df)
        
        with tab2:
            self.show_current_scores(assigned_game, participants_df)
        
        with tab3:
            self.show_entry_log(assigned_game, operator_username)
    
    def show_score_entry_form(self, assigned_game, operator_username, participants_df):
        """Show score entry form"""
        st.subheader(f"Enter Scores for Game {assigned_game}")
        
        # Search for participant
        search_term = st.text_input("🔍 Search participant", placeholder="Search by name or employee ID")
        
        if search_term:
            mask = (
                participants_df['name'].str.contains(search_term, case=False, na=False) |
                participants_df['emp_id'].str.contains(search_term, case=False, na=False)
            )
            filtered_participants = participants_df[mask]
        else:
            filtered_participants = participants_df
        
        if not filtered_participants.empty:
            # Select participant
            participant_options = []
            for _, row in filtered_participants.iterrows():
                participant_options.append(f"{row['name']} ({row['emp_id']})")
            
            selected_participant = st.selectbox(
                "Select Participant",
                participant_options,
                key=f"game{assigned_game}_participant_select"
            )
            
            if selected_participant:
                # Extract emp_id from selection
                emp_id = selected_participant.split("(")[1].split(")")[0]
                participant_name = selected_participant.split(" (")[0]
                
                # Get current scores
                current_scores = self.db.get_user_scores(emp_id)
                current_game_score = 0
                if current_scores:
                    current_game_score = current_scores.get(f'game{assigned_game}', 0)
                
                # Score entry form
                with st.form(f"game{assigned_game}_score_form"):
                    st.write(f"**Participant:** {participant_name}")
                    st.write(f"**Employee ID:** {emp_id}")
                    
                    if current_game_score > 0:
                        st.info(f"Current Game {assigned_game} Score: **{current_game_score}**")
                    
                    new_score = st.number_input(
                        f"Game {assigned_game} Score",
                        min_value=0,
                        max_value=10,
                        value=current_game_score,
                        help="Enter score between 0-10"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_score = st.form_submit_button("💾 Save Score", type="primary")
                    with col2:
                        if current_game_score > 0:
                            clear_score = st.form_submit_button("🗑️ Clear Score", type="secondary")
                        else:
                            clear_score = False
                    
                    if submit_score:
                        self.save_game_score(emp_id, participant_name, assigned_game, new_score, current_game_score, operator_username)
                    
                    if clear_score:
                        self.save_game_score(emp_id, participant_name, assigned_game, 0, current_game_score, operator_username)
        else:
            st.warning("No participants found matching your search.")
    
    def save_game_score(self, emp_id, participant_name, game_number, new_score, old_score, operator_username):
        """Save score for a specific game"""
        try:
            # Get current scores
            current_scores = self.db.get_user_scores(emp_id)
            
            if current_scores:
                # Update existing scores
                game_scores = {
                    'game1': current_scores.get('game1', 0),
                    'game2': current_scores.get('game2', 0),
                    'game3': current_scores.get('game3', 0),
                    'game4': current_scores.get('game4', 0),
                    'game5': current_scores.get('game5', 0)
                }
            else:
                # Initialize all games to 0
                game_scores = {
                    'game1': 0,
                    'game2': 0,
                    'game3': 0,
                    'game4': 0,
                    'game5': 0
                }
            
            # Update the specific game score
            game_scores[f'game{game_number}'] = new_score
            
            # Save to database
            success = self.db.update_scores(
                emp_id,
                game_scores['game1'],
                game_scores['game2'],
                game_scores['game3'],
                game_scores['game4'],
                game_scores['game5']
            )
            
            if success:
                # Log the entry
                self.logger.log_score_entry(
                    game_number, 
                    operator_username, 
                    emp_id, 
                    participant_name, 
                    new_score, 
                    old_score
                )
                
                if new_score == 0:
                    st.success(f"✅ Cleared Game {game_number} score for {participant_name}")
                else:
                    st.success(f"✅ Saved Game {game_number} score ({new_score}) for {participant_name}")
                st.rerun()
            else:
                st.error("❌ Failed to save score. Please try again.")
                
        except Exception as e:
            st.error(f"❌ Error saving score: {str(e)}")
    
    def show_current_scores(self, assigned_game, participants_df):
        """Show current scores for the assigned game"""
        st.subheader(f"Current Game {assigned_game} Scores")
        
        scores_df = self.db.get_all_scores()
        
        if not scores_df.empty:
            # Filter and prepare data for display
            game_column = f'game{assigned_game}'
            display_data = []
            
            for _, participant in participants_df.iterrows():
                emp_id = participant['emp_id']
                name = participant['name']
                
                # Get score for this participant
                participant_scores = scores_df[scores_df['emp_id'] == emp_id]
                if not participant_scores.empty:
                    game_score = participant_scores.iloc[0][game_column]
                    total_score = participant_scores.iloc[0]['total']
                else:
                    game_score = 0
                    total_score = 0
                
                display_data.append({
                    'Employee ID': emp_id,
                    'Name': name,
                    f'Game {assigned_game} Score': game_score,
                    'Total Score': total_score
                })
            
            # Convert to DataFrame and display
            display_df = pd.DataFrame(display_data)
            display_df = display_df.sort_values(f'Game {assigned_game} Score', ascending=False)
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_entries = len([d for d in display_data if d[f'Game {assigned_game} Score'] > 0])
                st.metric("Scores Entered", total_entries)
            with col2:
                pending_entries = len([d for d in display_data if d[f'Game {assigned_game} Score'] == 0])
                st.metric("Pending Entries", pending_entries)
            with col3:
                if total_entries > 0:
                    avg_score = sum([d[f'Game {assigned_game} Score'] for d in display_data]) / len(display_data)
                    st.metric("Average Score", f"{avg_score:.2f}")
            with col4:
                if total_entries > 0:
                    max_score = max([d[f'Game {assigned_game} Score'] for d in display_data])
                    st.metric("Highest Score", max_score)
        else:
            st.info("No scores entered yet.")
    
    def show_entry_log(self, assigned_game, operator_username):
        """Show entry log for the game operator"""
        st.subheader(f"Game {assigned_game} Entry Log")
        
        # Get entries for this game
        entries = self.logger.get_entries_by_game(assigned_game)
        
        if entries:
            # Convert to DataFrame for display
            log_data = []
            for entry in entries:
                log_data.append({
                    'Timestamp': entry['timestamp'][:19].replace('T', ' '),
                    'Participant': f"{entry['participant_name']} ({entry['participant_emp_id']})",
                    'Operator': entry['operator'],
                    'Action': entry['action'].title(),
                    'New Score': entry['new_score'],
                    'Previous Score': entry.get('old_score', 'N/A')
                })
            
            log_df = pd.DataFrame(log_data)
            st.dataframe(log_df, use_container_width=True, height=400)
            
            # Show only this operator's entries
            st.write("#### Your Recent Entries")
            operator_entries = self.logger.get_entries_by_operator(operator_username)
            if operator_entries:
                recent_operator_data = []
                for entry in operator_entries[:10]:  # Last 10 entries
                    recent_operator_data.append({
                        'Time': entry['timestamp'][:19].replace('T', ' '),
                        'Participant': entry['participant_name'],
                        'Game': entry['game_number'],
                        'Score': entry['new_score']
                    })
                
                recent_df = pd.DataFrame(recent_operator_data)
                st.dataframe(recent_df, use_container_width=True)
            else:
                st.info("No entries recorded yet.")
        else:
            st.info("No scoring activity recorded yet for this game.")
