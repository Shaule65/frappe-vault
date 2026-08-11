import frappe
from frappe.tests.utils import FrappeTestCase

from frappe_vault.api.folders import create as create_folder
from frappe_vault.api.folders import delete as delete_folder
from frappe_vault.services.secret_service import create_secret
from frappe_vault.services.sharing_service import (
    get_role_users,
    get_shares_for_secret,
    share_secret,
    unshare,
    update_share_permission,
)
from frappe_vault.utils.permissions import has_folder_permission, has_secret_permission


class TestSharingService(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("Vault Secret", {"title": "Test Shared Secret"})
        frappe.db.delete("Vault Share", {"shared_name": "Test Shared Secret"})
        frappe.db.commit()

        if not frappe.db.exists("User", "test_shared_1@example.com"):
            doc = frappe.get_doc(
                {"doctype": "User", "email": "test_shared_1@example.com", "first_name": "Test Shared 1"}
            )
            doc.insert(ignore_permissions=True)
            doc.append("roles", {"role": "Vault User"})
            doc.save(ignore_permissions=True)

    def tearDown(self):
        frappe.db.delete("Vault Secret", {"title": "Test Shared Secret"})
        frappe.db.delete(
            "Vault Secret", {"title": ["in", ["Test Shared Secret 2", "Test Shared Secret 2 2"]]}
        )
        frappe.db.delete("Vault Folder", {"folder_name": "Test Shared Folder"})
        frappe.db.delete("Vault Share", {"shared_by": "test_shared_1@example.com"})
        frappe.db.commit()

    def test_share_secret_with_role(self):
        # Create a secret
        secret = create_secret({"title": "Test Shared Secret", "secret_type": "Password", "password": "pass"})

        # Share secret with Role
        share_res = share_secret(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            share_type="Role",
            frappe_role="Vault User",
            permission_level="View Only",
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

        # Test with shared_by and user_list parameters
        filtered_users = get_role_users(
            "System Manager", shared_by=frappe.session.user, user_list=["Administrator"]
        )
        self.assertIsInstance(filtered_users, list)

    def test_save_role_member_permission(self):
        from frappe_vault.services.sharing_service import save_role_member_permission

        secret = create_secret({"title": "Test Shared Secret", "secret_type": "Password", "password": "pass"})
        res = save_role_member_permission(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            user="Administrator",
            permission_level="Full Control",
            is_revoked=False,
        )
        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("permission_level"), "Full Control")

    def test_role_unshare_notifications(self):
        secret = create_secret(
            {"title": "Test Shared Secret 2", "secret_type": "Password", "password": "pass"}
        )

        # Share secret with Role
        share_res = share_secret(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            share_type="Role",
            frappe_role="Vault User",
            permission_level="View Only",
        )

        # Ensure test1@gmail.com is in Vault User role for testing
        if not frappe.db.exists("Has Role", {"parent": "test1@gmail.com", "role": "Vault User"}):
            if not frappe.db.exists("User", "test1@gmail.com"):
                doc = frappe.get_doc({"doctype": "User", "email": "test1@gmail.com", "first_name": "Test1"})
                doc.insert(ignore_permissions=True)
            user_doc = frappe.get_doc("User", "test1@gmail.com")
            user_doc.append("roles", {"role": "Vault User"})
            user_doc.save(ignore_permissions=True)

        frappe.db.delete("Notification Log", {"for_user": "test1@gmail.com"})

        # Unshare
        unshare(share_res.get("name"))

        # Check if notification was created for role member
        notifications = frappe.get_all(
            "Notification Log", filters={"for_user": "test1@gmail.com"}, order_by="creation desc"
        )
        self.assertTrue(
            len(notifications) > 0, "No notification was sent to role members when role share was revoked"
        )

    def test_get_role_users_admin_not_revoked(self):
        secret = create_secret(
            {"title": "Test Shared Secret 3", "secret_type": "Password", "password": "pass"}
        )

        # Share secret with Role
        share_res = share_secret(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            share_type="Role",
            frappe_role="System Manager",
            permission_level="View Only",
        )

        # Revoke the role share
        unshare(share_res.get("name"))

        # Administrator is the owner and also a System Manager
        frappe.set_user("Administrator")
        users = get_role_users("System Manager", shared_name=secret.get("name"))

        admin_user = next((u for u in users if u.get("user") == "Administrator"), None)
        if admin_user:
            self.assertFalse(
                admin_user.get("is_revoked"),
                "Owner/Admin should not be marked as revoked even if the role share is revoked",
            )

    def test_get_role_users_direct_share_not_revoked(self):
        secret = create_secret(
            {"title": "Test Shared Secret 4", "secret_type": "Password", "password": "pass"}
        )

        # Ensure test2@example.com is in Vault User role for testing
        if not frappe.db.exists("Has Role", {"parent": "test2@example.com", "role": "Vault User"}):
            if not frappe.db.exists("User", "test2@example.com"):
                doc = frappe.get_doc({"doctype": "User", "email": "test2@example.com", "first_name": "Test2"})
                doc.insert(ignore_permissions=True)
            user_doc = frappe.get_doc("User", "test2@example.com")
            user_doc.append("roles", {"role": "Vault User"})
            user_doc.save(ignore_permissions=True)

        # Share secret with Role
        role_share_res = share_secret(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            share_type="Role",
            frappe_role="Vault User",
            permission_level="View Only",
        )

        # Share secret directly with test2@example.com
        _user_share_res = share_secret(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            share_type="User",
            user="test2@example.com",
            permission_level="Full Control",
        )

        # Revoke the role share
        unshare(role_share_res.get("name"))

        frappe.set_user("Administrator")
        users = get_role_users("Vault User", shared_name=secret.get("name"))

        test2_user = next((u for u in users if u.get("user") == "test2@example.com"), None)
        if test2_user:
            self.assertFalse(
                test2_user.get("is_revoked"),
                "User with active direct share should not be marked as revoked even if the role share is revoked",
            )
            self.assertEqual(
                test2_user.get("permission_level"),
                "Full Control",
                "User should retain Full Control from direct share",
            )

    def test_user_creates_and_shares_secret_with_own_role(self):
        # Act as standard user
        frappe.set_user("test_shared_1@example.com")

        # User creates their own secret
        secret = create_secret(
            {"title": "Test Shared Secret 2", "secret_type": "Password", "password": "pass"}
        )
        owner = frappe.db.get_value("Vault Secret", secret.get("name"), "owner")
        self.assertEqual(owner, "test_shared_1@example.com")

        # User has permission
        self.assertTrue(has_secret_permission(secret.get("name"), "read", "test_shared_1@example.com"))

        # User shares with Vault User role (which they are a member of)
        share_res = share_secret(
            shared_name=secret.get("name"),
            shared_doctype="Vault Secret",
            share_type="Role",
            frappe_role="Vault User",
            permission_level="View Only",
        )
        self.assertTrue(share_res.get("name"))

        # In the modal, they should not be marked as revoked because they are the OWNER
        users = get_role_users("Vault User", shared_name=secret.get("name"))
        owner_in_list = next((u for u in users if u.get("user") == "test_shared_1@example.com"), None)
        self.assertIsNotNone(owner_in_list)
        self.assertFalse(owner_in_list.get("is_revoked"))
        self.assertEqual(owner_in_list.get("permission_level"), "Full Control")

        # Now user revokes the role share
        unshare(share_res.get("name"))

        # Even after revoking the role, the owner MUST retain access to their own secret
        self.assertTrue(has_secret_permission(secret.get("name"), "read", "test_shared_1@example.com"))

        # And if they check the modal again, they are still listed as Full Control (since they are Owner)
        users = get_role_users("Vault User", shared_name=secret.get("name"))
        owner_in_list = next((u for u in users if u.get("user") == "test_shared_1@example.com"), None)
        if owner_in_list:
            self.assertFalse(owner_in_list.get("is_revoked"))
            self.assertEqual(owner_in_list.get("permission_level"), "Full Control")

    def test_folder_sharing_with_standard_user(self):
        # Helper to strictly verify notifications
        def assert_notification(subject_like, for_user=None):
            filters = {"subject": ["like", f"%{subject_like}%"]}
            if for_user:
                filters["for_user"] = for_user
            logs = frappe.get_all("Notification Log", filters=filters)
            self.assertTrue(
                len(logs) > 0, f"Expected notification '{subject_like}' but it was not found in the DB."
            )

        if not frappe.db.exists("User", "test_shared_2@example.com"):
            doc = frappe.get_doc(
                {"doctype": "User", "email": "test_shared_2@example.com", "first_name": "Test Shared 2"}
            )
            doc.insert(ignore_permissions=True)
            doc.append("roles", {"role": "Vault User"})
            doc.save(ignore_permissions=True)

        frappe.set_user("test_shared_1@example.com")

        # 1. Test Folder Creation & Notification
        folder_res = create_folder(folder_name="Test Shared Folder", color="Blue", icon="folder")
        folder = frappe.get_doc("Vault Folder", folder_res.get("name"))
        assert_notification("New Folder Created", "Administrator")

        # 2. Test Secret Creation & Notification
        secret = create_secret(
            {
                "title": "Test Shared Secret 4",
                "secret_type": "Password",
                "password": "pass",
                "folder": folder.get("name"),
            }
        )
        assert_notification("New Secret Created", "Administrator")

        # 3. Share folder with standard user & Verify Notification
        share_res = share_secret(
            shared_name=folder.get("name"),
            shared_doctype="Vault Folder",
            share_type="User",
            user="test_shared_2@example.com",
            permission_level="View Only",
        )
        assert_notification("Folder Shared with You: 'Test Shared Folder'", "test_shared_2@example.com")

        # 4. Verify cascading access for standard user
        frappe.set_user("test_shared_2@example.com")
        self.assertTrue(has_folder_permission(folder.get("name"), "read", "test_shared_2@example.com"))
        self.assertTrue(has_secret_permission(secret.get("name"), "read", "test_shared_2@example.com"))
        self.assertFalse(
            has_secret_permission(secret.get("name"), "write", "test_shared_2@example.com")
        )  # They only have View Only

        # 5. Revoke the folder & Verify Notification
        frappe.set_user("test_shared_1@example.com")
        unshare(share_res.get("name"))
        assert_notification("Access Revoked", "test_shared_2@example.com")

        # 6. Standard user loses access
        frappe.set_user("test_shared_2@example.com")
        self.assertFalse(has_folder_permission(folder.get("name"), "read", "test_shared_2@example.com"))
        self.assertFalse(has_secret_permission(secret.get("name"), "read", "test_shared_2@example.com"))

        # 7. Delete Secret & Folder & Verify Notifications
        frappe.set_user("test_shared_1@example.com")
        from frappe_vault.services.secret_service import delete_secret

        delete_secret(secret.get("name"))
        assert_notification("Secret Deleted", "Administrator")

        delete_folder(folder.get("name"))
        assert_notification("Folder Deleted", "Administrator")
