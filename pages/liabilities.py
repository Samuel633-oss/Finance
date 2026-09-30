"""
Liabilities tracking page for the Finance App.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from utils.database import fetch_all, execute_query
from utils.financial_calculations import format_currency


def show():
    """Show the liabilities page."""
    st.title("💳 Liabilities")
    
    user_id = st.session_state.current_user['id']
    
    # Add new liability
    with st.expander("➕ Add New Liability", expanded=True):
        with st.form("add_liability_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Liability Name", value="Loan")
                amount = st.number_input("Amount (₦)", min_value=0.01, step=0.01, value=100000.00)
            with col2:
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.01, value=0.0)
                due_date = st.date_input("Due Date")
            
            payment_amount = st.number_input("Payment Amount (₦)", min_value=0.0, step=0.01, value=0.0)
            remaining_balance = st.number_input("Remaining Balance (₦)", min_value=0.0, step=0.01, value=0.0)
            notes = st.text_input("Notes")
            
            if st.form_submit_button("Add Liability"):
                execute_query(
                    """INSERT INTO liabilities (user_id, name, amount, interest_rate, due_date, payment_amount, remaining_balance, notes) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, name, float(amount), float(interest_rate), due_date.isoformat(),
                     float(payment_amount), float(remaining_balance), notes)
                )
                st.success("Liability added successfully!")
                st.rerun()
    
    # Show liabilities
    st.subheader("📋 Your Liabilities")
    
    liabilities = fetch_all("SELECT * FROM liabilities WHERE user_id = ? ORDER BY due_date", (user_id,))
    
    if liabilities:
        total_liabilities = sum(Decimal(str(l.get('amount', 0))) for l in liabilities)
        total_remaining = sum(Decimal(str(l.get('remaining_balance', l.get('amount', 0)))) for l in liabilities)
        
        st.metric("Total Liabilities", format_currency(total_liabilities))
        st.metric("Total Remaining Balance", format_currency(total_remaining))
        
        # Display table
        for l in liabilities:
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
            col1.write(l.get('due_date', 'N/A')[:10])
            col2.write(l.get('name', 'N/A'))
            col3.write(format_currency(Decimal(str(l.get('amount', 0)))))
            col4.write(f"{l.get('interest_rate', 0):.2f}%")
            col5.write(format_currency(Decimal(str(l.get('remaining_balance', l.get('amount', 0))))))
            col6.write(l.get('notes', '')[:20])
    else:
        st.info("No liabilities recorded yet.")
