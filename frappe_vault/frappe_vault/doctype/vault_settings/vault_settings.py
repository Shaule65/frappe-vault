"""Vault Settings DocType controller."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, now_datetime
from frappe.utils.password import check_password, get_decrypted_password


class VaultSettings(Document):
    """Single DocType for Vault configuration and master password settings."""
    
    def validate(self):
        """Validate settings."""
        if self.enabled and not self.master_password:
            frappe.throw(_("Master Password is required when enabled"))
        
        if self.session_timeout < 0:
            frappe.throw(_("Session timeout cannot be negative"))
        
        if self.default_password_length < 8:
            frappe.throw(_("Default password length must be at least 8"))


@frappe.whitelist()
def verify_master_password(password: str) -> dict:
    """Verify the master password and create a session.
    
    Args:
        password: The master password to verify
        
    Returns:
        dict with success status and session info
    """
    settings = frappe.get_single("Vault Settings")
    
    if not settings.enabled:
        return {"success": True, "message": _("Master password not required")}
    
    # Get the stored master password
    stored_password = get_decrypted_password(
        "Vault Settings", "Vault Settings", "master_password"
    )
    
    if not stored_password:
        return {"success": True, "message": _("No master password set")}
    
    if password == stored_password:
        # Create session
        session_key = create_vault_session(settings.session_timeout)
        return {
            "success": True,
            "message": _("Master password verified"),
            "session_key": session_key,
            "timeout": settings.session_timeout
        }
    else:
        frappe.log_error(
            f"Failed master password attempt by {frappe.session.user}",
            "Vault Security"
        )
        return {"success": False, "message": _("Invalid master password")}


@frappe.whitelist()
def check_vault_session() -> dict:
    """Check if the current vault session is valid.
    
    Returns:
        dict with session validity status
    """
    settings = frappe.get_single("Vault Settings")
    
    if not settings.enabled:
        return {"valid": True, "required": False}
    
    session = get_vault_session()
    
    if session and session.get("valid"):
        return {
            "valid": True,
            "required": True,
            "expires_at": session.get("expires_at")
        }
    
    return {"valid": False, "required": True}


def create_vault_session(timeout_minutes: int) -> str:
    """Create a new vault session.
    
    Args:
        timeout_minutes: Session timeout in minutes
        
    Returns:
        Session key
    """
    import hashlib
    import secrets
    
    session_key = secrets.token_hex(32)
    user = frappe.session.user
    
    # Calculate expiry
    from datetime import timedelta
    if timeout_minutes > 0:
        expires_at = now_datetime() + timedelta(minutes=timeout_minutes)
    else:
        expires_at = None
    
    # Store session in cache
    cache_key = f"vault_session:{user}"
    frappe.cache().set_value(
        cache_key,
        {
            "session_key": session_key,
            "user": user,
            "created_at": str(now_datetime()),
            "expires_at": str(expires_at) if expires_at else None,
        },
        expires_in_sec=timeout_minutes * 60 if timeout_minutes > 0 else 86400 * 7
    )
    
    return session_key


def get_vault_session() -> dict:
    """Get the current vault session.
    
    Returns:
        Session dict or None
    """
    user = frappe.session.user
    cache_key = f"vault_session:{user}"
    
    session = frappe.cache().get_value(cache_key)
    
    if not session:
        return None
    
    # Check expiry
    if session.get("expires_at"):
        from frappe.utils import get_datetime
        expires_at = get_datetime(session["expires_at"])
        if now_datetime() > expires_at:
            frappe.cache().delete_value(cache_key)
            return None
    
    session["valid"] = True
    return session


def clear_vault_session():
    """Clear the current vault session."""
    user = frappe.session.user
    cache_key = f"vault_session:{user}"
    frappe.cache().delete_value(cache_key)


@frappe.whitelist()
def logout_vault() -> dict:
    """Log out of the vault session.
    
    Returns:
        dict with success status
    """
    clear_vault_session()
    return {"success": True, "message": _("Vault session ended")}


def require_master_password():
    """Check if master password is required for the current operation.
    
    Raises an exception if master password verification is required but not done.
    """
    settings = frappe.get_single("Vault Settings")
    
    if not settings.enabled:
        return True
    
    session = get_vault_session()
    
    if not session or not session.get("valid"):
        frappe.throw(
            _("Master password verification required. Please unlock your vault."),
            frappe.AuthenticationError
        )
    
    return True
