# auth.py — Handles user signup, login, and session management
# For portfolio purposes, users are stored in memory (a dictionary)
# In a real app, you'd use a database like PostgreSQL or MongoDB

import hashlib
import uuid

# In-memory user store: { email: { name, email, phone, password_hash, id } }
USERS = {}

# Active sessions: { session_token: email }
SESSIONS = {}


def hash_password(password):
    """Convert plain password to SHA-256 hash (never store plain passwords!)"""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_password_strength(password):
    """
    Check if password meets requirements:
    - Min 8 characters
    - At least one uppercase
    - At least one lowercase
    - At least one number
    - At least one special character
    Returns (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"


def signup(name, email, phone, password, confirm_password):
    """
    Register a new user.
    Returns (success: bool, message: str, data: dict or None)
    """
    # Basic field checks
    if not all([name, email, phone, password, confirm_password]):
        return False, "All fields are required", None

    if password != confirm_password:
        return False, "Passwords do not match", None

    if email in USERS:
        return False, "An account with this email already exists", None

    # Password strength check
    is_valid, msg = validate_password_strength(password)
    if not is_valid:
        return False, msg, None

    # Create and store user
    user_id = str(uuid.uuid4())
    USERS[email] = {
        "id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": hash_password(password),
        "location": "",
        "linkedin": "",
        "github": ""
    }

    return True, "Account created successfully!", {"name": name, "email": email}


def login(identifier, password):
    """
    Log in with email or phone + password.
    Returns (success: bool, message: str, session_token or None)
    """
    if not identifier or not password:
        return False, "Email/phone and password are required", None

    # Find user by email or phone
    user = None
    for u in USERS.values():
        if u["email"] == identifier or u["phone"] == identifier:
            user = u
            break

    if not user:
        return False, "No account found with this email or phone number", None

    if user["password_hash"] != hash_password(password):
        return False, "Incorrect password", None

    # Create session token
    token = str(uuid.uuid4())
    SESSIONS[token] = user["email"]

    return True, "Login successful!", {
        "token": token,
        "name": user["name"],
        "email": user["email"]
    }


def logout(token):
    """Remove session token"""
    if token in SESSIONS:
        del SESSIONS[token]
        return True, "Logged out successfully"
    return False, "Invalid session"


def get_user_by_token(token):
    """Return user data from session token, or None if invalid"""
    email = SESSIONS.get(token)
    if not email:
        return None
    return USERS.get(email)


def update_profile(token, updates):
    """
    Update user profile fields (name, phone, location, linkedin, github).
    Returns (success: bool, message: str)
    """
    user = get_user_by_token(token)
    if not user:
        return False, "Unauthorized. Please login again."

    allowed_fields = ["name", "phone", "location", "linkedin", "github"]
    for field in allowed_fields:
        if field in updates:
            user[field] = updates[field]

    return True, "Profile updated successfully"


def reset_password(email, new_password, confirm_password):
    """
    Simulate password reset (no actual email sending for portfolio).
    Returns (success: bool, message: str)
    """
    if email not in USERS:
        return False, "No account found with this email"

    if new_password != confirm_password:
        return False, "Passwords do not match"

    is_valid, msg = validate_password_strength(new_password)
    if not is_valid:
        return False, msg

    USERS[email]["password_hash"] = hash_password(new_password)
    return True, "Password reset successfully!"
