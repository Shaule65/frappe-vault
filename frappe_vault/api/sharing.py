"""Sharing API — share/unshare endpoints and one-time links."""

import frappe
from frappe import _


@frappe.whitelist()
def share(shared_name, shared_doctype="Vault Secret", share_type="User", user=None, group=None, frappe_role=None, permission_level="View Only", expires_on=None):
    from frappe_vault.services.sharing_service import share_secret
    return share_secret(shared_name=shared_name, shared_doctype=shared_doctype, share_type=share_type, user=user, group=group, frappe_role=frappe_role, permission_level=permission_level, expires_on=expires_on)


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
