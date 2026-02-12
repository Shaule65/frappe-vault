"""Tests for Vault Access Log DocType."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestVaultAccessLog(FrappeTestCase):
    """Test cases for Vault Access Log DocType."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test secret
        self.test_secret = frappe.get_doc({
            "doctype": "Vault Secret",
            "title": "Test Secret for Logs",
            "secret_type": "Password",
            "password": "test123"
        })
        self.test_secret.insert(ignore_permissions=True)
    
    def tearDown(self):
        """Clean up test data."""
        # Delete test logs
        for log in frappe.get_all(
            "Vault Access Log",
            filters={"secret": self.test_secret.name}
        ):
            frappe.delete_doc("Vault Access Log", log.name, force=True)
        
        # Delete test secret
        frappe.delete_doc("Vault Secret", self.test_secret.name, force=True)
    
    def test_create_access_log(self):
        """Test creating an access log entry."""
        from frappe_vault.frappe_vault.doctype.vault_secret.vault_secret import create_access_log
        
        create_access_log(self.test_secret.name, "viewed")
        
        logs = frappe.get_all(
            "Vault Access Log",
            filters={"secret": self.test_secret.name, "action": "viewed"}
        )
        
        self.assertGreater(len(logs), 0)
    
    def test_log_contains_user(self):
        """Test that log contains the current user."""
        from frappe_vault.frappe_vault.doctype.vault_secret.vault_secret import create_access_log
        
        create_access_log(self.test_secret.name, "updated")
        
        log = frappe.get_last_doc(
            "Vault Access Log",
            filters={"secret": self.test_secret.name}
        )
        
        self.assertEqual(log.user, frappe.session.user)
    
    def test_log_is_read_only(self):
        """Test that access logs are read-only after creation."""
        from frappe_vault.frappe_vault.doctype.vault_secret.vault_secret import create_access_log
        
        create_access_log(self.test_secret.name, "viewed")
        
        log = frappe.get_last_doc(
            "Vault Access Log",
            filters={"secret": self.test_secret.name}
        )
        
        # The DocType should be read-only
        doctype_meta = frappe.get_meta("Vault Access Log")
        self.assertTrue(doctype_meta.read_only)
