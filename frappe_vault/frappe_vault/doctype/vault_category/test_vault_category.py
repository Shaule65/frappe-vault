"""Tests for Vault Category DocType."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestVaultCategory(FrappeTestCase):
    """Test cases for Vault Category DocType."""
    
    def tearDown(self):
        """Clean up test data."""
        # Delete test categories (in reverse order to avoid tree conflicts)
        for cat in frappe.get_all(
            "Vault Category",
            filters={"category_name": ["like", "Test%"]},
            order_by="rgt desc"
        ):
            frappe.delete_doc("Vault Category", cat.name, force=True)
    
    def test_create_category(self):
        """Test creating a simple category."""
        category = frappe.get_doc({
            "doctype": "Vault Category",
            "category_name": "Test Simple Category",
            "is_group": 0
        })
        category.insert()
        
        self.assertEqual(category.category_name, "Test Simple Category")
        self.assertEqual(category.is_group, 0)
    
    def test_create_group_category(self):
        """Test creating a group category."""
        category = frappe.get_doc({
            "doctype": "Vault Category",
            "category_name": "Test Group Category",
            "is_group": 1
        })
        category.insert()
        
        self.assertEqual(category.is_group, 1)
    
    def test_nested_categories(self):
        """Test creating nested categories."""
        # Create parent
        parent = frappe.get_doc({
            "doctype": "Vault Category",
            "category_name": "Test Parent Category",
            "is_group": 1
        })
        parent.insert()
        
        # Create child
        child = frappe.get_doc({
            "doctype": "Vault Category",
            "category_name": "Test Child Category",
            "parent_vault_category": "Test Parent Category",
            "is_group": 0
        })
        child.insert()
        
        self.assertEqual(child.parent_vault_category, "Test Parent Category")
    
    def test_cannot_delete_category_with_secrets(self):
        """Test that categories with linked secrets cannot be deleted."""
        # Create category
        category = frappe.get_doc({
            "doctype": "Vault Category",
            "category_name": "Test Category With Secret",
            "is_group": 0
        })
        category.insert()
        
        # Create secret linked to category
        secret = frappe.get_doc({
            "doctype": "Vault Secret",
            "title": "Test Secret for Category",
            "secret_type": "Note",
            "category": "Test Category With Secret"
        })
        secret.insert()
        
        # Try to delete category
        with self.assertRaises(frappe.ValidationError):
            frappe.delete_doc("Vault Category", "Test Category With Secret")
        
        # Clean up secret first
        frappe.delete_doc("Vault Secret", secret.name, force=True)
    
    def test_category_with_icon_and_color(self):
        """Test category with icon and color."""
        category = frappe.get_doc({
            "doctype": "Vault Category",
            "category_name": "Test Styled Category",
            "is_group": 0,
            "icon": "lock",
            "color": "#FF5733"
        })
        category.insert()
        
        self.assertEqual(category.icon, "lock")
        self.assertEqual(category.color, "#FF5733")
