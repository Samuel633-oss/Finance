"""
Seed data for the finance application.
Creates sample data for demonstration purposes.
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
import random
from .database import (
    get_db_connection, execute_query, execute_many,
    get_user_by_username, create_user
)
from .auth import hash_password

# Sample categories
EXPENSE_CATEGORIES = [
    'Food', 'Transport', 'Housing', 'Utilities', 'Internet/Data',
    'Education', 'Health', 'Entertainment', 'Shopping', 'Subscriptions',
    'Family', 'Personal', 'Business', 'Other'
]

GIVING_CATEGORIES = ['Tithe', 'Offering', 'Kingdom Care', 'Other Giving']

INCOME_TYPES = ['Salary', 'Business', 'Freelance', 'Gift', 'Allowance', 'Other']

INCOME_SOURCES = ['Salary', 'Freelance Work', 'Business Income', 'Gift from Family', 'Allowance']

INVESTMENT_TYPES = [
    'Nigerian stocks', 'International stocks', 'ETFs', 'Equity funds',
    'Money market funds', 'Bonds', 'REITs', 'Other investments'
]

ASSET_TYPES = ['Cash', 'Bank savings', 'Investments', 'Property', 'Vehicle', 'Business interests', 'Other assets']

LIABILITY_TYPES = ['Loans', 'Debt', 'Credit balances', 'Money owed to someone', 'Other liabilities']


def random_date(start_date=None, end_date=None):
    """Generate a random date between start_date and end_date."""
    if start_date is None:
        start_date = date(2023, 1, 1)
    if end_date is None:
        end_date = date.today()
    
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    return start_date + timedelta(days=random_days)


def random_decimal(min_val=1, max_val=10000):
    """Generate a random decimal for amounts."""
    amount = random.uniform(min_val, max_val)
    return Decimal(str(amount)).quantize(Decimal('0.01'))


def create_sample_user():
    """Create a sample user for demonstration."""
    username = 'demo_user'
    existing = get_user_by_username(username)
    
    if not existing:
        password_hash = hash_password('password123')
        user_id = create_user(username, password_hash, 'demo@example.com')
        return user_id
    return existing['id']


def create_sample_allocation_settings(user_id):
    """Create sample allocation settings."""
    execute_query(
        """INSERT OR IGNORE INTO allocation_settings (user_id) 
           VALUES (?)""",
        (user_id,)
    )


def create_sample_income(user_id, count=10):
    """Create sample income records."""
    income_data = []
    for _ in range(count):
        amount = random_decimal(5000, 500000)
        days_ago = random.randint(0, 365)
        income_date = (date.today() - timedelta(days=days_ago)).isoformat()
        
        income_data.append({
            'user_id': user_id,
            'amount': float(amount),
            'date': income_date,
            'source': random.choice(INCOME_SOURCES),
            'income_type': random.choice(INCOME_TYPES),
            'is_recurring': random.choice([True, False]),
            'notes': f"Sample income entry"
        })
    
    # Insert using parameterized query
    for item in income_data:
        execute_query(
            """INSERT INTO income (user_id, amount, date, source, income_type, is_recurring, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (item['user_id'], item['amount'], item['date'], item['source'],
             item['income_type'], item['is_recurring'], item['notes'])
        )


def create_sample_giving(user_id, count=8):
    """Create sample giving records."""
    for _ in range(count):
        amount = random_decimal(1000, 100000)
        days_ago = random.randint(0, 365)
        giving_date = (date.today() - timedelta(days=days_ago)).isoformat()
        
        execute_query(
            """INSERT INTO giving (user_id, amount, date, category, notes) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, float(amount), giving_date, random.choice(GIVING_CATEGORIES), 'Sample giving')
        )


def create_sample_expense_categories(user_id):
    """Create sample expense categories."""
    for category in EXPENSE_CATEGORIES:
        try:
            execute_query(
                """INSERT INTO expense_categories (user_id, name, is_custom) 
                   VALUES (?, ?, ?)""",
                (user_id, category, False)
            )
        except:
            pass  # Category already exists


def create_sample_expenses(user_id, count=20):
    """Create sample expense records."""
    # First, get category IDs
    categories = execute_query(
        "SELECT id, name FROM expense_categories WHERE user_id = ?",
        (user_id,),
        fetch=True
    )
    
    category_map = {row['name']: row['id'] for row in categories} if categories else {}
    
    for _ in range(count):
        amount = random_decimal(100, 50000)
        days_ago = random.randint(0, 365)
        expense_date = (date.today() - timedelta(days=days_ago)).isoformat()
        
        category_name = random.choice(EXPENSE_CATEGORIES)
        category_id = category_map.get(category_name)
        
        payment_methods = ['Cash', 'Bank Transfer', 'Credit Card', 'Debit Card', 'Mobile Money']
        
        execute_query(
            """INSERT INTO expenses (user_id, amount, date, category_id, category_name, description, payment_method, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, float(amount), expense_date, category_id, category_name,
             f"Sample {category_name} expense", random.choice(payment_methods), 'Sample expense')
        )


