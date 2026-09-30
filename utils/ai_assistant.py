"""
AI Assistant for the finance application using Groq.
"""

import os
from typing import Dict, List, Any, Optional
from decimal import Decimal
from .financial_calculations import (
    format_currency, format_percentage,
    calculate_net_worth, calculate_budget_usage,
    calculate_savings_progress, calculate_investment_gain,
    calculate_cash_flow, calculate_giving_percentage,
    calculate_savings_rate
)
from datetime import datetime, date

# Try to import groq and streamlit, but make them optional
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class AIAssistant:
    """AI Assistant for financial analysis and advice."""
    
    def __init__(self):
        # Try Streamlit secrets first, then fall back to environment variable
        if STREAMLIT_AVAILABLE:
            self.api_key = st.secrets.get('GROQ_API_KEY', None)
        else:
            self.api_key = os.environ.get('GROQ_API_KEY')
        self.client = Groq(api_key=self.api_key) if GROQ_AVAILABLE and self.api_key else None
        self.system_prompt = """
You are a helpful financial assistant. You provide accurate, practical financial advice based on the user's actual data.

Guidelines:
1. Always base your answers on the provided financial data
2. Be clear and concise
3. Explain calculations simply
4. Never guarantee investment returns
5. Never execute trades
6. Clearly distinguish between facts, data, analysis, and opinions
7. Do not expose data belonging to another user
8. If you don't have enough information, say so

When analyzing spending, provide practical observations based on actual patterns.
When discussing investments, be educational and research-focused.
When calculating, show your work clearly.

Always remember: The application code performs authoritative calculations. You explain and interpret them.
"""
    
    def _format_financial_data(self, data: Dict) -> str:
        """Format financial data for AI consumption."""
        lines = []
        
        # Income
        if 'income' in data and data['income']:
            lines.append("\n=== INCOME ===")
            total_income = sum(Decimal(str(i.get('amount', 0))) for i in data['income'])
            lines.append(f"Total Income: {format_currency(total_income)}")
            for inc in data['income'][:10]:  # Limit to recent
                lines.append(f"- {inc.get('date', 'N/A')}: {format_currency(Decimal(str(inc.get('amount', 0))))} from {inc.get('source', 'Unknown')}")
        
        # Expenses
        if 'expenses' in data and data['expenses']:
            lines.append("\n=== EXPENSES ===")
            total_expenses = sum(Decimal(str(e.get('amount', 0))) for e in data['expenses'])
            lines.append(f"Total Expenses: {format_currency(total_expenses)}")
            
            # Group by category
            categories = {}
            for exp in data['expenses']:
                cat = exp.get('category_name', 'Other')
                categories[cat] = categories.get(cat, Decimal('0')) + Decimal(str(exp.get('amount', 0)))
            
            lines.append("\nBy Category:")
            for cat, amount in sorted(categories.items(), key=lambda x: -float(x[1]))[:10]:
                lines.append(f"- {cat}: {format_currency(amount)}")
        
        # Giving
        if 'giving' in data and data['giving']:
            lines.append("\n=== GIVING ===")
            total_giving = sum(Decimal(str(g.get('amount', 0))) for g in data['giving'])
            lines.append(f"Total Giving: {format_currency(total_giving)}")
            
            giving_by_category = {}
            for g in data['giving']:
                cat = g.get('category', 'Other')
                giving_by_category[cat] = giving_by_category.get(cat, Decimal('0')) + Decimal(str(g.get('amount', 0)))
            
            for cat, amount in giving_by_category.items():
                lines.append(f"- {cat}: {format_currency(amount)}")
        
        # Savings
        if 'savings' in data and data['savings']:
            lines.append("\n=== SAVINGS ===")
            total_savings = sum(Decimal(str(s.get('amount', 0))) for s in data['savings'])
            lines.append(f"Total Savings: {format_currency(total_savings)}")
        
        # Investments
        if 'investments' in data and data['investments']:
            lines.append("\n=== INVESTMENTS ===")
            total_value = sum(
                Decimal(str(i.get('current_price', 0))) * Decimal(str(i.get('quantity', 0))) 
                for i in data['investments']
            )
            lines.append(f"Total Investment Value: {format_currency(total_value)}")
        
        # Assets and Liabilities
        if ('assets' in data and data['assets']) or ('liabilities' in data and data['liabilities']):
            lines.append("\n=== NET WORTH ===")
            assets = data.get('assets', [])
            liabilities = data.get('liabilities', [])
            net_worth = calculate_net_worth(assets, liabilities)
            total_assets = sum(Decimal(str(a.get('value', 0))) for a in assets)
            total_liabilities = sum(Decimal(str(l.get('amount', 0))) for l in liabilities)
            lines.append(f"Total Assets: {format_currency(total_assets)}")
            lines.append(f"Total Liabilities: {format_currency(total_liabilities)}")
            lines.append(f"Net Worth: {format_currency(net_worth)}")
        
        # Budgets
        if 'budgets' in data and data['budgets']:
            lines.append("\n=== BUDGETS ===")
            for budget in data['budgets']:
                usage = calculate_budget_usage(
                    Decimal(str(budget.get('amount', 0))),
                    Decimal(str(budget.get('actual_spending', 0)))
                )
                lines.append(f"- {budget.get('name', 'Budget')}: {format_currency(Decimal(str(budget.get('amount', 0))))} budget, {format_currency(Decimal(str(budget.get('actual_spending', 0))))} spent ({usage['percentage_used']}% used)")
        
        # Goals
        if 'goals' in data and data['goals']:
            lines.append("\n=== FINANCIAL GOALS ===")
            for goal in data['goals']:
                progress = calculate_savings_progress(
                    Decimal(str(goal.get('target_amount', 0))),
                    Decimal(str(goal.get('current_amount', 0)))
                )
                lines.append(f"- {goal.get('name', 'Goal')}: {progress['progress_percent']}% complete ({format_currency(Decimal(str(goal.get('current_amount', 0))))} / {format_currency(Decimal(str(goal.get('target_amount', 0))))})")
        
        # Recurring expenses
        if 'recurring_expenses' in data and data['recurring_expenses']:
            lines.append("\n=== RECURRING EXPENSES ===")
            total_monthly = sum(Decimal(str(re.get('amount', 0))) for re in data['recurring_expenses'])
            lines.append(f"Total Monthly Recurring Cost: {format_currency(total_monthly)}")
            for re in data['recurring_expenses'][:10]:
                lines.append(f"- {re.get('description', 'Expense')}: {format_currency(Decimal(str(re.get('amount', 0))))} ({re.get('frequency', 'monthly')})")
        
        return "\n".join(lines)
    
    def _prepare_context(self, user_data: Dict, query: str) -> str:
        """Prepare context for AI query."""
        financial_data = self._format_financial_data(user_data)
        
        context = f"""Current date: {datetime.now().strftime('%Y-%m-%d')}

User Query: {query}

{financial_data}

Remember: Base your answers ONLY on the provided financial data. If you don't have enough information, say so."""
        
        return context
    
    def ask(self, query: str, user_data: Dict) -> str:
        """Ask the AI a financial question."""
        if not GROQ_AVAILABLE or not self.api_key or not self.client:
            return "AI assistant is not available. Please ensure Groq is installed and API key is configured."
        
        try:
            context = self._prepare_context(user_data, query)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": context}
            ]
            
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9,
                stop=None,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"
    
    def analyze_spending(self, expenses: List[Dict], income: List[Dict], budget: Optional[Dict] = None) -> Dict:
        """Analyze spending patterns without AI."""
        if not expenses:
            return {
                'summary': 'No expense data available',
                'observations': []
            }
        
        total_expenses = sum(Decimal(str(e.get('amount', 0))) for e in expenses)
        total_income = sum(Decimal(str(i.get('amount', 0))) for i in income)
        
        # Group by category
        categories = {}
        for exp in expenses:
            cat = exp.get('category_name', 'Other')
            categories[cat] = categories.get(cat, Decimal('0')) + Decimal(str(exp.get('amount', 0)))
        
        # Sort by amount (descending)
        sorted_categories = sorted(categories.items(), key=lambda x: -float(x[1]))
        
        observations = []
        
        # Largest categories
        if sorted_categories:
            largest = sorted_categories[0]
            observations.append(f"Largest spending category: {largest[0]} ({format_currency(largest[1])})")
        
        # Spending vs income
        if total_income > Decimal('0'):
            spending_ratio = (total_expenses / total_income * Decimal('100')).quantize(Decimal('0.01'))
            observations.append(f"Spending-to-income ratio: {format_percentage(spending_ratio)}")
        
        # Budget comparison
        if budget:
            budget_amount = Decimal(str(budget.get('amount', 0)))
            actual = Decimal(str(budget.get('actual_spending', 0)))
            usage = calculate_budget_usage(budget_amount, actual)
            
            if usage['over_budget']:
                observations.append(f"Budget overrun: {format_currency(usage['used'] - usage['remaining'])}")
            else:
                observations.append(f"Budget usage: {format_percentage(usage['percentage_used'])}")
        
        # Identify potential subscriptions
        recurring_patterns = self._identify_recurring_expenses(expenses)
        if recurring_patterns:
            observations.append(f"Potential recurring expenses identified: {len(recurring_patterns)}")
        
        return {
            'summary': f"Total spending: {format_currency(total_expenses)}",
            'categories': [{'name': cat, 'amount': float(amount)} for cat, amount in sorted_categories],
            'observations': observations,
            'total_expenses': float(total_expenses),
            'total_income': float(total_income)
        }
    
    def _identify_recurring_expenses(self, expenses: List[Dict]) -> List[Dict]:
        """Identify potential recurring expenses from transaction history."""
        from collections import defaultdict
        
        # Group by description and amount
        patterns = defaultdict(list)
        
        for exp in expenses:
            key = (exp.get('description', '').lower(), Decimal(str(exp.get('amount', 0))))
            patterns[key].append(exp)
        
        recurring = []
        
        for (desc, amount), transactions in patterns.items():
            # Need at least 2 transactions to be considered recurring
            if len(transactions) >= 2:
                # Check if they're roughly monthly apart
                dates = sorted([t.get('date') for t in transactions if t.get('date')])
                if len(dates) >= 2:
                    # Simple heuristic: if there are multiple transactions with similar amounts
                    # and they're spread out, consider it recurring
                    time_diffs = []
                    for i in range(1, len(dates)):
                        if isinstance(dates[i], str):
                            dates[i] = datetime.strptime(dates[i], '%Y-%m-%d').date()
                        if isinstance(dates[i-1], str):
                            dates[i-1] = datetime.strptime(dates[i-1], '%Y-%m-%d').date()
                        diff = (dates[i] - dates[i-1]).days
                        time_diffs.append(diff)
                    
                    # If average time between transactions is around 30 days, it's likely monthly
                    if time_diffs:
                        avg_days = sum(time_diffs) / len(time_diffs)
                        if 25 <= avg_days <= 35:  # Roughly monthly
                            recurring.append({
                                'description': desc,
                                'amount': float(amount),
                                'frequency': 'monthly',
                                'count': len(transactions),
                                'last_date': str(dates[-1])
                            })
        
        return recurring
    
    def analyze_budget(self, budget: Dict, actual_spending: Dict) -> Dict:
        """Analyze budget performance."""
        budget_amount = Decimal(str(budget.get('amount', 0)))
        actual = Decimal(str(actual_spending.get('total', 0)))
        
        usage = calculate_budget_usage(budget_amount, actual)
        
        analysis = {
            'budget': float(budget_amount),
            'actual': float(actual),
            'usage': {
                'used': float(usage['used']),
                'remaining': float(usage['remaining']),
                'percentage_used': float(usage['percentage_used']),
                'over_budget': usage['over_budget']
            },
            'observations': []
        }
        
        if usage['over_budget']:
            analysis['observations'].append(f"You are over budget by {format_currency(usage['used'] - usage['remaining'])}")
        elif usage['percentage_used'] > Decimal('80'):
            analysis['observations'].append(f"You have used {format_percentage(usage['percentage_used'])} of your budget")
        else:
            analysis['observations'].append(f"You have {format_currency(usage['remaining'])} remaining in your budget")
        
        # Category analysis
        if 'categories' in actual_spending:
            for cat, cat_data in actual_spending['categories'].items():
                if cat in budget.get('categories', {}):
                    budget_cat = Decimal(str(budget['categories'][cat]))
                    actual_cat = Decimal(str(cat_data.get('amount', 0)))
                    cat_usage = calculate_budget_usage(budget_cat, actual_cat)
                    
                    if cat_usage['over_budget']:
                        analysis['observations'].append(
                            f"Category '{cat}' is over budget by {format_currency(cat_usage['used'] - cat_usage['remaining'])}"
                        )
        
        return analysis
    
    def generate_financial_report(self, user_data: Dict, period: str = 'monthly') -> Dict:
        """Generate a comprehensive financial report."""
        report = {
            'period': period,
            'date': datetime.now().isoformat(),
            'summary': {},
            'details': {},
            'ai_observations': []
        }
        
        # Income
        income = user_data.get('income', [])
        total_income = sum(Decimal(str(i.get('amount', 0))) for i in income)
        report['summary']['total_income'] = float(total_income)
        
        # Expenses
        expenses = user_data.get('expenses', [])
        total_expenses = sum(Decimal(str(e.get('amount', 0))) for e in expenses)
        report['summary']['total_expenses'] = float(total_expenses)
        
        # Cash flow
        cash_flow = calculate_cash_flow(income, expenses)
        report['summary']['cash_flow'] = float(cash_flow)
        
        # Giving
        giving = user_data.get('giving', [])
        total_giving = sum(Decimal(str(g.get('amount', 0))) for g in giving)
        report['summary']['total_giving'] = float(total_giving)
        
        if total_income > Decimal('0'):
            report['summary']['giving_percentage'] = float(calculate_giving_percentage(giving, income))
        
        # Savings
        savings = user_data.get('savings', [])
        total_savings = sum(Decimal(str(s.get('amount', 0))) for s in savings)
        report['summary']['total_savings'] = float(total_savings)
        
        if total_income > Decimal('0'):
            report['summary']['savings_rate'] = float(calculate_savings_rate(income, savings))
        
        # Investments
        investments = user_data.get('investments', [])
        total_investment_value = sum(
            Decimal(str(i.get('current_price', 0))) * Decimal(str(i.get('quantity', 0))) 
            for i in investments
        )
        report['summary']['total_investments'] = float(total_investment_value)
        
        # Net worth
        assets = user_data.get('assets', [])
        liabilities = user_data.get('liabilities', [])
        net_worth = calculate_net_worth(assets, liabilities)
        report['summary']['net_worth'] = float(net_worth)
        report['summary']['total_assets'] = float(sum(Decimal(str(a.get('value', 0))) for a in assets))
        report['summary']['total_liabilities'] = float(sum(Decimal(str(l.get('amount', 0))) for l in liabilities))
        
        # Goals
        goals = user_data.get('goals', [])
        report['details']['goals'] = []
        for goal in goals:
            progress = calculate_savings_progress(
                Decimal(str(goal.get('target_amount', 0))),
                Decimal(str(goal.get('current_amount', 0)))
            )
            report['details']['goals'].append({
                'name': goal.get('name', 'Unknown'),
                'target': float(Decimal(str(goal.get('target_amount', 0)))),
                'current': float(Decimal(str(goal.get('current_amount', 0)))),
                'progress_percent': float(progress['progress_percent'])
            })
        
        # Add AI observations
        if total_income > Decimal('0'):
            savings_rate = calculate_savings_rate(income, savings)
            if savings_rate < Decimal('10'):
                report['ai_observations'].append(
                    f"Your savings rate is {format_percentage(savings_rate)}. Consider increasing your savings to build financial security."
                )
        
        if total_expenses > total_income:
            report['ai_observations'].append(
                "Your expenses exceed your income. You may need to adjust your spending or find additional income sources."
            )
        
        # Investment performance
        if investments:
            total_gain = Decimal('0')
            for inv in investments:
                gain_data = calculate_investment_gain(
                    Decimal(str(inv.get('purchase_price', 0))),
                    Decimal(str(inv.get('current_price', 0))),
                    Decimal(str(inv.get('quantity', 0)))
                )
                total_gain += gain_data['gain_loss']
            
            report['summary']['investment_gain'] = float(total_gain)
            if total_gain > Decimal('0'):
                report['ai_observations'].append(
                    f"Your investments have gained {format_currency(total_gain)} in total."
                )
            elif total_gain < Decimal('0'):
                report['ai_observations'].append(
                    f"Your investments have lost {format_currency(-total_gain)} in total."
                )
        
        return report
    
    def research_investments(self, query: str) -> Dict:
        """Research investment options."""
        if not GROQ_AVAILABLE or not self.api_key or not self.client:
            return {
                'error': 'AI research is not available',
                'suggestions': []
            }
        
        research_prompt = f"""
You are a financial research assistant. Provide accurate, up-to-date information about investment options.

User Query: {query}

Guidelines:
1. Provide factual information only
2. Clearly separate FACT from DATA from ANALYSIS from RISK from UNKNOWN
3. Do not guarantee returns
4. Do not claim an investment will definitely make money
5. Do not execute trades
6. Include source information when available
7. Focus on Nigerian and international options where relevant
8. Include fees, minimum investments, liquidity, and risk information

Structure your response with clear sections:
- Options Found
- Key Details (for each option)
- Comparison
- Important Disclosures
- Sources

Be educational and research-focused.
"""
        
        try:
            messages = [
                {"role": "system", "content": research_prompt},
                {"role": "user", "content": f"Research: {query}"}
            ]
            
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=3000,
                top_p=0.9,
                stop=None,
                stream=False
            )
            
            content = response.choices[0].message.content
            
            # Parse the response into a structured format
            return {
                'query': query,
                'response': content,
                'sources': self._extract_sources(content)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'query': query
            }
    
    def _extract_sources(self, text: str) -> List[Dict]:
        """Extract source information from research response."""
        sources = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('source:') or line.lower().startswith('sources:'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    sources.append({'source': parts[1].strip()})
            elif 'http://' in line or 'https://' in line:
                # Extract URLs
                import re
                urls = re.findall(r'https?://[^\s]+', line)
                for url in urls:
                    sources.append({'source': url})
        
        return sources


# Singleton instance
ai_assistant = AIAssistant()
