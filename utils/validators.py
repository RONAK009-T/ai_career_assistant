import re
from pathlib import Path
from config.settings import MAX_FILE_SIZE_MB, ALLOWED_RESUME_EXTENSIONS, ALLOWED_DOC_EXTENSIONS

def validate_email(email: str) -> bool:
    """Checks if email format is valid."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))

def validate_username(username: str) -> tuple[bool, str]:
    """Validates username length and characters."""
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(username) > 30:
        return False, "Username must be at most 30 characters."
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain alphanumeric characters and underscores."
    return True, ""

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validates basic password security standards."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def validate_uploaded_file(uploaded_file, allowed_types="resume") -> tuple[bool, str]:
    """Validates uploaded file size and extension."""
    if uploaded_file is None:
        return False, "No file selected."
    
    # Check size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f} MB) exceeds limit of {MAX_FILE_SIZE_MB} MB."
    
    # Check extension
    ext = Path(uploaded_file.name).suffix.lower()
    allowed = ALLOWED_RESUME_EXTENSIONS if allowed_types == "resume" else ALLOWED_DOC_EXTENSIONS
    if ext not in allowed:
        return False, f"Invalid file format '{ext}'. Allowed formats: {', '.join(allowed)}"
    
    return True, ""
