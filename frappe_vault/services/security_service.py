"""Security service — scoring, breach detection, weak password analysis."""

import frappe
from frappe import _
from frappe.utils import add_days, today


@frappe.whitelist()
def calculate_security_score(user: str | None = None) -> dict:
    total = frappe.db.count("Vault Secret", filters={"secret_type": "Password"})
    if not total:
        return {"score": 100, "breakdown": {"total": 0, "weak": 0, "old": 0, "strong": 0}, "suggestions": []}

    weak_count = frappe.db.count(
        "Vault Secret", filters={"secret_type": "Password", "password_strength": ["in", ["weak", "fair"]]}
    )
    threshold_date = add_days(today(), -90)
    old_count = frappe.db.count(
        "Vault Secret", filters={"secret_type": "Password", "password_last_changed": ["<", threshold_date]}
    )
    strong_count = frappe.db.count(
        "Vault Secret",
        filters={"secret_type": "Password", "password_strength": ["in", ["strong", "excellent"]]},
    )

    score = 100 - (weak_count / total) * 40 - (old_count / total) * 30
    score = max(0, min(100, score))

    suggestions = []
    if weak_count:
        suggestions.append(_("Update {0} weak password(s)").format(weak_count))
    if old_count:
        suggestions.append(_("Rotate {0} password(s) older than 90 days").format(old_count))

    return {
        "score": round(score),
        "breakdown": {"total": total, "weak": weak_count, "old": old_count, "strong": strong_count},
        "suggestions": suggestions,
    }


def check_password_breach(password: str) -> dict:
    """Breach check placeholder."""
    return {"is_breached": False, "count": 0}


def get_weak_passwords(user: str | None = None) -> list[dict]:
    return frappe.get_list(
        "Vault Secret",
        filters={"password_strength": ("in", ["weak", "fair"])},
        fields=["name", "title", "password_strength", "url", "password_last_changed"],
    )
