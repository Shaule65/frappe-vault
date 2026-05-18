"""Vault Audit Log DocType controller."""

from frappe.model.document import Document


class VaultAuditLog(Document):
    """Immutable audit log. No updates allowed after creation."""
    pass
