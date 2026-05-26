"""Secrets API — CRUD and search endpoints for Vault Secrets."""

import frappe
from frappe import _


@frappe.whitelist()
def list(search=None, title=None, username=None, secret_type=None, folder=None, favorites_only=False, tag=None, limit=20, offset=0, order_by="modified desc"):
    from frappe_vault.services.secret_service import get_secrets
    return get_secrets(search=search, title=title, username=username, secret_type=secret_type, folder=folder, favorites_only=frappe.utils.cint(favorites_only), tag=tag, limit=int(limit), offset=int(offset), order_by=order_by)


@frappe.whitelist()
def get(name, decrypt=False):
    from frappe_vault.services.secret_service import get_secret
    return get_secret(name, decrypt=frappe.utils.cint(decrypt))


@frappe.whitelist()
def create(**kwargs):
    from frappe_vault.services.secret_service import create_secret
    return create_secret(kwargs)


@frappe.whitelist()
def update(name, **kwargs):
    from frappe_vault.services.secret_service import update_secret
    return update_secret(name, kwargs)


@frappe.whitelist()
def delete(name):
    from frappe_vault.services.secret_service import delete_secret
    return delete_secret(name)


@frappe.whitelist()
def toggle_favorite(name):
    from frappe_vault.services.secret_service import toggle_favorite as _toggle
    return _toggle(name)


@frappe.whitelist()
def bulk_move(secret_names, target_folder):
    from frappe_vault.services.secret_service import bulk_move as _move
    if isinstance(secret_names, str):
        secret_names = frappe.parse_json(secret_names)
    return _move(secret_names, target_folder)


@frappe.whitelist()
def stats():
    from frappe_vault.services.secret_service import get_vault_stats
    return get_vault_stats()


@frappe.whitelist()
def decrypt(name):
    """Decrypt a secret's sensitive fields. Requires master password session."""
    from frappe_vault.vault.doctype.vault_settings.vault_settings import require_master_password
    require_master_password()
    from frappe_vault.services.secret_service import get_secret
    return get_secret(name, decrypt=True)
