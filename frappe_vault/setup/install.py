"""Post-install setup for Frappe Vault."""

import frappe


def after_install():
    """Create default roles and settings after app installation."""
    create_roles()
    create_default_settings()
    create_default_folders()
    create_default_policy()


def create_roles():
    """Create vault-specific roles."""
    for role_name in ["Vault User", "Vault Manager", "Vault Admin"]:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)


def create_default_settings():
    """Initialize Vault Settings singleton."""
    if not frappe.db.exists("Vault Settings"):
        doc = frappe.get_doc({"doctype": "Vault Settings"})
        doc.insert(ignore_permissions=True)


def create_default_folders():
    """Create starter folders."""
    folders = [
        {"folder_name": "Work", "icon": "briefcase", "color": "#3B82F6"},
        {"folder_name": "Personal", "icon": "user", "color": "#10B981"},
        {"folder_name": "Finance", "icon": "credit-card", "color": "#F59E0B"},
        {"folder_name": "Servers", "icon": "server", "color": "#8B5CF6"},
    ]
    for f in folders:
        if not frappe.db.exists("Vault Folder", f["folder_name"]):
            frappe.get_doc({"doctype": "Vault Folder", **f}).insert(ignore_permissions=True)


def create_default_policy():
    """Create a default password policy."""
    if not frappe.db.exists("Vault Policy", {"is_default": 1}):
        frappe.get_doc({
            "doctype": "Vault Policy",
            "policy_name": "Default Policy",
            "is_default": 1,
            "min_password_length": 12,
            "require_uppercase": 1,
            "require_lowercase": 1,
            "require_digits": 1,
            "require_special": 1,
            "max_password_age_days": 90,
            "prevent_reuse_count": 3,
            "auto_lock_timeout_mins": 30,
        }).insert(ignore_permissions=True)
