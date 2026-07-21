import frappe
from frappe.tests.utils import FrappeTestCase
from frappe_vault.services.secret_service import create_secret, get_secret, delete_secret

class TestSecretService(FrappeTestCase):
    def setUp(self):
        # Ensure we have a clean slate for test secret
        frappe.db.delete("Vault Secret", {"title": "Test Service Secret"})
        frappe.db.commit()

    def tearDown(self):
        frappe.db.delete("Vault Secret", {"title": "Test Service Secret"})
        frappe.db.commit()

    def test_create_and_get_secret(self):
        secret_data = {
            "title": "Test Service Secret",
            "secret_type": "Password",
            "username": "admin",
            "password": "SuperSecretPassword123!",
            "url": "https://example.com"
        }
        
        # Test creation
        new_secret = create_secret(secret_data)
        self.assertTrue(new_secret)
        self.assertEqual(new_secret.get("title"), "Test Service Secret")
        
        # Test retrieval (without decrypting password)
        retrieved = get_secret(new_secret.get("name"))
        self.assertEqual(retrieved.get("title"), "Test Service Secret")
        
        # Test decryption retrieval
        decrypted = get_secret(new_secret.get("name"), decrypt=True)
        self.assertEqual(decrypted.get("decrypted", {}).get("password"), "SuperSecretPassword123!")

    def test_delete_secret(self):
        secret_data = {
            "title": "Test Service Secret",
            "secret_type": "Note",
            "notes": "Some test notes"
        }
        
        new_secret = create_secret(secret_data)
        secret_name = new_secret.get("name")
        
        # Delete it
        delete_secret(secret_name)
        
        # Ensure it's in trash (Frappe's default behavior) or actually deleted
        exists = frappe.db.exists("Vault Secret", secret_name)
        self.assertFalse(exists)

    def test_toggle_bookmark(self):
        secret_data = {
            "title": "Test Bookmark Secret",
            "secret_type": "Note",
            "notes": "Some test notes"
        }
        new_secret = create_secret(secret_data)
        secret_name = new_secret.get("name")
        
        # Ensure it's not bookmarked initially
        from frappe_vault.services.secret_service import toggle_bookmark
        user = frappe.session.user
        fav_exists = frappe.db.exists("Vault Bookmark", {"user": user, "secret": secret_name})
        self.assertFalse(fav_exists)
        
        # Toggle on
        res = toggle_bookmark(secret_name)
        self.assertEqual(res.get("is_bookmark"), 1)
        self.assertTrue(frappe.db.exists("Vault Bookmark", {"user": user, "secret": secret_name}))
        
        # Toggle off
        res = toggle_bookmark(secret_name)
        self.assertEqual(res.get("is_bookmark"), 0)
        self.assertFalse(frappe.db.exists("Vault Bookmark", {"user": user, "secret": secret_name}))
        
        from frappe_vault.services.secret_service import delete_secret
        delete_secret(secret_name)