def create_sample_recurring_expenses(user_id, count=5):
    """Create sample recurring expenses."""
    descriptions = [
        'Internet subscription', 'Rent', 'Streaming subscription',
        'Software subscription', 'Transportation', 'School fees', 'Regular bills'
    ]
    frequencies = ['monthly', 'weekly', 'quarterly', 'yearly']
    
    for _ in range(count):
        amount = random_decimal(1000, 50000)
        next_date = (date.today() + timedelta(days=random.randint(1, 30))).isoformat()
        start_date = (date.today() - timedelta(days=random.randint(30, 365))).isoformat()
        
        execute_query(
            """INSERT INTO recurring_expenses (user_id, amount, frequency, next_date, start_date, description, category, is_confirmed) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, float(amount), random.choice(frequencies), next_date, start_date,
             random.choice(descriptions), random.choice(EXPENSE_CATEGORIES), True)
        )


def create_sample_budgets(user_id, count=3):
    """Create sample budgets."""
    budget_names = ['Monthly Budget', 'Food Budget', 'Entertainment Budget']
    periods = ['monthly', 'weekly', 'yearly']
    
    for i in range(count):
        amount = random_decimal(10000, 500000)
        start_date = (date.today() - timedelta(days=random.randint(0, 30))).isoformat()
        end_date = (date.today() + timedelta(days=30)).isoformat()
        
        execute_query(
            """INSERT INTO budgets (user_id, name, amount, period, start_date, end_date, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, budget_names[i], float(amount), random.choice(periods),
             start_date, end_date, f"Sample {budget_names[i]}")
        )


def create_sample_savings_accounts(user_id, count=2):
    """Create sample savings accounts."""
    account_names = ['Emergency Fund', 'Education Savings', 'General Savings']
    
    for i in range(count):
        execute_query(
            """INSERT INTO savings_accounts (user_id, name, description) 
               VALUES (?, ?, ?)""",
            (user_id, account_names[i], f"Sample {account_names[i]} account")
        )


def create_sample_savings_transactions(user_id, account_ids, count=10):
    """Create sample savings transactions."""
    transaction_types = ['Deposit', 'Withdrawal']
    
    for _ in range(count):
        account_id = random.choice(account_ids)
        amount = random_decimal(1000, 100000)
        days_ago = random.randint(0, 365)
        trans_date = (date.today() - timedelta(days=days_ago)).isoformat()
        trans_type = random.choice(transaction_types)
        
        execute_query(
            """INSERT INTO savings_transactions (account_id, user_id, amount, date, type, description, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (account_id, user_id, float(amount), trans_date, trans_type,
             f"Sample {trans_type}", 'Sample transaction')
        )


def create_sample_savings_goals(user_id, count=3):
    """Create sample savings goals."""
    goal_names = ['Emergency Fund', 'New Computer', 'Education Fund', 'Business Capital']
    
    for i in range(count):
        target_amount = random_decimal(50000, 5000000)
        current_amount = random_decimal(1000, float(target_amount) * 0.8)
        target_date = (date.today() + timedelta(days=random.randint(30, 730))).isoformat()
        
        execute_query(
            """INSERT INTO savings_goals (user_id, name, target_amount, current_amount, target_date, description) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, goal_names[i], float(target_amount), float(current_amount),
             target_date, f"Sample {goal_names[i]} goal")
        )


