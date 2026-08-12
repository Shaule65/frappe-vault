"""Folders API — folder CRUD endpoints."""

import frappe
from frappe import _


@frappe.whitelist()
def get_all() -> list[dict]:
    folders = frappe.get_list(
        "Vault Folder", fields=["name", "folder_name", "icon", "owner"], order_by="folder_name asc"
    )

    user = frappe.session.user
    roles = frappe.get_roles(user)
    is_admin = user == "Administrator" or "Vault Admin" in roles or "System Manager" in roles

    writable_folder_names = set()
    if not is_admin:
        # Use parameterized query instead of f-string
        writable_shares = frappe.db.sql(
            """
            SELECT shared_name FROM `tabVault Share`
            WHERE shared_doctype = 'Vault Folder'
            AND is_revoked = 0
            AND permission_level IN ('Edit', 'Full Control')
            AND (expires_on IS NULL OR expires_on > NOW())
            AND (
                (share_type = 'User' AND user = %(user)s)
                OR (share_type = 'Role' AND frappe_role IN (
                    SELECT role FROM `tabHas Role` WHERE parent = %(user)s
                ))
            )
            """,
            {"user": user},
            pluck=True,
        )
        writable_folder_names = set(writable_shares)

    for f in folders:
        if is_admin or f.get("owner") == user or f.get("name") in writable_folder_names:
            f["can_write"] = 1
        else:
            f["can_write"] = 0

    return folders


@frappe.whitelist()
def create(folder_name: str, icon: str | None = None, **kwargs) -> dict:
    if not folder_name or not isinstance(folder_name, str):
        frappe.throw(_("Folder name is required"), frappe.ValidationError)
    if not frappe.has_permission("Vault Folder", "create"):
        frappe.throw(_("You don't have permission to create folders"), frappe.PermissionError)

    doc = frappe.get_doc({"doctype": "Vault Folder", "folder_name": folder_name, "icon": icon})
    doc.insert()

    # Notify Vault Admins of new folder creation
    from frappe_vault.services.notification_service import notify_vault_admins

    creator_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
    notify_vault_admins(
        subject=f"New Folder Created: '{doc.folder_name}'",
        email_content=f"{creator_name} created folder '{doc.folder_name}'.",
        document_type="Vault Folder",
        document_name=doc.name,
    )

    return {"name": doc.name}


@frappe.whitelist()
def delete(name: str, delete_secrets: bool = False) -> dict:
    if not name or not isinstance(name, str):
        frappe.throw(_("Invalid folder identifier"), frappe.ValidationError)
    from frappe_vault.utils.permissions import has_folder_permission

    if not has_folder_permission(name, ptype="delete"):
        frappe.throw(_("You don't have permission to delete this folder"), frappe.PermissionError)

    folder_name = frappe.db.get_value("Vault Folder", name, "folder_name") or name

    should_delete_secrets = (
        frappe.utils.cint(delete_secrets) if not isinstance(delete_secrets, bool) else delete_secrets
    )

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
    shares = frappe.get_all(
        "Vault Share", filters={"shared_doctype": "Vault Folder", "shared_name": name}, pluck="name"
    )
    for share_name in shares:
        frappe.delete_doc("Vault Share", share_name, force=True, ignore_permissions=True)

    # Unlink historical Vault Audit Log records for this folder so audit trail remains intact without blocking deletion
    frappe.db.sql("UPDATE `tabVault Audit Log` SET folder = NULL WHERE folder = %s", (name,))

    # Delete the folder document itself
    frappe.delete_doc(
        "Vault Folder", name, force=True, ignore_doctypes=["Vault Audit Log"], ignore_permissions=True
    )

    # Notify Vault Admins
    from frappe_vault.services.notification_service import notify_vault_admins

    actor_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
    notify_vault_admins(
        subject=f"Folder Deleted: '{folder_name}'",
        email_content=f"{actor_name} deleted folder '{folder_name}'.",
        document_type="Vault Folder",
        document_name=name,
    )

    return {"deleted": name, "deleted_secrets": bool(should_delete_secrets)}


@frappe.whitelist()
def update(name: str, folder_name: str | None = None, icon: str | None = None, **kwargs) -> dict:
    if not name or not isinstance(name, str):
        frappe.throw(_("Invalid folder identifier"), frappe.ValidationError)
    from frappe_vault.utils.permissions import has_folder_permission

    if not has_folder_permission(name, ptype="write"):
        frappe.throw(_("You don't have permission to update this folder"), frappe.PermissionError)

    if folder_name and folder_name != name and isinstance(folder_name, str):
        from frappe.model.rename_doc import rename_doc as _rename_doc

        name = _rename_doc("Vault Folder", name, folder_name)

    doc = frappe.get_doc("Vault Folder", name)
    if icon is not None:
        doc.icon = icon

    doc.save()
    return {"name": doc.name}


@frappe.whitelist()
def get_folder_secrets(folder_name: str, limit: int = 50, offset: int = 0) -> dict:
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
        limit=int(limit),
        limit_start=int(offset),
    )
    total = frappe.db.count("Vault Secret", filters=filters)
    return {"secrets": secrets, "total": total}
