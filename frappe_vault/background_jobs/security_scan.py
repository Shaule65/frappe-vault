"""Weekly security scan."""

import frappe

from frappe_vault.services.security_service import calculate_security_score


def run_security_scan():
    """Recalculate security scores for all vault users."""
    users = frappe.db.sql_list("SELECT DISTINCT owner FROM `tabVault Secret`")
    for user in users:
        try:
            calculate_security_score(user)
        except Exception as e:
            frappe.log_error(f"Security scan failed for {user}: {e}", "Vault Security Scan")