def create_sample_investment_accounts(user_id, count=2):
    """Create sample investment accounts."""
    account_names = ['Stock Portfolio', 'Mutual Fund Account']
    providers = ['GT Bank', 'Stanbic IBTC', 'Zenith Bank', 'First Bank']
    
    for i in range(count):
        execute_query(
            """INSERT INTO investment_accounts (user_id, name, provider, account_type, description) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, account_names[i], random.choice(providers), 'Brokerage',
             f"Sample {account_names[i]}")
        )


def create_sample_investment_holdings(user_id, account_ids, count=5):
    """Create sample investment holdings."""
    holding_names = ['MTN Nigeria', 'Dangote Cement', 'GT Bank', 'Zenith Bank', 'Access Bank']
    
    for i in range(count):
        account_id = random.choice(account_ids)
        quantity = random.uniform(1, 1000)
        purchase_price = random_decimal(1, 500)
        current_price = purchase_price * Decimal(str(random.uniform(0.8, 1.5)))
        purchase_date = (date.today() - timedelta(days=random.randint(30, 730))).isoformat()
        
        execute_query(
            """INSERT INTO investment_holdings (account_id, user_id, name, investment_type, quantity, purchase_price, current_price, purchase_date, fees, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (account_id, user_id, holding_names[i], 'Nigerian stocks',
             float(quantity), float(purchase_price), float(current_price),
             purchase_date, float(random_decimal(10, 500)), 'Sample holding')
        )


def create_sample_assets(user_id, count=5):
    """Create sample assets."""
    asset_names = ['Cash in Bank', 'Car', 'Laptop', 'Jewelry', 'Real Estate']
    
    for i in range(count):
        value = random_decimal(10000, 5000000)
        acquisition_date = (date.today() - timedelta(days=random.randint(30, 1095))).isoformat()
        
        execute_query(
            """INSERT INTO assets (user_id, name, type, value, acquisition_date, notes) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, asset_names[i], random.choice(ASSET_TYPES), float(value),
             acquisition_date, f"Sample {asset_names[i]}")
        )


def create_sample_liabilities(user_id, count=3):
    """Create sample liabilities."""
    liability_names = ['Student Loan', 'Car Loan', 'Credit Card Balance']
    
    for i in range(count):
        amount = random_decimal(50000, 2000000)
        interest_rate = random.uniform(0, 20)
        due_date = (date.today() + timedelta(days=random.randint(30, 730))).isoformat()
        remaining_balance = amount * Decimal(str(random.uniform(0.1, 1.0)))
        
        execute_query(
            """INSERT INTO liabilities (user_id, name, amount, interest_rate, due_date, remaining_balance, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, liability_names[i], float(amount), float(interest_rate),
             due_date, float(remaining_balance), f"Sample {liability_names[i]}")
        )


def create_sample_financial_goals(user_id, count=3):
    """Create sample financial goals."""
    goal_names = ['Buy a House', 'Start a Business', 'Retirement Fund', 'Education']
    goal_types = ['Long-term', 'Medium-term', 'Short-term']
    
    for i in range(count):
        target_amount = random_decimal(100000, 10000000)
        current_amount = random_decimal(1000, float(target_amount) * 0.5)
        target_date = (date.today() + timedelta(days=random.randint(90, 2555))).isoformat()
        
        execute_query(
            """INSERT INTO financial_goals (user_id, name, target_amount, current_amount, target_date, goal_type, description) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, goal_names[i], float(target_amount), float(current_amount),
             target_date, random.choice(goal_types), f"Sample {goal_names[i]} goal")
        )


def seed_database():
    """Seed the database with sample data."""
    print("Seeding database...")
    
    # Create sample user
    user_id = create_sample_user()
    print(f"Created sample user with ID: {user_id}")
    
    # Create allocation settings
    create_sample_allocation_settings(user_id)
    print("Created allocation settings")
    
    # Create income
    create_sample_income(user_id, 10)
    print("Created sample income records")
    
    # Create giving
    create_sample_giving(user_id, 8)
    print("Created sample giving records")
    
    # Create expense categories
    create_sample_expense_categories(user_id)
    print("Created sample expense categories")
    
    # Create expenses
    create_sample_expenses(user_id, 20)
    print("Created sample expense records")
    
    # Create recurring expenses
    create_sample_recurring_expenses(user_id, 5)
    print("Created sample recurring expenses")
    
    # Create budgets
    create_sample_budgets(user_id, 3)
    print("Created sample budgets")
    
    # Create savings accounts
    create_sample_savings_accounts(user_id, 2)
    account_ids = execute_query(
        "SELECT id FROM savings_accounts WHERE user_id = ?",
        (user_id,),
        fetch=True
    )
    account_ids = [row['id'] for row in account_ids] if account_ids else []
    
    # Create savings transactions
    create_sample_savings_transactions(user_id, account_ids, 10)
    print("Created sample savings accounts and transactions")
    
    # Create savings goals
    create_sample_savings_goals(user_id, 3)
    print("Created sample savings goals")
    
    # Create investment accounts
    create_sample_investment_accounts(user_id, 2)
    inv_account_ids = execute_query(
        "SELECT id FROM investment_accounts WHERE user_id = ?",
        (user_id,),
        fetch=True
    )
    inv_account_ids = [row['id'] for row in inv_account_ids] if inv_account_ids else []
    
    # Create investment holdings
    create_sample_investment_holdings(user_id, inv_account_ids, 5)
    print("Created sample investment accounts and holdings")
    
    # Create assets
    create_sample_assets(user_id, 5)
    print("Created sample assets")
    
    # Create liabilities
    create_sample_liabilities(user_id, 3)
    print("Created sample liabilities")
    
    # Create financial goals
    create_sample_financial_goals(user_id, 3)
    print("Created sample financial goals")
    
    print("Database seeding completed!")


if __name__ == '__main__':
    seed_database()
