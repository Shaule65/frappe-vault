"""Vault Policy DocType controller."""

import frappe
from frappe import _
from frappe.model.document import Document


class VaultPolicy(Document):
    """Password and access policy for the vault."""

    def validate(self):
        if self.is_default:
            # Unset any other default policy
            frappe.db.set_value(
                "Vault Policy",
                {"is_default": 1, "name": ("!=", self.name)},
                "is_default",
                0,
            )
