"""Sharing API — share/unshare endpoints and one-time links."""

import frappe
from frappe import _


@frappe.whitelist()
def share(shared_name, shared_doctype="Vault Secret", share_type="User", user=None, frappe_role=None, permission_level="View Only", expires_on=None):
    from frappe_vault.services.sharing_service import share_secret
    return share_secret(shared_name=shared_name, shared_doctype=shared_doctype, share_type=share_type, user=user, frappe_role=frappe_role, permission_level=permission_level, expires_on=expires_on)


@frappe.whitelist()
def unshare(share_name):
    from frappe_vault.services.sharing_service import unshare as _unshare
    return _unshare(share_name)


@frappe.whitelist()
def get_shares(secret_name):
    from frappe_vault.services.sharing_service import get_shares_for_secret
    return get_shares_for_secret(secret_name)


@frappe.whitelist()
def shared_with_me(limit=20, offset=0):
    from frappe_vault.services.sharing_service import get_shared_with_me
    return get_shared_with_me(limit=int(limit), offset=int(offset))


@frappe.whitelist()
def create_one_time_link(secret_name, expiry_hours=24, max_views=1, passphrase=None):
    from frappe_vault.services.sharing_service import create_one_time_link as _create
    return _create(secret_name, expiry_hours=int(expiry_hours), max_views=int(max_views), passphrase=passphrase)


@frappe.whitelist(allow_guest=True)
def consume_link(token, passphrase=None):
    from frappe_vault.services.sharing_service import consume_one_time_link
    return consume_one_time_link(token, passphrase=passphrase)


@frappe.whitelist()
def get_share_options():
    # Only authenticated users
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw(_("Not logged in"), frappe.PermissionError)

    # 1. Fetch active, non-system users (excluding guest, administrator, and current user)
    users = frappe.get_all(
        "User",
        filters={
            "enabled": 1,
            "user_type": "System User",
            "name": ["not in", ["Guest", "Administrator", frappe.session.user]]
        },
        fields=["name", "full_name"],
        order_by="full_name asc"
    )
    
    # Filter out users with admin roles as they already have full access
    admin_users = set(
        frappe.get_all(
            "Has Role",
            filters={"role": ["in", ["Vault Admin", "System Manager"]]},
            pluck="parent"
        )
    )
    non_admin_users = [u for u in users if u.name not in admin_users]
            
    user_options = [{"value": u.name, "label": u.full_name or u.name} for u in non_admin_users]

    # 2. Fetch active system roles
    roles = frappe.get_all(
        "Role",
        filters={
            "disabled": 0,
        },
        fields=["name"],
        order_by="name asc"
    )
    role_options = [{"value": r.name, "label": r.name} for r in roles]

    return {
        "users": user_options,
        "roles": role_options
    }


@frappe.whitelist()
def bulk_delete_shares(share_names):
    from frappe_vault.services.sharing_service import bulk_delete_shares as _bulk_delete
    if isinstance(share_names, str):
        share_names = frappe.parse_json(share_names)
    return _bulk_delete(share_names)

