"""Vault One Time Link DocType controller."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime
import secrets


class VaultOneTimeLink(Document):
    """One-time shareable links for secrets."""

    def before_insert(self):
        """Generate unique token and set creator."""
        self.token = secrets.token_urlsafe(32)
        self.created_by = frappe.session.user

    def is_valid(self):
        """Check if link is still valid."""
        if self.is_consumed:
            return False
        if self.view_count >= (self.max_views or 1):
            return False
        if self.expires_at and now_datetime() > self.expires_at:
            return False
        return True

    def consume(self):
        """Mark the link as consumed and increment view count."""
        self.view_count = (self.view_count or 0) + 1
        if self.view_count >= (self.max_views or 1):
            self.is_consumed = 1
        self.save(ignore_permissions=True)
