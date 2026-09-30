"""
Savings tracking page for the Finance App.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from utils.database import fetch_all, execute_query
from utils.financial_calculations import (
    calculate_savings_progress, calculate_goal_contribution, format_currency
)


def show():
    """Show the savings page."""
    st.title("💰 Savings")
    
    user_id = st.session_state.current_user['id']
    
    # Create savings account
    with st.expander("➕ Create Savings Account", expanded=True):
        with st.form("create_savings_account_form"):
            name = st.text_input("Account Name", value="Emergency Fund")
            description = st.text_input("Description")
            
            if st.form_submit_button("Create Account"):
                execute_query(
                    """INSERT INTO savings_accounts (user_id, name, description) 
                       VALUES (?, ?, ?)""",
                    (user_id, name, description)
                )
                st.success("Savings account created successfully!")
                st.rerun()
    
    # Show savings accounts
    st.subheader("📋 Savings Accounts")
    
    accounts = fetch_all("SELECT * FROM savings_accounts WHERE user_id = ?", (user_id,))
    
    if accounts:
        for account in accounts:
            with st.expander(f"💾 {account.get('name', 'Account')}"):
                transactions = fetch_all(
                    "SELECT * FROM savings_transactions WHERE account_id = ? AND user_id = ? ORDER BY date DESC",
                    (account['id'], user_id)
                )
                
                if transactions:
                    balance = sum(
                        Decimal(str(t.get('amount', 0))) if t.get('type') == 'Deposit' 
                        else -Decimal(str(t.get('amount', 0)))
                        for t in transactions
                    )
                    
                    st.metric("Current Balance", format_currency(balance))
                    
                    with st.form(f"add_transaction_{account['id']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            trans_type = st.selectbox("Type", ["Deposit", "Withdrawal"])
                        with col2:
                            trans_amount = st.number_input("Amount (₦)", min_value=0.01, step=0.01, value=1000.00)
                        with col3:
                            trans_date = st.date_input("Date", value=date.today())
                        
                        trans_desc = st.text_input("Description")
                        
                        if st.form_submit_button("Add Transaction"):
                            execute_query(
                                """INSERT INTO savings_transactions (account_id, user_id, amount, date, type, description, notes) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (account['id'], user_id, float(trans_amount), trans_date.isoformat(),
                                 trans_type, trans_desc, "")
                            )
                            st.success("Transaction added!")
                            st.rerun()
                    
                    st.write("**Recent Transactions:**")
                    for t in transactions[:10]:
                        col1, col2, col3, col4 = st.columns(4)
                        col1.write(t.get('date', 'N/A')[:10])
                        col2.write(t.get('type', 'N/A'))
                        col3.write(t.get('description', 'N/A')[:20])
                        col4.write(format_currency(Decimal(str(t.get('amount', 0)))))
                else:
                    st.info("No transactions yet.")
    else:
        st.info("No savings accounts yet.")
    
    # Savings goals
    st.subheader("🎯 Savings Goals")
    
    with st.expander("➕ Create New Goal", expanded=True):
        with st.form("create_goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                goal_name = st.text_input("Goal Name", value="Emergency Fund")
                target_amount = st.number_input("Target Amount (₦)", min_value=0.01, step=0.01, value=100000.00)
            with col2:
                current_amount = st.number_input("Current Amount (₦)", min_value=0.0, step=0.01, value=0.0)
                target_date = st.date_input("Target Date")
            
            goal_desc = st.text_input("Description")
            
            if st.form_submit_button("Create Goal"):
                execute_query(
                    """INSERT INTO savings_goals (user_id, name, target_amount, current_amount, target_date, description) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, goal_name, float(target_amount), float(current_amount),
                     target_date.isoformat(), goal_desc)
                )
                st.success("Goal created successfully!")
                st.rerun()
    
    goals = fetch_all("SELECT * FROM savings_goals WHERE user_id = ? ORDER BY target_date", (user_id,))
    
    if goals:
        for goal in goals:
            progress = calculate_savings_progress(
                Decimal(str(goal.get('target_amount', 0))),
                Decimal(str(goal.get('current_amount', 0)))
            )
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Goal", goal.get('name', 'N/A'))
            col2.metric("Progress", f"{progress['progress_percent']:.1f}%")
            col3.metric("Remaining", format_currency(progress['amount_remaining']))
            
            st.progress(float(progress['progress_percent']) / 100)
            
            contribution = calculate_goal_contribution(
                Decimal(str(goal.get('target_amount', 0))),
                Decimal(str(goal.get('current_amount', 0))),
                datetime.strptime(goal.get('target_date', ''), '%Y-%m-%d').date()
            )
            
            st.write(f"To reach your goal, you need to save:")
            st.write(f"- **Daily:** {format_currency(contribution['daily_required'])}")
            st.write(f"- **Weekly:** {format_currency(contribution['weekly_required'])}")
            st.write(f"- **Monthly:** {format_currency(contribution['monthly_required'])}")
    else:
        st.info("No savings goals yet.")
