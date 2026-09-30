"""
Dashboard page for the Finance App.
"""

import streamlit as st
from datetime import datetime, date, timedelta
from decimal import Decimal
from utils.database import fetch_all
from utils.financial_calculations import (
    calculate_net_worth, calculate_budget_usage, calculate_cash_flow,
    calculate_giving_percentage, calculate_savings_rate, format_currency, format_percentage
)
from utils.ai_assistant import ai_assistant


def show():
    """Show the dashboard page."""
    st.title("📊 Financial Dashboard")
    
    user_id = st.session_state.current_user['id']
    
    # Get data
    income = fetch_all("SELECT * FROM income WHERE user_id = ? ORDER BY date DESC", (user_id,))
    expenses = fetch_all("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (user_id,))
    giving = fetch_all("SELECT * FROM giving WHERE user_id = ? ORDER BY date DESC", (user_id,))
    savings_trans = fetch_all("SELECT * FROM savings_transactions WHERE user_id = ? AND type = 'Deposit' ORDER BY date DESC", (user_id,))
    investments = fetch_all("SELECT * FROM investment_holdings WHERE user_id = ? ORDER BY purchase_date DESC", (user_id,))
    assets = fetch_all("SELECT * FROM assets WHERE user_id = ? ORDER BY acquisition_date DESC", (user_id,))
    liabilities = fetch_all("SELECT * FROM liabilities WHERE user_id = ? ORDER BY due_date DESC", (user_id,))
    goals = fetch_all("SELECT * FROM financial_goals WHERE user_id = ? ORDER BY target_date DESC", (user_id,))
    budgets = fetch_all("SELECT * FROM budgets WHERE user_id = ? ORDER BY start_date DESC", (user_id,))
    recurring = fetch_all("SELECT * FROM recurring_expenses WHERE user_id = ? ORDER BY next_date DESC", (user_id,))
    
    # Calculate metrics
    total_income = sum(Decimal(str(i.get('amount', 0))) for i in income)
    total_expenses = sum(Decimal(str(e.get('amount', 0))) for e in expenses)
    total_giving = sum(Decimal(str(g.get('amount', 0))) for g in giving)
    total_savings = sum(Decimal(str(s.get('amount', 0))) for s in savings_trans)
    
    total_investment_value = sum(
        Decimal(str(i.get('current_price', 0))) * Decimal(str(i.get('quantity', 0))) 
        for i in investments
    )
    
    net_worth = calculate_net_worth(assets, liabilities)
    total_assets = sum(Decimal(str(a.get('value', 0))) for a in assets)
    total_liabilities = sum(Decimal(str(l.get('amount', 0))) for l in liabilities)
    cash_flow = calculate_cash_flow(income, expenses)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Total Income", format_currency(total_income))
        st.metric("💸 Total Expenses", format_currency(total_expenses))
    
    with col2:
        st.metric("🙏 Total Giving", format_currency(total_giving))
        st.metric("💰 Total Savings", format_currency(total_savings))
    
    with col3:
        st.metric("📈 Investments", format_currency(total_investment_value))
        st.metric("💼 Net Worth", format_currency(net_worth))
    
    with col4:
        st.metric("➕ Cash Flow", format_currency(cash_flow))
        if total_income > Decimal('0'):
            savings_rate = calculate_savings_rate(income, savings_trans)
            st.metric("📊 Savings Rate", format_percentage(savings_rate))
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Income vs Expenses")
        if income or expenses:
            try:
                import plotly.graph_objects as go
                
                income_by_month = {}
                expenses_by_month = {}
                
                for i in income:
                    month = i.get('date', '')[:7]
                    income_by_month[month] = income_by_month.get(month, Decimal('0')) + Decimal(str(i.get('amount', 0)))
                
                for e in expenses:
                    month = e.get('date', '')[:7]
                    expenses_by_month[month] = expenses_by_month.get(month, Decimal('0')) + Decimal(str(e.get('amount', 0)))
                
                all_months = sorted(set(list(income_by_month.keys()) + list(expenses_by_month.keys())))
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=all_months,
                    y=[float(income_by_month.get(m, Decimal('0'))) for m in all_months],
                    name='Income',
                    marker_color='lightgreen'
                ))
                fig.add_trace(go.Bar(
                    x=all_months,
                    y=[float(expenses_by_month.get(m, Decimal('0'))) for m in all_months],
                    name='Expenses',
                    marker_color='lightcoral'
                ))
                fig.update_layout(
                    barmode='group',
                    xaxis_title="Month",
                    yaxis_title="Amount (₦)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("Chart could not be displayed")
    
    with col2:
        st.subheader("💰 Net Worth Over Time")
        st.info("Net worth tracking requires historical data. Sample chart shown.")
        
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                y=[100000, 150000, 180000, 200000, 220000, 250000],
                mode='lines+markers',
                name='Net Worth',
                line=dict(color='royalblue', width=2)
            ))
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Net Worth (₦)",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            pass
    
    # Budget status
    st.subheader("💼 Budget Status")
    if budgets:
        latest_budget = budgets[0]
        actual_spending = sum(Decimal(str(e.get('amount', 0))) for e in expenses 
                             if e.get('date', '') >= latest_budget.get('start_date', ''))
        
        usage = calculate_budget_usage(
            Decimal(str(latest_budget.get('amount', 0))),
            actual_spending
        )
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Budget", format_currency(Decimal(str(latest_budget.get('amount', 0)))))
        col2.metric("Spent", format_currency(usage['used']))
        col3.metric("Remaining", format_currency(usage['remaining']))
        col4.metric("Usage", f"{usage['percentage_used']:.1f}%")
        
        st.progress(float(usage['percentage_used']) / 100)
        if usage['over_budget']:
            st.error("⚠️ You are over budget!")
    else:
        st.info("No budgets created yet.")
    
    # Recent transactions
    st.subheader("📝 Recent Transactions")
    
    all_transactions = []
    for i in income[:5]:
        all_transactions.append({'date': i.get('date'), 'type': 'Income', 'amount': i.get('amount'), 'description': i.get('source')})
    for e in expenses[:5]:
        all_transactions.append({'date': e.get('date'), 'type': 'Expense', 'amount': e.get('amount'), 'description': e.get('description')})
    for g in giving[:5]:
        all_transactions.append({'date': g.get('date'), 'type': 'Giving', 'amount': g.get('amount'), 'description': g.get('category')})
    
    all_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    for trans in all_transactions[:10]:
        col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
        col1.write(trans.get('date', 'N/A')[:10])
        col2.write(trans.get('description', 'N/A'))
        col3.write(trans.get('type', 'N/A'))
        col4.write(format_currency(Decimal(str(trans.get('amount', 0)))))
    
    # Recurring expenses
    st.subheader("🔄 Recurring Expenses")
    if recurring:
        total_monthly = sum(Decimal(str(r.get('amount', 0))) for r in recurring)
        st.metric("Total Monthly Recurring Cost", format_currency(total_monthly))
        
        for re in recurring[:5]:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            col1.write(re.get('description', 'N/A'))
            col2.write(re.get('frequency', 'N/A'))
            col3.write(re.get('next_date', 'N/A')[:10] if re.get('next_date') else 'N/A')
            col4.write(format_currency(Decimal(str(re.get('amount', 0)))))
    else:
        st.info("No recurring expenses identified yet.")
    
    # AI Insights
    st.subheader("🤖 AI Financial Insights")
    
    insights = []
    
    if total_income > Decimal('0'):
        giving_pct = calculate_giving_percentage(giving, income)
        insights.append(f"Your giving percentage is {format_percentage(giving_pct)} of your income.")
    
    if total_expenses > total_income:
        insights.append("⚠️ Your expenses exceed your income. Consider adjusting your spending.")
    
    if total_savings > Decimal('0') and total_income > Decimal('0'):
        savings_pct = calculate_savings_rate(income, savings_trans)
        if savings_pct < Decimal('10'):
            insights.append(f"Your savings rate is {format_percentage(savings_pct)}. Consider saving more.")
        elif savings_pct >= Decimal('20'):
            insights.append(f"Great job! Your savings rate is {format_percentage(savings_pct)}.")
    
    if investments:
        total_gain = Decimal('0')
        for inv in investments:
            gain_data = calculate_investment_gain(
                Decimal(str(inv.get('purchase_price', 0))),
                Decimal(str(inv.get('current_price', 0))),
                Decimal(str(inv.get('quantity', 0)))
            )
            total_gain += gain_data['gain_loss']
        
        if total_gain > Decimal('0'):
            insights.append(f"📈 Your investments have gained {format_currency(total_gain)} in total.")
        elif total_gain < Decimal('0'):
            insights.append(f"📉 Your investments have lost {format_currency(-total_gain)} in total.")
    
    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.info("Add more financial data to get personalized insights.")
