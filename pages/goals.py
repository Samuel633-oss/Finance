"""
Financial goals page for the Finance App.
"""

import streamlit as st
from datetime import date, datetime
from decimal import Decimal
from utils.database import fetch_all, execute_query
from utils.financial_calculations import (
    calculate_savings_progress, calculate_goal_contribution, format_currency
)


def show():
    """Show the goals page."""
    st.title("🎯 Financial Goals")
    
    user_id = st.session_state.current_user['id']
    
    # Create new goal
    with st.expander("➕ Create New Financial Goal", expanded=True):
        with st.form("create_goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Goal Name", value="Buy a House")
                target_amount = st.number_input("Target Amount (₦)", min_value=0.01, step=0.01, value=1000000.00)
            with col2:
                current_amount = st.number_input("Current Amount (₦)", min_value=0.0, step=0.01, value=0.0)
                target_date = st.date_input("Target Date")
            
            goal_type = st.selectbox("Goal Type", ["Short-term", "Medium-term", "Long-term"])
            description = st.text_input("Description")
            
            if st.form_submit_button("Create Goal"):
                execute_query(
                    """INSERT INTO financial_goals (user_id, name, target_amount, current_amount, target_date, goal_type, description) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, name, float(target_amount), float(current_amount),
                     target_date.isoformat(), goal_type, description)
                )
                st.success("Goal created successfully!")
                st.rerun()
    
    # Show goals
    st.subheader("📋 Your Financial Goals")
    
    goals = fetch_all("SELECT * FROM financial_goals WHERE user_id = ? ORDER BY target_date", (user_id,))
    
    if goals:
        for goal in goals:
            progress = calculate_savings_progress(
                Decimal(str(goal.get('target_amount', 0))),
                Decimal(str(goal.get('current_amount', 0)))
            )
            
            contribution = calculate_goal_contribution(
                Decimal(str(goal.get('target_amount', 0))),
                Decimal(str(goal.get('current_amount', 0))),
                datetime.strptime(goal.get('target_date', ''), '%Y-%m-%d').date()
            )
            
            with st.expander(f"🎯 {goal.get('name', 'Goal')}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Target", format_currency(Decimal(str(goal.get('target_amount', 0)))))
                col2.metric("Current", format_currency(Decimal(str(goal.get('current_amount', 0)))))
                col3.metric("Progress", f"{progress['progress_percent']:.1f}%")
                
                st.progress(float(progress['progress_percent']) / 100)
                
                if not progress['completed']:
                    st.write(f"**Time remaining:** {contribution['days_remaining']} days")
                    st.write(f"**To reach goal, save:**")
                    st.write(f"- Daily: {format_currency(contribution['daily_required'])}")
                    st.write(f"- Weekly: {format_currency(contribution['weekly_required'])}")
                    st.write(f"- Monthly: {format_currency(contribution['monthly_required'])}")
                else:
                    st.success("✅ Goal achieved!")
    else:
        st.info("No financial goals yet.")
    
    # Goals progress chart
    st.subheader("📊 Goals Progress")
    if goals:
        try:
            import plotly.graph_objects as go
            
            goal_names = [g.get('name', 'Goal')[:20] for g in goals]
            progress_values = []
            for g in goals:
                progress = calculate_savings_progress(
                    Decimal(str(g.get('target_amount', 0))),
                    Decimal(str(g.get('current_amount', 0)))
                )
                progress_values.append(float(progress['progress_percent']))
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=goal_names,
                y=progress_values,
                marker_color='lightgreen',
                text=[f"{p:.1f}%" for p in progress_values],
                textposition='auto'
            ))
            fig.update_layout(
                xaxis_title="Goal",
                yaxis_title="Progress (%)",
                yaxis_range=[0, 100],
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart could not be displayed")
