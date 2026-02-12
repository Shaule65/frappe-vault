"""Vault Secret DocType controller."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class VaultSecret(Document):
    """Controller for Vault Secret - the main secrets storage DocType."""
    
    def validate(self):
        """Validate the secret before saving."""
        self.validate_title()
        self.calculate_password_strength()
    
    def validate_title(self):
        """Ensure title is not empty and is trimmed."""
        if self.title:
            self.title = self.title.strip()
        if not self.title:
            frappe.throw(_("Title is required"))
    
    def calculate_password_strength(self):
        """Calculate and update password strength when password changes."""
        if self.secret_type == "Password" and self.password:
            from frappe_vault.utils.password_generator import calculate_password_strength
            
            # Get the actual password value
            password = self.password
            if password:
                strength = calculate_password_strength(password)
                self.password_strength = strength.get("level", "")
    
    def before_save(self):
        """Handle pre-save tasks."""
        # Track password changes
        if self.is_new() or self.has_value_changed("password"):
            self.password_last_changed = today()
    
    def after_insert(self):
        """Handle post-insert tasks."""
        self.update_access_metadata()
    
    def on_update(self):
        """Handle post-update tasks."""
        pass
    
    def update_access_metadata(self):
        """Update access tracking metadata."""
        self.db_set("last_accessed", now_datetime(), update_modified=False)
        self.db_set("access_count", (self.access_count or 0) + 1, update_modified=False)


def log_access(doc, method):
    """Log access to a vault secret.
    
    Called via doc_events hook.
    """
    if method in ["after_insert", "on_update"]:
        action = "created" if method == "after_insert" else "updated"
    else:
        action = "viewed"
    
    create_access_log(doc.name, action)


def create_access_log(secret_name: str, action: str = "viewed"):
    """Create an access log entry.
    
    Args:
        secret_name: The name of the Vault Secret that was accessed
        action: The action performed (viewed, created, updated, shared)
    """
    try:
        log = frappe.get_doc({
            "doctype": "Vault Access Log",
            "secret": secret_name,
            "user": frappe.session.user,
            "action": action,
            "access_time": now_datetime(),
            "ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else "",
        })
        log.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to create access log: {e}", "Vault Access Log Error")


@frappe.whitelist()
def get_decrypted_password(secret_name: str) -> dict:
    """Get the decrypted password for a secret.
    
    This method requires authentication, master password verification, and logs the access.
    
    Args:
        secret_name: The name of the Vault Secret
        
    Returns:
        dict with password field
    """
    # Check permission
    if not frappe.has_permission("Vault Secret", "read", secret_name):
        frappe.throw(_("You don't have permission to access this secret"))
    
    # Check master password session
    from frappe_vault.frappe_vault.doctype.vault_settings.vault_settings import require_master_password
    require_master_password()
    
    doc = frappe.get_doc("Vault Secret", secret_name)
    
    # Log the access
    create_access_log(secret_name, "viewed")
    
    # Update access metadata
    doc.update_access_metadata()
    
    # Return decrypted password
    from frappe.utils.password import get_decrypted_password as decrypt_pwd
    
    password = decrypt_pwd("Vault Secret", secret_name, "password") or ""
    api_secret = ""
    
    if doc.secret_type == "API Key":
        api_secret = decrypt_pwd("Vault Secret", secret_name, "api_secret") or ""
    
    return {
        "password": password,
        "api_secret": api_secret,
    }


@frappe.whitelist()
def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_special: bool = True,
    exclude_ambiguous: bool = False,
) -> dict:
    """Generate a secure random password.
    
    Args:
        length: Password length
        use_uppercase: Include uppercase letters
        use_lowercase: Include lowercase letters
        use_digits: Include digits
        use_special: Include special characters
        exclude_ambiguous: Exclude ambiguous characters
        
    Returns:
        dict with password and strength info
    """
    from frappe_vault.utils.password_generator import (
        calculate_password_strength,
        generate_password as gen_pwd,
    )
    
    # Convert string booleans if needed
    length = int(length)
    use_uppercase = frappe.utils.cint(use_uppercase)
    use_lowercase = frappe.utils.cint(use_lowercase)
    use_digits = frappe.utils.cint(use_digits)
    use_special = frappe.utils.cint(use_special)
    exclude_ambiguous = frappe.utils.cint(exclude_ambiguous)
    
    password = gen_pwd(
        length=length,
        use_uppercase=use_uppercase,
        use_lowercase=use_lowercase,
        use_digits=use_digits,
        use_special=use_special,
        exclude_ambiguous=exclude_ambiguous,
    )
    
    strength = calculate_password_strength(password)
    
    return {
        "password": password,
        "strength": strength,
    }


@frappe.whitelist()
def get_vault_stats() -> dict:
    """Get vault statistics for the dashboard.
    
    Returns:
        dict with various statistics
    """
    user = frappe.session.user
    
    # Total secrets owned by user
    total_secrets = frappe.db.count(
        "Vault Secret",
        filters={"owner": user}
    )
    
    # Favorites
    favorites = frappe.db.count(
        "Vault Secret",
        filters={"owner": user, "is_favorite": 1}
    )
    
    # Weak passwords
    weak_passwords = frappe.db.count(
        "Vault Secret",
        filters={"owner": user, "password_strength": ["in", ["weak", "fair"]]}
    )
    
    # Secrets by type
    secrets_by_type = frappe.db.sql("""
        SELECT secret_type, COUNT(*) as count
        FROM `tabVault Secret`
        WHERE owner = %s
        GROUP BY secret_type
    """, (user,), as_dict=True)
    
    # Recently accessed
    recent_secrets = frappe.get_all(
        "Vault Secret",
        filters={"owner": user},
        fields=["name", "title", "secret_type", "category", "last_accessed"],
        order_by="last_accessed desc",
        limit=5
    )
    
    return {
        "total_secrets": total_secrets,
        "favorites": favorites,
        "weak_passwords": weak_passwords,
        "secrets_by_type": {s.secret_type: s.count for s in secrets_by_type},
        "recent_secrets": recent_secrets,
    }
