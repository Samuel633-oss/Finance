"""
Investment research page for the Finance App.
"""

import streamlit as st
from utils.ai_assistant import ai_assistant


def show():
    """Show the research page."""
    st.title("🔍 Investment Research")
    
    st.write("Research investment options and get educational information.")
    st.write("Examples:")
    st.write("- What investment options are available in Nigeria?")
    st.write("- What are current money market fund options?")
    st.write("- What equity funds exist?")
    st.write("- What are the fees for mutual funds?")
    
    # Research form
    with st.form("research_form"):
        query = st.text_input("Research Query", placeholder="Ask about investment options...")
        
        if st.form_submit_button("Research"):
            with st.spinner("Researching..."):
                result = ai_assistant.research_investments(query)
            
            if 'error' in result:
                st.error(result['error'])
            else:
                st.subheader("📊 Research Results")
                st.markdown(result['response'])
                
                if result.get('sources'):
                    st.subheader("📚 Sources")
                    for source in result['sources']:
                        st.write(f"- {source.get('source', 'N/A')}")
    
    # Quick research options
    st.subheader("💡 Quick Research Options")
    
    quick_queries = [
        "What investment options are available in Nigeria?",
        "What are current money market fund options?",
        "What equity funds exist in Nigeria?",
        "What are the fees for mutual funds?",
        "What is the minimum investment for Nigerian stocks?"
    ]
    
    for query in quick_queries:
        if st.button(query):
            with st.spinner("Researching..."):
                result = ai_assistant.research_investments(query)
            
            if 'error' not in result:
                st.markdown(result['response'])
