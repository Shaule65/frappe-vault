"""Vault Folder DocType controller."""

import frappe
from frappe.utils.nestedset import NestedSet


class VaultFolder(NestedSet):
    """Tree-based folder organization for vault secrets."""

    nsm_parent_field = "parent_vault_folder"

    def validate(self):
        if self.folder_name:
            self.folder_name = self.folder_name.strip()
