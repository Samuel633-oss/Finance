"""
Settings page for the Finance App.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from utils.database import (
    get_allocation_settings, create_allocation_settings, update_allocation_settings,
    execute_query, fetch_all
)
from utils.financial_calculations import (
    calculate_allocation_amounts, get_default_allocation, format_currency
)
from utils.seed_data import (
    create_sample_income, create_sample_giving, create_sample_expenses,
    create_sample_expense_categories, create_sample_recurring_expenses,
    create_sample_budgets, create_sample_savings_accounts, create_sample_savings_transactions,
    create_sample_savings_goals, create_sample_investment_accounts, create_sample_investment_holdings,
    create_sample_assets, create_sample_liabilities, create_sample_financial_goals
)


def show():
    """Show the settings page."""
    st.title("⚙️ Settings")
    
    user_id = st.session_state.current_user['id']
    
    # Allocation settings
    st.subheader("💰 Default Money Allocation")
    
    allocation = get_allocation_settings(user_id)
    
    if not allocation:
        allocation = {
            'tithe_percent': 10.00,
            'offering_percent': 3.00,
            'kingdom_care_percent': 2.00,
            'savings_percent': 10.00,
            'investment_percent': 25.00,
            'recurrent_expenditure_percent': 50.00
        }
        create_allocation_settings(user_id)
    
    with st.form("allocation_form"):
        col1, col2 = st.columns(2)
        with col1:
            tithe = st.number_input("Tithe %", min_value=0.0, max_value=100.0, step=0.01, 
                                    value=float(allocation.get('tithe_percent', 10.00)))
            offering = st.number_input("Offering %", min_value=0.0, max_value=100.0, step=0.01,
                                       value=float(allocation.get('offering_percent', 3.00)))
            kingdom_care = st.number_input("Kingdom Care %", min_value=0.0, max_value=100.0, step=0.01,
                                            value=float(allocation.get('kingdom_care_percent', 2.00)))
        with col2:
            savings = st.number_input("Savings %", min_value=0.0, max_value=100.0, step=0.01,
                                     value=float(allocation.get('savings_percent', 10.00)))
            investment = st.number_input("Investment %", min_value=0.0, max_value=100.0, step=0.01,
                                         value=float(allocation.get('investment_percent', 25.00)))
            recurrent = st.number_input("Recurrent Expenditure %", min_value=0.0, max_value=100.0, step=0.01,
                                        value=float(allocation.get('recurrent_expenditure_percent', 50.00)))
        
        total = tithe + offering + kingdom_care + savings + investment + recurrent
        st.write(f"**Total: {total:.2f}%**")
        
        if total != 100.0:
            st.error("Total must equal exactly 100%")
        
        if st.form_submit_button("Save Allocation Settings"):
            if abs(total - 100.0) < 0.01:
                update_allocation_settings(user_id, {
                    'tithe_percent': tithe,
                    'offering_percent': offering,
                    'kingdom_care_percent': kingdom_care,
                    'savings_percent': savings,
                    'investment_percent': investment,
                    'recurrent_expenditure_percent': recurrent
                })
                st.success("Allocation settings saved successfully!")
            else:
                st.error("Total must equal exactly 100%")
    
    # Test allocation
    st.subheader("🧪 Test Allocation")
    
    test_amount = st.number_input("Test with income amount (₦)", min_value=0, value=100000)
    
    if st.button("Calculate"):
        try:
            allocation_test = {
                'Tithe': Decimal(str(tithe)),
                'Offering': Decimal(str(offering)),
                'Kingdom Care': Decimal(str(kingdom_care)),
                'Savings': Decimal(str(savings)),
                'Investment': Decimal(str(investment)),
                'Recurrent Expenditure': Decimal(str(recurrent))
            }
            
            amounts = calculate_allocation_amounts(Decimal(str(test_amount)), allocation_test)
            
            st.write("**Allocation Breakdown:**")
            for category, amount in amounts.items():
                st.write(f"- **{category}:** {format_currency(amount)}")
        except ValueError as e:
            st.error(str(e))
    
    # Seed data option
    st.subheader("🌱 Seed Sample Data")
    st.write("Add sample data to your account for demonstration purposes.")
    
    if st.button("Add Sample Data"):
        with st.spinner("Adding sample data..."):
            create_sample_expense_categories(user_id)
            create_sample_income(user_id, 5)
            create_sample_giving(user_id, 4)
            create_sample_expenses(user_id, 10)
            create_sample_recurring_expenses(user_id, 3)
            create_sample_budgets(user_id, 2)
            
            accounts = fetch_all("SELECT id FROM savings_accounts WHERE user_id = ?", (user_id,))
            if not accounts:
                create_sample_savings_accounts(user_id, 2)
                accounts = fetch_all("SELECT id FROM savings_accounts WHERE user_id = ?", (user_id,))
            
            if accounts:
                account_ids = [a['id'] for a in accounts]
                create_sample_savings_transactions(user_id, account_ids, 5)
                create_sample_savings_goals(user_id, 2)
            
            inv_accounts = fetch_all("SELECT id FROM investment_accounts WHERE user_id = ?", (user_id,))
            if not inv_accounts:
                create_sample_investment_accounts(user_id, 1)
                inv_accounts = fetch_all("SELECT id FROM investment_accounts WHERE user_id = ?", (user_id,))
            
            if inv_accounts:
                inv_account_ids = [a['id'] for a in inv_accounts]
                create_sample_investment_holdings(user_id, inv_account_ids, 3)
            
            create_sample_assets(user_id, 3)
            create_sample_liabilities(user_id, 2)
            create_sample_financial_goals(user_id, 2)
        
        st.success("Sample data added successfully! Refresh the page to see the data.")
