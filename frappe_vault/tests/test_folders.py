import frappe
from frappe.tests.utils import FrappeTestCase
from frappe_vault.api.folders import create, get_all

class TestFolders(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("Vault Folder", {"folder_name": "Test Folder"})
        frappe.db.commit()

    def tearDown(self):
        frappe.db.delete("Vault Folder", {"folder_name": "Test Folder"})
        frappe.db.commit()

    def test_create_and_get_folders(self):
        folder = create("Test Folder", icon="folder")
        self.assertTrue(folder)
        
        folders = get_all()
        self.assertTrue(any(f.get("folder_name") == "Test Folder" for f in folders))

    def test_delete_folder_keep_secrets(self):
        folder = create("Test Folder", icon="folder")
        folder_name = folder["name"]

        from frappe_vault.api.secrets import create as create_secret
        from frappe_vault.api.folders import delete as delete_folder

        secret = create_secret(title="Secret to keep", folder=folder_name, password="Password123!")
        secret_name = secret["name"]

        # Delete folder but keep secrets (move to unfoldered)
        result = delete_folder(folder_name, delete_secrets=False)
        self.assertEqual(result["deleted"], folder_name)
        self.assertFalse(frappe.db.exists("Vault Folder", folder_name))
        self.assertTrue(frappe.db.exists("Vault Secret", secret_name))
        
        # Verify secret's folder field is now None / empty
        sec_folder = frappe.db.get_value("Vault Secret", secret_name, "folder")
        self.assertIsNone(sec_folder)

    def test_delete_folder_and_secrets(self):
        folder = create("Test Folder", icon="folder")
        folder_name = folder["name"]

        from frappe_vault.api.secrets import create as create_secret
        from frappe_vault.api.folders import delete as delete_folder

        secret = create_secret(title="Secret to delete", folder=folder_name, password="Password123!")
        secret_name = secret["name"]

        # Delete folder AND secrets
        result = delete_folder(folder_name, delete_secrets=True)
        self.assertEqual(result["deleted"], folder_name)
        self.assertFalse(frappe.db.exists("Vault Folder", folder_name))
        self.assertFalse(frappe.db.exists("Vault Secret", secret_name))

