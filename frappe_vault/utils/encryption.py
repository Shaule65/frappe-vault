"""Encryption utilities for Frappe Vault.

Uses Frappe's built-in encryption capabilities to securely store sensitive data.
"""

import frappe
from frappe.utils.password import get_decrypted_password, set_encrypted_password

# Field name used for storing encrypted passwords
PASSWORD_FIELD = "password"


def encrypt_secret(doctype: str, docname: str, fieldname: str, value: str) -> None:
    """Encrypt and store a secret value.
    
    Uses Frappe's built-in encryption which relies on the site's encryption key.
    
    Args:
        doctype: The DocType name
        docname: The document name
        fieldname: The field to encrypt
        value: The plaintext value to encrypt
    """
    set_encrypted_password(doctype, docname, value, fieldname)


def decrypt_secret(doctype: str, docname: str, fieldname: str) -> str:
    """Decrypt and retrieve a secret value.
    
    Args:
        doctype: The DocType name
        docname: The document name
        fieldname: The field to decrypt
        
    Returns:
        The decrypted plaintext value
    """
    return get_decrypted_password(doctype, docname, fieldname) or ""


def get_encryption_key() -> str:
    """Get the current encryption key (for verification purposes only).
    
    Returns:
        A masked version of the encryption key status
    """
    from frappe.utils.password import get_encryption_key as frappe_get_key
    
    try:
        key = frappe_get_key()
        if key:
            return "Encryption key is configured"
        return "No encryption key found"
    except Exception:
        return "Encryption key error"
