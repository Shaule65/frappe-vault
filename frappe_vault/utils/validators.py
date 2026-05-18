"""Input validation helpers for Frappe Vault."""

import frappe
from frappe import _


def validate_secret_type(secret_type: str):
    """Validate that the secret type is allowed."""
    from frappe_vault.utils.constants import SECRET_TYPES

    if secret_type not in SECRET_TYPES:
        frappe.throw(_("Invalid secret type: {0}").format(secret_type))


def validate_permission_level(level: str):
    """Validate sharing permission level."""
    from frappe_vault.utils.constants import PERMISSION_LEVELS

    if level not in PERMISSION_LEVELS:
        frappe.throw(_("Invalid permission level: {0}").format(level))


def sanitize_string(value: str, max_length: int = 140) -> str:
    """Sanitize and truncate a string input."""
    if not value:
        return ""
    return str(value).strip()[:max_length]
