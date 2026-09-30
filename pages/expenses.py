"""
Expenses tracking page for the Finance App.
"""

import streamlit as st
from datetime import date, datetime, timedelta
from decimal import Decimal
from utils.database import fetch_all, execute_query, fetch_one
from utils.financial_calculations import format_currency


def show():
    """Show the expenses page."""
    st.title("💸 Expenses")
    
    user_id = st.session_state.current_user['id']
    
    # Add new expense
    with st.expander("➕ Add New Expense", expanded=True):
        with st.form("add_expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Amount (₦)", min_value=0.01, step=0.01, value=1000.00)
                expense_date = st.date_input("Date", value=date.today())
                category = st.selectbox(
                    "Category",
                    ["Food", "Transport", "Housing", "Utilities", "Internet/Data",
                     "Education", "Health", "Entertainment", "Shopping", "Subscriptions",
                     "Family", "Personal", "Business", "Other"]
                )
            with col2:
                description = st.text_input("Description")
                payment_method = st.selectbox(
                    "Payment Method",
                    ["Cash", "Bank Transfer", "Credit Card", "Debit Card", "Mobile Money"]
                )
                notes = st.text_input("Notes")
            
            if st.form_submit_button("Add Expense"):
                cat_id = fetch_one(
                    "SELECT id FROM expense_categories WHERE user_id = ? AND name = ?",
                    (user_id, category)
                )
                
                if cat_id:
                    category_id = cat_id['id']
                else:
                    execute_query(
                        "INSERT INTO expense_categories (user_id, name) VALUES (?, ?)",
                        (user_id, category)
                    )
                    category_id = None
                
                execute_query(
                    """INSERT INTO expenses (user_id, amount, date, category_id, category_name, description, payment_method, notes) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, float(amount), expense_date.isoformat(), category_id, category,
                     description, payment_method, notes)
                )
                st.success("Expense added successfully!")
                st.rerun()
    
    # Show expense records
    st.subheader("📋 Expense Records")
    
    expenses = fetch_all("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (user_id,))
    
    if expenses:
        total_expenses = sum(Decimal(str(e.get('amount', 0))) for e in expenses)
        st.metric("Total Expenses", format_currency(total_expenses))
        
        # Display table
        for e in expenses[:20]:
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
            col1.write(e.get('date', 'N/A')[:10])
            col2.write(e.get('category_name', 'N/A'))
            col3.write(e.get('description', 'N/A')[:20])
            col4.write(e.get('payment_method', 'N/A'))
            col5.write(format_currency(Decimal(str(e.get('amount', 0)))))
            col6.write(e.get('notes', '')[:15])
    else:
        st.info("No expense records yet.")
    
    # Expense by category chart
    st.subheader("📊 Expenses by Category")
    if expenses:
        try:
            import plotly.express as px
            
            category_totals = {}
            for e in expenses:
                cat = e.get('category_name', 'Other')
                category_totals[cat] = category_totals.get(cat, Decimal('0')) + Decimal(str(e.get('amount', 0)))
            
            fig = px.bar(
                x=list(category_totals.keys()),
                y=[float(v) for v in category_totals.values()],
                labels={'x': 'Category', 'y': 'Amount (₦)'},
                title="Expense Distribution by Category"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart could not be displayed")
