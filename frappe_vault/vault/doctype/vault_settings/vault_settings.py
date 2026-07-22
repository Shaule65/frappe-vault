"""Vault Settings DocType controller."""

import frappe
from frappe.model.document import Document


class VaultSettings(Document):
    """App-wide settings for Frappe Vault."""
    pass


def get_vault_settings():
    """Get cached vault settings."""
    return frappe.get_cached_doc("Vault Settings")
