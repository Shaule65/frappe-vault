import frappe
from frappe.tests.utils import FrappeTestCase

from frappe_vault.services.notification_service import (
    get_user_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
    send_vault_notification,
)
from frappe_vault.services.secret_service import create_secret
from frappe_vault.services.sharing_service import share_secret, unshare


class TestNotifications(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("Notification Log", {"for_user": "Administrator"})
        frappe.db.delete("Vault Secret", {"title": "Notification Test Secret"})
        frappe.db.commit()

    def tearDown(self):
        frappe.db.delete("Notification Log", {"for_user": "Administrator"})
        frappe.db.delete("Vault Secret", {"title": "Notification Test Secret"})
        frappe.db.commit()

    def test_send_and_get_notifications(self):
        # Create a notification directly
        notif_name = send_vault_notification(
            for_user="Administrator",
            subject="Test Vault Alert",
            email_content="Testing notification creation",
            notification_type="Alert",
            document_type="Vault Secret",
        )
        self.assertTrue(notif_name)

        # Get notifications
        res = get_user_notifications()
        self.assertGreaterEqual(res["unread_count"], 1)
        self.assertTrue(any(n["name"] == notif_name for n in res["notifications"]))

        # Mark as read
        read_res = mark_notification_as_read(notif_name)
        self.assertTrue(read_res["success"])

        # Mark all as read
        all_read_res = mark_all_notifications_as_read()
        self.assertIn("marked_count", all_read_res)

    def test_sharing_triggers_notification(self):
        if not frappe.db.exists("User", "test_user_vault@example.com"):
            user_doc = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": "test_user_vault@example.com",
                    "first_name": "Test",
                    "send_welcome_email": 0,
                }
            )
            user_doc.insert(ignore_permissions=True)

        secret = create_secret(
            {"title": "Notification Test Secret", "secret_type": "Password", "password": "secretpassword123"}
        )

        share_res = share_secret(
            shared_name=secret["name"],
            shared_doctype="Vault Secret",
            share_type="User",
            user="test_user_vault@example.com",
            permission_level="View Only",
        )
        self.assertTrue(share_res.get("name"))

        notifications = frappe.get_all(
            "Notification Log", filters={"for_user": "test_user_vault@example.com"}
        )
        self.assertTrue(len(notifications) > 0)

        unshare_res = unshare(share_res["name"])
        self.assertEqual(unshare_res.get("removed"), share_res["name"])

        revocation_notifs = frappe.get_all(
            "Notification Log", filters={"for_user": "test_user_vault@example.com", "type": "Alert"}
        )
        self.assertTrue(len(revocation_notifs) > 0)
