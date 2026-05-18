"""Daily password expiry check."""

import frappe
from frappe import _
from frappe.utils import add_days, today


def check_password_expiry():
    """Send notifications for passwords older than policy threshold."""
    threshold_days = frappe.db.get_single_value("Vault Settings", "default_password_length") or 90
    # Use policy max age if available
    default_policy = frappe.db.get_single_value("Vault Settings", "default_password_policy")
    if default_policy:
        threshold_days = frappe.db.get_value("Vault Policy", default_policy, "max_password_age_days") or 90

    threshold_date = add_days(today(), -threshold_days)
    old_passwords = frappe.get_all("Vault Secret", filters={"secret_type": "Password", "password_last_changed": ("<", threshold_date)},
                                    fields=["name", "title", "owner", "password_last_changed"])

    by_owner = {}
    for s in old_passwords:
        by_owner.setdefault(s.owner, []).append(s)

    for owner, secrets in by_owner.items():
        if owner == "Administrator":
            continue
        try:
            frappe.get_doc({"doctype": "Notification Log", "subject": _("Password Update Reminder"),
                           "email_content": _("You have {0} password(s) that need rotation.").format(len(secrets)),
                           "for_user": owner, "type": "Alert", "document_type": "Vault Secret", "document_name": secrets[0].name}).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Password expiry notification failed for {owner}: {e}", "Vault")
