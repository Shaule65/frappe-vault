"""Folders API — folder CRUD endpoints."""

import frappe


@frappe.whitelist()
def get_all():
    return frappe.get_all("Vault Folder", fields=["name", "folder_name", "parent_vault_folder", "is_group", "icon", "color", "description"], order_by="lft")


@frappe.whitelist()
def create(folder_name, parent_vault_folder=None, icon=None, color=None, description=None):
    doc = frappe.get_doc({"doctype": "Vault Folder", "folder_name": folder_name, "parent_vault_folder": parent_vault_folder, "icon": icon, "color": color, "description": description})
    doc.insert()
    return {"name": doc.name}


@frappe.whitelist()
def delete(name):
    frappe.delete_doc("Vault Folder", name)
    return {"deleted": name}


@frappe.whitelist()
def get_folder_secrets(folder_name, limit=50, offset=0):
    from frappe_vault.utils.constants import LIST_VIEW_FIELDS
    secrets = frappe.get_all("Vault Secret", filters={"folder": folder_name}, fields=LIST_VIEW_FIELDS, order_by="modified desc", limit_page_length=int(limit), limit_start=int(offset))
    total = frappe.db.count("Vault Secret", filters={"folder": folder_name})
    return {"secrets": secrets, "total": total}
