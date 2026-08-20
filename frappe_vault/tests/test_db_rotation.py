"""Rotation of Database secrets, and the target-apply configuration around it.

Nothing here contacts a real database server — the engine handlers are exercised
against live servers only in manual testing. What is covered is everything that
decides *whether* and *how* a connection would be made: which field rotates,
which configurations are allowed to be saved at all, and how a Vault Secret
resolves into a connection target.
"""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from frappe_vault.services.db_rotation_service import (
    DEFAULT_PORTS,
    MONGODB,
    MYSQL,
    POSTGRESQL,
    TargetApplyError,
    build_target,
    describe,
)
from frappe_vault.vault.doctype.vault_secret.vault_secret import ROTATABLE_FIELD_BY_TYPE

TEST_TITLES = [
    "DB Rotation Postgres Secret",
    "DB Rotation MySQL Secret",
    "DB Rotation Mongo Secret",
    "DB Rotation Admin Secret",
    "DB Rotation Due Secret",
    "DB Rotation Invalid Secret",
    "DB Rotation History Secret",
]


def make_db_secret(**kwargs):
    """Create a Database Vault Secret with sane defaults for these tests."""
    doc = frappe.get_doc(
        {
            "doctype": "Vault Secret",
            "secret_type": "Database",
            "database_type": POSTGRESQL,
            "db_host": "db.internal.example",
            "db_name": "appdb",
            "username": "app_user",
            "db_password": "InitialDbPassword123!",
            **kwargs,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc


class TestDatabaseRotation(FrappeTestCase):
    def setUp(self):
        self.cleanup()

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        # This site's tests run against the live DB, so fixtures must not
        # survive the run.
        names = frappe.get_all("Vault Secret", filters={"title": ["in", TEST_TITLES]}, pluck="name")
        for name in names:
            frappe.db.delete("Vault Share", {"shared_name": name})
            frappe.db.delete("Vault Audit Log", {"secret": name})
            frappe.delete_doc("Vault Secret", name, force=True, ignore_permissions=True)

        # One test commits so the due-secret query can see its fixture. The test
        # case rolls back afterwards, which would take this delete with it — so
        # commit the cleanup too, or that fixture outlives the run.
        frappe.db.commit()  # nosemgrep — test fixtures must not survive on this site

    # ------------------------------------------------------------------
    # Which field rotates
    # ------------------------------------------------------------------

    def test_database_secret_rotates_its_db_password(self):
        doc = make_db_secret(title="DB Rotation Postgres Secret")
        self.assertEqual(doc.rotating_field, "db_password")

    def test_password_secret_still_rotates_its_password(self):
        self.assertEqual(ROTATABLE_FIELD_BY_TYPE["Password"], "password")

    def test_unrotatable_type_has_no_rotating_field(self):
        doc = frappe.get_doc({"doctype": "Vault Secret", "title": "x", "secret_type": "API Key"})
        self.assertIsNone(doc.rotating_field)

    # ------------------------------------------------------------------
    # Rotation schedule
    # ------------------------------------------------------------------

    def test_database_secret_may_enable_rotation(self):
        doc = make_db_secret(
            title="DB Rotation Postgres Secret",
            enable_rotation=1,
            rotation_interval=30,
            rotation_unit="Days",
        )
        self.assertIsNotNone(doc.next_rotation_on)

    def test_due_query_includes_database_secrets(self):
        due = make_db_secret(
            title="DB Rotation Due Secret",
            enable_rotation=1,
            rotation_interval=1,
            rotation_unit="Hours",
        )
        frappe.db.set_value(
            "Vault Secret", due.name, "next_rotation_on", add_to_date(now_datetime(), hours=-2)
        )
        frappe.db.commit()

        selected = frappe.get_all(
            "Vault Secret",
            filters={
                "enable_rotation": 1,
                "secret_type": ["in", sorted(ROTATABLE_FIELD_BY_TYPE)],
                "next_rotation_on": ["<=", now_datetime()],
                "title": ["in", TEST_TITLES],
            },
            pluck="name",
        )
        self.assertIn(due.name, selected)

    # ------------------------------------------------------------------
    # History and the reuse policy follow the rotating field
    # ------------------------------------------------------------------

    def test_history_is_recorded_for_db_password(self):
        doc = make_db_secret(title="DB Rotation History Secret")
        self.assertEqual(len(doc.password_history), 1)
        self.assertTrue(doc.password_history[0].password_hash)

    def test_is_password_reused_matches_a_previous_db_password(self):
        doc = make_db_secret(title="DB Rotation History Secret")
        self.assertTrue(doc.is_password_reused("InitialDbPassword123!", reuse_count=5))
        self.assertFalse(doc.is_password_reused("SomethingCompletelyElse456!", reuse_count=5))

    def test_reuse_check_is_off_when_the_policy_allows_zero(self):
        doc = make_db_secret(title="DB Rotation History Secret")
        self.assertFalse(doc.is_password_reused("InitialDbPassword123!", reuse_count=0))

    # ------------------------------------------------------------------
    # Target-apply configuration
    # ------------------------------------------------------------------

    def test_apply_to_target_requires_a_database_type(self):
        with self.assertRaises(frappe.ValidationError):
            make_db_secret(
                title="DB Rotation Invalid Secret",
                database_type=None,
                enable_rotation=1,
                rotation_interval=30,
                rotation_unit="Days",
                apply_rotation_to_target=1,
            )

    def test_apply_to_target_requires_a_username(self):
        with self.assertRaises(frappe.ValidationError):
            make_db_secret(
                title="DB Rotation Invalid Secret",
                username=None,
                enable_rotation=1,
                rotation_interval=30,
                rotation_unit="Days",
                apply_rotation_to_target=1,
            )

    def test_apply_to_target_requires_an_admin_password_alongside_an_admin_user(self):
        with self.assertRaises(frappe.ValidationError):
            make_db_secret(
                title="DB Rotation Invalid Secret",
                enable_rotation=1,
                rotation_interval=30,
                rotation_unit="Days",
                apply_rotation_to_target=1,
                rotation_admin_username="postgres",
            )

    def test_apply_to_target_is_cleared_when_rotation_is_disabled(self):
        doc = make_db_secret(
            title="DB Rotation Postgres Secret",
            enable_rotation=1,
            rotation_interval=30,
            rotation_unit="Days",
            apply_rotation_to_target=1,
        )
        doc.enable_rotation = 0
        doc.save(ignore_permissions=True)
        self.assertFalse(doc.apply_rotation_to_target)

    def test_dropping_the_admin_username_drops_its_password(self):
        doc = make_db_secret(
            title="DB Rotation Admin Secret",
            enable_rotation=1,
            rotation_interval=30,
            rotation_unit="Days",
            apply_rotation_to_target=1,
            rotation_admin_username="postgres",
            rotation_admin_password="AdminPassword123!",
        )
        self.assertTrue(doc.get_password("rotation_admin_password", raise_exception=False))

        doc.rotation_admin_username = ""
        doc.save(ignore_permissions=True)

        self.assertFalse(doc.rotation_admin_username)
        self.assertFalse(doc.get_password("rotation_admin_password", raise_exception=False))

    # ------------------------------------------------------------------
    # Resolving a secret into a connection target
    # ------------------------------------------------------------------

    def test_target_defaults_the_port_per_engine(self):
        for engine in (POSTGRESQL, MYSQL, MONGODB):
            doc = make_db_secret(title="DB Rotation Postgres Secret", database_type=engine, db_port=None)
            target = build_target(doc, "InitialDbPassword123!")
            self.assertEqual(target.port, DEFAULT_PORTS[engine])
            self.cleanup()

    def test_target_keeps_an_explicit_port(self):
        doc = make_db_secret(title="DB Rotation Postgres Secret", db_port=6543)
        target = build_target(doc, "InitialDbPassword123!")
        self.assertEqual(target.port, 6543)

    def test_target_authenticates_as_the_account_itself_by_default(self):
        doc = make_db_secret(title="DB Rotation Postgres Secret")
        target = build_target(doc, "InitialDbPassword123!")

        self.assertFalse(target.via_admin)
        self.assertEqual(target.auth_username, "app_user")
        self.assertEqual(target.auth_password, "InitialDbPassword123!")

    def test_target_prefers_the_rotation_admin_when_one_is_set(self):
        doc = make_db_secret(
            title="DB Rotation Admin Secret",
            enable_rotation=1,
            rotation_interval=30,
            rotation_unit="Days",
            apply_rotation_to_target=1,
            rotation_admin_username="postgres",
            rotation_admin_password="AdminPassword123!",
        )
        target = build_target(doc, "InitialDbPassword123!")

        self.assertTrue(target.via_admin)
        self.assertEqual(target.auth_username, "postgres")
        self.assertEqual(target.auth_password, "AdminPassword123!")
        # The account being *changed* is still the secret's own user.
        self.assertEqual(target.username, "app_user")

    def test_target_defaults_the_mongo_auth_source(self):
        doc = make_db_secret(
            title="DB Rotation Mongo Secret", database_type=MONGODB, db_auth_source=None
        )
        target = build_target(doc, "InitialDbPassword123!")
        self.assertEqual(target.auth_source, "admin")

    def test_target_rejects_an_unsupported_engine(self):
        doc = make_db_secret(title="DB Rotation Invalid Secret")
        doc.database_type = "Cassandra"

        with self.assertRaises(TargetApplyError):
            build_target(doc, "InitialDbPassword123!")

    def test_target_rejects_a_non_database_secret(self):
        doc = frappe.get_doc(
            {"doctype": "Vault Secret", "title": "x", "secret_type": "Password", "password": "y"}
        )
        with self.assertRaises(TargetApplyError):
            build_target(doc, "y")

    def test_target_without_any_usable_credential_is_refused(self):
        doc = make_db_secret(title="DB Rotation Invalid Secret")

        # No admin configured and no current password to authenticate with.
        with self.assertRaises(TargetApplyError):
            build_target(doc, "")

    def test_describe_names_the_server_without_leaking_a_password(self):
        doc = make_db_secret(title="DB Rotation MySQL Secret", database_type=MYSQL, db_port=3306)
        description = describe(build_target(doc, "InitialDbPassword123!"))

        self.assertIn("db.internal.example:3306", description)
        self.assertIn("app_user", description)
        self.assertNotIn("InitialDbPassword123!", description)
