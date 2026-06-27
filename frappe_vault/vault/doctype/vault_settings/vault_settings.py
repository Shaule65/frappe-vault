"""Vault Settings DocType controller."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.password import check_password as verify_password


class VaultSettings(Document):
    """App-wide settings for Frappe Vault."""
    pass


def get_vault_settings():
    """Get cached vault settings."""
    return frappe.get_cached_doc("Vault Settings")


def require_master_password():
    """Verify master password session is active. Throws if not."""
    settings = get_vault_settings()
    if not settings.enable_master_password:
        return

    session_key = f"vault_master_pwd_verified:{frappe.session.user}"
    verified_at = frappe.cache().get_value(session_key)

    if not verified_at:
        frappe.throw(
            _("Master password verification required"),
            frappe.ValidationError,
        )

    # Check session timeout
    from frappe.utils import now_datetime, time_diff_in_seconds
    timeout_secs = (settings.session_timeout or 30) * 60
    elapsed = time_diff_in_seconds(now_datetime(), verified_at)

    if elapsed > timeout_secs:
        frappe.cache().delete_value(session_key)
        frappe.throw(
            _("Master password session expired"),
            frappe.ValidationError,
        )


@frappe.whitelist()
def verify_master_password(password: str) -> dict:
    """Verify master password and create session."""
    settings = get_vault_settings()
    if not settings.enable_master_password:
        return {"verified": True}

    from frappe.utils.password import get_decrypted_password
    stored = get_decrypted_password("Vault Settings", "Vault Settings", "master_password")

    if stored and password == stored:
        session_key = f"vault_master_pwd_verified:{frappe.session.user}"
        frappe.cache().set_value(session_key, frappe.utils.now_datetime())
        return {"verified": True}

    frappe.throw(_("Invalid master password"))
