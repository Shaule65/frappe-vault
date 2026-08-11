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
        self.validate_totp_secret()

    def validate_title(self):
        """Ensure title is present and trimmed."""
        if self.title:
            self.title = self.title.strip()
        if not self.title:
            frappe.throw(_("Title is required"))

    def validate_totp_secret(self):
        """Ensure the provided TOTP secret is a valid Base32 string and auto-pad if needed."""
        totp_secret_val = getattr(self, "totp_secret", None)
        if totp_secret_val and totp_secret_val != "*****":
            import re

            import pyotp

            clean_secret = str(totp_secret_val).strip().replace(" ", "").upper()
            if not clean_secret:
                self.totp_secret = ""
                return

            if clean_secret.isdigit() and len(clean_secret) in (6, 8):
                frappe.throw(
                    _(
                        "You entered a 6-digit TOTP passcode instead of the TOTP Secret Key. Please enter the Base32 2FA seed key."
                    )
                )

            unpadded = clean_secret.rstrip("=")
            if not unpadded or not re.match(r"^[A-Z2-7]+$", unpadded):
                frappe.throw(
                    _(
                        "Invalid TOTP Secret Key. Base32 keys can only contain letters A-Z and digits 2-7 (equal signs are only allowed at the end)."
                    )
                )

            if len(unpadded) < 8:
                frappe.throw(
                    _("TOTP Secret Key is too short. Base32 seed keys must be at least 8 characters long.")
                )

            rem = len(unpadded) % 8
            if rem in (1, 3, 6):
                frappe.throw(_("Invalid Base32 TOTP Secret key length."))

            if "=" in clean_secret:
                expected_pad_len = {0: 0, 2: 6, 4: 4, 5: 3, 7: 1}[rem]
                actual_pad_len = len(clean_secret) - len(unpadded)
                if actual_pad_len != expected_pad_len:
                    frappe.throw(
                        _("Incorrect Base32 padding. Found {0} equal sign(s), expected {1}.").format(
                            actual_pad_len, expected_pad_len
                        )
                    )

            padded = unpadded + ("=" * {2: 6, 4: 4, 5: 3, 7: 1}.get(rem, 0))

            try:
                pyotp.TOTP(padded).now()
                self.totp_secret = padded
            except Exception:
                frappe.throw(
                    _("Invalid TOTP Secret (2FA Seed). Please ensure you pasted a valid Base32 key.")
                )

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
        except Exception:
            # Log the error with full traceback but never let statistics tracking block secret retrieval
            frappe.log_error(title=f"Vault Access Metadata Error ({self.name})")
