"""Vault Secret DocType controller."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class VaultSecret(Document):
    """Controller for Vault Secret — the core secrets storage DocType."""

    def validate(self):
        """Validate the secret before saving."""
        self.validate_title()
        self.calculate_password_strength()

    def validate_title(self):
        """Ensure title is present and trimmed."""
        if self.title:
            self.title = self.title.strip()
        if not self.title:
            frappe.throw(_("Title is required"))

    def calculate_password_strength(self):
        """Auto-calculate password strength when password changes."""
        if self.secret_type == "Password" and self.password:
            from frappe_vault.services.generator_service import calculate_password_strength

            strength = calculate_password_strength(self.password)
            self.password_strength = strength.get("level", "")

    def before_save(self):
        """Track password changes."""
        if self.is_new() or self.has_value_changed("password"):
            self.password_last_changed = today()

    def after_insert(self):
        """Post-insert: update access metadata."""
        self.update_access_metadata()

    def update_access_metadata(self):
        """Update access tracking fields without triggering modified."""
        try:
            # Use direct frappe.db.set_value to avoid document reload deadlocks
            frappe.db.set_value(
                "Vault Secret",
                self.name,
                {
                    "last_accessed": now_datetime(),
                    "access_count": (self.access_count or 0) + 1,
                },
                update_modified=False,
            )
        except Exception as e:
            # Log the error but never let statistics tracking block secret retrieval
            frappe.log_error(f"Failed to update access metadata for {self.name}: {e}", "Vault Access Metadata Error")
