"""Password generation utilities for Frappe Vault."""

import secrets
import string


def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_special: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """Generate a secure random password.
    
    Args:
        length: The length of the password (default: 16)
        use_uppercase: Include uppercase letters (default: True)
        use_lowercase: Include lowercase letters (default: True)
        use_digits: Include digits (default: True)
        use_special: Include special characters (default: True)
        exclude_ambiguous: Exclude ambiguous characters like 0, O, l, 1 (default: False)
        
    Returns:
        A secure random password string
        
    Raises:
        ValueError: If no character types are selected
    """
    characters = ""
    required_chars = []
    
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Remove ambiguous characters if requested
    if exclude_ambiguous:
        uppercase = uppercase.replace("O", "").replace("I", "")
        lowercase = lowercase.replace("l", "").replace("o", "")
        digits = digits.replace("0", "").replace("1", "")
    
    if use_uppercase:
        characters += uppercase
        required_chars.append(secrets.choice(uppercase))
        
    if use_lowercase:
        characters += lowercase
        required_chars.append(secrets.choice(lowercase))
        
    if use_digits:
        characters += digits
        required_chars.append(secrets.choice(digits))
        
    if use_special:
        characters += special
        required_chars.append(secrets.choice(special))
    
    if not characters:
        raise ValueError("At least one character type must be selected")
    
    # Ensure minimum length accommodates required characters
    if length < len(required_chars):
        length = len(required_chars)
    
    # Generate remaining characters
    remaining_length = length - len(required_chars)
    password_chars = required_chars + [secrets.choice(characters) for _ in range(remaining_length)]
    
    # Shuffle and return
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def calculate_password_strength(password: str) -> dict:
    """Calculate the strength of a password.
    
    Args:
        password: The password to evaluate
        
    Returns:
        A dictionary with strength metrics:
        - score: 0-100 strength score
        - level: 'weak', 'fair', 'good', 'strong', 'excellent'
        - feedback: List of improvement suggestions
    """
    score = 0
    feedback = []
    
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~`" for c in password)
    
    # Length scoring
    if length >= 16:
        score += 30
    elif length >= 12:
        score += 20
    elif length >= 8:
        score += 10
    else:
        feedback.append("Password should be at least 8 characters long")
    
    # Character variety scoring
    if has_upper:
        score += 15
    else:
        feedback.append("Add uppercase letters")
        
    if has_lower:
        score += 15
    else:
        feedback.append("Add lowercase letters")
        
    if has_digit:
        score += 15
    else:
        feedback.append("Add numbers")
        
    if has_special:
        score += 25
    else:
        feedback.append("Add special characters")
    
    # Determine level
    if score >= 90:
        level = "excellent"
    elif score >= 70:
        level = "strong"
    elif score >= 50:
        level = "good"
    elif score >= 30:
        level = "fair"
    else:
        level = "weak"
    
    return {
        "score": min(score, 100),
        "level": level,
        "feedback": feedback,
    }
