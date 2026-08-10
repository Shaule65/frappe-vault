"""Encryption utilities for Frappe Vault."""

import frappe
from frappe.utils.password import get_decrypted_password


def decrypt_secret_field(doctype: str, name: str, fieldname: str) -> str:
    """Decrypt a password field value safely.

    Args:
        doctype: DocType name
        name: Document name
        fieldname: The password field to decrypt

    Returns:
        Decrypted string or empty string
    """
    try:
        val = get_decrypted_password(doctype, name, fieldname, raise_exception=False)
        if val:
            return val
    except Exception:
        frappe.log_error(title=f"Vault Secret Decryption Warning ({name}.{fieldname})")

    # Direct Auth table fallback for unauthenticated guest link consumers
    try:
        auth_val = frappe.db.get_value(
            "__Auth", {"doctype": doctype, "docname": name, "fieldname": fieldname}, "password"
        )
        if auth_val:
            from frappe.utils.password import decrypt

            return decrypt(auth_val)
    except Exception:
        frappe.log_error(title=f"Vault Auth Fallback Decryption Warning ({name}.{fieldname})")

    return ""


def get_decrypted_secret_data(secret_name: str) -> dict:
    """Get all decrypted fields for a Vault Secret based on its type.

    Args:
        secret_name: Vault Secret document name

    Returns:
        dict with decrypted field values
    """
    doc = frappe.get_doc("Vault Secret", secret_name)
    result = {}

    if doc.secret_type == "Password":
        result["password"] = decrypt_secret_field("Vault Secret", secret_name, "password")
        result["totp_secret"] = decrypt_secret_field("Vault Secret", secret_name, "totp_secret")
    elif doc.secret_type == "API Key":
        result["api_key"] = doc.api_key
        result["api_secret"] = decrypt_secret_field("Vault Secret", secret_name, "api_secret")
        result["totp_secret"] = decrypt_secret_field("Vault Secret", secret_name, "totp_secret")
    elif doc.secret_type == "Credit Card":
        result["card_number"] = decrypt_secret_field("Vault Secret", secret_name, "card_number")
        result["card_cvv"] = decrypt_secret_field("Vault Secret", secret_name, "card_cvv")
        result["card_holder"] = doc.card_holder
        result["card_expiry"] = doc.card_expiry
    elif doc.secret_type == "Database":
        result["db_host"] = doc.db_host
        result["db_port"] = doc.db_port
        result["db_name"] = doc.db_name
        result["username"] = doc.username
        result["db_password"] = decrypt_secret_field("Vault Secret", secret_name, "db_password")
    elif doc.secret_type == "SSH Key":
        result["username"] = doc.username
        result["ssh_private_key"] = doc.ssh_private_key
    elif doc.secret_type == "Certificate":
        result["certificate"] = doc.certificate

    return result
