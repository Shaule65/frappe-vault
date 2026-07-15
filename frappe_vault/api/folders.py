"""Folders API — folder CRUD endpoints."""

import frappe
from frappe import _


@frappe.whitelist()
def get_all():
    return frappe.get_list(
        "Vault Folder",
        fields=["name", "folder_name", "parent_vault_folder", "is_group", "icon", "color", "description"],
        order_by="lft"
    )


@frappe.whitelist()
def create(folder_name, parent_vault_folder=None, icon=None, color=None, description=None):
    if not frappe.has_permission("Vault Folder", "create"):
        frappe.throw(_("You don't have permission to create folders"), frappe.PermissionError)

    doc = frappe.get_doc({
        "doctype": "Vault Folder",
        "folder_name": folder_name,
        "parent_vault_folder": parent_vault_folder,
        "icon": icon,
        "color": color,
        "description": description
    })
    doc.insert()
    return {"name": doc.name}


@frappe.whitelist()
def delete(name):
    from frappe_vault.utils.permissions import has_folder_permission
    if not has_folder_permission(name, ptype="delete"):
        frappe.throw(_("You don't have permission to delete this folder"), frappe.PermissionError)

    # Cascading delete: delete all secrets stored inside this folder first
    from frappe_vault.services.secret_service import delete_secret
    secrets = frappe.get_all("Vault Secret", filters={"folder": name}, fields=["name"])
    for s in secrets:
        # Ignore permissions when cascading deleting secrets if we have permission to delete the folder
        try:
            # We already have permission to delete the folder, so we are allowed to delete secrets inside it
            # We bypass the inner delete check to prevent permission mismatches
            frappe.delete_doc("Vault Secret", s.name, force=True, ignore_doctypes=["Vault Audit Log"], ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to delete secret {s.name} during folder deletion: {str(e)}")

    # Delete folder shares
    shares = frappe.get_all("Vault Share", filters={"shared_doctype": "Vault Folder", "shared_name": name}, pluck="name")
    for share_name in shares:
        frappe.delete_doc("Vault Share", share_name, force=True, ignore_permissions=True)

    frappe.delete_doc("Vault Folder", name, ignore_permissions=True)
    return {"deleted": name}


@frappe.whitelist()
def update(name, folder_name, color=None, description=None):
    from frappe_vault.utils.permissions import has_folder_permission
    if not has_folder_permission(name, ptype="write"):
        frappe.throw(_("You don't have permission to update this folder"), frappe.PermissionError)

    if folder_name and folder_name != name:
        # Since autoname is mapped to folder_name, we must rename the doc properly
        # so that all linked Vault Secrets, Shares, etc. are updated automatically.
        from frappe.model.rename_doc import rename_doc as _rename_doc
        name = _rename_doc("Vault Folder", name, folder_name, ignore_permissions=True)

    doc = frappe.get_doc("Vault Folder", name)
    if color is not None:
        doc.color = color
    if description is not None:
        doc.description = description
    
    doc.flags.ignore_permissions = True
    doc.save()
    return {"name": doc.name}


@frappe.whitelist()
def get_folder_secrets(folder_name, limit=50, offset=0):
    if not frappe.has_permission("Vault Folder", "read", folder_name):
        frappe.throw(_("You don't have permission to view this folder"), frappe.PermissionError)

    from frappe_vault.utils.constants import LIST_VIEW_FIELDS
    filters = {"folder": folder_name}
    secrets = frappe.get_list(
        "Vault Secret",
        filters=filters,
        fields=LIST_VIEW_FIELDS,
        order_by="modified desc",
        limit_page_length=int(limit),
        limit_start=int(offset)
    )
    total = frappe.db.count("Vault Secret", filters=filters)
    return {"secrets": secrets, "total": total}
