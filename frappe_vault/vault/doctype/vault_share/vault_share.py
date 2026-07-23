"""Vault Share DocType controller."""

import frappe
from frappe import _
from frappe.model.document import Document


class VaultShare(Document):
    """Controls sharing of secrets and folders with users or roles."""

    def validate(self):
        self.validate_share_target()
        self.set_shared_by()

    def validate_share_target(self):
        """Ensure exactly one target is set based on share_type."""
        if self.share_type == "User" and not self.user:
            frappe.throw(_("User is required when Share Type is User"))
        elif self.share_type == "Role" and not self.frappe_role:
            frappe.throw(_("Role is required when Share Type is Role"))

    def set_shared_by(self):
        """Auto-set the sharing user."""
        if not self.shared_by:
            self.shared_by = frappe.session.user
