"""Encryption utilities for Frappe Vault."""

import frappe
from frappe.utils.password import get_decrypted_password


def decrypt_secret_field(doctype: str, name: str, fieldname: str) -> str:
    """Decrypt a password field value.

    Args:
        doctype: DocType name
        name: Document name
        fieldname: The password field to decrypt

    Returns:
        Decrypted string or empty string
    """
    return get_decrypted_password(doctype, name, fieldname) or ""


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
    elif doc.secret_type == "API Key":
        result["api_key"] = doc.api_key
        result["api_secret"] = decrypt_secret_field("Vault Secret", secret_name, "api_secret")
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
        result["ssh_private_key"] = doc.ssh_private_key  # Code field, not encrypted by Frappe
    elif doc.secret_type == "Certificate":
        result["certificate"] = doc.certificate

    return result
