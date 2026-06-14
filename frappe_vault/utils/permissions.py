"""Permission query conditions for Frappe Vault.

Ensures row-level security: users only see secrets they own or that are shared with them.
"""

import frappe


def get_secret_permission_query(user=None):
    """Return SQL condition to filter Vault Secrets for current user.

    A user can see a secret if:
    1. They own it, OR
    2. It has been shared with them directly, OR
    3. The secret's folder has been shared with them (User/Group/Role)
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    # Check if user has Vault Admin or System Manager role — they see everything
    roles = frappe.get_roles(user)
    if "Vault Admin" in roles or "System Manager" in roles:
        return ""

    user_escaped = frappe.db.escape(user)

    return f"""(
        `tabVault Secret`.owner = {user_escaped}
        OR `tabVault Secret`.name IN (
            SELECT vs.shared_name
            FROM `tabVault Share` vs
            WHERE vs.shared_doctype = 'Vault Secret'
            AND vs.is_revoked = 0
            AND (
                (vs.share_type = 'User' AND vs.user = {user_escaped})
                OR (vs.share_type = 'Group' AND vs.`group` IN (
                    SELECT vgm.parent
                    FROM `tabVault Group Member` vgm
                    WHERE vgm.user = {user_escaped}
                ))
                OR (vs.share_type = 'Role' AND vs.frappe_role IN (
                    SELECT role FROM `tabHas Role`
                    WHERE parent = {user_escaped}
                ))
            )
            AND (vs.expires_on IS NULL OR vs.expires_on > NOW())
        )
        OR (
            `tabVault Secret`.folder IS NOT NULL
            AND `tabVault Secret`.folder IN (
                SELECT vs.shared_name
                FROM `tabVault Share` vs
                WHERE vs.shared_doctype = 'Vault Folder'
                AND vs.is_revoked = 0
                AND (
                    (vs.share_type = 'User' AND vs.user = {user_escaped})
                    OR (vs.share_type = 'Group' AND vs.`group` IN (
                        SELECT vgm.parent
                        FROM `tabVault Group Member` vgm
                        WHERE vgm.user = {user_escaped}
                    ))
                    OR (vs.share_type = 'Role' AND vs.frappe_role IN (
                        SELECT role FROM `tabHas Role`
                        WHERE parent = {user_escaped}
                    ))
                )
                AND (vs.expires_on IS NULL OR vs.expires_on > NOW())
            )
        )
    )"""


def has_secret_permission(doc, ptype="read", user=None):
    """Check if a user has permission on a specific Vault Secret document."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = frappe.get_roles(user)
    if "Vault Admin" in roles or "System Manager" in roles:
        return True

    if ptype == "create":
        return True

    # Safely resolve document name, owner and folder
    if isinstance(doc, str):
        doc_name = doc
        res = frappe.db.get_value("Vault Secret", doc_name, ["owner", "folder"])
        doc_owner, doc_folder = res if res else (None, None)
    elif isinstance(doc, dict):
        doc_name = doc.get("name")
        doc_owner = doc.get("owner")
        doc_folder = doc.get("folder")
        if not doc_owner or not doc_folder:
            res = frappe.db.get_value("Vault Secret", doc_name, ["owner", "folder"])
            if res:
                doc_owner, doc_folder = res
    else:
        doc_name = doc.name
        doc_owner = doc.owner
        doc_folder = doc.folder

    if not doc_name:
        return False

    # Owner always has access
    if doc_owner == user:
        return True

    # Check active shares (secret itself or parent folder) applying to the user
    conditions = [
        "(expires_on IS NULL OR expires_on > NOW())",
        "is_revoked = 0"
    ]
    target_conds = [f"(shared_doctype = 'Vault Secret' AND shared_name = {frappe.db.escape(doc_name)})"]
    if doc_folder:
        target_conds.append(f"(shared_doctype = 'Vault Folder' AND shared_name = {frappe.db.escape(doc_folder)})")
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
        SELECT permission_level FROM `tabVault Share`
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
        level = perm_map.get(highest_share.permission_level, 1)
        
        if ptype in ("read",):
            return level >= 1
        elif ptype in ("write",):
            return level >= 3
        elif ptype in ("delete", "share"):
            return level >= 4
            
    return False


def get_folder_permission_query(user=None):
    """Return SQL condition to filter Vault Folders for current user.

    A user can see a folder if:
    1. They own it, OR
    2. The folder has been shared with them directly, or with their group, or with their role, OR
    3. They have read/write/share access to at least one secret inside that folder.
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)
    if "Vault Admin" in roles or "System Manager" in roles:
        return ""

    user_escaped = frappe.db.escape(user)

    return f"""(
        `tabVault Folder`.owner = {user_escaped}
        OR `tabVault Folder`.name IN (
            SELECT vs.shared_name
            FROM `tabVault Share` vs
            WHERE vs.shared_doctype = 'Vault Folder'
            AND vs.is_revoked = 0
            AND (
                (vs.share_type = 'User' AND vs.user = {user_escaped})
                OR (vs.share_type = 'Group' AND vs.`group` IN (
                    SELECT vgm.parent
                    FROM `tabVault Group Member` vgm
                    WHERE vgm.user = {user_escaped}
                ))
                OR (vs.share_type = 'Role' AND vs.frappe_role IN (
                    SELECT role FROM `tabHas Role`
                    WHERE parent = {user_escaped}
                ))
            )
            AND (vs.expires_on IS NULL OR vs.expires_on > NOW())
        )
    )"""


def has_folder_permission(doc, ptype="read", user=None):
    """Check if a user has permission on a specific Vault Folder document."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = frappe.get_roles(user)
    if "Vault Admin" in roles or "System Manager" in roles:
        return True

    if ptype == "create":
        return True

    # Safely resolve folder name
    if isinstance(doc, str):
        doc_name = doc
        doc_owner = frappe.db.get_value("Vault Folder", doc_name, "owner")
    elif isinstance(doc, dict):
        doc_name = doc.get("name")
        doc_owner = doc.get("owner") or frappe.db.get_value("Vault Folder", doc_name, "owner")
    else:
        doc_name = doc.name
        doc_owner = doc.owner

    if doc_owner == user:
        return True

    # Check active shares for this folder
    conditions = [
        "shared_doctype = 'Vault Folder'",
        f"shared_name = {frappe.db.escape(doc_name)}",
        "is_revoked = 0"
    ]
    share_conds = [f"(share_type = 'User' AND user = {frappe.db.escape(user)})"]
    
    user_groups = frappe.get_all("Vault Group Member", filters={"user": user}, pluck="parent")
    if user_groups:
        groups_str = ", ".join([frappe.db.escape(g) for g in user_groups])
        share_conds.append(f"(share_type = 'Group' AND `group` IN ({groups_str}))")
        
    if roles:
        roles_str = ", ".join([frappe.db.escape(r) for r in roles])
        share_conds.append(f"(share_type = 'Role' AND frappe_role IN ({roles_str}))")
        
    conditions.append("(" + " OR ".join(share_conds) + ")")
    conditions.append("(expires_on IS NULL OR expires_on > NOW())")
    
    shares = frappe.db.sql(f"""
        SELECT permission_level FROM `tabVault Share`
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
        level = perm_map.get(highest_share.permission_level, 1)
        
        if ptype in ("read",):
            return level >= 1
        elif ptype in ("write",):
            return level >= 3
        elif ptype in ("delete", "share"):
            return level >= 4
                
    return False
