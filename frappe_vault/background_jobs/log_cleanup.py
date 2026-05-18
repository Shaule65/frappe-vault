"""Weekly audit log cleanup."""

import frappe
from frappe.utils import add_days, today


def cleanup_old_logs():
    """Delete audit logs older than configured retention period."""
    retention_days = frappe.db.get_single_value("Vault Settings", "log_retention_days") or 365
    threshold = add_days(today(), -retention_days)
    frappe.db.delete("Vault Audit Log", {"timestamp": ("<", threshold)})
    frappe.db.commit()
