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
                OR (vs.share_type = 'Role' AND vs.frappe_role IN (
                    SELECT role FROM `tabHas Role`
                    WHERE parent = {user_escaped}
                ) AND NOT EXISTS (
                    SELECT 1 FROM `tabVault Share` override
                    WHERE override.shared_doctype = 'Vault Secret'
                    AND override.shared_name = vs.shared_name
                    AND override.share_type = 'User'
                    AND override.user = {user_escaped}
                    AND override.is_revoked = 1
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
                    OR (vs.share_type = 'Role' AND vs.frappe_role IN (
                        SELECT role FROM `tabHas Role`
                        WHERE parent = {user_escaped}
                    ) AND NOT EXISTS (
                        SELECT 1 FROM `tabVault Share` override
                        WHERE override.shared_doctype = 'Vault Folder'
                        AND override.shared_name = vs.shared_name
                        AND override.share_type = 'User'
                        AND override.user = {user_escaped}
                        AND override.is_revoked = 1
                    ))
                )
                AND (vs.expires_on IS NULL OR vs.expires_on > NOW())
            )
        )
        OR (
            `tabVault Secret`.folder IS NOT NULL
            AND `tabVault Secret`.folder IN (
                SELECT name FROM `tabVault Folder`
                WHERE owner = {user_escaped}
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

    # Folder owner always has access to secrets inside
    if doc_folder:
        folder_owner = frappe.db.get_value("Vault Folder", doc_folder, "owner")
        if folder_owner == user:
            return True

    # Check active user-specific share first (explicit user level takes priority over everything else)
    user_shares = frappe.db.sql(
        """
        SELECT permission_level FROM `tabVault Share`
        WHERE share_type = 'User'
          AND user = %s
          AND is_revoked = 0
          AND (expires_on IS NULL OR expires_on > NOW())
          AND (
              (shared_doctype = 'Vault Secret' AND shared_name = %s)
              OR (shared_doctype = 'Vault Folder' AND shared_name = %s)
          )
    """,
        (user, doc_name, doc_folder or ""),
        as_dict=True,
    )

    perm_map = {"View Only": 1, "View & Copy": 2, "Edit": 3, "Full Control": 4}

    if user_shares:
        highest_share = max(user_shares, key=lambda s: perm_map.get(s.permission_level, 0))
        level = perm_map.get(highest_share.permission_level, 1)
        if ptype in ("read",):
            return level >= 1
        elif ptype in ("write",):
            return level >= 3
        elif ptype in ("delete", "share"):
            return level >= 4

    # If no active user share exists, check if user was explicitly revoked
    # This prevents them from inheriting access via a role if they were explicitly removed
    if frappe.db.exists(
        "Vault Share",
        {
            "shared_name": doc_name,
            "shared_doctype": "Vault Secret",
            "share_type": "User",
            "user": user,
            "is_revoked": 1,
        },
    ):
        return False

    # Check active role shares if no explicit user share exists
    if roles:
        role_shares = frappe.db.sql(
            """
            SELECT permission_level FROM `tabVault Share`
            WHERE share_type = 'Role'
              AND frappe_role IN %s
              AND is_revoked = 0
              AND (expires_on IS NULL OR expires_on > NOW())
              AND (
                  (shared_doctype = 'Vault Secret' AND shared_name = %s)
                  OR (shared_doctype = 'Vault Folder' AND shared_name = %s)
              )
        """,
            (tuple(roles), doc_name, doc_folder or ""),
            as_dict=True,
        )
        if role_shares:
            highest_share = max(role_shares, key=lambda s: perm_map.get(s.permission_level, 0))
            level = perm_map.get(highest_share.permission_level, 1)
            if ptype in ("read",):
                return level >= 1
            elif ptype in ("write",):
                return level >= 3
            elif ptype in ("delete", "share"):
                return level >= 4

    return False


def get_folder_permission_query(user=None):
    """Return SQL condition to filter Vault Folders for current user."""
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
                OR (vs.share_type = 'Role' AND vs.frappe_role IN (
                    SELECT role FROM `tabHas Role`
                    WHERE parent = {user_escaped}
                ) AND NOT EXISTS (
                    SELECT 1 FROM `tabVault Share` override
                    WHERE override.shared_doctype = 'Vault Folder'
                    AND override.shared_name = vs.shared_name
                    AND override.share_type = 'User'
                    AND override.user = {user_escaped}
                    AND override.is_revoked = 1
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

    # Check explicit active user-specific share for this folder first
    user_shares = frappe.db.sql(
        """
        SELECT permission_level FROM `tabVault Share`
        WHERE shared_doctype = 'Vault Folder'
          AND shared_name = %s
          AND share_type = 'User'
          AND user = %s
          AND is_revoked = 0
          AND (expires_on IS NULL OR expires_on > NOW())
    """,
        (doc_name, user),
        as_dict=True,
    )

    perm_map = {"View Only": 1, "View & Copy": 2, "Edit": 3, "Full Control": 4}

    if user_shares:
        highest_share = max(user_shares, key=lambda s: perm_map.get(s.permission_level, 0))
        level = perm_map.get(highest_share.permission_level, 1)
        if ptype in ("read",):
            return level >= 1
        elif ptype in ("write",):
            return level >= 3
        elif ptype in ("delete", "share"):
            return level >= 4

    # Check active role shares if no explicit user share exists for this folder
    if roles:
        role_shares = frappe.db.sql(
            """
            SELECT permission_level FROM `tabVault Share`
            WHERE shared_doctype = 'Vault Folder'
              AND shared_name = %s
              AND share_type = 'Role'
              AND frappe_role IN %s
              AND is_revoked = 0
              AND (expires_on IS NULL OR expires_on > NOW())
        """,
            (doc_name, tuple(roles)),
            as_dict=True,
        )
        if role_shares:
            highest_share = max(role_shares, key=lambda s: perm_map.get(s.permission_level, 0))
            level = perm_map.get(highest_share.permission_level, 1)
            if ptype in ("read",):
                return level >= 1
            elif ptype in ("write",):
                return level >= 3
            elif ptype in ("delete", "share"):
                return level >= 4

    return False


def has_file_permission(doc, ptype="read", user=None):
    """Check if user has permission to read a File attached to a Vault Secret."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    roles = frappe.get_roles(user)
    if "Vault Admin" in roles or "System Manager" in roles:
        return True

    if isinstance(doc, str):
        try:
            doc = frappe.get_doc("File", doc)
        except Exception:
            return None

    if doc and doc.attached_to_doctype == "Vault Secret" and doc.attached_to_name:
        return has_secret_permission(doc.attached_to_name, ptype="read", user=user)

    return None
