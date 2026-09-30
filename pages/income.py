"""
Income tracking page for the Finance App.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from utils.database import fetch_all, execute_query
from utils.financial_calculations import (
    calculate_allocation_amounts, get_default_allocation, format_currency
)
from utils.database import get_allocation_settings


def show():
    """Show the income page."""
    st.title("💵 Income")
    
    user_id = st.session_state.current_user['id']
    
    # Add new income
    with st.expander("➕ Add New Income", expanded=True):
        with st.form("add_income_form"):
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Amount (₦)", min_value=0.01, step=0.01, value=1000.00)
                income_date = st.date_input("Date", value=date.today())
                source = st.selectbox("Source", ["Salary", "Business", "Freelance", "Gift", "Allowance", "Other"])
            with col2:
                income_type = st.selectbox("Type", ["Salary", "Business", "Freelance", "Gift", "Allowance", "Other"])
                is_recurring = st.checkbox("Recurring")
                notes = st.text_input("Notes")
            
            if st.form_submit_button("Add Income"):
                execute_query(
                    """INSERT INTO income (user_id, amount, date, source, income_type, is_recurring, notes) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, float(amount), income_date.isoformat(), source, income_type, is_recurring, notes)
                )
                st.success("Income added successfully!")
                st.rerun()
    
    # Show income list
    st.subheader("📋 Income Records")
    
    income = fetch_all("SELECT * FROM income WHERE user_id = ? ORDER BY date DESC", (user_id,))
    
    if income:
        total_income = sum(Decimal(str(i.get('amount', 0))) for i in income)
        st.metric("Total Income", format_currency(total_income))
        
        # Display table
        for i in income[:20]:
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
            col1.write(i.get('date', 'N/A')[:10])
            col2.write(i.get('source', 'N/A'))
            col3.write(i.get('income_type', 'N/A'))
            col4.write(format_currency(Decimal(str(i.get('amount', 0)))))
            col5.write("✅" if i.get('is_recurring') else "❌")
            col6.write(i.get('notes', '')[:20])
    else:
        st.info("No income records yet.")
    
    # Income by source chart
    st.subheader("📊 Income by Source")
    if income:
        try:
            import plotly.express as px
            
            source_totals = {}
            for i in income:
                source = i.get('source', 'Other')
                source_totals[source] = source_totals.get(source, Decimal('0')) + Decimal(str(i.get('amount', 0)))
            
            fig = px.pie(
                values=[float(v) for v in source_totals.values()],
                names=list(source_totals.keys()),
                title="Income Distribution by Source"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart could not be displayed")
    
    # Allocation calculator
    st.subheader("💡 Income Allocation Calculator")
    
    allocation = get_allocation_settings(user_id)
    if not allocation:
        allocation = get_default_allocation()
    else:
        allocation = {
            'Tithe': Decimal(str(allocation.get('tithe_percent', 10))),
            'Offering': Decimal(str(allocation.get('offering_percent', 3))),
            'Kingdom Care': Decimal(str(allocation.get('kingdom_care_percent', 2))),
            'Savings': Decimal(str(allocation.get('savings_percent', 10))),
            'Investment': Decimal(str(allocation.get('investment_percent', 25))),
            'Recurrent Expenditure': Decimal(str(allocation.get('recurrent_expenditure_percent', 50)))
        }
    
    sample_income = st.number_input("Enter income amount to calculate allocation", min_value=0, value=100000)
    
    if st.button("Calculate Allocation"):
        try:
            amounts = calculate_allocation_amounts(Decimal(str(sample_income)), allocation)
            
            st.subheader("📊 Allocation Breakdown")
            for category, amount in amounts.items():
                st.write(f"**{category}:** {format_currency(amount)}")
        except ValueError as e:
            st.error(str(e))
