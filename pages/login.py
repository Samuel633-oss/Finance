"""
Login and registration page for the Finance App.
"""

import streamlit as st
from utils.auth import login_user, register_user, hash_password, get_user_by_username
from utils.database import create_user, create_allocation_settings


def show():
    """Show the login page."""
    st.title("💰 Finance App - Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_btn = st.form_submit_button("Login", key="login_submit")
        with col2:
            create_account_btn = st.form_submit_button("Create Account", key="create_account_btn")
    
    # Handle Create Account button
    if 'create_account_btn' in st.session_state and st.session_state.create_account_btn:
        st.session_state.page = "register"
        st.rerun()
    
    if submit_btn:
        if username and password:
            session_id = login_user(username, password)
            if session_id:
                st.session_state.session_id = session_id
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter both username and password")


def show_register():
    """Show the registration page."""
    st.title("💰 Finance App - Create Account")
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
        email = st.text_input("Email (optional)", placeholder="your@email.com", key="reg_email")
        password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_btn = st.form_submit_button("Create Account", key="reg_submit")
        with col2:
            back_login_btn = st.form_submit_button("Back to Login", key="back_login_btn")
    
    # Handle Back to Login button
    if 'back_login_btn' in st.session_state and st.session_state.back_login_btn:
        st.session_state.page = "login"
        st.rerun()
    
    if submit_btn:
        if not username:
            st.error("Username is required")
        elif not password:
            st.error("Password is required")
        elif password != confirm_password:
            st.error("Passwords do not match")
        elif get_user_by_username(username):
            st.error("Username already exists")
        else:
            user_id = register_user(username, password, email)
            if user_id:
                create_allocation_settings(user_id)
                session_id = login_user(username, password)
                if session_id:
                    st.session_state.session_id = session_id
                    st.session_state.page = "dashboard"
                    st.rerun()
            else:
                st.error("Failed to create account")
