"""Sharing service — share/unshare secrets and folders with users, groups, roles."""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date
import secrets as secrets_module


def share_secret(
    shared_name: str,
    shared_doctype: str = "Vault Secret",
    share_type: str = "User",
    user: str = None,
    group: str = None,
    frappe_role: str = None,
    permission_level: str = "View Only",
    expires_on: str = None,
) -> dict:
    """Share a secret or folder with a user, group, or role.

    Returns:
        dict with share document name
    """
    # Verify caller owns or has Full Control on the item
    if shared_doctype == "Vault Secret":
        if not frappe.has_permission("Vault Secret", "share", shared_name):
            frappe.throw(_("You don't have permission to share this secret"), frappe.PermissionError)
    elif shared_doctype == "Vault Folder":
        if not frappe.has_permission("Vault Folder", "share", shared_name):
            frappe.throw(_("You don't have permission to share this folder"), frappe.PermissionError)

    if share_type == "User" and user:
        owner = frappe.db.get_value(shared_doctype, shared_name, "owner")
        if user == owner:
            frappe.throw(_("You cannot share an item with its owner"))

    doc = frappe.get_doc({
        "doctype": "Vault Share",
        "share_type": share_type,
        "user": user if share_type == "User" else None,
        "group": group if share_type == "Group" else None,
        "frappe_role": frappe_role if share_type == "Role" else None,
        "permission_level": permission_level,
        "shared_doctype": shared_doctype,
        "shared_name": shared_name,
        "expires_on": expires_on,
        "shared_by": frappe.session.user,
    })
    doc.insert()

    return {"name": doc.name}


def unshare(share_name: str) -> dict:
    """Mark a share as revoked instead of deleting it, so it remains in the sharing audit log."""
    doc = frappe.get_doc("Vault Share", share_name)

    # Only the sharer or owner of the item can unshare
    if doc.shared_by != frappe.session.user and "Vault Admin" not in frappe.get_roles():
        if frappe.db.exists(doc.shared_doctype, doc.shared_name):
            owner = frappe.db.get_value(doc.shared_doctype, doc.shared_name, "owner")
            if owner != frappe.session.user:
                frappe.throw(_("Not permitted"), frappe.PermissionError)
        else:
            frappe.throw(_("Not permitted"), frappe.PermissionError)

    frappe.db.set_value("Vault Share", share_name, {
        "is_revoked": 1,
        "revoked_by": frappe.session.user
    })
    
    # Log the activity
    from frappe_vault.services.audit_service import log_share_removed
    log_share_removed(doc, None)
    
    frappe.db.commit()
    return {"removed": share_name}


def get_shares_for_secret(secret_name: str) -> list:
    """Get all shares for a secret."""
    shares = frappe.get_all(
        "Vault Share",
        filters={
            "shared_doctype": "Vault Secret",
            "shared_name": secret_name,
        },
        fields=["name", "share_type", "user", "group", "frappe_role",
                "permission_level", "expires_on", "shared_by", "is_revoked", "revoked_by"],
        order_by="creation desc",
    )
    return shares


def get_shared_with_me(limit: int = 20, offset: int = 0) -> dict:
    """Get secrets/folders shared with the current user or all shares if Admin."""
    user = frappe.session.user
    user_roles = frappe.get_roles(user)

    is_admin = user == "Administrator" or "Vault Admin" in user_roles or "System Manager" in user_roles

    if is_admin:
        where = "1=1"
    else:
        user_groups = frappe.get_all("Vault Group Member", filters={"user": user}, pluck="parent")
        conditions = [f"vs.share_type = 'User' AND vs.user = {frappe.db.escape(user)}"]
        if user_groups:
            groups_str = ", ".join([frappe.db.escape(g) for g in user_groups])
            conditions.append(f"vs.share_type = 'Group' AND vs.`group` IN ({groups_str})")
        if user_roles:
            roles_str = ", ".join([frappe.db.escape(r) for r in user_roles])
            conditions.append(f"vs.share_type = 'Role' AND vs.frappe_role IN ({roles_str})")
        where = " OR ".join(f"({c})" for c in conditions)

    secrets = frappe.db.sql(f"""
        SELECT vs.name as share_name, vs.shared_doctype, vs.shared_name,
               vs.permission_level, vs.shared_by, vs.expires_on,
               vs.share_type, vs.user, vs.group, vs.frappe_role,
               vs.is_revoked, vs.revoked_by,
               COALESCE(sec.title, fld.folder_name) as title,
               sec.secret_type, sec.url, sec.folder
        FROM `tabVault Share` vs
        LEFT JOIN `tabVault Secret` sec ON vs.shared_name = sec.name AND vs.shared_doctype = 'Vault Secret'
        LEFT JOIN `tabVault Folder` fld ON vs.shared_name = fld.name AND vs.shared_doctype = 'Vault Folder'
        WHERE ({where}) AND (sec.name IS NOT NULL OR fld.name IS NOT NULL)
        ORDER BY vs.creation DESC
        LIMIT %s OFFSET %s
    """, (limit, offset), as_dict=True)

    total = frappe.db.sql(f"""
        SELECT count(*)
        FROM `tabVault Share` vs
        LEFT JOIN `tabVault Secret` sec ON vs.shared_name = sec.name AND vs.shared_doctype = 'Vault Secret'
        LEFT JOIN `tabVault Folder` fld ON vs.shared_name = fld.name AND vs.shared_doctype = 'Vault Folder'
        WHERE ({where}) AND (sec.name IS NOT NULL OR fld.name IS NOT NULL)
    """)[0][0]

    return {"shared": secrets, "total": total, "limit": limit, "offset": offset}


