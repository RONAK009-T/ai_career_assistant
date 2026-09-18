import hashlib
import os
import streamlit as st
from database.models import (
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_user_password
)

def hash_password(password: str, salt: str = None) -> str:
    """Securely hashes a password using PBKDF2 with SHA-256 and salt."""
    if not salt:
        salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"{salt}${pwd_hash}"

def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """Verifies a provided password against stored salted hash."""
    try:
        salt, pwd_hash = stored_password_hash.split('$')
        check_hash = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return check_hash == pwd_hash
    except Exception:
        return False

def init_session():
    """Initializes Streamlit session state keys for user authentication."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

def login_user(username_or_email, password):
    """Authenticates a user and establishes session state."""
    user = get_user_by_username(username_or_email) or get_user_by_email(username_or_email)
    if not user:
        return False, "User not found. Please check your credentials or register."
    
    if verify_password(user['password_hash'], password):
        st.session_state.authenticated = True
        st.session_state.user = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'target_role': user.get('target_role', 'Software Engineer'),
            'bio': user.get('bio', '')
        }
        return True, "Login successful!"
    return False, "Incorrect password. Please try again."

def register_user(username, email, password, full_name, target_role="Software Engineer", bio=""):
    """Registers a new user after verifying uniqueness."""
    if get_user_by_username(username):
        return False, "Username is already taken. Please choose another."
    if get_user_by_email(email):
        return False, "An account with this email already exists."
    
    pwd_hash = hash_password(password)
    user_id = create_user(username, email, pwd_hash, full_name, target_role, bio)
    if user_id:
        st.session_state.authenticated = True
        st.session_state.user = {
            'id': user_id,
            'username': username.lower(),
            'email': email.lower(),
            'full_name': full_name,
            'target_role': target_role,
            'bio': bio
        }
        return True, "Account registered and logged in successfully!"
    return False, "Failed to create account. Please try again."

def reset_password(email, new_password):
    """Resets user password by email."""
    user = get_user_by_email(email)
    if not user:
        return False, "No account found with this email."
    pwd_hash = hash_password(new_password)
    success = update_user_password(user['id'], pwd_hash)
    if success:
        return True, "Password updated successfully. Please log in with your new password."
    return False, "Failed to update password. Please try again."

def logout_user():
    """Logs out the active user and clears session state."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

def get_current_user():
    """Returns current active user dict or None."""
    if st.session_state.get('authenticated') and st.session_state.get('user'):
        user_id = st.session_state.user['id']
        fresh = get_user_by_id(user_id)
        if fresh:
            st.session_state.user['full_name'] = fresh['full_name']
            st.session_state.user['target_role'] = fresh.get('target_role', 'Software Engineer')
            st.session_state.user['bio'] = fresh.get('bio', '')
        return st.session_state.user
    return None
