"""Secret service — core CRUD and business logic for vault secrets."""

import frappe
from frappe import _
from frappe_vault.utils.constants import LIST_VIEW_FIELDS, SENSITIVE_FIELDS
from frappe_vault.services.audit_service import log_secret_viewed, log_secret_copied


def get_secrets(
    search: str = None,
    secret_type: str = None,
    folder: str = None,
    favorites_only: bool = False,
    tag: str = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str = "modified desc",
) -> dict:
    """Get list of secrets visible to current user (respects permission_query_conditions).

    Returns:
        dict with secrets list, total count, and pagination
    """
    filters = {}

    if secret_type:
        filters["secret_type"] = secret_type
    if folder:
        filters["folder"] = folder
    if favorites_only:
        filters["is_favorite"] = 1

    or_filters = None
    if search:
        or_filters = [
            ["title", "like", f"%{search}%"],
            ["url", "like", f"%{search}%"],
            ["username", "like", f"%{search}%"],
            ["email", "like", f"%{search}%"],
        ]

    secrets = frappe.get_all(
        "Vault Secret",
        filters=filters,
        or_filters=or_filters,
        fields=LIST_VIEW_FIELDS,
        order_by=order_by,
        limit_page_length=limit,
        limit_start=offset,
    )

    total = frappe.db.count("Vault Secret", filters=filters)

    return {
        "secrets": secrets,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def get_secret(name: str, decrypt: bool = False) -> dict:
    """Get a single secret with optional decryption.

    Args:
        name: Vault Secret document name
        decrypt: Whether to include decrypted sensitive fields

    Returns:
        dict with secret data
    """
    if not frappe.has_permission("Vault Secret", "read", name):
        frappe.throw(_("You don't have permission to access this secret"), frappe.PermissionError)

    doc = frappe.get_doc("Vault Secret", name)

    result = {
        "name": doc.name,
        "title": doc.title,
        "secret_type": doc.secret_type,
        "folder": doc.folder,
        "url": doc.url,
        "username": doc.username,
        "email": doc.email,
        "notes": doc.notes,
        "is_favorite": doc.is_favorite,
        "password_strength": doc.password_strength,
        "password_last_changed": doc.password_last_changed,
        "last_accessed": str(doc.last_accessed) if doc.last_accessed else None,
        "access_count": doc.access_count,
        "expires_on": str(doc.expires_on) if doc.expires_on else None,
        "tags": [t.tag for t in (doc.tags or [])],
        "owner": doc.owner,
        "modified": str(doc.modified),
    }

    # Type-specific non-sensitive fields
    if doc.secret_type == "API Key":
        result["api_key"] = doc.api_key
    elif doc.secret_type == "Credit Card":
        result["card_holder"] = doc.card_holder
        result["card_expiry"] = doc.card_expiry
    elif doc.secret_type == "Database":
        result["db_host"] = doc.db_host
        result["db_port"] = doc.db_port
        result["db_name"] = doc.db_name

    if decrypt:
        from frappe_vault.utils.encryption import get_decrypted_secret_data
        result["decrypted"] = get_decrypted_secret_data(name)

    # Log access and update metadata
    log_secret_viewed(name)
    doc.update_access_metadata()

    return result


def create_secret(data: dict) -> dict:
    """Create a new vault secret.

    Args:
        data: dict with secret fields

    Returns:
        dict with created secret name
    """
    if not frappe.has_permission("Vault Secret", "create"):
        frappe.throw(_("You don't have permission to create secrets"), frappe.PermissionError)

    doc = frappe.get_doc({
        "doctype": "Vault Secret",
        **{k: v for k, v in data.items() if k not in ("doctype", "name")},
    })
    doc.insert()

    return {"name": doc.name, "title": doc.title}


def update_secret(name: str, data: dict) -> dict:
    """Update an existing vault secret.

    Args:
        name: Vault Secret document name
        data: dict with fields to update

    Returns:
        dict with updated secret name
    """
    if not frappe.has_permission("Vault Secret", "write", name):
        frappe.throw(_("You don't have permission to update this secret"), frappe.PermissionError)

    doc = frappe.get_doc("Vault Secret", name)

    allowed_fields = [
        "title", "secret_type", "folder", "url", "username", "email",
        "password", "api_key", "api_secret", "notes", "is_favorite",
        "ssh_private_key", "certificate", "card_holder", "card_number",
        "card_expiry", "card_cvv", "db_host", "db_port", "db_name",
        "db_password", "expires_on", "custom_fields_json",
    ]

    for field, value in data.items():
        if field in allowed_fields:
            doc.set(field, value)

    doc.save()
    return {"name": doc.name, "title": doc.title}


def delete_secret(name: str) -> dict:
    """Delete a vault secret."""
    if not frappe.has_permission("Vault Secret", "delete", name):
        frappe.throw(_("You don't have permission to delete this secret"), frappe.PermissionError)

    title = frappe.db.get_value("Vault Secret", name, "title")
    frappe.delete_doc("Vault Secret", name)
    return {"name": name, "title": title}


def toggle_favorite(name: str) -> dict:
    """Toggle favorite status."""
    if not frappe.has_permission("Vault Secret", "write", name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    doc = frappe.get_doc("Vault Secret", name)
    doc.is_favorite = 0 if doc.is_favorite else 1
    doc.save()

    return {"name": doc.name, "is_favorite": doc.is_favorite}


def bulk_move(secret_names: list, target_folder: str) -> dict:
    """Move multiple secrets to a target folder."""
    moved = 0
    for name in secret_names:
        if frappe.has_permission("Vault Secret", "write", name):
            frappe.db.set_value("Vault Secret", name, "folder", target_folder)
            moved += 1
    frappe.db.commit()
    return {"moved": moved}


def get_vault_stats() -> dict:
    """Get dashboard statistics for current user."""
    user = frappe.session.user

    total = frappe.db.count("Vault Secret", filters={"owner": user})
    favorites = frappe.db.count("Vault Secret", filters={"owner": user, "is_favorite": 1})
    weak = frappe.db.count("Vault Secret", filters={"owner": user, "password_strength": ("in", ["weak", "fair"])})

    by_type = frappe.db.sql("""
        SELECT secret_type, COUNT(*) as count
        FROM `tabVault Secret`
        WHERE owner = %s
        GROUP BY secret_type
    """, (user,), as_dict=True)

    recent = frappe.get_all(
        "Vault Secret",
        filters={"owner": user},
        fields=["name", "title", "secret_type", "folder", "last_accessed", "url"],
        order_by="last_accessed desc",
        limit=5,
    )

    return {
        "total_secrets": total,
        "favorites": favorites,
        "weak_passwords": weak,
        "secrets_by_type": {s.secret_type: s.count for s in by_type},
        "recent_secrets": recent,
    }
