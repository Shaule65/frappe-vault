"""Background tasks for Frappe Vault."""

import frappe
from frappe import _
from frappe.utils import add_days, getdate, today


def check_password_expiry():
    """Check for passwords that haven't been changed in a while.
    
    Sends notifications for passwords older than 90 days.
    Called via scheduler.
    """
    threshold_days = 90
    threshold_date = add_days(today(), -threshold_days)
    
    # Get all secrets with old passwords
    old_passwords = frappe.get_all(
        "Vault Secret",
        filters={
            "secret_type": "Password",
            "password_last_changed": ["<", threshold_date]
        },
        fields=["name", "title", "owner", "password_last_changed"]
    )
    
    # Group by owner
    by_owner = {}
    for secret in old_passwords:
        owner = secret.get("owner")
        if owner not in by_owner:
            by_owner[owner] = []
        by_owner[owner].append(secret)
    
    # Send notifications
    for owner, secrets in by_owner.items():
        if owner == "Administrator":
            continue
            
        try:
            send_password_expiry_notification(owner, secrets)
        except Exception as e:
            frappe.log_error(
                f"Failed to send password expiry notification to {owner}: {e}",
                "Vault Password Expiry"
            )


def send_password_expiry_notification(user: str, secrets: list):
    """Send password expiry notification to a user.
    
    Args:
        user: The user email
        secrets: List of secrets with old passwords
    """
    if not secrets:
        return
    
    # Create notification
    doc = frappe.get_doc({
        "doctype": "Notification Log",
        "subject": _("Password Update Reminder"),
        "email_content": _("You have {0} password(s) that haven't been updated in over 90 days.").format(len(secrets)),
        "for_user": user,
        "type": "Alert",
        "document_type": "Vault Secret",
        "document_name": secrets[0].get("name")
    })
    doc.insert(ignore_permissions=True)


def cleanup_old_access_logs():
    """Clean up access logs older than configured retention period.
    
    Default retention is 365 days. Called via scheduler.
    """
    retention_days = frappe.db.get_single_value("Vault Settings", "log_retention_days") or 365
    threshold_date = add_days(today(), -retention_days)
    
    # Delete old logs
    frappe.db.delete("Vault Access Log", {
        "access_time": ["<", threshold_date]
    })
    
    frappe.db.commit()


def calculate_security_score(user: str = None) -> dict:
    """Calculate a security score for a user's vault.
    
    Args:
        user: User email (defaults to current user)
        
    Returns:
        dict with score and breakdown
    """
    user = user or frappe.session.user
    
    secrets = frappe.get_all(
        "Vault Secret",
        filters={"owner": user, "secret_type": "Password"},
        fields=["name", "password_strength", "password_last_changed"]
    )
    
    if not secrets:
        return {"score": 100, "breakdown": {}, "suggestions": []}
    
    total = len(secrets)
    
    # Score breakdown
    weak_count = sum(1 for s in secrets if s.get("password_strength") in ["weak", "fair"])
    old_count = sum(1 for s in secrets if s.get("password_last_changed") and 
                    getdate(s["password_last_changed"]) < add_days(today(), -90))
    strong_count = sum(1 for s in secrets if s.get("password_strength") in ["strong", "excellent"])
    
    # Calculate score
    score = 100
    score -= (weak_count / total) * 40  # -40 max for weak passwords
    score -= (old_count / total) * 30   # -30 max for old passwords
    score = max(0, min(100, score))
    
    suggestions = []
    if weak_count > 0:
        suggestions.append(_("Update {0} weak password(s)").format(weak_count))
    if old_count > 0:
        suggestions.append(_("Rotate {0} password(s) older than 90 days").format(old_count))
    
    return {
        "score": round(score),
        "breakdown": {
            "total": total,
            "weak": weak_count,
            "old": old_count,
            "strong": strong_count
        },
        "suggestions": suggestions
    }


@frappe.whitelist()
def get_security_score() -> dict:
    """Get security score for current user.
    
    Returns:
        dict with score details
    """
    return calculate_security_score(frappe.session.user)
