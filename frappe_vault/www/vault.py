"""Vault frontend page context."""

import frappe

no_cache = 1


def get_context(context):
    """Set up context for the vault frontend page."""
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    
    context.title = "Frappe Vault"
    context.csrf_token = csrf_token
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/vault"
        raise frappe.Redirect
    
    return context
