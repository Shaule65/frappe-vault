import frappe
from frappe.tests.utils import FrappeTestCase
from frappe_vault.services.secret_service import create_secret
from frappe_vault.services.sharing_service import share_secret, get_shares_for_secret, unshare

class TestSharingService(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("Vault Secret", {"title": "Test Shared Secret"})
        frappe.db.delete("Vault Share", {"shared_name": "Test Shared Secret"})
        frappe.db.commit()

    def tearDown(self):
        frappe.db.delete("Vault Secret", {"title": "Test Shared Secret"})
        frappe.db.commit()

    def test_share_secret_with_role(self):
        # Create a secret
        secret = create_secret({
            "title": "Test Shared Secret",
            "secret_type": "Password",
            "password": "pass"
        })
        
        # Share secret with Role
        share_res = share_secret(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            share_type="Role",
            frappe_role="Vault User",
            permission_level="View Only"
        )
        self.assertTrue(share_res.get("name"))
        
        # Get shares for secret
        shares = get_shares_for_secret(secret.get("name"))
        self.assertEqual(len(shares), 1)
        self.assertEqual(shares[0].get("share_type"), "Role")
        self.assertEqual(shares[0].get("frappe_role"), "Vault User")
        self.assertEqual(shares[0].get("permission_level"), "View Only")
        
        # Unshare/Revoke
        unshare_res = unshare(shares[0].get("name"))
        self.assertEqual(unshare_res.get("removed"), shares[0].get("name"))
