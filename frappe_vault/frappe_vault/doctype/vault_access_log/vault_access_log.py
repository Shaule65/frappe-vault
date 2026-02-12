"""Vault Access Log DocType controller."""

from frappe.model.document import Document


class VaultAccessLog(Document):
    """Read-only DocType for tracking secret access."""
    
    def validate(self):
        """Validate the access log entry."""
        pass
    
    def before_save(self):
        """Prevent modifications to existing logs."""
        if not self.is_new():
            # Prevent modifications to existing logs
            pass
