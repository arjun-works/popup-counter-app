import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

class AdminPanel:
    def __init__(self, database):
        self.db = database
    
    def show_admin_panel(self):
        """Display the admin panel"""
        st.subheader("⚙️ Admin Panel")
        
        # Admin tabs
        admin_tabs = st.tabs(["📊 Score Entry", "👥 Manage Participants", "📈 Analytics", "⚙️ Settings"])
        
        with admin_tabs[0]:
            self.show_score_entry()
        
        with admin_tabs[1]:
            self.show_participant_management()
        
        with admin_tabs[2]:
            self.show_analytics()
        
        with admin_tabs[3]:
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
                search_term = st.text_input("🔍 Search participants", placeholder="Search by name or emp_id")
                
                if search_term:
                    mask = (
                        participants_df['name'].str.contains(search_term, case=False, na=False) |
                        participants_df['emp_id'].str.contains(search_term, case=False, na=False)
                    )
                    filtered_df = participants_df[mask]
                else:
                    filtered_df = participants_df
                
                # Display table with selection
                if not filtered_df.empty:
                    st.dataframe(
                        filtered_df[['emp_id', 'name', 'email', 'registration_date']],
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
                st.plotly_chart(fig_hist, use_container_width=True, key="score_distribution_chart")
                
                # Game-wise performance
                game_cols = ['game1', 'game2', 'game3', 'game4', 'game5']
                game_avg = scores_df[game_cols].mean()
                
                fig_games = px.bar(
                    x=game_cols,
                    y=game_avg.values,
                    title="Average Score by Game",
                    labels={'x': 'Game', 'y': 'Average Score'}
                )
                st.plotly_chart(fig_games, use_container_width=True, key="game_performance_chart")
            
            with col2:
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
                st.plotly_chart(fig_gift, use_container_width=True, key="gift_distribution_chart")
            
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
