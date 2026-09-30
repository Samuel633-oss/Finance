"""
AI Assistant page for the Finance App.
"""

import streamlit as st
from utils.database import fetch_all
from utils.ai_assistant import ai_assistant


def show():
    """Show the AI assistant page."""
    st.title("🤖 AI Financial Assistant")
    
    user_id = st.session_state.current_user['id']
    
    st.write("Ask me questions about your finances!")
    st.write("Examples:")
    st.write("- How much did I spend this month?")
    st.write("- What did I spend the most on?")
    st.write("- How much did I give this month?")
    st.write("- What is my net worth?")
    st.write("- Am I over budget?")
    
    # Collect user data
    user_data = {
        'income': fetch_all("SELECT * FROM income WHERE user_id = ?", (user_id,)),
        'expenses': fetch_all("SELECT * FROM expenses WHERE user_id = ?", (user_id,)),
        'giving': fetch_all("SELECT * FROM giving WHERE user_id = ?", (user_id,)),
        'savings': fetch_all("SELECT * FROM savings_transactions WHERE user_id = ? AND type = 'Deposit'", (user_id,)),
        'investments': fetch_all("SELECT * FROM investment_holdings WHERE user_id = ?", (user_id,)),
        'assets': fetch_all("SELECT * FROM assets WHERE user_id = ?", (user_id,)),
        'liabilities': fetch_all("SELECT * FROM liabilities WHERE user_id = ?", (user_id,)),
        'goals': fetch_all("SELECT * FROM financial_goals WHERE user_id = ?", (user_id,)),
        'budgets': fetch_all("SELECT * FROM budgets WHERE user_id = ?", (user_id,)),
        'recurring_expenses': fetch_all("SELECT * FROM recurring_expenses WHERE user_id = ?", (user_id,))
    }
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask your financial question"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Thinking..."):
            response = ai_assistant.ask(prompt, user_data)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
