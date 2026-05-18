"""Permission query conditions for Frappe Vault.

Ensures row-level security: users only see secrets they own or that are shared with them.
"""

import frappe


def get_secret_permission_query(user=None):
    """Return SQL condition to filter Vault Secrets for current user.

    A user can see a secret if:
    1. They own it, OR
    2. It has been shared with them directly, OR
    3. It has been shared with a group they belong to, OR
    4. It has been shared with a role they have
    """
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    # Check if user has Vault Admin role — they see everything
    if "Vault Admin" in frappe.get_roles(user):
        return ""

    user_escaped = frappe.db.escape(user)

    return f"""(
        `tabVault Secret`.owner = {user_escaped}
        OR `tabVault Secret`.name IN (
            SELECT vs.shared_name
            FROM `tabVault Share` vs
            WHERE vs.shared_doctype = 'Vault Secret'
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


def has_secret_permission(doc, ptype="read", user=None):
    """Check if a user has permission on a specific Vault Secret document."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    if "Vault Admin" in frappe.get_roles(user):
        return True

    # Owner always has access
    if doc.owner == user:
        return True

    # Check sharing
    shared = frappe.db.exists("Vault Share", {
        "shared_doctype": "Vault Secret",
        "shared_name": doc.name,
        "share_type": "User",
        "user": user,
    })

    if shared:
        if ptype in ("read",):
            return True
        # Check permission level for write/delete
        share = frappe.get_doc("Vault Share", shared)
        if ptype == "write" and share.permission_level in ("Edit", "Full Control"):
            return True
        if ptype == "delete" and share.permission_level == "Full Control":
            return True
        if ptype == "read":
            return True

    # Check group sharing
    user_groups = frappe.get_all(
        "Vault Group Member",
        filters={"user": user},
        pluck="parent",
    )
    if user_groups:
        group_shared = frappe.db.exists("Vault Share", {
            "shared_doctype": "Vault Secret",
            "shared_name": doc.name,
            "share_type": "Group",
            "group": ("in", user_groups),
        })
        if group_shared:
            return True

    # Check role sharing
    user_roles = frappe.get_roles(user)
    if user_roles:
        role_shared = frappe.db.exists("Vault Share", {
            "shared_doctype": "Vault Secret",
            "shared_name": doc.name,
            "share_type": "Role",
            "frappe_role": ("in", user_roles),
        })
        if role_shared:
            return True

    return False
