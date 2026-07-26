import frappe
from frappe.tests.utils import FrappeTestCase
from frappe_vault.services.secret_service import create_secret
from frappe_vault.services.sharing_service import share_secret, get_shares_for_secret, unshare, update_share_permission, get_role_users

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

        # Update permission level
        update_res = update_share_permission(shares[0].get("name"), "Edit")
        self.assertEqual(update_res.get("permission_level"), "Edit")
        
        # Unshare/Revoke
        unshare_res = unshare(shares[0].get("name"))
        self.assertEqual(unshare_res.get("removed"), shares[0].get("name"))

    def test_get_role_users(self):
        users = get_role_users("System Manager")
        self.assertIsInstance(users, list)

    def test_save_role_member_permission(self):
        from frappe_vault.services.sharing_service import save_role_member_permission
        secret = create_secret({
            "title": "Test Shared Secret",
            "secret_type": "Password",
            "password": "pass"
        })
        res = save_role_member_permission(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            user="Administrator",
            permission_level="Full Control",
            is_revoked=False
        )
        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("permission_level"), "Full Control")
