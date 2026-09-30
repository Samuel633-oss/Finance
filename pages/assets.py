"""
Assets tracking page for the Finance App.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from utils.database import fetch_all, execute_query
from utils.financial_calculations import format_currency


def show():
    """Show the assets page."""
    st.title("🏠 Assets")
    
    user_id = st.session_state.current_user['id']
    
    # Add new asset
    with st.expander("➕ Add New Asset", expanded=True):
        with st.form("add_asset_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Asset Name", value="Car")
                asset_type = st.selectbox(
                    "Type",
                    ["Cash", "Bank savings", "Investments", "Property", "Vehicle", "Business interests", "Other assets"]
                )
            with col2:
                value = st.number_input("Value (₦)", min_value=0.01, step=0.01, value=100000.00)
                acquisition_date = st.date_input("Acquisition Date")
            
            notes = st.text_input("Notes")
            
            if st.form_submit_button("Add Asset"):
                execute_query(
                    """INSERT INTO assets (user_id, name, type, value, acquisition_date, notes) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, name, asset_type, float(value), acquisition_date.isoformat(), notes)
                )
                st.success("Asset added successfully!")
                st.rerun()
    
    # Show assets
    st.subheader("📋 Your Assets")
    
    assets = fetch_all("SELECT * FROM assets WHERE user_id = ? ORDER BY acquisition_date DESC", (user_id,))
    
    if assets:
        total_assets = sum(Decimal(str(a.get('value', 0))) for a in assets)
        st.metric("Total Assets Value", format_currency(total_assets))
        
        # Display table
        for a in assets:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
            col1.write(a.get('acquisition_date', 'N/A')[:10])
            col2.write(a.get('name', 'N/A'))
            col3.write(a.get('type', 'N/A'))
            col4.write(format_currency(Decimal(str(a.get('value', 0)))))
            col5.write(a.get('notes', '')[:30])
    else:
        st.info("No assets recorded yet.")
    
    # Assets by type chart
    st.subheader("📊 Assets by Type")
    if assets:
        try:
            import plotly.express as px
            
            type_totals = {}
            for a in assets:
                atype = a.get('type', 'Other')
                type_totals[atype] = type_totals.get(atype, Decimal('0')) + Decimal(str(a.get('value', 0)))
            
            fig = px.pie(
                values=[float(v) for v in type_totals.values()],
                names=list(type_totals.keys()),
                title="Asset Distribution by Type"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart could not be displayed")
