# Utility functions for the api

from flask import jsonify

# Validate username
def validate_name(name: str) -> bool:
    """Validate that the name is a non-empty string."""
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Invalid name"}), 400
    if len(name) < 3 or len(name) > 50:
        return jsonify({"error": "Name must be between 3 and 50 characters"}), 400
    if not name.isalnum() and ' ' not in name:
        return jsonify({"error": "Name must be alphanumeric or contain spaces"}), 400
    if not name[0].isalpha():
        return jsonify({"error": "Name must start with a letter"}), 400
    if not name.isascii():
        return jsonify({"error": "Name must contain only ASCII characters"}), 400
    return True

# Validate email
def validate_email(email: str) -> bool:
    """Validate that the email is a non-empty string."""
    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Invalid email"}), 400
    if len(email) < 5 or len(email) > 120:
        return jsonify({"error": "Email must be between 5 and 120 characters"}), 400
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({"error": "Email must contain '@' and a domain"}), 400
    return True

# Validate password
def validate_password(password: str) -> bool:
    """Validate that the password is a non-empty string."""
    if not isinstance(password, str) or not password.strip():
        return jsonify({"error": "Invalid password"}), 400
    if len(password) < 8 or len(password) > 128:
        return jsonify({"error": "Password must be between 8 and 128 characters"}), 400
    return True

# Hash password
def hash_password(password: str) -> str:
    """Hash the password using a secure hashing algorithm."""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

# Verify password
def verify_password(password: str, hashed_password: str) -> bool:
    """Verify the password against the hashed password."""
    from werkzeug.security import check_password_hash
    return check_password_hash(hashed_password, password)

# Encode image to base64
def encode_image_to_base64(image_data: bytes) -> str:
    """Encode image data to a base64 string."""
    import base64
    return base64.b64encode(image_data).decode('utf-8')