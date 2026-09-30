"""
Investments tracking page for the Finance App.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from utils.database import fetch_all, execute_query
from utils.financial_calculations import calculate_investment_gain, format_currency


def show():
    """Show the investments page."""
    st.title("📈 Investments")
    
    user_id = st.session_state.current_user['id']
    
    # Create investment account
    with st.expander("➕ Create Investment Account", expanded=True):
        with st.form("create_investment_account_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Account Name", value="Stock Portfolio")
                provider = st.text_input("Provider/Broker")
            with col2:
                account_type = st.selectbox("Account Type", ["Brokerage", "Retirement", "Savings"])
                description = st.text_input("Description")
            
            if st.form_submit_button("Create Account"):
                execute_query(
                    """INSERT INTO investment_accounts (user_id, name, provider, account_type, description) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, name, provider, account_type, description)
                )
                st.success("Investment account created successfully!")
                st.rerun()
    
    # Show investment accounts
    st.subheader("📋 Investment Accounts")
    
    accounts = fetch_all("SELECT * FROM investment_accounts WHERE user_id = ?", (user_id,))
    
    if accounts:
        for account in accounts:
            with st.expander(f"📊 {account.get('name', 'Account')}"):
                holdings = fetch_all(
                    "SELECT * FROM investment_holdings WHERE account_id = ? AND user_id = ?",
                    (account['id'], user_id)
                )
                
                if holdings:
                    total_value = sum(
                        Decimal(str(h.get('current_price', 0))) * Decimal(str(h.get('quantity', 0)))
                        for h in holdings
                    )
                    
                    st.metric("Total Value", format_currency(total_value))
                    
                    with st.form(f"add_holding_{account['id']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            holding_name = st.text_input("Investment Name")
                            holding_type = st.selectbox(
                                "Type",
                                ["Nigerian stocks", "International stocks", "ETFs", "Equity funds",
                                 "Money market funds", "Bonds", "REITs", "Other investments"]
                            )
                        with col2:
                            quantity = st.number_input("Quantity", min_value=0.000001, step=0.000001, value=1.0)
                            purchase_price = st.number_input("Purchase Price (₦)", min_value=0.01, step=0.01, value=100.00)
                        with col3:
                            current_price = st.number_input("Current Price (₦)", min_value=0.01, step=0.01, value=100.00)
                            purchase_date = st.date_input("Purchase Date", value=date.today())
                        
                        if st.form_submit_button("Add Holding"):
                            execute_query(
                                """INSERT INTO investment_holdings (account_id, user_id, name, investment_type, quantity, purchase_price, current_price, purchase_date, fees, notes) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (account['id'], user_id, holding_name, holding_type, float(quantity),
                                 float(purchase_price), float(current_price), purchase_date.isoformat(),
                                 0.0, "")
                            )
                            st.success("Holding added!")
                            st.rerun()
                    
                    st.write("**Your Holdings:**")
                    for h in holdings:
                        gain_data = calculate_investment_gain(
                            Decimal(str(h.get('purchase_price', 0))),
                            Decimal(str(h.get('current_price', 0))),
                            Decimal(str(h.get('quantity', 0)))
                        )
                        
                        col1, col2, col3, col4, col5, col6 = st.columns(6)
                        col1.write(h.get('name', 'N/A')[:15])
                        col2.write(h.get('investment_type', 'N/A')[:15])
                        col3.write(str(h.get('quantity', 0)))
                        col4.write(format_currency(Decimal(str(h.get('purchase_price', 0)))))
                        col5.write(format_currency(Decimal(str(h.get('current_price', 0)))))
                        col6.write(format_currency(gain_data['gain_loss']))
                else:
                    st.info("No holdings yet.")
    else:
        st.info("No investment accounts yet.")
    
    # Portfolio summary
    st.subheader("📊 Portfolio Summary")
    
    all_holdings = fetch_all(
        """SELECT h.* FROM investment_holdings h 
           WHERE h.user_id = ?""",
        (user_id,)
    )
    
    if all_holdings:
        total_value = sum(
            Decimal(str(h.get('current_price', 0))) * Decimal(str(h.get('quantity', 0)))
            for h in all_holdings
        )
        total_cost = sum(
            Decimal(str(h.get('purchase_price', 0))) * Decimal(str(h.get('quantity', 0)))
            for h in all_holdings
        )
        total_gain = total_value - total_cost
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Value", format_currency(total_value))
        col2.metric("Total Cost", format_currency(total_cost))
        col3.metric("Total Gain/Loss", format_currency(total_gain))
        
        if total_cost > Decimal('0'):
            gain_pct = (total_gain / total_cost * Decimal('100')).quantize(Decimal('0.01'))
            st.metric("Overall Return", f"{gain_pct:.2f}%")
