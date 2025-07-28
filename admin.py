import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from game_config import GameConfigManager, GameOperatorManager

class AdminPanel:
    def __init__(self, database, auth_system):
        self.db = database
        self.auth = auth_system
        self.game_config = GameConfigManager()
        self.operator_manager = GameOperatorManager(auth_system)
    
    def show_admin_panel(self):
        """Display the admin panel"""
        st.subheader("⚙️ Admin Panel")
        
        # Admin tabs
        admin_tabs = st.tabs([
            "📊 Score Entry", 
            "👥 Manage Participants", 
            "🎮 Game Configuration",
            "🎯 Game Operators", 
            "📈 Analytics", 
            "⚙️ Settings"
        ])
        
        with admin_tabs[0]:
            self.show_score_entry()
        
        with admin_tabs[1]:
            self.show_participant_management()
        
        with admin_tabs[2]:
            self.show_game_configuration()
        
        with admin_tabs[3]:
            self.show_game_operators_management()
        
        with admin_tabs[4]:
            self.show_analytics()
        
        with admin_tabs[5]:
            self.show_settings()
    
    def show_score_entry(self):
        """Score entry interface"""
        st.write("### 🎮 Game Score Entry")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Score entry form
            with st.form("score_entry_form"):
                st.write("Enter scores for a participant:")
                
                # Get all participants for dropdown
                participants = self.db.get_all_participants()
                if not participants.empty:
                    participant_options = []
                    for _, p in participants.iterrows():
                        participant_options.append(f"{p['emp_id']} - {p['name']}")
                    
                    selected_participant = st.selectbox(
                        "Select Participant",
                        options=participant_options
                    )
                    
                    if selected_participant:
                        emp_id = selected_participant.split(' - ')[0]
                        
                        # Game score inputs
                        col_g1, col_g2, col_g3, col_g4, col_g5 = st.columns(5)
                        
                        with col_g1:
                            game1 = st.number_input("Game 1", min_value=0, max_value=10, value=0)
                        with col_g2:
                            game2 = st.number_input("Game 2", min_value=0, max_value=10, value=0)
                        with col_g3:
                            game3 = st.number_input("Game 3", min_value=0, max_value=10, value=0)
                        with col_g4:
                            game4 = st.number_input("Game 4", min_value=0, max_value=10, value=0)
                        with col_g5:
                            game5 = st.number_input("Game 5", min_value=0, max_value=10, value=0)
                        
                        # Calculate total and gift type preview
                        total = game1 + game2 + game3 + game4 + game5
                        gift_type = self.db.calculate_gift_type(total)
                        
                        col_total, col_gift = st.columns(2)
                        with col_total:
                            st.info(f"**Total Score:** {total}")
                        with col_gift:
                            gift_color = {"Gold": "🟡", "Silver": "⚪", "Participation": "🔵"}
                            st.info(f"**Gift Type:** {gift_color.get(gift_type, '🎁')} {gift_type}")
                        
                        if st.form_submit_button("💾 Save Scores", type="primary"):
                            if self.db.update_scores(emp_id, game1, game2, game3, game4, game5):
                                st.success(f"✅ Scores updated successfully for {selected_participant}!")
                                st.rerun()
                            else:
                                st.error("❌ Error updating scores. Please try again.")
                else:
                    st.warning("No participants found. Please register participants first.")
        
        with col2:
            # Quick score overview
            st.write("### 📋 Recent Scores")
            scores_df = self.db.get_all_scores()
            if not scores_df.empty:
                # Show last 5 updated scores
                recent_scores = scores_df.sort_values('last_updated', ascending=False).head(5)
                for _, score in recent_scores.iterrows():
                    with st.container():
                        st.write(f"**{score['name']}** ({score['emp_id']})")
                        st.write(f"Score: {score['total']} | Gift: {score['gift_type']}")
                        st.write("---")
            else:
                st.info("No scores entered yet.")
    
    def show_participant_management(self):
        """Participant management interface"""
        st.write("### 👥 Participant Management")
        
        participants_df = self.db.get_all_participants()
        
        if not participants_df.empty:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Display participants table
                st.write("#### Registered Participants")
                
                # Add search functionality
                search_term = st.text_input("🔍 Search participants", placeholder="Search by name, emp_id, or department")
                
                if search_term:
                    mask = (
                        participants_df['name'].str.contains(search_term, case=False, na=False) |
                        participants_df['emp_id'].str.contains(search_term, case=False, na=False) |
                        participants_df['department'].str.contains(search_term, case=False, na=False)
                    )
                    filtered_df = participants_df[mask]
                else:
                    filtered_df = participants_df
                
                # Display table with selection
                if not filtered_df.empty:
                    st.dataframe(
                        filtered_df[['emp_id', 'name', 'email', 'department', 'registration_date']],
                        use_container_width=True,
                        height=400
                    )
                    
                    # Bulk operations
                    st.write("#### Bulk Operations")
                    selected_participants = st.multiselect(
                        "Select participants for bulk operations",
                        options=filtered_df['emp_id'].tolist(),
                        format_func=lambda x: f"{x} - {filtered_df[filtered_df['emp_id']==x]['name'].iloc[0]}"
                    )
                    
                    if selected_participants:
                        col_bulk1, col_bulk2 = st.columns(2)
                        
                        with col_bulk1:
                            if st.button("📧 Send Bulk Email", help="Send email to selected participants"):
                                st.info("Bulk email feature will be implemented")
                        
                        with col_bulk2:
                            if st.button("🗑️ Delete Selected", help="Delete selected participants", type="secondary"):
                                if st.session_state.get('confirm_bulk_delete', False):
                                    for emp_id in selected_participants:
                                        self.db.delete_participant(emp_id)
                                    st.success(f"Deleted {len(selected_participants)} participants")
                                    st.rerun()
                                else:
                                    st.session_state['confirm_bulk_delete'] = True
                                    st.warning("Click again to confirm deletion")
                else:
                    st.info("No participants match your search criteria.")
            
            with col2:
                # Statistics
                st.write("#### 📊 Statistics")
                stats = self.db.get_statistics()
                
                st.metric("Total Registered", stats['total_participants'])
                st.metric("Scored Participants", stats['total_scored'])
                st.metric("Pending Scores", stats['total_participants'] - stats['total_scored'])
                
                # Department distribution
                dept_counts = participants_df['department'].value_counts()
                fig_dept = px.pie(
                    values=dept_counts.values,
                    names=dept_counts.index,
                    title="Department Distribution",
                    height=300
                )
                st.plotly_chart(fig_dept, use_container_width=True)
                
                # Export options
                st.write("#### 📤 Export Data")
                if st.button("📊 Export to Excel", help="Export all data to Excel"):
                    excel_buffer = self.db.export_data_to_excel()
                    if excel_buffer:
                        st.download_button(
                            label="📥 Download Excel File",
                            data=excel_buffer,
                            file_name=f"event_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        else:
            st.info("No participants registered yet.")
    
    def show_analytics(self):
        """Analytics dashboard"""
        st.write("### 📈 Analytics Dashboard")
        
        scores_df = self.db.get_all_scores()
        participants_df = self.db.get_all_participants()
        
        if not scores_df.empty:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Participants", len(participants_df))
            with col2:
                st.metric("Average Score", f"{scores_df['total'].mean():.1f}")
            with col3:
                st.metric("Participation Rate", f"{len(scores_df)/len(participants_df)*100:.1f}%")
            with col4:
                st.metric("Gold Winners", len(scores_df[scores_df['gift_type'] == 'Gold']))
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Score distribution histogram
                fig_hist = px.histogram(
                    scores_df,
                    x='total',
                    nbins=20,
                    title="Score Distribution",
                    labels={'total': 'Total Score', 'count': 'Number of Participants'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Game-wise performance
                game_cols = ['game1', 'game2', 'game3', 'game4', 'game5']
                game_avg = scores_df[game_cols].mean()
                
                fig_games = px.bar(
                    x=game_cols,
                    y=game_avg.values,
                    title="Average Score by Game",
                    labels={'x': 'Game', 'y': 'Average Score'}
                )
                st.plotly_chart(fig_games, use_container_width=True)
            
            with col2:
                # Department performance
                if not participants_df.empty:
                    dept_scores = scores_df.merge(
                        participants_df[['emp_id', 'department']], 
                        on='emp_id', 
                        how='left'
                    )
                    dept_avg = dept_scores.groupby('department')['total'].mean().sort_values(ascending=False)
                    
                    fig_dept = px.bar(
                        x=dept_avg.index,
                        y=dept_avg.values,
                        title="Average Score by Department",
                        labels={'x': 'Department', 'y': 'Average Score'}
                    )
                    st.plotly_chart(fig_dept, use_container_width=True)
                
                # Gift type distribution over time
                gift_counts = scores_df['gift_type'].value_counts()
                fig_gift = px.pie(
                    values=gift_counts.values,
                    names=gift_counts.index,
                    title="Gift Distribution",
                    color_discrete_map={
                        'Gold': '#FFD700',
                        'Silver': '#C0C0C0',
                        'Participation': '#87CEEB'
                    }
                )
                st.plotly_chart(fig_gift, use_container_width=True)
            
            # Detailed performance analysis
            st.write("#### 🎯 Detailed Performance Analysis")
            
            # Top performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🏆 Top 10 Performers**")
                top_performers = scores_df.nlargest(10, 'total')[['name', 'total', 'gift_type']]
                st.dataframe(top_performers, use_container_width=True, hide_index=True)
            
            with col2:
                st.write("**📊 Score Range Analysis**")
                score_ranges = pd.cut(
                    scores_df['total'], 
                    bins=[0, 20, 30, 40, 50], 
                    labels=['0-19', '20-29', '30-39', '40+']
                ).value_counts()
                
                for range_name, count in score_ranges.items():
                    st.write(f"**{range_name} points:** {count} participants")
        
        else:
            st.info("No score data available for analytics. Start adding scores to see insights!")
    
    def show_settings(self):
        """Settings and configuration"""
        st.write("### ⚙️ System Settings")
        
        # Scoring configuration
        st.write("#### 🎯 Scoring Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Gift Thresholds**")
            gold_threshold = st.number_input("Gold Gift Threshold", value=40, min_value=0, max_value=50)
            silver_threshold = st.number_input("Silver Gift Threshold", value=30, min_value=0, max_value=50)
            
            if st.button("💾 Update Thresholds"):
                st.success("Thresholds updated! (Feature to be implemented)")
        
        with col2:
            st.write("**Game Configuration**")
            max_score_per_game = st.number_input("Max Score per Game", value=10, min_value=1, max_value=20)
            number_of_games = st.number_input("Number of Games", value=5, min_value=1, max_value=10)
            
            if st.button("🎮 Update Game Config"):
                st.success("Game configuration updated! (Feature to be implemented)")
        
        # Data management
        st.write("#### 🗄️ Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Backup Data", help="Create a backup of all data"):
                excel_buffer = self.db.export_data_to_excel()
                if excel_buffer:
                    st.download_button(
                        label="📥 Download Backup",
                        data=excel_buffer,
                        file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        with col2:
            if st.button("🗑️ Clear All Scores", help="Delete all score data"):
                if st.session_state.get('confirm_clear_scores', False):
                    # Clear scores logic would go here
                    st.success("All scores cleared!")
                    st.session_state['confirm_clear_scores'] = False
                else:
                    st.session_state['confirm_clear_scores'] = True
                    st.warning("Click again to confirm clearing all scores")
        
        with col3:
            if st.button("⚠️ Reset System", help="Reset entire system", type="secondary"):
                if st.session_state.get('confirm_reset', False):
                    st.error("System reset confirmed! (Feature to be implemented)")
                    st.session_state['confirm_reset'] = False
                else:
                    st.session_state['confirm_reset'] = True
                    st.warning("⚠️ This will delete ALL data. Click again to confirm.")
        
        # System information
        st.write("#### ℹ️ System Information")
        stats = self.db.get_statistics()
        
        info_data = {
            'Metric': [
                'Total Participants',
                'Participants with Scores',
                'Average Score',
                'Highest Score',
                'Gold Winners',
                'Silver Winners',
                'Participation Gifts',
                'Last Updated'
            ],
            'Value': [
                stats['total_participants'],
                stats['total_scored'],
                stats['average_score'],
                stats['highest_score'],
                stats['gold_winners'],
                stats['silver_winners'],
                stats['participation_gifts'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        info_df = pd.DataFrame(info_data)
        st.dataframe(info_df, use_container_width=True, hide_index=True)
    
    def show_game_configuration(self):
        """Game configuration management"""
        st.write("### 🎮 Game Configuration Management")
        
        config = self.game_config.load_config()
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Games", config['total_games'])
        with col2:
            active_games = len([g for g in config['games'].values() if g.get('active')])
            st.metric("Active Games", active_games)
        with col3:
            points_games = len([g for g in config['games'].values() if g.get('scoring_type') == 'points'])
            st.metric("Points-based", points_games)
        with col4:
            win_lose_games = len([g for g in config['games'].values() if g.get('scoring_type') == 'win_lose'])
            st.metric("Win/Lose", win_lose_games)
        
        # Configuration tabs
        config_tabs = st.tabs(["📝 Manage Games", "➕ Add New Game", "🏆 Gift Thresholds", "📋 Game Templates"])
        
        with config_tabs[0]:
            self.show_existing_games()
        
        with config_tabs[1]:
            self.show_add_new_game()
        
        with config_tabs[2]:
            self.show_gift_thresholds()
        
        with config_tabs[3]:
            self.show_game_templates()
    
    def show_existing_games(self):
        """Show and manage existing games"""
        st.write("#### 📝 Existing Games Configuration")
        
        config = self.game_config.load_config()
        
        if not config['games']:
            st.info("No games configured yet. Add a new game to get started.")
            return
        
        # Display games in a table format
        games_data = []
        for game_num, game_data in config['games'].items():
            games_data.append({
                'Game #': game_num,
                'Name': game_data['name'],
                'Scoring Type': game_data['scoring_type'].replace('_', ' ').title(),
                'Max Points': game_data.get('max_points', 'N/A'),
                'Win Points': game_data.get('win_points', 'N/A'),
                'Lose Points': game_data.get('lose_points', 'N/A'),
                'Status': '🟢 Active' if game_data.get('active') else '🔴 Inactive',
                'Description': game_data.get('description', '')[:50] + ('...' if len(game_data.get('description', '')) > 50 else '')
            })
        
        games_df = pd.DataFrame(games_data)
        st.dataframe(games_df, use_container_width=True, height=300)
        
        # Game modification section
        st.write("#### ✏️ Modify Game Configuration")
        
        game_to_edit = st.selectbox(
            "Select game to modify",
            options=list(config['games'].keys()),
            format_func=lambda x: f"Game {x}: {config['games'][x]['name']}"
        )
        
        if game_to_edit:
            game_data = config['games'][game_to_edit]
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Game Name", value=game_data['name'])
                new_scoring_type = st.selectbox(
                    "Scoring Type",
                    options=['points', 'win_lose'],
                    index=0 if game_data['scoring_type'] == 'points' else 1,
                    format_func=lambda x: 'Points (0-100)' if x == 'points' else 'Win/Lose'
                )
                new_description = st.text_area("Description", value=game_data.get('description', ''))
            
            with col2:
                if new_scoring_type == 'points':
                    new_max_points = st.number_input(
                        "Maximum Points",
                        min_value=1, max_value=100,
                        value=game_data.get('max_points', 10)
                    )
                    new_win_points = new_max_points
                    new_lose_points = 0
                else:
                    new_max_points = st.number_input(
                        "Points for Win",
                        min_value=1, max_value=100,
                        value=game_data.get('win_points', 10)
                    )
                    new_win_points = new_max_points
                    new_lose_points = st.number_input(
                        "Points for Loss",
                        min_value=0, max_value=50,
                        value=game_data.get('lose_points', 0)
                    )
                
                new_active = st.checkbox("Game Active", value=game_data.get('active', True))
            
            col_update, col_delete = st.columns(2)
            
            with col_update:
                if st.button(f"🔄 Update Game {game_to_edit}", type="primary"):
                    updated_config = {
                        'name': new_name,
                        'scoring_type': new_scoring_type,
                        'max_points': new_max_points,
                        'win_points': new_win_points,
                        'lose_points': new_lose_points,
                        'description': new_description,
                        'active': new_active
                    }
                    
                    if self.game_config.update_game_config(int(game_to_edit), updated_config):
                        st.success(f"✅ Game {game_to_edit} updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update game configuration")
            
            with col_delete:
                if st.button(f"🗑️ Delete Game {game_to_edit}", type="secondary"):
                    if st.session_state.get(f'confirm_delete_game_{game_to_edit}', False):
                        if self.game_config.remove_game(int(game_to_edit)):
                            st.success(f"✅ Game {game_to_edit} deleted successfully!")
                            st.session_state[f'confirm_delete_game_{game_to_edit}'] = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete game")
                    else:
                        st.session_state[f'confirm_delete_game_{game_to_edit}'] = True
                        st.warning("⚠️ Click again to confirm deletion")
    
    def show_add_new_game(self):
        """Add new game configuration"""
        st.write("#### ➕ Add New Game")
        
        config = self.game_config.load_config()
        existing_game_numbers = [int(k) for k in config['games'].keys()]
        next_game_number = max(existing_game_numbers) + 1 if existing_game_numbers else 1
        
        with st.form("add_new_game_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                game_number = st.number_input(
                    "Game Number",
                    min_value=1, max_value=20,
                    value=next_game_number
                )
                
                game_name = st.text_input(
                    "Game Name",
                    value=f"Game {game_number}",
                    placeholder="Enter game name"
                )
                
                scoring_type = st.selectbox(
                    "Scoring Type",
                    options=['points', 'win_lose'],
                    format_func=lambda x: 'Points (0-100)' if x == 'points' else 'Win/Lose'
                )
            
            with col2:
                if scoring_type == 'points':
                    max_points = st.number_input(
                        "Maximum Points",
                        min_value=1, max_value=100,
                        value=10
                    )
                    win_points = max_points
                    lose_points = 0
                    
                    st.info(f"Points scoring: 0 to {max_points} points")
                else:
                    win_points = st.number_input(
                        "Points for Win",
                        min_value=1, max_value=100,
                        value=10
                    )
                    lose_points = st.number_input(
                        "Points for Loss",
                        min_value=0, max_value=50,
                        value=0
                    )
                    max_points = win_points
                    
                    st.info(f"Win/Lose scoring: {win_points} for win, {lose_points} for loss")
            
            description = st.text_area(
                "Game Description",
                placeholder="Describe the game activity..."
            )
            
            submitted = st.form_submit_button("➕ Add Game", type="primary")
            
            if submitted:
                # Validate inputs
                if not game_name.strip():
                    st.error("❌ Game name is required")
                elif game_number in existing_game_numbers:
                    st.error(f"❌ Game {game_number} already exists")
                else:
                    # Add the game
                    if self.game_config.add_new_game(
                        game_number, game_name, scoring_type,
                        max_points, win_points, lose_points, description
                    ):
                        st.success(f"✅ Game {game_number}: {game_name} added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add game")
    
    def show_gift_thresholds(self):
        """Configure gift thresholds"""
        st.write("#### 🏆 Gift Threshold Configuration")
        
        config = self.game_config.load_config()
        current_thresholds = config['gift_thresholds']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current Thresholds**")
            st.metric("🏆 Gold Gift", f"{current_thresholds['gold']}+ points")
            st.metric("🥈 Silver Gift", f"{current_thresholds['silver']}-{current_thresholds['gold']-1} points")
            st.metric("🎁 Participation", f"0-{current_thresholds['silver']-1} points")
        
        with col2:
            st.write("**Update Thresholds**")
            
            with st.form("update_thresholds_form"):
                gold_threshold = st.number_input(
                    "Gold Gift Threshold",
                    min_value=1, max_value=100,
                    value=current_thresholds['gold']
                )
                
                silver_threshold = st.number_input(
                    "Silver Gift Threshold",
                    min_value=1, max_value=gold_threshold-1,
                    value=current_thresholds['silver']
                )
                
                # Preview
                st.write("**Preview:**")
                st.info(f"🏆 Gold: {gold_threshold}+ points")
                st.info(f"🥈 Silver: {silver_threshold}-{gold_threshold-1} points")
                st.info(f"🎁 Participation: 0-{silver_threshold-1} points")
                
                if st.form_submit_button("🔄 Update Thresholds", type="primary"):
                    if self.game_config.update_gift_thresholds(gold_threshold, silver_threshold):
                        st.success("✅ Gift thresholds updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update thresholds")
        
        # Show impact analysis
        st.write("#### 📊 Threshold Impact Analysis")
        scores_df = self.db.get_all_scores()
        
        if not scores_df.empty:
            # Calculate current distribution
            gold_count = len(scores_df[scores_df['total'] >= current_thresholds['gold']])
            silver_count = len(scores_df[
                (scores_df['total'] >= current_thresholds['silver']) & 
                (scores_df['total'] < current_thresholds['gold'])
            ])
            participation_count = len(scores_df[scores_df['total'] < current_thresholds['silver']])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏆 Gold Winners", gold_count)
            with col2:
                st.metric("🥈 Silver Winners", silver_count)
            with col3:
                st.metric("🎁 Participation", participation_count)
        else:
            st.info("No scores available for impact analysis")
    
    def show_game_templates(self):
        """Show predefined game templates"""
        st.write("#### 📋 Game Templates")
        st.info("Quick setup with predefined game configurations")
        
        templates = {
            "Quiz Competition": {
                "games": 5,
                "scoring": "points",
                "max_points": 20,
                "description": "Knowledge-based quiz games"
            },
            "Sports Tournament": {
                "games": 8,
                "scoring": "win_lose", 
                "win_points": 15,
                "lose_points": 5,
                "description": "Win/lose sports activities"
            },
            "Skill Challenge": {
                "games": 3,
                "scoring": "points",
                "max_points": 100,
                "description": "High-stakes skill-based challenges"
            },
            "Team Building": {
                "games": 6,
                "scoring": "win_lose",
                "win_points": 10,
                "lose_points": 7,
                "description": "Collaborative team activities"
            }
        }
        
        selected_template = st.selectbox(
            "Choose a template",
            options=list(templates.keys()),
            help="Select a template to auto-configure games"
        )
        
        if selected_template:
            template = templates[selected_template]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{selected_template} Template**")
                st.write(f"• **Games:** {template['games']}")
                st.write(f"• **Scoring:** {template['scoring'].replace('_', ' ').title()}")
                if template['scoring'] == 'points':
                    st.write(f"• **Max Points:** {template['max_points']}")
                else:
                    st.write(f"• **Win Points:** {template['win_points']}")
                    st.write(f"• **Lose Points:** {template['lose_points']}")
                st.write(f"• **Description:** {template['description']}")
            
            with col2:
                if st.button(f"🚀 Apply {selected_template} Template", type="primary"):
                    if st.session_state.get(f'confirm_template_{selected_template}', False):
                        # Apply template
                        config = self.game_config.load_config()
                        
                        # Clear existing games
                        config['games'] = {}
                        
                        # Add games from template
                        for i in range(1, template['games'] + 1):
                            if template['scoring'] == 'points':
                                self.game_config.add_new_game(
                                    i, f"Game {i}", template['scoring'],
                                    template['max_points'], template['max_points'], 0,
                                    f"{template['description']} - Activity {i}"
                                )
                            else:
                                self.game_config.add_new_game(
                                    i, f"Game {i}", template['scoring'],
                                    template['win_points'], template['win_points'], 
                                    template['lose_points'],
                                    f"{template['description']} - Activity {i}"
                                )
                        
                        st.success(f"✅ {selected_template} template applied successfully!")
                        st.session_state[f'confirm_template_{selected_template}'] = False
                        st.rerun()
                    else:
                        st.session_state[f'confirm_template_{selected_template}'] = True
                        st.warning("⚠️ This will replace all existing games. Click again to confirm.")
    
    def show_game_operators_management(self):
        """Game operators management"""
        st.write("### 🎯 Game Operators Management")
        
        # Quick stats
        operators = self.operator_manager.get_all_game_operators()
        config = self.game_config.load_config()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Operators", len(operators))
        with col2:
            assigned_games = len([op for op in operators.values() if op.get('assigned_game')])
            st.metric("Assigned Games", assigned_games)
        with col3:
            st.metric("Total Games", len(config['games']))
        with col4:
            unassigned = len(config['games']) - assigned_games
            st.metric("Unassigned Games", unassigned)
        
        # Operator management tabs
        operator_tabs = st.tabs([
            "👥 Current Operators", 
            "➕ Create Operator", 
            "🔧 Bulk Operations", 
            "📊 Operator Analytics"
        ])
        
        with operator_tabs[0]:
            self.show_current_operators()
        
        with operator_tabs[1]:
            self.show_create_operator()
        
        with operator_tabs[2]:
            self.show_bulk_operations()
        
        with operator_tabs[3]:
            self.show_operator_analytics()
    
    def show_current_operators(self):
        """Show current game operators"""
        st.write("#### 👥 Current Game Operators")
        
        operators = self.operator_manager.get_all_game_operators()
        
        if not operators:
            st.info("No game operators found. Create operators to get started.")
            return
        
        # Display operators table
        operators_data = []
        for username, operator_data in operators.items():
            operators_data.append({
                'Username': username,
                'Name': operator_data['name'],
                'Assigned Game': operator_data.get('assigned_game', 'N/A'),
                'Employee ID': operator_data['emp_id'],
                'Email': operator_data['email'],
                'Created': operator_data.get('created_date', 'N/A')[:10] if operator_data.get('created_date') else 'N/A',
                'Status': '🟢 Active'
            })
        
        operators_df = pd.DataFrame(operators_data)
        st.dataframe(operators_df, use_container_width=True, height=300)
        
        # Operator actions
        st.write("#### ⚙️ Operator Actions")
        
        selected_operator = st.selectbox(
            "Select operator for actions",
            options=list(operators.keys()),
            format_func=lambda x: f"{x} - Game {operators[x].get('assigned_game', 'N/A')}"
        )
        
        if selected_operator:
            operator_data = operators[selected_operator]
            game_number = operator_data.get('assigned_game')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"🔑 Reset Password", help="Generate new password"):
                    if game_number:
                        new_password = self.operator_manager.generate_secure_password()
                        if self.operator_manager.update_operator_password(game_number, new_password):
                            st.success(f"✅ Password reset successfully!")
                            st.code(f"New password: {new_password}")
                        else:
                            st.error("❌ Failed to reset password")
            
            with col2:
                if st.button(f"📧 Send Credentials", help="Email login details"):
                    st.info("Email functionality will be implemented")
            
            with col3:
                if st.button(f"🗑️ Remove Operator", type="secondary"):
                    if st.session_state.get(f'confirm_remove_{selected_operator}', False):
                        if game_number and self.operator_manager.remove_game_operator(game_number):
                            st.success(f"✅ Operator {selected_operator} removed successfully!")
                            st.session_state[f'confirm_remove_{selected_operator}'] = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to remove operator")
                    else:
                        st.session_state[f'confirm_remove_{selected_operator}'] = True
                        st.warning("⚠️ Click again to confirm removal")
    
    def show_create_operator(self):
        """Create new game operator"""
        st.write("#### ➕ Create New Game Operator")
        
        config = self.game_config.load_config()
        operators = self.operator_manager.get_all_game_operators()
        
        # Find unassigned games
        assigned_games = [op.get('assigned_game') for op in operators.values()]
        available_games = [
            int(game_num) for game_num in config['games'].keys() 
            if int(game_num) not in assigned_games
        ]
        
        if not available_games:
            st.warning("⚠️ All games have assigned operators. Remove an operator or add more games first.")
            return
        
        with st.form("create_operator_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_game = st.selectbox(
                    "Assign to Game",
                    options=available_games,
                    format_func=lambda x: f"Game {x}: {config['games'][str(x)]['name']}"
                )
                
                operator_name = st.text_input(
                    "Operator Name",
                    value=f"Game {selected_game} Operator",
                    placeholder="Enter operator name"
                )
            
            with col2:
                use_custom_password = st.checkbox("Use custom password")
                
                if use_custom_password:
                    custom_password = st.text_input(
                        "Custom Password",
                        type="password",
                        placeholder="Enter custom password"
                    )
                else:
                    custom_password = None
                    st.info("🔐 Secure password will be auto-generated")
            
            submitted = st.form_submit_button("➕ Create Operator", type="primary")
            
            if submitted:
                if not operator_name.strip():
                    st.error("❌ Operator name is required")
                elif use_custom_password and not custom_password:
                    st.error("❌ Custom password is required")
                else:
                    success, result = self.operator_manager.create_game_operator(
                        selected_game, operator_name, custom_password
                    )
                    
                    if success:
                        st.success(f"✅ Operator created successfully!")
                        
                        # Display credentials
                        st.write("**📋 Operator Credentials:**")
                        credentials_col1, credentials_col2 = st.columns(2)
                        
                        with credentials_col1:
                            st.code(f"Username: {result['username']}")
                            st.code(f"Password: {result['password']}")
                        
                        with credentials_col2:
                            st.code(f"Name: {result['name']}")
                            st.code(f"Game: {selected_game}")
                        
                        st.warning("⚠️ Save these credentials securely. The password won't be shown again.")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
    
    def show_bulk_operations(self):
        """Bulk operations for operators"""
        st.write("#### 🔧 Bulk Operations")
        
        config = self.game_config.load_config()
        operators = self.operator_manager.get_all_game_operators()
        
        bulk_tabs = st.tabs(["🚀 Auto-Create All", "🔑 Reset All Passwords", "📧 Email All Credentials"])
        
        with bulk_tabs[0]:
            st.write("**Auto-Create Operators for All Games**")
            
            assigned_games = [op.get('assigned_game') for op in operators.values()]
            unassigned_games = [
                int(game_num) for game_num in config['games'].keys()
                if int(game_num) not in assigned_games
            ]
            
            if not unassigned_games:
                st.info("✅ All games already have assigned operators")
            else:
                st.write(f"Games without operators: {', '.join(map(str, unassigned_games))}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    use_default_names = st.checkbox("Use default names", value=True)
                    if not use_default_names:
                        st.info("Operators will be named 'Game X Operator'")
                
                with col2:
                    auto_generate_passwords = st.checkbox("Auto-generate passwords", value=True)
                    if not auto_generate_passwords:
                        st.info("Default password 'game123' will be used")
                
                if st.button("🚀 Create All Missing Operators", type="primary"):
                    passwords = None if auto_generate_passwords else {game: "game123" for game in unassigned_games}
                    
                    results = self.operator_manager.bulk_create_operators(unassigned_games, passwords)
                    
                    success_count = sum(1 for r in results if r['success'])
                    
                    if success_count > 0:
                        st.success(f"✅ Created {success_count} operators successfully!")
                        
                        # Display all credentials
                        st.write("**📋 All Operator Credentials:**")
                        for result in results:
                            if result['success']:
                                st.write(f"**Game {result['game']}:** `{result['username']}` / `{result['password']}`")
                        
                        st.warning("⚠️ Save these credentials securely!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create operators")
        
        with bulk_tabs[1]:
            st.write("**Reset All Operator Passwords**")
            
            if not operators:
                st.info("No operators found")
            else:
                st.write(f"This will reset passwords for {len(operators)} operators")
                
                if st.button("🔑 Reset All Passwords", type="secondary"):
                    if st.session_state.get('confirm_bulk_reset', False):
                        results = self.operator_manager.reset_all_operator_passwords()
                        success_count = sum(1 for r in results if r['success'])
                        
                        if success_count > 0:
                            st.success(f"✅ Reset {success_count} passwords successfully!")
                            
                            # Display new passwords
                            st.write("**🔑 New Passwords:**")
                            for result in results:
                                if result['success']:
                                    st.write(f"**{result['username']}:** `{result['new_password']}`")
                            
                            st.warning("⚠️ Save these new passwords securely!")
                        else:
                            st.error("❌ Failed to reset passwords")
                        
                        st.session_state['confirm_bulk_reset'] = False
                    else:
                        st.session_state['confirm_bulk_reset'] = True
                        st.warning("⚠️ Click again to confirm password reset for all operators")
        
        with bulk_tabs[2]:
            st.write("**Email Credentials to All Operators**")
            st.info("Email functionality will be implemented in the next update")
            
            if operators:
                st.write("**Current Operators:**")
                for username, operator_data in operators.items():
                    st.write(f"• {operator_data['name']} ({operator_data['email']})")
                
                if st.button("📧 Send All Credentials", disabled=True):
                    st.info("Email service integration coming soon")
    
    def show_operator_analytics(self):
        """Operator analytics and monitoring"""
        st.write("#### 📊 Operator Analytics")
        
        operators = self.operator_manager.get_all_game_operators()
        
        if not operators:
            st.info("No operators found for analytics")
            return
        
        # Activity tracking would be implemented with logging
        st.info("📈 Operator activity tracking will be available with logging system integration")
        
        # Current operator summary
        st.write("**Current Operator Summary:**")
        
        summary_data = []
        for username, operator_data in operators.items():
            game_num = operator_data.get('assigned_game')
            
            # This would be enhanced with actual activity data
            summary_data.append({
                'Operator': operator_data['name'],
                'Game': f"Game {game_num}",
                'Username': username,
                'Status': '🟢 Active',
                'Last Login': 'N/A',  # Would be tracked
                'Scores Entered': 'N/A',  # Would be tracked
                'Created': operator_data.get('created_date', 'N/A')[:10] if operator_data.get('created_date') else 'N/A'
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
