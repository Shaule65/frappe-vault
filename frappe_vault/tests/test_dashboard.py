import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate
from frappe_vault.api.dashboard import get_vault_dashboard
from frappe_vault.services.secret_service import create_secret


class TestVaultDashboard(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("Vault Secret", {"title": "Dashboard Test Secret"})
        frappe.db.commit()

    def tearDown(self):
        frappe.db.delete("Vault Secret", {"title": "Dashboard Test Secret"})
        frappe.db.commit()

    def test_get_vault_dashboard_with_date_range(self):
        today_str = nowdate()
        from_date = str(add_days(today_str, -7))
        to_date = today_str

        # Create a test secret
        secret = create_secret({
            "title": "Dashboard Test Secret",
            "secret_type": "Password",
            "password": "dashboardpass123"
        })
        self.assertTrue(secret.get("name"))

        # Fetch dashboard layout data
        res = get_vault_dashboard(from_date=from_date, to_date=to_date)
        self.assertIsInstance(res, list)
        self.assertGreaterEqual(len(res), 4)

        # Check total secrets chart item
        total_secrets_item = next((item for item in res if item.get("name") == "total_secrets"), None)
        self.assertIsNotNone(total_secrets_item)
        self.assertEqual(total_secrets_item["type"], "number_chart")
        self.assertIn("value", total_secrets_item["data"])

        # Check vault trend chart item
        vault_trend_item = next((item for item in res if item.get("name") == "vault_trend"), None)
        self.assertIsNotNone(vault_trend_item)
        self.assertEqual(vault_trend_item["type"], "axis_chart")
        self.assertIn("data", vault_trend_item["data"])

        # Check secrets by folder chart item
        folder_item = next((item for item in res if item.get("name") == "secrets_by_folder"), None)
        self.assertIsNotNone(folder_item)
        self.assertEqual(folder_item["type"], "donut_chart")
        self.assertIn("categoryColumn", folder_item["data"])
