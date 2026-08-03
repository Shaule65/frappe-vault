"""Audit API — audit log query endpoints."""

import frappe
from frappe import _


@frappe.whitelist()
def get_logs(
    secret: str | None = None,
    user: str | None = None,
    action: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Get audit logs with filters. Vault Admin only."""
    if "Vault Admin" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    filters = {}
    if secret:
        filters["secret"] = secret
    if user:
        filters["user"] = user
    if action:
        filters["action"] = action
    if from_date:
        filters["timestamp"] = (">=", from_date)
    if to_date:
        if "timestamp" in filters:
            filters["timestamp"] = ("between", [from_date, to_date])
        else:
            filters["timestamp"] = ("<=", to_date)

    logs = frappe.get_all(
        "Vault Audit Log",
        filters=filters,
        fields=["name", "action", "secret", "folder", "user", "timestamp", "ip_address", "details"],
        order_by="timestamp desc",
        limit_page_length=int(limit),
        limit_start=int(offset),
    )
    total = frappe.db.count("Vault Audit Log", filters=filters)
    return {"logs": logs, "total": total}


@frappe.whitelist()
def get_secret_activity(secret_name: str, limit: int = 20) -> list[dict]:
    """Get activity timeline for a specific secret."""
    if not frappe.has_permission("Vault Secret", "read", secret_name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    return frappe.get_all(
        "Vault Audit Log",
        filters={"secret": secret_name},
        fields=["name", "action", "user", "timestamp", "details"],
        order_by="timestamp desc",
        limit_page_length=int(limit),
    )
