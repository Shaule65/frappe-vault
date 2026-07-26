"""Security service — scoring, breach detection, weak password analysis."""

import frappe
from frappe import _
from frappe.utils import add_days, getdate, today


@frappe.whitelist()
def calculate_security_score(user=None):
    secrets = frappe.get_list("Vault Secret", filters={"secret_type": "Password"},
                             fields=["name", "password_strength", "password_last_changed", "expires_on"])
    if not secrets:
        return {"score": 100, "breakdown": {}, "suggestions": []}

    total = len(secrets)
    weak_count = sum(1 for s in secrets if s.password_strength in ("weak", "fair"))
    old_count = sum(1 for s in secrets if s.password_last_changed and getdate(s.password_last_changed) < getdate(add_days(today(), -90)))
    strong_count = sum(1 for s in secrets if s.password_strength in ("strong", "excellent"))

    score = 100 - (weak_count / total) * 40 - (old_count / total) * 30
    score = max(0, min(100, score))

    suggestions = []
    if weak_count:
        suggestions.append(_("Update {0} weak password(s)").format(weak_count))
    if old_count:
        suggestions.append(_("Rotate {0} password(s) older than 90 days").format(old_count))

    return {"score": round(score), "breakdown": {"total": total, "weak": weak_count, "old": old_count, "strong": strong_count}, "suggestions": suggestions}


def check_password_breach(password):
    """Breach check placeholder."""
    return {"is_breached": False, "count": 0}


def get_weak_passwords(user=None):
    return frappe.get_list("Vault Secret", filters={"password_strength": ("in", ["weak", "fair"])},
                           fields=["name", "title", "password_strength", "url", "password_last_changed"])
