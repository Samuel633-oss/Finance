"""
Simple authentication utilities for the finance application.
"""

import hashlib
import secrets
import os
from typing import Optional, Dict
from .database import get_user_by_username, get_user_by_id, create_user

# Simple session management using in-memory storage
# For production, consider using a more robust solution
sessions = {}


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    salt = os.environ.get('PASSWORD_SALT', 'finance_app_salt')
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(stored_hash: str, provided_password: str) -> bool:
    """Verify a password against the stored hash."""
    return hash_password(provided_password) == stored_hash


def create_session(user_id: int) -> str:
    """Create a new session for a user."""
    session_id = secrets.token_hex(32)
    sessions[session_id] = {
        'user_id': user_id,
        'created_at': __import__('datetime').datetime.now().isoformat()
    }
    return session_id


def get_session(session_id: str) -> Optional[Dict]:
    """Get session information."""
    return sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """Delete a session."""
    if session_id in sessions:
        del sessions[session_id]
        return True
    return False


def get_current_user(session_id: str) -> Optional[Dict]:
    """Get the current user from session."""
    session = get_session(session_id)
    if session:
        return get_user_by_id(session['user_id'])
    return None


def login_user(username: str, password: str) -> Optional[str]:
    """Authenticate a user and create a session."""
    user = get_user_by_username(username)
    if user and verify_password(user['password_hash'], password):
        return create_session(user['id'])
    return None


def register_user(username: str, password: str, email: str = None) -> Optional[int]:
    """Register a new user."""
    if get_user_by_username(username):
        return None  # Username already exists
    
    password_hash = hash_password(password)
    user_id = create_user(username, password_hash, email)
    return user_id


def require_auth(session_id: str):
    """Decorator to require authentication."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_current_user(session_id)
            if not user:
                raise PermissionError("Authentication required")
            kwargs['current_user'] = user
            return func(*args, **kwargs)
        return wrapper
    return decorator
