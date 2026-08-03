"""Vault Dashboard API — Whitelisted endpoints for dashboard layout and charts."""

import json

import frappe
from frappe import _


@frappe.whitelist()
def get_vault_dashboard(from_date=None, to_date=None, user=None):
    from frappe_vault.services.dashboard_service import get_dashboard_layout

    return get_dashboard_layout(from_date=from_date, to_date=to_date, user=user)


@frappe.whitelist()
def get_chart(name, type, from_date=None, to_date=None, user=None):
    from frappe_vault.services import dashboard_service

    method_name = f"get_{name}"
    if hasattr(dashboard_service, method_name):
        func = getattr(dashboard_service, method_name)
        return func(from_date, to_date, user)
    return {"error": _("Chart not found")}


@frappe.whitelist()
def save_dashboard_layout(layout):
    user_roles = frappe.get_roles()
    is_admin = (
        frappe.session.user == "Administrator"
        or "Vault Admin" in user_roles
        or "System Manager" in user_roles
    )
    if not is_admin:
        frappe.throw(_("Only Vault Admins can modify the dashboard layout."), frappe.PermissionError)

    if isinstance(layout, list):
        layout = json.dumps(layout)
    frappe.db.set_value("Vault Settings", "Vault Settings", "dashboard_layout", layout)
    frappe.db.commit()
    return {"status": "success"}


@frappe.whitelist()
def reset_dashboard_layout():
    user_roles = frappe.get_roles()
    is_admin = (
        frappe.session.user == "Administrator"
        or "Vault Admin" in user_roles
        or "System Manager" in user_roles
    )
    if not is_admin:
        frappe.throw(_("Only Vault Admins can reset the dashboard layout."), frappe.PermissionError)

    frappe.db.set_value("Vault Settings", "Vault Settings", "dashboard_layout", None)
    frappe.db.commit()
    return {"status": "reset"}
