"""Public API for Frappe Vault.

This module exposes whitelisted methods that can be called via REST API.
All endpoints require authentication.
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_secrets(
    category: str = None,
    secret_type: str = None,
    search: str = None,
    favorites_only: bool = False,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """Get a list of secrets accessible by the current user.
    
    Args:
        category: Filter by category
        secret_type: Filter by secret type
        search: Search term for title
        favorites_only: Only return favorites
        limit: Maximum number of results
        offset: Pagination offset
        
    Returns:
        dict with secrets list and pagination info
    """
    filters = {"owner": frappe.session.user}
    
    if category:
        filters["category"] = category
    
    if secret_type:
        filters["secret_type"] = secret_type
    
    if favorites_only:
        filters["is_favorite"] = 1
    
    if search:
        filters["title"] = ["like", f"%{search}%"]
    
    secrets = frappe.get_all(
        "Vault Secret",
        filters=filters,
        fields=[
            "name", "title", "secret_type", "category", 
            "url", "username", "is_favorite", "password_strength",
            "last_accessed", "modified"
        ],
        order_by="modified desc",
        limit_page_length=limit,
        limit_start=offset
    )
    
    total = frappe.db.count("Vault Secret", filters=filters)
    
    return {
        "secrets": secrets,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@frappe.whitelist()
def get_secret(name: str) -> dict:
    """Get a single secret with decrypted credentials.
    
    Args:
        name: The secret document name
        
    Returns:
        dict with secret data including decrypted password
    """
    if not frappe.has_permission("Vault Secret", "read", name):
        frappe.throw(_("You don't have permission to access this secret"))
    
    doc = frappe.get_doc("Vault Secret", name)
    
    # Log access
    from frappe_vault.frappe_vault.doctype.vault_secret.vault_secret import create_access_log
    create_access_log(name, "viewed")
    
    # Update access metadata
    doc.update_access_metadata()
    
    # Get decrypted password
    from frappe.utils.password import get_decrypted_password
    
    result = {
        "name": doc.name,
        "title": doc.title,
        "secret_type": doc.secret_type,
        "category": doc.category,
        "url": doc.url,
        "username": doc.username,
        "notes": doc.notes,
        "is_favorite": doc.is_favorite,
        "password_strength": doc.password_strength,
        "password_last_changed": doc.password_last_changed,
        "last_accessed": doc.last_accessed,
        "access_count": doc.access_count,
    }
    
    # Add decrypted credentials based on type
    if doc.secret_type == "Password":
        result["password"] = get_decrypted_password("Vault Secret", name, "password") or ""
    elif doc.secret_type == "API Key":
        result["api_key"] = doc.api_key
        result["api_secret"] = get_decrypted_password("Vault Secret", name, "api_secret") or ""
    
    return result


@frappe.whitelist()
def create_secret(
    title: str,
    secret_type: str = "Password",
    category: str = None,
    url: str = None,
    username: str = None,
    password: str = None,
    api_key: str = None,
    api_secret: str = None,
    notes: str = None,
    is_favorite: bool = False,
) -> dict:
    """Create a new vault secret.
    
    Args:
        title: Secret title
        secret_type: Type of secret (Password, API Key, Note, etc.)
        category: Category link
        url: Associated URL
        username: Username for password type
        password: Password value (will be encrypted)
        api_key: API key for API Key type
        api_secret: API secret (will be encrypted)
        notes: Additional notes
        is_favorite: Mark as favorite
        
    Returns:
        dict with created secret name
    """
    if not frappe.has_permission("Vault Secret", "create"):
        frappe.throw(_("You don't have permission to create secrets"))
    
    doc = frappe.get_doc({
        "doctype": "Vault Secret",
        "title": title,
        "secret_type": secret_type,
        "category": category,
        "url": url,
        "username": username,
        "password": password,
        "api_key": api_key,
        "api_secret": api_secret,
        "notes": notes,
        "is_favorite": 1 if is_favorite else 0,
    })
    
    doc.insert()
    
    return {"name": doc.name, "message": _("Secret created successfully")}


@frappe.whitelist()
def update_secret(name: str, **kwargs) -> dict:
    """Update an existing vault secret.
    
    Args:
        name: Secret document name
        **kwargs: Fields to update
        
    Returns:
        dict with success message
    """
    if not frappe.has_permission("Vault Secret", "write", name):
        frappe.throw(_("You don't have permission to update this secret"))
    
    doc = frappe.get_doc("Vault Secret", name)
    
    allowed_fields = [
        "title", "secret_type", "category", "url", "username",
        "password", "api_key", "api_secret", "notes", "is_favorite"
    ]
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            doc.set(field, value)
    
    doc.save()
    
    return {"name": doc.name, "message": _("Secret updated successfully")}


@frappe.whitelist()
def delete_secret(name: str) -> dict:
    """Delete a vault secret.
    
    Args:
        name: Secret document name
        
    Returns:
        dict with success message
    """
    if not frappe.has_permission("Vault Secret", "delete", name):
        frappe.throw(_("You don't have permission to delete this secret"))
    
    frappe.delete_doc("Vault Secret", name)
    
    return {"message": _("Secret deleted successfully")}


@frappe.whitelist()
def get_categories() -> list:
    """Get all vault categories.
    
    Returns:
        list of categories in tree structure
    """
    categories = frappe.get_all(
        "Vault Category",
        fields=["name", "category_name", "parent_vault_category", "is_group", "icon", "color"],
        order_by="lft"
    )
    
    return categories


@frappe.whitelist()
def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_special: bool = True,
    exclude_ambiguous: bool = False,
) -> dict:
    """Generate a secure random password.
    
    This is a wrapper around the vault_secret method for API access.
    """
    from frappe_vault.frappe_vault.doctype.vault_secret.vault_secret import (
        generate_password as gen_pwd,
    )
    
    return gen_pwd(
        length=length,
        use_uppercase=use_uppercase,
        use_lowercase=use_lowercase,
        use_digits=use_digits,
        use_special=use_special,
        exclude_ambiguous=exclude_ambiguous,
    )


@frappe.whitelist()
def get_stats() -> dict:
    """Get vault statistics for the current user.
    
    This is a wrapper around the vault_secret method for API access.
    """
    from frappe_vault.frappe_vault.doctype.vault_secret.vault_secret import get_vault_stats
    
    return get_vault_stats()


@frappe.whitelist()
def toggle_favorite(name: str) -> dict:
    """Toggle the favorite status of a secret.
    
    Args:
        name: Secret document name
        
    Returns:
        dict with new favorite status
    """
    if not frappe.has_permission("Vault Secret", "write", name):
        frappe.throw(_("You don't have permission to update this secret"))
    
    doc = frappe.get_doc("Vault Secret", name)
    doc.is_favorite = 0 if doc.is_favorite else 1
    doc.save()
    
    return {
        "name": doc.name,
        "is_favorite": doc.is_favorite,
        "message": _("Added to favorites") if doc.is_favorite else _("Removed from favorites")
    }


@frappe.whitelist()
def export_secrets(format: str = "json", category: str = None) -> dict:
    """Export user's secrets to JSON or CSV format.
    
    Note: Passwords are NOT exported for security reasons.
    
    Args:
        format: Export format ('json' or 'csv')
        category: Optional category filter
        
    Returns:
        dict with file content
    """
    from frappe_vault.utils.import_export import export_secrets as do_export
    
    return do_export(format=format, category=category)


@frappe.whitelist()
def import_secrets(data: str, format: str = "json") -> dict:
    """Import secrets from JSON or CSV format.
    
    Args:
        data: The file content as string
        format: Import format ('json' or 'csv')
        
    Returns:
        dict with import results
    """
    from frappe_vault.utils.import_export import import_secrets as do_import
    
    return do_import(data=data, format=format)


@frappe.whitelist()
def get_import_template() -> dict:
    """Get a CSV template for importing secrets.
    
    Returns:
        dict with template content
    """
    from frappe_vault.utils.import_export import get_export_template
    
    return get_export_template()


@frappe.whitelist()
def get_security_score() -> dict:
    """Get security score for current user's vault.
    
    Returns:
        dict with score and breakdown
    """
    from frappe_vault.tasks import get_security_score as calc_score
    
    return calc_score()
