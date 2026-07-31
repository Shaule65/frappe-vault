"""Vault Folder DocType controller."""

from frappe.model.document import Document


class VaultFolder(Document):
    """Folder organization for vault secrets."""

    def validate(self):
        if self.folder_name:
            self.folder_name = self.folder_name.strip()
