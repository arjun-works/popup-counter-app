import streamlit as st
from auth import Authentication

class UserDashboard:
    def __init__(self, database):
        self.db = database
        self.auth = Authentication()
    
    def show_dashboard(self, username):
        """Display user dashboard"""
        st.subheader("🏠 Your Dashboard")
        
        # Get user info
        user_info = self.auth.get_user_info(username)
        if not user_info:
            st.error("User information not found!")
            return
        
        emp_id = user_info.get('emp_id')
        user_name = user_info.get('name')
        
        # Welcome message
        st.markdown(f"### Welcome back, **{user_name}**! 👋")
        st.markdown(f"**Employee ID:** {emp_id}")
        st.markdown("---")
        
        # Get user scores
        user_scores = self.db.get_user_scores(emp_id)
        
        if user_scores:
            self.show_user_scores(user_scores)
        else:
            self.show_no_scores_message()
        
        # Show user rank
        self.show_user_rank(emp_id)
    
    def show_user_scores(self, scores):
        """Display user scores"""
        st.subheader("🎮 Your Game Scores")
        
        # Score cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        games = [
            ("Game 1", scores['game1'], col1),
            ("Game 2", scores['game2'], col2),
            ("Game 3", scores['game3'], col3),
            ("Game 4", scores['game4'], col4),
            ("Game 5", scores['game5'], col5)
        ]
        
        for game_name, score, col in games:
            with col:
                st.markdown(f"""
                <div class="score-card">
                    <h3>{game_name}</h3>
                    <h2>{score}/10</h2>
                </div>
                """, unsafe_allow_html=True)
        
        # Total score and gift
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="score-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <h2>Total Score</h2>
                <h1>{scores['total']}/50</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            gift_type = scores['gift_type']
            gift_styles = {
                'Gold': 'gold-gift',
                'Silver': 'silver-gift',
                'Participation': 'participation-gift'
            }
            gift_emojis = {
                'Gold': '🏆',
                'Silver': '🥈',
                'Participation': '🎁'
            }
            
            st.markdown(f"""
            <div class="gift-card {gift_styles.get(gift_type, 'participation-gift')}">
                <h2>Your Gift</h2>
                <h1>{gift_emojis.get(gift_type, '🎁')} {gift_type}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        # Performance visualization
        st.subheader("📊 Your Performance")
        
        # Create performance chart
        import plotly.graph_objects as go
        
        game_names = ['Game 1', 'Game 2', 'Game 3', 'Game 4', 'Game 5']
        game_scores = [scores['game1'], scores['game2'], scores['game3'], scores['game4'], scores['game5']]
        
        fig = go.Figure()
        
        # Add user scores
        fig.add_trace(go.Bar(
            x=game_names,
            y=game_scores,
            name='Your Scores',
            marker_color='lightblue',
            text=game_scores,
            textposition='auto',
        ))
        
        # Add maximum possible scores
        fig.add_trace(go.Bar(
            x=game_names,
            y=[10] * 5,
            name='Maximum Score',
            marker_color='lightgray',
            opacity=0.3
        ))
        
        fig.update_layout(
            title='Your Game Performance',
            xaxis_title='Games',
            yaxis_title='Score',
            yaxis=dict(range=[0, 10]),
            barmode='overlay',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True, key="user_performance_chart")
        
        # Achievement badges
        self.show_achievement_badges(scores)
        
        # Performance insights
        self.show_performance_insights(scores)
    
    def show_no_scores_message(self):
        """Display message when user has no scores"""
        st.info("🎮 Your scores haven't been entered yet. Check back soon!")
        
        # Show placeholder cards
        st.subheader("🎯 Games Overview")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        for i, col in enumerate([col1, col2, col3, col4, col5], 1):
            with col:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 1rem;
                    border-radius: 10px;
                    text-align: center;
                    margin: 0.5rem 0;
                    color: #666;
                ">
                    <h3>Game {i}</h3>
                    <h2>--/10</h2>
                </div>
                """, unsafe_allow_html=True)
        
        # Motivational message
        st.markdown("""
        ### 🚀 Get Ready!
        
        Your gaming adventure is about to begin! Here's what you can expect:
        
        - **5 Exciting Games** to test your skills
        - **Gold, Silver, or Participation Gifts** based on your performance
        - **Real-time Leaderboard** to track your progress
        - **Instant Results** once scores are entered
        
        Good luck and have fun! 🎉
        """)
    
    def show_user_rank(self, emp_id):
        """Show user's current rank"""
        all_scores = self.db.get_all_scores()
        
        if not all_scores.empty and emp_id in all_scores['emp_id'].values:
            # Sort by total score and find user's rank
            sorted_scores = all_scores.sort_values('total', ascending=False).reset_index(drop=True)
            user_rank = sorted_scores[sorted_scores['emp_id'] == emp_id].index[0] + 1
            total_participants = len(sorted_scores)
            
            st.subheader("🏅 Your Ranking")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Rank", f"#{user_rank}")
            
            with col2:
                st.metric("Out of", f"{total_participants} participants")
            
            with col3:
                percentile = (total_participants - user_rank + 1) / total_participants * 100
                st.metric("Percentile", f"{percentile:.1f}%")
            
            # Rank visualization
            if user_rank <= 3:
                rank_emoji = ["🥇", "🥈", "🥉"][user_rank - 1]
                st.success(f"{rank_emoji} Congratulations! You're in the top 3!")
            elif user_rank <= total_participants * 0.1:
                st.success("🌟 Great job! You're in the top 10%!")
            elif user_rank <= total_participants * 0.25:
                st.info("👏 Well done! You're in the top 25%!")
            else:
                st.info("Keep going! There's always room for improvement! 💪")
    
    def show_achievement_badges(self, scores):
        """Show achievement badges based on performance"""
        st.subheader("🏆 Achievements")
        
        achievements = []
        
        # Score-based achievements
        if scores['total'] >= 40:
            achievements.append(("🏆", "Gold Champion", "Scored 40+ points"))
        elif scores['total'] >= 30:
            achievements.append(("🥈", "Silver Star", "Scored 30+ points"))
        else:
            achievements.append(("🎁", "Participant", "Joined the event"))
        
        # Game-specific achievements
        perfect_games = sum(1 for game in ['game1', 'game2', 'game3', 'game4', 'game5'] if scores[game] == 10)
        if perfect_games > 0:
            achievements.append(("🎯", "Perfect Shot", f"Perfect score in {perfect_games} game(s)"))
        
        # Consistency achievement
        game_scores = [scores['game1'], scores['game2'], scores['game3'], scores['game4'], scores['game5']]
        if max(game_scores) - min(game_scores) <= 2:
            achievements.append(("⚖️", "Consistent Player", "Balanced performance across games"))
        
        # High scorer
        if scores['total'] >= 45:
            achievements.append(("🚀", "High Flyer", "Exceptional performance"))
        
        # Display achievements
        cols = st.columns(len(achievements))
        for i, (emoji, title, description) in enumerate(achievements):
            with cols[i]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem;
                    border-radius: 10px;
                    text-align: center;
                    color: white;
                    margin: 0.5rem 0;
                ">
                    <div style="font-size: 2rem;">{emoji}</div>
                    <div style="font-weight: bold; margin: 0.5rem 0;">{title}</div>
                    <div style="font-size: 0.8rem; opacity: 0.9;">{description}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def show_performance_insights(self, scores):
        """Show performance insights and tips"""
        st.subheader("💡 Performance Insights")
        
        game_scores = [scores['game1'], scores['game2'], scores['game3'], scores['game4'], scores['game5']]
        
        # Find best and worst performing games
        best_game = game_scores.index(max(game_scores)) + 1
        worst_game = game_scores.index(min(game_scores)) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"🌟 **Strongest Game:** Game {best_game} ({max(game_scores)}/10)")
            if max(game_scores) == 10:
                st.write("Perfect score! 🎯")
            elif max(game_scores) >= 8:
                st.write("Excellent performance! 👏")
            else:
                st.write("Good job! Keep it up! 💪")
        
        with col2:
            if min(game_scores) < max(game_scores):
                st.info(f"🎯 **Growth Area:** Game {worst_game} ({min(game_scores)}/10)")
                if min(game_scores) < 5:
                    st.write("Room for improvement! 📈")
                else:
                    st.write("Still a solid performance! 👍")
            else:
                st.success("🎉 **Consistent Performance** across all games!")
        
        # Overall assessment
        if scores['total'] >= 40:
            st.success("🏆 **Outstanding Performance!** You've earned the Gold gift!")
        elif scores['total'] >= 30:
            st.info("🥈 **Great Performance!** You've earned the Silver gift!")
        else:
            st.info("🎁 **Thanks for Participating!** Every participant is a winner!")
        
        # Improvement suggestions
        if scores['total'] < 40:
            points_needed = 40 - scores['total']
            st.write(f"💪 **Tip:** You need {points_needed} more points to reach Gold level!")
        
        # Average comparison
        all_scores = self.db.get_all_scores()
        if not all_scores.empty and len(all_scores) > 1:
            avg_score = all_scores['total'].mean()
            if scores['total'] > avg_score:
                st.success(f"📊 You're performing above average! (Avg: {avg_score:.1f})")
            elif scores['total'] == avg_score:
                st.info(f"📊 You're performing at the average level! (Avg: {avg_score:.1f})")
            else:
                st.info(f"📊 Average score is {avg_score:.1f}. You can catch up! 🚀")
