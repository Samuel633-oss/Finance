"""
Budget management page for the Finance App.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from utils.database import fetch_all, execute_query
from utils.financial_calculations import calculate_budget_usage, format_currency


def show():
    """Show the budget page."""
    st.title("💼 Budget")
    
    user_id = st.session_state.current_user['id']
    
    # Create new budget
    with st.expander("➕ Create New Budget", expanded=True):
        with st.form("create_budget_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Budget Name", value="Monthly Budget")
                amount = st.number_input("Budget Amount (₦)", min_value=0.01, step=0.01, value=100000.00)
                period = st.selectbox("Period", ["Monthly", "Weekly", "Yearly"])
            with col2:
                start_date = st.date_input("Start Date", value=date.today())
                end_date = st.date_input("End Date", value=date.today() + timedelta(days=30))
                notes = st.text_input("Notes")
            
            if st.form_submit_button("Create Budget"):
                execute_query(
                    """INSERT INTO budgets (user_id, name, amount, period, start_date, end_date, notes) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, name, float(amount), period.lower(),
                     start_date.isoformat(), end_date.isoformat(), notes)
                )
                st.success("Budget created successfully!")
                st.rerun()
    
    # Show budgets
    st.subheader("📋 Your Budgets")
    
    budgets = fetch_all("SELECT * FROM budgets WHERE user_id = ? ORDER BY start_date DESC", (user_id,))
    
    if budgets:
        for budget in budgets:
            with st.expander(f"📊 {budget.get('name', 'Budget')} - {format_currency(Decimal(str(budget.get('amount', 0))))}"):
                expenses = fetch_all(
                    """SELECT * FROM expenses WHERE user_id = ? AND date >= ? AND date <= ?""",
                    (user_id, budget.get('start_date'), budget.get('end_date'))
                )
                actual_spending = sum(Decimal(str(e.get('amount', 0))) for e in expenses)
                
                usage = calculate_budget_usage(
                    Decimal(str(budget.get('amount', 0))),
                    actual_spending
                )
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Budget", format_currency(Decimal(str(budget.get('amount', 0)))))
                col2.metric("Spent", format_currency(usage['used']))
                col3.metric("Remaining", format_currency(usage['remaining']))
                col4.metric("Usage", f"{usage['percentage_used']:.1f}%")
                
                st.progress(float(usage['percentage_used']) / 100)
                
                if usage['over_budget']:
                    st.error("⚠️ Over budget!")
                
                st.write(f"**Expenses in this period:** {len(expenses)}")
                for e in expenses[:5]:
                    st.write(f"- {e.get('date', 'N/A')[:10]}: {format_currency(Decimal(str(e.get('amount', 0))))} - {e.get('description', 'N/A')}")
    else:
        st.info("No budgets created yet.")
    
    # Budget vs Actual chart
    st.subheader("📊 Budget vs Actual Spending")
    if budgets:
        try:
            import plotly.graph_objects as go
            
            budget_names = [b.get('name', 'Budget') for b in budgets]
            budget_amounts = [float(Decimal(str(b.get('amount', 0)))) for b in budgets]
            
            actual_amounts = []
            for b in budgets:
                expenses = fetch_all(
                    """SELECT * FROM expenses WHERE user_id = ? AND date >= ? AND date <= ?""",
                    (user_id, b.get('start_date'), b.get('end_date'))
                )
                actual = sum(Decimal(str(e.get('amount', 0))) for e in expenses)
                actual_amounts.append(float(actual))
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=budget_names,
                y=budget_amounts,
                name='Budget',
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                x=budget_names,
                y=actual_amounts,
                name='Actual',
                marker_color='lightcoral'
            ))
            fig.update_layout(
                barmode='group',
                xaxis_title="Budget",
                yaxis_title="Amount (₦)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart could not be displayed")
