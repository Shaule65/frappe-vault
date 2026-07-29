"""Sharing service — share/unshare secrets and folders with users, roles."""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date
import secrets as secrets_module


def share_secret(
    shared_name: str,
    shared_doctype: str = "Vault Secret",
    share_type: str = "User",
    user: str = None,
    frappe_role: str = None,
    permission_level: str = "View Only",
    expires_on: str = None,
) -> dict:
    """Share a secret or folder with a user or role.

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

        existing_share = frappe.db.get_value(
            "Vault Share",
            {
                "shared_doctype": shared_doctype,
                "shared_name": shared_name,
                "share_type": "User",
                "user": user,
                "shared_by": frappe.session.user,
            },
            "name",
        )
        if existing_share:
            frappe.db.set_value(
                "Vault Share",
                existing_share,
                {
                    "is_revoked": 0,
                    "is_role_override": 0,
                    "is_custom_override": 1,
                    "permission_level": permission_level,
                    "shared_by": frappe.session.user,
                    "expires_on": expires_on,
                },
            )
            doc = frappe.get_doc("Vault Share", existing_share)
            from frappe_vault.services.notification_service import send_vault_notification
            item_title = frappe.db.get_value(shared_doctype, shared_name, "title" if shared_doctype == "Vault Secret" else "folder_name") or shared_name
            sharer_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
            send_vault_notification(
                for_user=user,
                subject=f"{sharer_name} shared '{item_title}' with you",
                email_content=f"You have been granted '{permission_level}' access to {shared_doctype} '{item_title}'.",
                notification_type="Share",
                document_type=shared_doctype,
                document_name=shared_name,
                from_user=frappe.session.user
            )
            return {"name": doc.name}

    doc = frappe.get_doc({
        "doctype": "Vault Share",
        "share_type": share_type,
        "user": user if share_type == "User" else None,
        "frappe_role": frappe_role if share_type == "Role" else None,
        "permission_level": permission_level,
        "shared_doctype": shared_doctype,
        "shared_name": shared_name,
        "expires_on": expires_on,
        "shared_by": frappe.session.user,
    })
    doc.insert()

    # Send notifications
    from frappe_vault.services.notification_service import send_vault_notification, notify_vault_admins
    item_title = frappe.db.get_value(shared_doctype, shared_name, "title" if shared_doctype == "Vault Secret" else "folder_name") or shared_name
    sharer_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user

    if share_type == "User" and user:
        send_vault_notification(
            for_user=user,
            subject=f"Secret Shared with You: '{item_title}'",
            email_content=f"<b>{sharer_name}</b> shared {shared_doctype} <b>'{item_title}'</b> with you with <b>'{permission_level}'</b> access.",
            notification_type="Share",
            document_type=shared_doctype,
            document_name=shared_name,
            from_user=frappe.session.user
        )
    elif share_type == "Role" and frappe_role:
        role_users = frappe.get_all("Has Role", filters={"role": frappe_role, "parenttype": "User"}, pluck="parent")
        for r_user in set(role_users):
            if r_user != frappe.session.user:
                send_vault_notification(
                    for_user=r_user,
                    subject=f"Secret Shared via Role ({frappe_role}): '{item_title}'",
                    email_content=f"You have been granted <b>'{permission_level}'</b> access to {shared_doctype} <b>'{item_title}'</b> via role {frappe_role}.",
                    notification_type="Share",
                    document_type=shared_doctype,
                    document_name=shared_name,
                    from_user=frappe.session.user
                )

    # Notify Vault Admins
    notify_vault_admins(
        subject=f"Secret Shared: '{item_title}'",
        email_content=f"<b>{sharer_name}</b> shared {shared_doctype} <b>'{item_title}'</b> with {user or frappe_role} (Access: {permission_level}).",
        document_type=shared_doctype,
        document_name=shared_name
    )

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

    # If revoking a Role share, also mark all role share records and member overrides as revoked
    if doc.share_type == "Role" and doc.frappe_role:
        frappe.db.sql("""
            UPDATE `tabVault Share`
            SET `is_revoked` = 1, `revoked_by` = %s
            WHERE `shared_doctype` = %s AND `shared_name` = %s AND `share_type` = 'Role' AND `frappe_role` = %s
        """, (frappe.session.user, doc.shared_doctype, doc.shared_name, doc.frappe_role))

        role_users = frappe.get_all("Has Role", filters={"role": doc.frappe_role, "parenttype": "User"}, pluck="parent")
        if role_users:
            users_str = ", ".join([frappe.db.escape(u) for u in set(role_users) if u])
            if users_str:
                frappe.db.sql(f"""
                    UPDATE `tabVault Share`
                    SET `is_revoked` = 1, `revoked_by` = {frappe.db.escape(frappe.session.user)}
                    WHERE `shared_doctype` = {frappe.db.escape(doc.shared_doctype)}
                      AND `shared_name` = {frappe.db.escape(doc.shared_name)}
                      AND `user` IN ({users_str})
                """)
    elif doc.share_type == "User":
        frappe.db.sql("""
            UPDATE `tabVault Share`
            SET `is_revoked` = 1, `revoked_by` = %s
            WHERE `shared_doctype` = %s AND `shared_name` = %s AND `share_type` = 'User' AND `shared_by` = %s
        """, (frappe.session.user, doc.shared_doctype, doc.shared_name, doc.shared_by))
    
    # Log the activity
    from frappe_vault.services.audit_service import log_share_removed
    log_share_removed(doc, None)

    item_title = frappe.db.get_value(doc.shared_doctype, doc.shared_name, "title" if doc.shared_doctype == "Vault Secret" else "folder_name") or doc.shared_name
    revoker_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user

    # Notify recipient if revoked
    if doc.share_type == "User" and doc.user:
        from frappe_vault.services.notification_service import send_vault_notification
        send_vault_notification(
            for_user=doc.user,
            subject=f"Access Revoked for '{item_title}'",
            email_content=f"<b>{revoker_name}</b> revoked your access to {doc.shared_doctype} <b>'{item_title}'</b>.",
            notification_type="Alert",
            document_type=doc.shared_doctype,
            document_name=doc.shared_name,
            from_user=frappe.session.user
        )

    # Notify Vault Admins
    from frappe_vault.services.notification_service import notify_vault_admins
    notify_vault_admins(
        subject=f"Access Revoked: '{item_title}'",
        email_content=f"<b>{revoker_name}</b> revoked access to {doc.shared_doctype} <b>'{item_title}'</b> for {doc.user or doc.frappe_role}.",
        document_type=doc.shared_doctype,
        document_name=doc.shared_name
    )

    frappe.db.commit()
    return {"removed": share_name}


def update_share_permission(share_name: str, permission_level: str) -> dict:
    """Update permission level of an active share."""
    if not frappe.db.exists("Vault Share", share_name):
        frappe.throw(_("Share record not found"), frappe.DoesNotExistError)

    doc = frappe.get_doc("Vault Share", share_name)

    # Only the sharer, owner, or Vault Admin can update permission
    user_roles = frappe.get_roles()
    is_admin = frappe.session.user == "Administrator" or "Vault Admin" in user_roles

    if not is_admin and doc.shared_by != frappe.session.user:
        owner = frappe.db.get_value(doc.shared_doctype, doc.shared_name, "owner")
        if owner != frappe.session.user:
            frappe.throw(_("Not permitted"), frappe.PermissionError)

    frappe.db.set_value("Vault Share", share_name, "permission_level", permission_level)
    doc.reload()

    from frappe_vault.services.audit_service import log_share_created
    log_share_created(doc, None)

    if doc.share_type == "Role" and doc.frappe_role:
        # Update non-custom member overrides to inherit the new role baseline
        overrides = frappe.get_all(
            "Vault Share",
            filters={
                "shared_doctype": doc.shared_doctype,
                "shared_name": doc.shared_name,
                "is_role_override": 1,
                "is_custom_override": 0,
                "is_revoked": 0,
            },
            pluck="name",
        )
        for ov_name in overrides:
            frappe.db.set_value("Vault Share", ov_name, "permission_level", permission_level)

    frappe.db.commit()

    # Send notifications for permission update
    item_title = frappe.db.get_value(doc.shared_doctype, doc.shared_name, "title" if doc.shared_doctype == "Vault Secret" else "folder_name") or doc.shared_name
    updater_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user

    if doc.share_type == "User" and doc.user:
        from frappe_vault.services.notification_service import send_vault_notification
        send_vault_notification(
            for_user=doc.user,
            subject=f"Permission Updated for '{item_title}'",
            email_content=f"<b>{updater_name}</b> updated your access on {doc.shared_doctype} <b>'{item_title}'</b> to <b>'{permission_level}'</b>.",
            notification_type="Share",
            document_type=doc.shared_doctype,
            document_name=doc.shared_name,
            from_user=frappe.session.user
        )

    from frappe_vault.services.notification_service import notify_vault_admins
    notify_vault_admins(
        subject=f"Share Permission Updated: '{item_title}'",
        email_content=f"<b>{updater_name}</b> updated {doc.user or doc.frappe_role}'s access on {doc.shared_doctype} <b>'{item_title}'</b> to <b>'{permission_level}'</b>.",
        document_type=doc.shared_doctype,
        document_name=doc.shared_name
    )

    return {"name": share_name, "permission_level": permission_level}


def get_role_users(role_name: str = None, shared_name: str = None, shared_doctype: str = "Vault Secret", shared_by: str = None, user_list: list = None) -> list:
    """Get list of users (from role or direct user shares) along with per-user share status."""
    user = frappe.session.user
    roles = frappe.get_roles(user)
    is_admin = user == "Administrator" or "Vault Admin" in roles

    if not is_admin and not frappe.has_permission("Vault Share", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    user_ids = []
    role_share_perm = "View Only"
    parent_is_revoked = False

    if user_list:
        if isinstance(user_list, str):
            import json
            try:
                user_list = json.loads(user_list)
            except Exception:
                user_list = [user_list]
        user_ids = list(dict.fromkeys(user_list))
    elif role_name:
        role_users = frappe.get_all(
            "Has Role",
            filters={"role": role_name, "parenttype": "User"},
            fields=["parent as user"],
            order_by="parent asc"
        )
        user_ids = [u["user"] for u in role_users]
        if shared_name:
            role_share_filters = {
                "shared_name": shared_name,
                "shared_doctype": shared_doctype,
                "share_type": "Role",
                "frappe_role": role_name,
            }
            if shared_by:
                role_share_filters["shared_by"] = shared_by
            role_share = frappe.db.get_value(
                "Vault Share",
                role_share_filters,
                ["permission_level", "is_revoked"],
                as_dict=True
            )
            if role_share:
                role_share_perm = role_share.permission_level or role_share_perm
                parent_is_revoked = bool(role_share.is_revoked)
    elif shared_name:
        direct_filters = {
            "shared_name": shared_name,
            "shared_doctype": shared_doctype,
            "share_type": "User",
            "is_role_override": 0,
        }
        if shared_by:
            direct_filters["shared_by"] = shared_by
        direct_users = frappe.get_all(
            "Vault Share",
            filters=direct_filters,
            pluck="user",
            order_by="creation asc"
        )
        user_ids = list(dict.fromkeys(direct_users))

    user_details = []
    for user_id in user_ids:
        if not user_id or user_id in ["Administrator", "Guest"]:
            continue
        full_name = frappe.db.get_value("User", user_id, "full_name") or user_id

        is_revoked = parent_is_revoked
        perm_level = role_share_perm
        if shared_name:
            user_share_filters = {
                "shared_name": shared_name,
                "shared_doctype": shared_doctype,
                "share_type": "User",
                "user": user_id,
            }
            if shared_by:
                user_share_filters["shared_by"] = shared_by
            user_share = frappe.db.get_value(
                "Vault Share",
                user_share_filters,
                ["name", "permission_level", "is_revoked", "is_custom_override"],
                as_dict=True,
            )
            if user_share:
                is_revoked = bool(user_share.is_revoked)
                perm_level = user_share.permission_level or role_share_perm

        user_details.append({
            "user": user_id,
            "full_name": full_name,
            "permission_level": perm_level,
            "is_revoked": is_revoked,
        })
    return user_details


def save_role_member_permission(
    shared_name: str,
    shared_doctype: str = "Vault Secret",
    user: str = None,
    permission_level: str = "View Only",
    is_revoked: bool = False,
) -> dict:
    """Save or update individual user permission/revocation for a shared item."""
    if not user or not shared_name:
        frappe.throw(_("User and shared item name are required"))

    # Permission check: must be owner, sharer, or Vault Admin
    user_roles = frappe.get_roles()
    is_admin = frappe.session.user == "Administrator" or "Vault Admin" in user_roles
    if not is_admin:
        owner = frappe.db.get_value(shared_doctype, shared_name, "owner")
        if owner != frappe.session.user:
            frappe.throw(_("Not permitted"), frappe.PermissionError)

    role_share_perm = frappe.db.get_value(
        "Vault Share",
        {
            "shared_name": shared_name,
            "shared_doctype": shared_doctype,
            "share_type": "Role",
            "is_revoked": 0,
        },
        "permission_level",
    ) or "View Only"

    is_custom = 1 if (is_revoked or (permission_level and permission_level != role_share_perm)) else 0

    has_parent_role = frappe.db.exists(
        "Vault Share",
        {
            "shared_name": shared_name,
            "shared_doctype": shared_doctype,
            "share_type": "Role",
            "is_revoked": 0,
        },
    )
    is_role_override_val = 1 if has_parent_role else 0

    existing_name = frappe.db.get_value(
        "Vault Share",
        {
            "shared_name": shared_name,
            "shared_doctype": shared_doctype,
            "share_type": "User",
            "user": user,
            "shared_by": frappe.session.user,
        },
        "name",
    )

    from frappe_vault.services.audit_service import log_share_created, log_share_removed

    if is_revoked:
        if existing_name:
            frappe.db.set_value(
                "Vault Share",
                existing_name,
                {"is_revoked": 1, "revoked_by": frappe.session.user, "is_role_override": is_role_override_val, "is_custom_override": 1},
            )
            share_doc = frappe.get_doc("Vault Share", existing_name)
            log_share_removed(share_doc, None)
        else:
            doc = frappe.get_doc({
                "doctype": "Vault Share",
                "share_type": "User",
                "user": user,
                "permission_level": permission_level or role_share_perm,
                "shared_doctype": shared_doctype,
                "shared_name": shared_name,
                "is_revoked": 1,
                "is_role_override": is_role_override_val,
                "is_custom_override": 1,
                "shared_by": frappe.session.user,
                "revoked_by": frappe.session.user,
            })
            doc.insert(ignore_permissions=True)
    else:
        target_perm = permission_level or role_share_perm
        if existing_name:
            frappe.db.set_value(
                "Vault Share",
                existing_name,
                {"is_revoked": 0, "permission_level": target_perm, "is_role_override": is_role_override_val, "is_custom_override": is_custom},
            )
            share_doc = frappe.get_doc("Vault Share", existing_name)
            log_share_created(share_doc, None)
        else:
            doc = frappe.get_doc({
                "doctype": "Vault Share",
                "share_type": "User",
                "user": user,
                "permission_level": target_perm,
                "shared_doctype": shared_doctype,
                "shared_name": shared_name,
                "is_revoked": 0,
                "is_role_override": is_role_override_val,
                "is_custom_override": is_custom,
                "shared_by": frappe.session.user,
            })
            doc.insert(ignore_permissions=True)

    frappe.db.commit()
    return {"status": "success", "user": user, "permission_level": permission_level, "is_revoked": is_revoked}


def get_shares_for_secret(secret_name: str) -> list:
    """Get consolidated primary shares for a secret (both active and revoked), excluding role member overrides."""
    shares = frappe.get_all(
        "Vault Share",
        filters={
            "shared_doctype": "Vault Secret",
            "shared_name": secret_name,
            "is_role_override": 0,
        },
        fields=["name", "share_type", "user", "frappe_role",
                "permission_level", "expires_on", "shared_by", "is_revoked", "revoked_by", "creation"],
        order_by="creation desc",
    )

    roles_seen = set()
    user_groups = {}
    consolidated = []

    for s in shares:
        if s.share_type == "Role":
            role_key = f"{s.frappe_role}_{s.is_revoked}"
            if role_key not in roles_seen:
                roles_seen.add(role_key)
                consolidated.append(s)
        elif s.share_type == "User":
            sharer = s.shared_by or "Administrator"
            state_key = "revoked" if s.is_revoked else "active"
            key = f"{sharer}_{state_key}"
            if key not in user_groups:
                user_groups[key] = {
                    "active_shares": [],
                    "revoked_shares": []
                }
            if s.is_revoked:
                user_groups[key]["revoked_shares"].append(s)
            else:
                user_groups[key]["active_shares"].append(s)

    for key, g in user_groups.items():
        active = g["active_shares"]
        revoked = g["revoked_shares"]

        if len(active) > 1:
            primary = active[0].copy()
            primary["share_type"] = "UserGroup"
            primary["user_count"] = len(active)
            primary["user_list"] = [u.user for u in active]
            primary["user"] = f"{len(active)} Users"
            consolidated.append(primary)
        elif len(active) == 1:
            consolidated.append(active[0])

        if len(revoked) > 1:
            primary = revoked[0].copy()
            primary["share_type"] = "UserGroup"
            primary["user_count"] = len(revoked)
            primary["user_list"] = [u.user for u in revoked]
            primary["user"] = f"{len(revoked)} Users"
            consolidated.append(primary)
        elif len(revoked) == 1:
            consolidated.append(revoked[0])

    return consolidated


def get_shared_with_me(limit: int = 20, offset: int = 0) -> dict:
    """Get secrets/folders shared with current user or all shares if Admin, consolidated by primary item and sharer."""
    user = frappe.session.user
    user_roles = frappe.get_roles(user)

    is_admin = user == "Administrator" or "Vault Admin" in user_roles

    if is_admin:
        where = "(vs.is_role_override = 0 OR vs.is_role_override IS NULL)"
    else:
        conditions = [f"vs.share_type = 'User' AND vs.user = {frappe.db.escape(user)}"]
        if user_roles:
            roles_str = ", ".join([frappe.db.escape(r) for r in user_roles])
            conditions.append(f"vs.share_type = 'Role' AND vs.frappe_role IN ({roles_str})")
        where = f"((vs.is_role_override = 0 OR vs.is_role_override IS NULL) AND ({' OR '.join(f'({c})' for c in conditions)}))"

    raw_shares = frappe.db.sql(f"""
        SELECT vs.name as share_name, vs.shared_doctype, vs.shared_name,
               vs.permission_level, vs.shared_by, vs.expires_on,
               vs.share_type, vs.user, vs.frappe_role,
               vs.is_revoked, vs.revoked_by, vs.creation,
               COALESCE(sec.title, fld.folder_name) as title,
               sec.secret_type, sec.url, sec.folder,
               COALESCE(fld.icon, parent_fld.icon) as folder_icon,
               COALESCE(fld.folder_name, parent_fld.folder_name) as folder_name
        FROM `tabVault Share` vs
        LEFT JOIN `tabVault Secret` sec ON vs.shared_name = sec.name AND vs.shared_doctype = 'Vault Secret'
        LEFT JOIN `tabVault Folder` fld ON vs.shared_name = fld.name AND vs.shared_doctype = 'Vault Folder'
        LEFT JOIN `tabVault Folder` parent_fld ON sec.folder IS NOT NULL AND (sec.folder = parent_fld.name OR sec.folder = parent_fld.folder_name)
        WHERE ({where}) AND (sec.name IS NOT NULL OR fld.name IS NOT NULL)
        ORDER BY vs.creation DESC
    """, as_dict=True)

    groups = {}
    for s in raw_shares:
        if s.share_type == "Role":
            key = f"Role_{s.shared_doctype}_{s.shared_name}_{s.frappe_role}"
            if key not in groups:
                groups[key] = s
        elif s.share_type == "User":
            sharer = s.shared_by or "Administrator"
            key = f"UserGroup_{s.shared_doctype}_{s.shared_name}_{sharer}"
            if key not in groups:
                groups[key] = {
                    "share_name": s.share_name,
                    "shared_doctype": s.shared_doctype,
                    "shared_name": s.shared_name,
                    "permission_level": s.permission_level,
                    "shared_by": s.shared_by,
                    "expires_on": s.expires_on,
                    "share_type": "User",
                    "user": s.user,
                    "frappe_role": None,
                    "is_revoked": True,
                    "revoked_by": s.revoked_by,
                    "title": s.title,
                    "secret_type": s.secret_type,
                    "url": s.url,
                    "folder": s.folder,
                    "folder_icon": s.folder_icon,
                    "folder_name": s.folder_name,
                    "total_count": 0,
                    "active_count": 0,
                    "user_list": []
                }

            groups[key]["user_list"].append(s.user)
            groups[key]["total_count"] += 1
            if not s.is_revoked:
                groups[key]["active_count"] += 1
                groups[key]["is_revoked"] = False

    consolidated_list = []
    for g in groups.values():
        total_members = g.get("total_count", 1)
        if total_members > 1:
            g["share_type"] = "UserGroup"
            g["user_count"] = total_members
            g["user"] = f"{total_members} Users"
        consolidated_list.append(g)

    total = len(consolidated_list)
    paginated = consolidated_list[offset:offset + limit]

    return {"shared": paginated, "total": total, "limit": limit, "offset": offset}


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
        "share_url": doc.share_url,
    }


def consume_one_time_link(token: str, passphrase: str = None) -> dict:
    """Consume a one-time link and return the secret data."""
    link_name = frappe.db.get_value("Vault One Time Link", {"token": token}, "name")

    if not link_name:
        frappe.throw(_("Link not found"), frappe.DoesNotExistError)

    link = frappe.get_doc("Vault One Time Link", link_name)

    if not link.is_valid():
        frappe.throw(_("This link has expired or been consumed"))

    # Verify passphrase if configured
    stored_passphrase = None
    try:
        from frappe.utils.password import get_decrypted_password
        stored_passphrase = get_decrypted_password("Vault One Time Link", link.name, "passphrase", raise_exception=False)
    except Exception:
        pass

    if not stored_passphrase:
        try:
            auth_val = frappe.db.get_value("__Auth", {"doctype": "Vault One Time Link", "docname": link.name, "fieldname": "passphrase"}, "password")
            if auth_val:
                from frappe.utils.password import decrypt
                stored_passphrase = decrypt(auth_val)
        except Exception:
            pass

    if stored_passphrase:
        if not passphrase or passphrase != stored_passphrase:
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

    # Log audit event
    try:
        from frappe_vault.services.audit_service import log_one_time_link_consumed
        log_one_time_link_consumed(link)
    except Exception:
        pass

    return result


def bulk_delete_shares(share_names: list) -> dict:
    """Delete multiple shares permanently. Checks permission for each."""
    user = frappe.session.user
    roles = frappe.get_roles(user)
    is_admin = user == "Administrator" or "Vault Admin" in roles

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
            elif doc.share_type == "Role":
                if doc.frappe_role in roles:
                    can_delete = True
                    
        if can_delete:
            if doc.share_type == "Role" and doc.frappe_role:
                matching_shares = frappe.get_all(
                    "Vault Share",
                    filters={
                        "shared_doctype": doc.shared_doctype,
                        "shared_name": doc.shared_name,
                        "share_type": "Role",
                        "frappe_role": doc.frappe_role
                    },
                    pluck="name"
                )
                for s_name in matching_shares:
                    frappe.delete_doc("Vault Share", s_name, ignore_permissions=True)
                    deleted.append(s_name)
            elif doc.share_type == "User":
                matching_shares = frappe.get_all(
                    "Vault Share",
                    filters={
                        "shared_doctype": doc.shared_doctype,
                        "shared_name": doc.shared_name,
                        "share_type": "User",
                        "shared_by": doc.shared_by,
                        "is_revoked": doc.is_revoked
                    },
                    pluck="name"
                )
                for s_name in matching_shares:
                    frappe.delete_doc("Vault Share", s_name, ignore_permissions=True)
                    deleted.append(s_name)
            else:
                frappe.delete_doc("Vault Share", name, ignore_permissions=True)
                deleted.append(name)
            
    frappe.db.commit()
    return {"deleted": deleted}
