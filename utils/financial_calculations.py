"""
Financial calculation utilities for the finance application.
All calculations are deterministic and use Decimal for precision.
"""

from decimal import Decimal, getcontext
from typing import Dict, List, Optional
from datetime import date, datetime

# Set high precision for financial calculations
getcontext().prec = 28


def validate_allocation_percentages(allocation: Dict[str, Decimal]) -> bool:
    """Validate that allocation percentages sum to exactly 100%."""
    total = sum(allocation.values())
    return total == Decimal('100')


def calculate_allocation_amounts(amount: Decimal, allocation: Dict[str, Decimal]) -> Dict[str, Decimal]:
    """Calculate monetary amounts for each allocation percentage."""
    if not validate_allocation_percentages(allocation):
        raise ValueError("Allocation percentages must sum to exactly 100%")
    
    return {category: (amount * percentage / Decimal('100')).quantize(Decimal('0.01')) 
            for category, percentage in allocation.items()}


def calculate_net_worth(assets: List[Dict], liabilities: List[Dict]) -> Decimal:
    """Calculate net worth: Total Assets - Total Liabilities."""
    def safe_decimal(value):
        """Safely convert value to Decimal, handling None and other edge cases."""
        if value is None:
            return Decimal('0')
        try:
            return Decimal(str(value))
        except (TypeError, ValueError, AttributeError):
            return Decimal('0')
    
    total_assets = sum(safe_decimal(asset.get('value', 0)) for asset in (assets or []))
    total_liabilities = sum(safe_decimal(liability.get('amount', 0)) for liability in (liabilities or []))
    return (total_assets - total_liabilities).quantize(Decimal('0.01'))


def calculate_budget_usage(budget: Decimal, actual: Decimal) -> Dict:
    """Calculate budget usage statistics."""
    if budget == Decimal('0'):
        return {
            'used': Decimal('0'),
            'remaining': Decimal('0'),
            'percentage_used': Decimal('0'),
            'over_budget': False
        }
    
    percentage_used = (actual / budget * Decimal('100')).quantize(Decimal('0.01'))
    remaining = (budget - actual).quantize(Decimal('0.01'))
    
    return {
        'used': actual.quantize(Decimal('0.01')),
        'remaining': remaining,
        'percentage_used': percentage_used,
        'over_budget': actual > budget
    }


def calculate_savings_progress(target: Decimal, current: Decimal) -> Dict:
    """Calculate savings goal progress."""
    if target == Decimal('0'):
        return {
            'progress_percent': Decimal('0'),
            'amount_remaining': Decimal('0'),
            'completed': False
        }
    
    progress_percent = (current / target * Decimal('100')).quantize(Decimal('0.01'))
    amount_remaining = (target - current).quantize(Decimal('0.01'))
    
    return {
        'progress_percent': progress_percent,
        'amount_remaining': amount_remaining,
        'completed': current >= target
    }


def calculate_investment_gain(purchase_price: Decimal, current_price: Decimal, quantity: Decimal) -> Dict:
    """Calculate investment gain/loss."""
    total_cost = (purchase_price * quantity).quantize(Decimal('0.01'))
    total_value = (current_price * quantity).quantize(Decimal('0.01'))
    gain_loss = (total_value - total_cost).quantize(Decimal('0.01'))
    
    if total_cost == Decimal('0'):
        gain_percent = Decimal('0')
    else:
        gain_percent = (gain_loss / total_cost * Decimal('100')).quantize(Decimal('0.01'))
    
    return {
        'total_cost': total_cost,
        'total_value': total_value,
        'gain_loss': gain_loss,
        'gain_percent': gain_percent
    }


def calculate_goal_contribution(target: Decimal, current: Decimal, target_date: date) -> Dict:
    """Calculate required periodic contribution to reach a savings goal."""
    today = date.today()
    days_remaining = (target_date - today).days
    
    if days_remaining <= 0:
        return {
            'daily_required': Decimal('0'),
            'weekly_required': Decimal('0'),
            'monthly_required': Decimal('0'),
            'days_remaining': 0
        }
    
    amount_remaining = (target - current).quantize(Decimal('0.01'))
    
    if amount_remaining <= Decimal('0'):
        return {
            'daily_required': Decimal('0'),
            'weekly_required': Decimal('0'),
            'monthly_required': Decimal('0'),
            'days_remaining': days_remaining
        }
    
    daily_required = (amount_remaining / Decimal(str(days_remaining))).quantize(Decimal('0.01'))
    weekly_required = (daily_required * Decimal('7')).quantize(Decimal('0.01'))
    monthly_required = (daily_required * Decimal('30')).quantize(Decimal('0.01'))
    
    return {
        'daily_required': daily_required,
        'weekly_required': weekly_required,
        'monthly_required': monthly_required,
        'days_remaining': days_remaining
    }


def calculate_cash_flow(income: List[Dict], expenses: List[Dict], date_range: Optional[Dict] = None) -> Decimal:
    """Calculate cash flow (income - expenses) for a given period."""
    start_date = date_range.get('start') if date_range else None
    end_date = date_range.get('end') if date_range else None
    
    total_income = Decimal('0')
    for inc in income:
        inc_date = inc.get('date')
        if inc_date:
            if start_date and inc_date < start_date:
                continue
            if end_date and inc_date > end_date:
                continue
        total_income += Decimal(str(inc.get('amount', 0)))
    
    total_expenses = Decimal('0')
    for exp in expenses:
        exp_date = exp.get('date')
        if exp_date:
            if start_date and exp_date < start_date:
                continue
            if end_date and exp_date > end_date:
                continue
        total_expenses += Decimal(str(exp.get('amount', 0)))
    
    return (total_income - total_expenses).quantize(Decimal('0.01'))


def calculate_giving_percentage(giving: List[Dict], income: List[Dict]) -> Decimal:
    """Calculate giving as a percentage of income."""
    total_giving = sum(Decimal(str(g.get('amount', 0))) for g in giving)
    total_income = sum(Decimal(str(i.get('amount', 0))) for i in income)
    
    if total_income == Decimal('0'):
        return Decimal('0')
    
    return (total_giving / total_income * Decimal('100')).quantize(Decimal('0.01'))


def calculate_savings_rate(income: List[Dict], savings: List[Dict]) -> Decimal:
    """Calculate savings rate as a percentage of income."""
    total_income = sum(Decimal(str(i.get('amount', 0))) for i in income)
    total_savings = sum(Decimal(str(s.get('amount', 0))) for s in savings)
    
    if total_income == Decimal('0'):
        return Decimal('0')
    
    return (total_savings / total_income * Decimal('100')).quantize(Decimal('0.01'))


def get_default_allocation() -> Dict[str, Decimal]:
    """Get default money allocation percentages."""
    return {
        'Tithe': Decimal('10'),
        'Offering': Decimal('3'),
        'Kingdom Care': Decimal('2'),
        'Savings': Decimal('10'),
        'Investment': Decimal('25'),
        'Recurrent Expenditure': Decimal('50')
    }


def format_currency(amount: Decimal, currency: str = '₦') -> str:
    """Format amount as currency string."""
    return f"{currency}{amount:,.2f}"


def format_percentage(value: Decimal) -> str:
    """Format percentage value."""
    return f"{value:.2f}%"
