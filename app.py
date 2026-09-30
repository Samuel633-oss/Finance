"""
Main Streamlit application for the Finance App.
This is the entry point for the application.
"""

import streamlit as st
from datetime import datetime, date, timedelta
from decimal import Decimal
import os
import sys

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

# Import utilities
from utils.database import (
    init_db, fetch_one, fetch_all, execute_query,
    get_user_by_username, get_user_by_id, create_user,
    get_allocation_settings, create_allocation_settings, update_allocation_settings
)
from utils.auth import (
    hash_password, verify_password, create_session, get_session,
    delete_session, get_current_user, login_user, register_user
)
from utils.financial_calculations import (
    validate_allocation_percentages, calculate_allocation_amounts,
    calculate_net_worth, calculate_budget_usage, calculate_savings_progress,
    calculate_investment_gain, calculate_cash_flow, calculate_giving_percentage,
    calculate_savings_rate, get_default_allocation, format_currency, format_percentage
)
from utils.ai_assistant import ai_assistant

# Initialize database
init_db()

# Set page configuration
st.set_page_config(
    page_title="Finance App",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)


def get_session_id():
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    return st.session_state.session_id


def set_session_id(session_id):
    st.session_state.session_id = session_id


def logout():
    session_id = get_session_id()
    if session_id:
        delete_session(session_id)
        set_session_id(None)
        st.session_state.current_user = None
        st.rerun()


def check_auth():
    session_id = get_session_id()
    if not session_id:
        return False
    user = get_current_user(session_id)
    if user:
        st.session_state.current_user = user
        return True
    return False


def get_current_user_id():
    if check_auth():
        return st.session_state.current_user['id']
    return None


# Include page modules
import pages.dashboard
import pages.income
import pages.giving
import pages.expenses
import pages.budget
import pages.savings
import pages.investments
import pages.assets
import pages.liabilities
import pages.goals
import pages.reports
import pages.ai_assistant
import pages.research
import pages.settings
import pages.login


def main():
    """Main entry point."""
    if 'page' not in st.session_state:
        st.session_state.page = None
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None

    # Route to appropriate page
    if st.session_state.page is None:
        if check_auth():
            st.session_state.page = "dashboard"
            pages.dashboard.show()
        else:
            pages.login.show()
    elif st.session_state.page == "login":
        pages.login.show()
    elif st.session_state.page == "register":
        pages.login.show_register()
    else:
        # Check auth for all other pages
        if not check_auth():
            st.session_state.page = "login"
            pages.login.show()
        else:
            # Show the selected page
            page_mapping = {
                "dashboard": pages.dashboard.show,
                "income": pages.income.show,
                "giving": pages.giving.show,
                "expenses": pages.expenses.show,
                "budget": pages.budget.show,
                "savings": pages.savings.show,
                "investments": pages.investments.show,
                "assets": pages.assets.show,
                "liabilities": pages.liabilities.show,
                "goals": pages.goals.show,
                "reports": pages.reports.show,
                "ai_assistant": pages.ai_assistant.show,
                "research": pages.research.show,
                "settings": pages.settings.show,
            }
            
            func = page_mapping.get(st.session_state.page)
            if func:
                func()
            else:
                pages.dashboard.show()


if __name__ == "__main__":
    main()
