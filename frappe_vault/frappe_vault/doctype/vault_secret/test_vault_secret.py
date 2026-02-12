"""Tests for Vault Secret DocType."""

import frappe
from frappe.tests.utils import FrappeTestCase

from frappe_vault.utils.password_generator import (
    calculate_password_strength,
    generate_password,
)


class TestVaultSecret(FrappeTestCase):
    """Test cases for Vault Secret DocType."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test category
        if not frappe.db.exists("Vault Category", "Test Category"):
            frappe.get_doc({
                "doctype": "Vault Category",
                "category_name": "Test Category",
                "is_group": 0
            }).insert(ignore_permissions=True)
    
    def tearDown(self):
        """Clean up test data."""
        # Delete test secrets
        for secret in frappe.get_all("Vault Secret", filters={"title": ["like", "Test%"]}):
            frappe.delete_doc("Vault Secret", secret.name, force=True)
    
    def test_create_password_secret(self):
        """Test creating a password-type secret."""
        secret = frappe.get_doc({
            "doctype": "Vault Secret",
            "title": "Test Password Secret",
            "secret_type": "Password",
            "username": "testuser",
            "password": "TestPassword123!",
            "url": "https://example.com"
        })
        secret.insert()
        
        self.assertEqual(secret.title, "Test Password Secret")
        self.assertEqual(secret.secret_type, "Password")
        self.assertIsNotNone(secret.password_strength)
    
    def test_create_api_key_secret(self):
        """Test creating an API key-type secret."""
        secret = frappe.get_doc({
            "doctype": "Vault Secret",
            "title": "Test API Secret",
            "secret_type": "API Key",
            "api_key": "test_api_key_12345",
            "api_secret": "test_api_secret_67890"
        })
        secret.insert()
        
        self.assertEqual(secret.title, "Test API Secret")
        self.assertEqual(secret.secret_type, "API Key")
    
    def test_password_strength_calculation(self):
        """Test password strength calculation."""
        # Weak password
        weak = calculate_password_strength("12345678")
        self.assertEqual(weak["level"], "weak")
        
        # Strong password
        strong = calculate_password_strength("MyStr0ng!P@ssw0rd")
        self.assertIn(strong["level"], ["strong", "excellent"])
    
    def test_password_generation(self):
        """Test password generation."""
        password = generate_password(length=20)
        self.assertEqual(len(password), 20)
        
        # Test with only lowercase
        lower_only = generate_password(
            length=16,
            use_uppercase=False,
            use_digits=False,
            use_special=False
        )
        self.assertTrue(lower_only.islower())
    
    def test_favorite_toggle(self):
        """Test toggling favorite status."""
        secret = frappe.get_doc({
            "doctype": "Vault Secret",
            "title": "Test Favorite Secret",
            "secret_type": "Note",
            "notes": "Test notes"
        })
        secret.insert()
        
        self.assertEqual(secret.is_favorite, 0)
        
        secret.is_favorite = 1
        secret.save()
        
        # Reload and verify
        secret.reload()
        self.assertEqual(secret.is_favorite, 1)
    
    def test_access_count_increment(self):
        """Test that access count increments."""
        secret = frappe.get_doc({
            "doctype": "Vault Secret",
            "title": "Test Access Count Secret",
            "secret_type": "Password",
            "password": "test123"
        })
        secret.insert()
        
        initial_count = secret.access_count or 0
        secret.update_access_metadata()
        
        secret.reload()
        self.assertEqual(secret.access_count, initial_count + 1)
    
    def test_title_required(self):
        """Test that title is required."""
        with self.assertRaises(frappe.ValidationError):
            secret = frappe.get_doc({
                "doctype": "Vault Secret",
                "title": "",
                "secret_type": "Password"
            })
            secret.insert()
    
    def test_category_link(self):
        """Test linking to a category."""
        secret = frappe.get_doc({
            "doctype": "Vault Secret",
            "title": "Test Category Link Secret",
            "secret_type": "Password",
            "password": "test123",
            "category": "Test Category"
        })
        secret.insert()
        
        self.assertEqual(secret.category, "Test Category")


class TestPasswordGenerator(FrappeTestCase):
    """Test cases for password generator utility."""
    
    def test_default_password_generation(self):
        """Test default password generation."""
        password = generate_password()
        self.assertEqual(len(password), 16)
        
        # Should have mixed characters
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        self.assertTrue(has_upper)
        self.assertTrue(has_lower)
        self.assertTrue(has_digit)
    
    def test_custom_length(self):
        """Test custom length passwords."""
        for length in [8, 12, 24, 32, 64]:
            password = generate_password(length=length)
            self.assertEqual(len(password), length)
    
    def test_exclude_ambiguous(self):
        """Test excluding ambiguous characters."""
        # Generate many passwords and check none have ambiguous chars
        ambiguous = set("0O1lI")
        for _ in range(10):
            password = generate_password(length=50, exclude_ambiguous=True)
            self.assertFalse(any(c in ambiguous for c in password))
    
    def test_no_character_types_raises_error(self):
        """Test that at least one character type is required."""
        with self.assertRaises(ValueError):
            generate_password(
                use_uppercase=False,
                use_lowercase=False,
                use_digits=False,
                use_special=False
            )
    
    def test_strength_scoring(self):
        """Test password strength scoring."""
        # Very weak
        result = calculate_password_strength("abc")
        self.assertLess(result["score"], 30)
        
        # Excellent
        result = calculate_password_strength("MyV3ry$tr0ng!P@ssw0rd#2026")
        self.assertGreaterEqual(result["score"], 90)
