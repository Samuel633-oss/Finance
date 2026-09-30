"""
Simple database management for the finance application.
Uses SQLite for simplicity and ease of deployment.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import json

# Database configuration
DB_PATH = "finance.db"


def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database with all required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Allocation settings (per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allocation_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tithe_percent DECIMAL(5,2) DEFAULT 10.00,
            offering_percent DECIMAL(5,2) DEFAULT 3.00,
            kingdom_care_percent DECIMAL(5,2) DEFAULT 2.00,
            savings_percent DECIMAL(5,2) DEFAULT 10.00,
            investment_percent DECIMAL(5,2) DEFAULT 25.00,
            recurrent_expenditure_percent DECIMAL(5,2) DEFAULT 50.00,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id)
        )
    """)
    
    # Income table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            date DATE NOT NULL,
            source TEXT,
            income_type TEXT,
            is_recurring BOOLEAN DEFAULT FALSE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Giving table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS giving (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Expense categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            is_custom BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, name)
        )
    """)
    
    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            date DATE NOT NULL,
            category_id INTEGER,
            category_name TEXT,
            description TEXT,
            payment_method TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES expense_categories(id)
        )
    """)
    
    # Recurring expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recurring_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            expense_id INTEGER,
            amount DECIMAL(15,2) NOT NULL,
            frequency TEXT NOT NULL,
            next_date DATE,
            start_date DATE,
            end_date DATE,
            description TEXT,
            category TEXT,
            is_confirmed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (expense_id) REFERENCES expenses(id)
        )
    """)
    
    # Budgets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            period TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Budget categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            allocated_amount DECIMAL(15,2) NOT NULL,
            FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE,
            UNIQUE(budget_id, category_name)
        )
    """)
    
    # Savings accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Savings transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            date DATE NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES savings_accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Savings goals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount DECIMAL(15,2) NOT NULL,
            current_amount DECIMAL(15,2) DEFAULT 0.00,
            target_date DATE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Investment accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            provider TEXT,
            account_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Investment holdings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            investment_type TEXT NOT NULL,
            quantity DECIMAL(15,6) NOT NULL,
            purchase_price DECIMAL(15,2) NOT NULL,
            current_price DECIMAL(15,2),
            purchase_date DATE NOT NULL,
            fees DECIMAL(15,2) DEFAULT 0.00,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES investment_accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Investment transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            holding_id INTEGER,
            account_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            quantity DECIMAL(15,6),
            price DECIMAL(15,2),
            date DATE NOT NULL,
            fees DECIMAL(15,2) DEFAULT 0.00,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (holding_id) REFERENCES investment_holdings(id),
            FOREIGN KEY (account_id) REFERENCES investment_accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Investment dividends table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_dividends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            holding_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            date DATE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (holding_id) REFERENCES investment_holdings(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Assets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            value DECIMAL(15,2) NOT NULL,
            acquisition_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Liabilities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS liabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            interest_rate DECIMAL(5,2),
            due_date DATE,
            payment_amount DECIMAL(15,2),
            remaining_balance DECIMAL(15,2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Financial goals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount DECIMAL(15,2) NOT NULL,
            current_amount DECIMAL(15,2) DEFAULT 0.00,
            target_date DATE,
            goal_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # AI insights table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            insight_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            data_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Research reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            report_type TEXT NOT NULL,
            content TEXT NOT NULL,
            source_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Research sources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            url TEXT,
            source_type TEXT,
            date DATE,
            reliability TEXT,
            FOREIGN KEY (report_id) REFERENCES research_reports(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


def execute_query(query: str, params: tuple = (), fetch: bool = False):
    """Execute a database query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_many(query: str, params_list: List[tuple]):
    """Execute multiple database queries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.executemany(query, params_list)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def fetch_one(query: str, params: tuple = ()):
    """Fetch a single row from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()


def fetch_all(query: str, params: tuple = ()):
    """Fetch all rows from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get a user by username."""
    return fetch_one("SELECT * FROM users WHERE username = ?", (username,))


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get a user by ID."""
    return fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))


def create_user(username: str, password_hash: str, email: str = None) -> int:
    """Create a new user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                   (username, password_hash, email))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_allocation_settings(user_id: int) -> Optional[Dict]:
    """Get allocation settings for a user."""
    return fetch_one("SELECT * FROM allocation_settings WHERE user_id = ?", (user_id,))


def create_allocation_settings(user_id: int) -> int:
    """Create default allocation settings for a user."""
    result = execute_query(
        """INSERT INTO allocation_settings (user_id) 
           VALUES (?)""",
        (user_id,)
    )
    return result.lastrowid


def update_allocation_settings(user_id: int, settings: Dict) -> bool:
    """Update allocation settings for a user."""
    existing = get_allocation_settings(user_id)
    if existing:
        execute_query(
            """UPDATE allocation_settings SET 
               tithe_percent = ?, offering_percent = ?, kingdom_care_percent = ?,
               savings_percent = ?, investment_percent = ?, recurrent_expenditure_percent = ?
               WHERE user_id = ?""",
            (settings.get('tithe_percent', 10.00),
             settings.get('offering_percent', 3.00),
             settings.get('kingdom_care_percent', 2.00),
             settings.get('savings_percent', 10.00),
             settings.get('investment_percent', 25.00),
             settings.get('recurrent_expenditure_percent', 50.00),
             user_id)
        )
        return True
    else:
        create_allocation_settings(user_id)
        return update_allocation_settings(user_id, settings)
    return False


# Helper function to convert Decimal to float for JSON serialization
def decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def row_to_dict(row: sqlite3.Row) -> Dict:
    """Convert a SQLite row to a dictionary with proper type conversion."""
    if row is None:
        return None
    
    result = {}
    for key in row.keys():
        val = row[key]
        if isinstance(val, Decimal):
            result[key] = float(val)
        elif isinstance(val, (datetime, date)):
            result[key] = val.isoformat() if val else None
        else:
            result[key] = val
    return result


# Initialize database on import
init_db()
