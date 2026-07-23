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
