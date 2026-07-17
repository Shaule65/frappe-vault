"""Secret service — core CRUD and business logic for vault secrets."""

import frappe
from frappe import _
from frappe_vault.utils.constants import LIST_VIEW_FIELDS, SENSITIVE_FIELDS
from frappe_vault.services.audit_service import log_secret_viewed, log_secret_copied


def get_secrets(
    search: str = None,
    title: str = None,
    username: str = None,
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

    # Resolve user favorites
    user = frappe.session.user
    user_favorites = set(frappe.get_all("Vault Favorite", filters={"user": user}, pluck="secret"))

    if favorites_only:
        if not user_favorites:
            return {
                "secrets": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
            }
        filters["name"] = ["in", list(user_favorites)]

    if title:
        filters["title"] = ["like", f"%{title}%"]
    if username:
        filters["username"] = ["like", f"%{username}%"]

    or_filters = None
    if search:
        or_filters = [
            ["title", "like", f"%{search}%"],
            ["url", "like", f"%{search}%"],
            ["username", "like", f"%{search}%"],
            ["email", "like", f"%{search}%"],
        ]

    secrets = frappe.get_list(
        "Vault Secret",
        filters=filters,
        or_filters=or_filters,
        fields=LIST_VIEW_FIELDS,
        order_by=order_by,
        limit_page_length=limit,
        limit_start=offset,
    )

    # Populate is_favorite dynamically per-user
    for s in secrets:
        s["is_favorite"] = 1 if s["name"] in user_favorites else 0

    # Fix total count leak by counting only visible records
    total = len(frappe.get_list("Vault Secret", filters=filters, or_filters=or_filters, pluck="name"))

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

    # Determine user permission level for this secret
    user = frappe.session.user
    roles = frappe.get_roles(user)
    is_admin = user == "Administrator" or "Vault Admin" in roles or "System Manager" in roles

    is_folder_owner = False
    if doc.folder:
        folder_owner = frappe.db.get_value("Vault Folder", doc.folder, "owner")
        if folder_owner == user:
            is_folder_owner = True

    shared_by = None
    if is_admin or doc.owner == user or is_folder_owner:
        user_permission = "Full Control"
    else:
        conditions = [
            "(expires_on IS NULL OR expires_on > NOW())",
            "is_revoked = 0"
        ]
        target_conds = [f"(shared_doctype = 'Vault Secret' AND shared_name = {frappe.db.escape(doc.name)})"]
        if doc.folder:
            target_conds.append(f"(shared_doctype = 'Vault Folder' AND shared_name = {frappe.db.escape(doc.folder)})")
        conditions.append("(" + " OR ".join(target_conds) + ")")

        share_conds = [f"(share_type = 'User' AND user = {frappe.db.escape(user)})"]
        
        user_groups = frappe.get_all("Vault Group Member", filters={"user": user}, pluck="parent")
        if user_groups:
            groups_str = ", ".join([frappe.db.escape(g) for g in user_groups])
            share_conds.append(f"(share_type = 'Group' AND `group` IN ({groups_str}))")
            
        if roles:
            roles_str = ", ".join([frappe.db.escape(r) for r in roles])
            share_conds.append(f"(share_type = 'Role' AND frappe_role IN ({roles_str}))")
            
        conditions.append("(" + " OR ".join(share_conds) + ")")
        
        shares = frappe.db.sql(f"""
            SELECT permission_level, shared_by FROM `tabVault Share`
            WHERE {" AND ".join(conditions)}
        """, as_dict=True)
        
        if shares:
            perm_map = {
                "View Only": 1,
                "View & Copy": 2,
                "Edit": 3,
                "Full Control": 4
            }
            highest_share = max(shares, key=lambda s: perm_map.get(s.permission_level, 0))
            user_permission = highest_share.permission_level
            shared_by = highest_share.shared_by
        else:
            user_permission = "View Only"
            shared_by = doc.owner

    result = {
        "name": doc.name,
        "title": doc.title,
        "secret_type": doc.secret_type,
        "folder": doc.folder,
        "url": doc.url,
        "username": doc.username,
        "email": doc.email,
        "notes": doc.notes,
        "is_favorite": 1 if frappe.db.exists("Vault Favorite", {"user": frappe.session.user, "secret": doc.name}) else 0,
        "password_strength": doc.password_strength,
        "password_last_changed": doc.password_last_changed,
        "last_accessed": str(doc.last_accessed) if doc.last_accessed else None,
        "access_count": doc.access_count,
        "expires_on": str(doc.expires_on) if doc.expires_on else None,
        "tags": [t.tag for t in (doc.tags or [])],
        "owner": doc.owner,
        "shared_by": shared_by,
        "modified": str(doc.modified),
        "user_permission": user_permission,
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

    folder = data.get("folder")
    if folder:
        from frappe_vault.utils.permissions import has_folder_permission
        if not has_folder_permission(folder, ptype="write"):
            frappe.throw(_("You don't have permission to add secrets to this folder"), frappe.PermissionError)

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

    new_folder = data.get("folder")
    if new_folder and new_folder != doc.folder:
        from frappe_vault.utils.permissions import has_folder_permission
        if not has_folder_permission(new_folder, ptype="write"):
            frappe.throw(_("You don't have permission to move secrets to this folder"), frappe.PermissionError)

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
    from frappe_vault.utils.permissions import has_secret_permission
    if not has_secret_permission(name, ptype="delete"):
        frappe.throw(_("You don't have permission to delete this secret"), frappe.PermissionError)

    title = frappe.db.get_value("Vault Secret", name, "title")

    # 1. Clean up associated shareable One Time Links
    one_time_links = frappe.get_all("Vault One Time Link", filters={"secret": name}, pluck="name")
    for link_name in one_time_links:
        frappe.delete_doc("Vault One Time Link", link_name, force=True, ignore_permissions=True)

    # 2. Delete associated share settings
    shares = frappe.get_all("Vault Share", filters={"shared_doctype": "Vault Secret", "shared_name": name}, pluck="name")
    for share_name in shares:
        frappe.delete_doc("Vault Share", share_name, force=True, ignore_permissions=True)

    # 3. Clean up associated favorites
    favorites = frappe.get_all("Vault Favorite", filters={"secret": name}, pluck="name")
    for fav_name in favorites:
        frappe.delete_doc("Vault Favorite", fav_name, force=True, ignore_permissions=True)

    # 4. Finally delete the Vault Secret document itself.
    # We bypass link verification for Vault Audit Log so we can keep the historical
    # Vault Audit Logs intact and displaying the raw secret ID in list views!
    frappe.delete_doc("Vault Secret", name, force=True, ignore_doctypes=["Vault Audit Log"], ignore_permissions=True)

    return {"name": name, "title": title}


def bulk_delete(secret_names: list) -> dict:
    """Delete multiple vault secrets. Skips any the user lacks permission for."""
    deleted = 0
    skipped = 0
    failed = 0
    error = None
    for name in secret_names:
        if not frappe.db.exists("Vault Secret", name):
            continue  # already deleted
        try:
            delete_secret(name)
            deleted += 1
        except frappe.PermissionError:
            # User doesn't own this secret and doesn't have Full Control — skip gracefully
            skipped += 1
        except Exception as e:
            failed += 1
            error = str(e)

    return {"deleted": deleted, "skipped": skipped, "failed": failed, "error": error}


def toggle_favorite(name: str) -> dict:
    """Toggle favorite status."""
    if not frappe.has_permission("Vault Secret", "read", name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    user = frappe.session.user
    fav_exists = frappe.db.exists("Vault Favorite", {"user": user, "secret": name})
    if fav_exists:
        frappe.delete_doc("Vault Favorite", fav_exists, force=True, ignore_permissions=True)
        is_favorite = 0
    else:
        fav_doc = frappe.get_doc({
            "doctype": "Vault Favorite",
            "user": user,
            "secret": name
        })
        fav_doc.insert(ignore_permissions=True)
        is_favorite = 1

    return {"name": name, "is_favorite": is_favorite}


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
    user_roles = frappe.get_roles(user)
    is_admin = user == "Administrator" or "Vault Admin" in user_roles or "System Manager" in user_roles

    secrets = frappe.get_list(
        "Vault Secret",
        fields=["name", "password_strength", "secret_type"]
    )

    total = len(secrets)
    user_favorites = set(frappe.get_all("Vault Favorite", filters={"user": user}, pluck="secret"))
    favorites = sum(1 for s in secrets if s.get("name") in user_favorites)
    weak = sum(1 for s in secrets if s.get("password_strength") in ["weak", "fair"])

    secrets_by_type = {}
    for s in secrets:
        stype = s.get("secret_type") or "Other"
        secrets_by_type[stype] = secrets_by_type.get(stype, 0) + 1

    recent = frappe.get_list(
        "Vault Secret",
        fields=["name", "title", "secret_type", "folder", "last_accessed", "url"],
        order_by="last_accessed desc",
        limit=5,
    )

    from frappe_vault.services.demo_service import check_has_demo_data

    return {
        "total_secrets": total,
        "favorites": favorites,
        "weak_passwords": weak,
        "secrets_by_type": secrets_by_type,
        "recent_secrets": recent,
        "is_admin": is_admin,
        "has_demo_data": check_has_demo_data(),
    }
