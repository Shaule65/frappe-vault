"""Post-install setup for Frappe Vault."""

import frappe


def after_install():
    """Run after app install."""

    # Ensure module exists first
    ensure_module()

    frappe.clear_cache()

    create_roles()
    create_default_settings()
    create_default_folders()
    create_desktop_icon()

    frappe.db.commit()


def ensure_module():
    """Create Vault module if missing."""
    if not frappe.db.exists("Module Def", "Vault"):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": "Vault",
            "app_name": "frappe_vault"
        }).insert(ignore_permissions=True)


def create_roles():
    """Create vault-specific roles."""
    for role_name in [
        "Vault User",
        "Vault Admin"
    ]:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1
            }).insert(ignore_permissions=True)


def create_default_settings():
    """Initialize Vault Settings singleton."""
    if frappe.db.exists("DocType", "Vault Settings"):
        if not frappe.db.exists("Vault Settings"):
            frappe.get_doc({
                "doctype": "Vault Settings"
            }).insert(ignore_permissions=True)


def create_default_folders():
    """Create starter folders."""
    folders = [
        {"folder_name": "Work", "icon": "briefcase", "color": "#3B82F6"},
        {"folder_name": "Personal", "icon": "user", "color": "#10B981"},
        {"folder_name": "Finance", "icon": "credit-card", "color": "#F59E0B"},
        {"folder_name": "Servers", "icon": "server", "color": "#8B5CF6"},
    ]

    if frappe.db.exists("DocType", "Vault Folder"):
        for folder in folders:
            if not frappe.db.exists(
                "Vault Folder",
                folder["folder_name"]
            ):
                frappe.get_doc({
                    "doctype": "Vault Folder",
                    **folder
                }).insert(ignore_permissions=True)


def create_desktop_icon():
    """Create Desk desktop icon for the Vault app."""
    try:
        from frappe.desk.doctype.desktop_icon.desktop_icon import (
            create_desktop_icons_from_installed_apps,
        )

        create_desktop_icons_from_installed_apps()
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Frappe Vault Desktop Icon Creation Failed",
        )
