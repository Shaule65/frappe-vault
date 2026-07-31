"""Folders API — folder CRUD endpoints."""

import frappe
from frappe import _


@frappe.whitelist()
def get_all():
    folders = frappe.get_list(
        "Vault Folder",
        fields=["name", "folder_name", "icon", "owner"],
        order_by="folder_name asc"
    )

    user = frappe.session.user
    roles = frappe.get_roles(user)
    is_admin = user == "Administrator" or "Vault Admin" in roles or "System Manager" in roles

    writable_folder_names = set()
    if not is_admin:
        share_conds = ["shared_doctype = 'Vault Folder'", "is_revoked = 0", "permission_level IN ('Edit', 'Full Control')", "(expires_on IS NULL OR expires_on > NOW())"]
        target_user_conds = [f"(share_type = 'User' AND user = {frappe.db.escape(user)})"]
        if roles:
            roles_str = ", ".join([frappe.db.escape(r) for r in roles])
            target_user_conds.append(f"(share_type = 'Role' AND frappe_role IN ({roles_str}))")
        share_conds.append("(" + " OR ".join(target_user_conds) + ")")

        writable_shares = frappe.db.sql(f"""
            SELECT shared_name FROM `tabVault Share`
            WHERE {" AND ".join(share_conds)}
        """, pluck=True)
        writable_folder_names = set(writable_shares)

    for f in folders:
        if is_admin or f.get("owner") == user or f.get("name") in writable_folder_names:
            f["can_write"] = 1
        else:
            f["can_write"] = 0

    return folders


@frappe.whitelist()
def create(folder_name, icon=None, **kwargs):
    if not folder_name or not isinstance(folder_name, str):
        frappe.throw(_("Folder name is required"), frappe.ValidationError)
    if not frappe.has_permission("Vault Folder", "create"):
        frappe.throw(_("You don't have permission to create folders"), frappe.PermissionError)

    doc = frappe.get_doc({
        "doctype": "Vault Folder",
        "folder_name": folder_name,
        "icon": icon
    })
    doc.insert()
    return {"name": doc.name}


@frappe.whitelist()
def delete(name, delete_secrets=False):
    if not name or not isinstance(name, str):
        frappe.throw(_("Invalid folder identifier"), frappe.ValidationError)
    from frappe_vault.utils.permissions import has_folder_permission
    if not has_folder_permission(name, ptype="delete"):
        frappe.throw(_("You don't have permission to delete this folder"), frappe.PermissionError)

    should_delete_secrets = frappe.utils.cint(delete_secrets) if not isinstance(delete_secrets, bool) else delete_secrets

    secrets = frappe.get_all("Vault Secret", filters={"folder": name}, fields=["name"])
    if should_delete_secrets:
        from frappe_vault.services.secret_service import delete_secret
        for s in secrets:
            delete_secret(s.name)
    else:
        # Move secrets to root (no folder)
        for s in secrets:
            frappe.db.set_value("Vault Secret", s.name, "folder", None)

    # Delete folder shares
    shares = frappe.get_all("Vault Share", filters={"shared_doctype": "Vault Folder", "shared_name": name}, pluck="name")
    for share_name in shares:
        frappe.delete_doc("Vault Share", share_name, force=True, ignore_permissions=True)

    # Unlink historical Vault Audit Log records for this folder so audit trail remains intact without blocking deletion
    frappe.db.sql("UPDATE `tabVault Audit Log` SET folder = NULL WHERE folder = %s", (name,))

    # Delete the folder document itself
    frappe.delete_doc("Vault Folder", name, force=True, ignore_doctypes=["Vault Audit Log"], ignore_permissions=True)
    return {"deleted": name, "deleted_secrets": bool(should_delete_secrets)}


@frappe.whitelist()
def update(name, folder_name=None, icon=None, **kwargs):
    if not name or not isinstance(name, str):
        frappe.throw(_("Invalid folder identifier"), frappe.ValidationError)
    from frappe_vault.utils.permissions import has_folder_permission
    if not has_folder_permission(name, ptype="write"):
        frappe.throw(_("You don't have permission to update this folder"), frappe.PermissionError)

    if folder_name and folder_name != name and isinstance(folder_name, str):
        from frappe.model.rename_doc import rename_doc as _rename_doc
        name = _rename_doc("Vault Folder", name, folder_name, ignore_permissions=True)

    doc = frappe.get_doc("Vault Folder", name)
    if icon is not None:
        doc.icon = icon

    doc.flags.ignore_permissions = True
    doc.save()
    return {"name": doc.name}


@frappe.whitelist()
def get_folder_secrets(folder_name, limit=50, offset=0):
    if not folder_name or not isinstance(folder_name, str):
        frappe.throw(_("Invalid folder identifier"), frappe.ValidationError)
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

