"""
Giving tracking page for the Finance App.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from utils.database import fetch_all, execute_query
from utils.financial_calculations import calculate_giving_percentage, format_currency, format_percentage


def show():
    """Show the giving page."""
    st.title("🙏 Giving")
    
    user_id = st.session_state.current_user['id']
    
    # Add new giving
    with st.expander("➕ Add New Giving", expanded=True):
        with st.form("add_giving_form"):
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Amount (₦)", min_value=0.01, step=0.01, value=1000.00)
                giving_date = st.date_input("Date", value=date.today())
            with col2:
                category = st.selectbox("Category", ["Tithe", "Offering", "Kingdom Care", "Other Giving"])
                notes = st.text_input("Notes")
            
            if st.form_submit_button("Add Giving"):
                execute_query(
                    """INSERT INTO giving (user_id, amount, date, category, notes) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, float(amount), giving_date.isoformat(), category, notes)
                )
                st.success("Giving recorded successfully!")
                st.rerun()
    
    # Show giving records
    st.subheader("📋 Giving Records")
    
    giving = fetch_all("SELECT * FROM giving WHERE user_id = ? ORDER BY date DESC", (user_id,))
    income = fetch_all("SELECT * FROM income WHERE user_id = ?", (user_id,))
    
    if giving:
        total_giving = sum(Decimal(str(g.get('amount', 0))) for g in giving)
        st.metric("Total Giving", format_currency(total_giving))
        
        if income:
            giving_pct = calculate_giving_percentage(giving, income)
            st.metric("Giving % of Income", format_percentage(giving_pct))
        
        # Display table
        for g in giving[:20]:
            col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
            col1.write(g.get('date', 'N/A')[:10])
            col2.write(g.get('category', 'N/A'))
            col3.write(format_currency(Decimal(str(g.get('amount', 0)))))
            col4.write(g.get('notes', '')[:30])
    else:
        st.info("No giving records yet.")
    
    # Giving by category chart
    st.subheader("📊 Giving by Category")
    if giving:
        try:
            import plotly.express as px
            
            category_totals = {}
            for g in giving:
                cat = g.get('category', 'Other')
                category_totals[cat] = category_totals.get(cat, Decimal('0')) + Decimal(str(g.get('amount', 0)))
            
            fig = px.pie(
                values=[float(v) for v in category_totals.values()],
                names=list(category_totals.keys()),
                title="Giving Distribution by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart could not be displayed")
