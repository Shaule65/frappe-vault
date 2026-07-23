"""Vault Settings DocType controller."""

import frappe
from frappe.model.document import Document


class VaultSettings(Document):
    """App-wide settings for Frappe Vault."""

    def onload(self):
        """Ensure settings is not submittable and docstatus is 0 (Editable/Saveable)."""
        frappe.db.sql("UPDATE `tabDocType` SET is_submittable = 0 WHERE name = 'Vault Settings'")
        if self.docstatus != 0:
            frappe.db.set_value("Vault Settings", "Vault Settings", "docstatus", 0)
            self.docstatus = 0


def get_vault_settings():
    """Get cached vault settings."""
    return frappe.get_cached_doc("Vault Settings")