def create_one_time_link(
    secret_name: str,
    expiry_hours: int = 24,
    max_views: int = 1,
    passphrase: str = None,
) -> dict:
    """Create a one-time shareable link for a secret."""
    if not frappe.has_permission("Vault Secret", "read", secret_name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    if not frappe.has_permission("Vault One Time Link", "create"):
        frappe.throw(_("You don't have permission to create links"), frappe.PermissionError)

    doc = frappe.get_doc({
        "doctype": "Vault One Time Link",
        "secret": secret_name,
        "expires_at": add_to_date(now_datetime(), hours=expiry_hours),
        "max_views": max_views,
        "passphrase": passphrase,
    })
    doc.insert()

    return {
        "name": doc.name,
        "token": doc.token,
        "expires_at": str(doc.expires_at),
        "url": f"/vault/shared/{doc.token}",
    }


def consume_one_time_link(token: str, passphrase: str = None) -> dict:
    """Consume a one-time link and return the secret data."""
    link_name = frappe.db.get_value("Vault One Time Link", {"token": token}, "name")

    if not link_name:
        frappe.throw(_("Link not found"), frappe.DoesNotExistError)

    link = frappe.get_doc("Vault One Time Link", link_name)

    if not link.is_valid():
        frappe.throw(_("This link has expired or been consumed"))

    # Verify passphrase if set
    if link.passphrase:
        from frappe.utils.password import get_decrypted_password
        stored = get_decrypted_password("Vault One Time Link", link.name, "passphrase")
        if stored and passphrase != stored:
            frappe.throw(_("Invalid passphrase"))

    # Get secret data
    from frappe_vault.utils.encryption import get_decrypted_secret_data
    secret = frappe.get_doc("Vault Secret", link.secret)

    result = {
        "title": secret.title,
        "secret_type": secret.secret_type,
        "url": secret.url,
        "username": secret.username,
        "email": secret.email,
        "notes": secret.notes,
        "decrypted": get_decrypted_secret_data(link.secret),
    }

    # Consume the link
    link.consume()

    return result


def bulk_delete_shares(share_names: list) -> dict:
    """Delete multiple shares permanently. Checks permission for each."""
    user = frappe.session.user
    roles = frappe.get_roles(user)
    is_admin = user == "Administrator" or "Vault Admin" in roles or "System Manager" in roles

    deleted = []
    for name in share_names:
        if not frappe.db.exists("Vault Share", name):
            continue
        doc = frappe.get_doc("Vault Share", name)
        
        # Check permissions:
        # Admin can delete anything.
        # Standard user can delete if they are the sharer (shared_by) OR the recipient (user/group member/role)
        can_delete = is_admin or doc.shared_by == user
        
        if not can_delete:
            if doc.share_type == "User" and doc.user == user:
                can_delete = True
            elif doc.share_type == "Group":
                user_groups = frappe.get_all("Vault Group Member", filters={"user": user}, pluck="parent")
                if doc.group in user_groups:
                    can_delete = True
            elif doc.share_type == "Role":
                if doc.frappe_role in roles:
                    can_delete = True
                    
        if can_delete:
            frappe.delete_doc("Vault Share", name, ignore_permissions=True)
            deleted.append(name)
            
    frappe.db.commit()
    return {"deleted": deleted}
