"""
Reports page for the Finance App.
"""

import streamlit as st
from decimal import Decimal
from utils.database import fetch_all
from utils.ai_assistant import ai_assistant
from utils.financial_calculations import format_currency
import io


def show():
    """Show the reports page."""
    st.title("📄 Financial Reports")
    
    user_id = st.session_state.current_user['id']
    
    st.subheader("📊 Generate Report")
    
    report_type = st.selectbox("Report Type", ["Monthly", "Quarterly", "Yearly"])
    
    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
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
            
            report = ai_assistant.generate_financial_report(user_data, report_type)
            
            st.success("Report generated successfully!")
            
            st.subheader(f"📄 {report_type} Financial Report")
            st.write(f"**Generated on:** {report['date'][:10]}")
            
            # Summary
            st.subheader("📊 Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Income", format_currency(Decimal(str(report['summary'].get('total_income', 0)))))
                st.metric("Total Expenses", format_currency(Decimal(str(report['summary'].get('total_expenses', 0)))))
                st.metric("Cash Flow", format_currency(Decimal(str(report['summary'].get('cash_flow', 0)))))
            with col2:
                st.metric("Total Giving", format_currency(Decimal(str(report['summary'].get('total_giving', 0)))))
                st.metric("Total Savings", format_currency(Decimal(str(report['summary'].get('total_savings', 0)))))
                if report['summary'].get('savings_rate'):
                    st.metric("Savings Rate", f"{report['summary']['savings_rate']:.2f}%")
            with col3:
                st.metric("Total Investments", format_currency(Decimal(str(report['summary'].get('total_investments', 0)))))
                st.metric("Net Worth", format_currency(Decimal(str(report['summary'].get('net_worth', 0)))))
                if report['summary'].get('giving_percentage'):
                    st.metric("Giving %", f"{report['summary']['giving_percentage']:.2f}%")
            
            # Goals
            if report.get('details', {}).get('goals'):
                st.subheader("🎯 Goals Progress")
                for goal in report['details']['goals']:
                    st.write(f"- **{goal['name']}:** {goal['progress_percent']:.1f}% ({format_currency(Decimal(str(goal['current'])))} / {format_currency(Decimal(str(goal['target'])))))")
            
            # AI Observations
            if report.get('ai_observations'):
                st.subheader("🤖 AI Observations")
                for obs in report['ai_observations']:
                    st.info(obs)
            
            # Export
            st.subheader("💾 Export Options")
            csv_data = _export_to_csv(report)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"financial_report_{report_type.lower()}.csv",
                mime="text/csv"
            )


def _export_to_csv(report):
    """Export report data to CSV format."""
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Financial Report"])
    writer.writerow(["Generated", report.get('date', '')])
    writer.writerow([])
    
    writer.writerow(["Summary"])
    writer.writerow(["Metric", "Amount"])
    
    summary = report.get('summary', {})
    for key, value in summary.items():
        if isinstance(value, (int, float, str)):
            writer.writerow([key, value])
    
    return output.getvalue()
