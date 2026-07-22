"""Audit service — centralized audit logging for all vault operations."""

import frappe
from frappe.utils import now_datetime


def _create_log(action: str, secret: str = None, folder: str = None, details: dict = None):
    """Create an audit log entry. Never throws — failures are logged silently."""
    try:
        log = frappe.get_doc({
            "doctype": "Vault Audit Log",
            "action": action,
            "secret": secret,
            "folder": folder,
            "user": frappe.session.user,
            "timestamp": now_datetime(),
            "ip_address": getattr(frappe.local, "request_ip", ""),
            "user_agent": (
                frappe.request.headers.get("User-Agent", "")[:500]
                if hasattr(frappe, "request") and frappe.request
                else ""
            ),
            "details": frappe.as_json(details) if details else None,
        })
        log.insert(ignore_permissions=True)
    except Exception as e:
        try:
            frappe.log_error(f"Vault audit log failed: {e}", "Vault Audit Log Error")
        except Exception:
            pass


# --- Doc event hooks (called from hooks.py doc_events) ---

def log_secret_created(doc, method):
    _create_log("Created", secret=doc.name)


def log_secret_updated(doc, method):
    _create_log("Updated", secret=doc.name)


def log_secret_deleted(doc, method):
    _create_log("Deleted", secret=doc.name, details={"title": doc.title})


def log_share_created(doc, method):
    recipient = doc.user if doc.share_type == "User" else doc.frappe_role
    details = {
        "share_type": doc.share_type,
        "permission": doc.permission_level,
        "recipient": recipient
    }
    if doc.expires_on:
        details["expires_on"] = str(doc.expires_on)
    _create_log("Shared", secret=doc.shared_name if doc.shared_doctype == "Vault Secret" else None,
                folder=doc.shared_name if doc.shared_doctype == "Vault Folder" else None,
                details=details)


def log_share_removed(doc, method):
    recipient = doc.user if doc.share_type == "User" else doc.frappe_role
    _create_log("Unshared", secret=doc.shared_name if doc.shared_doctype == "Vault Secret" else None,
                details={"share_type": doc.share_type, "recipient": recipient})


# --- Callable from services ---

def log_secret_viewed(secret_name: str):
    _create_log("Viewed", secret=secret_name)


def log_secret_copied(secret_name: str, field: str = "password"):
    _create_log("Copied", secret=secret_name, details={"field": field})


def log_password_generated():
    _create_log("Generated")


def log_export(count: int, format: str):
    _create_log("Exported", details={"count": count, "format": format})


def log_import(count: int, format: str):
    _create_log("Imported", details={"count": count, "format": format})
