"""Generator service — password generation and strength analysis."""

import math
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
    """Generate a cryptographically secure random password.

    Args:
        length: Password length (8-128)
        use_uppercase: Include A-Z
        use_lowercase: Include a-z
        use_digits: Include 0-9
        use_special: Include special characters
        exclude_ambiguous: Exclude O/0/l/1/I etc.

    Returns:
        Generated password string
    """
    length = max(8, min(128, int(length)))

    charset = ""
    required_chars = []

    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if exclude_ambiguous:
        upper = upper.replace("O", "").replace("I", "")
        lower = lower.replace("l", "")
        digits = digits.replace("0", "").replace("1", "")

    if use_uppercase:
        charset += upper
        required_chars.append(secrets.choice(upper))
    if use_lowercase:
        charset += lower
        required_chars.append(secrets.choice(lower))
    if use_digits:
        charset += digits
        required_chars.append(secrets.choice(digits))
    if use_special:
        charset += special
        required_chars.append(secrets.choice(special))

    if not charset:
        charset = lower
        required_chars = [secrets.choice(lower)]

    # Fill remaining length with random chars
    remaining = length - len(required_chars)
    password_chars = required_chars + [secrets.choice(charset) for _ in range(remaining)]

    # Shuffle to avoid predictable positions
    password_list = list(password_chars)
    # Fisher-Yates shuffle with secrets
    for i in range(len(password_list) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_list[i], password_list[j] = password_list[j], password_list[i]

    return "".join(password_list)


def calculate_password_strength(password: str) -> dict:
    """Analyze password strength.

    Returns:
        dict with level, score (0-100), and feedback list
    """
    if not password:
        return {"level": "weak", "score": 0, "feedback": ["Password is empty"]}

    score = 0
    feedback = []
    length = len(password)

    # Length scoring (up to 30 points)
    if length >= 16:
        score += 30
    elif length >= 12:
        score += 20
    elif length >= 8:
        score += 10
    else:
        feedback.append("Use at least 8 characters")

    # Character variety (up to 40 points)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in password)

    variety_count = sum([has_upper, has_lower, has_digit, has_special])
    score += variety_count * 10

    if not has_upper:
        feedback.append("Add uppercase letters")
    if not has_lower:
        feedback.append("Add lowercase letters")
    if not has_digit:
        feedback.append("Add numbers")
    if not has_special:
        feedback.append("Add special characters")

    # Entropy estimation (up to 30 points)
    charset_size = 0
    if has_upper:
        charset_size += 26
    if has_lower:
        charset_size += 26
    if has_digit:
        charset_size += 10
    if has_special:
        charset_size += 30

    if charset_size > 0:
        entropy = length * math.log2(charset_size)
        if entropy >= 80:
            score += 30
        elif entropy >= 60:
            score += 20
        elif entropy >= 40:
            score += 10

    # Determine level
    if score >= 85:
        level = "excellent"
    elif score >= 65:
        level = "strong"
    elif score >= 45:
        level = "good"
    elif score >= 25:
        level = "fair"
    else:
        level = "weak"

    return {"level": level, "score": min(100, score), "feedback": feedback}
