"""Rotating a Linux account across one or many machines.

Nothing here contacts a real host — reaching live machines over SSH is manual
territory. What is covered is everything that decides *whether* and *how* a run
would be made: which hosts are in the inventory, that the automation credential
cannot be the account being rotated, that the secret never reaches a command
line, and that a partial failure is treated as a failure.
"""

import json
import os

import frappe
from frappe.tests.utils import FrappeTestCase

from frappe_vault.services.linux_rotation_service import (
    KEY_AUTH,
    PASSWORD_AUTH,
    HostOutcome,
    LinuxApplyError,
    RunResult,
    _build_env,
    _build_inventory,
    _normalise_hosts,
    _parse_result,
    build_linux_target,
    hash_password,
    make_linux_target,
)
from frappe_vault.vault.doctype.vault_secret.vault_secret import (
    ROTATABLE_FIELD_BY_TYPE,
    SYNCED_TYPES,
)

TEST_TITLES = ["Linux Rotation Secret", "Linux Rotation Bulk Secret", "Linux Rotation Invalid Secret"]

FAKE_KEY = "-----BEGIN OPENSSH PRIVATE KEY-----\nfakekeymaterial\n-----END OPENSSH PRIVATE KEY-----"


def make_linux_secret(**kwargs):
    hosts = kwargs.pop("hosts", [{"hostname": "vm1.example", "ssh_port": 22}])
    doc = frappe.get_doc(
        {
            "doctype": "Vault Secret",
            "secret_type": "Linux Server",
            "username": "svc_account",
            "password": "InitialLinuxPassword123!",
            "ansible_user": "automation",
            "ansible_auth_method": KEY_AUTH,
            "ansible_ssh_private_key": FAKE_KEY,
            "linux_hosts": hosts,
            **kwargs,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc


def make_target(**kwargs):
    base = dict(
        username="svc_account",
        hosts=[{"hostname": "vm1.example", "ssh_port": 22}],
        ansible_user="automation",
        auth_method=KEY_AUTH,
        ssh_private_key=FAKE_KEY,
    )
    base.update(kwargs)
    return make_linux_target(**base)


class TestLinuxTarget(FrappeTestCase):
    def setUp(self):
        self.cleanup()

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        for name in frappe.get_all("Vault Secret", filters={"title": ["in", TEST_TITLES]}, pluck="name"):
            frappe.db.delete("Vault Audit Log", {"secret": name})
            frappe.delete_doc("Vault Secret", name, force=True, ignore_permissions=True)
        frappe.db.commit()  # nosemgrep — fixtures must not survive on this site

    # ------------------------------------------------------------------
    # Which field rotates
    # ------------------------------------------------------------------

    def test_linux_secret_rotates_the_password_field(self):
        doc = make_linux_secret(title="Linux Rotation Secret")
        self.assertEqual(doc.rotating_field, "password")
        self.assertEqual(ROTATABLE_FIELD_BY_TYPE["Linux Server"], "password")

    def test_linux_is_a_synced_type(self):
        self.assertIn("Linux Server", SYNCED_TYPES)

    # ------------------------------------------------------------------
    # Inventory: one VM or many
    # ------------------------------------------------------------------

    def test_a_single_host_is_valid(self):
        target = make_target()
        self.assertEqual(len(target.hosts), 1)

    def test_many_hosts_are_carried_together(self):
        target = make_target(
            hosts=[{"hostname": f"vm{i}.example", "ssh_port": 22} for i in range(1, 21)]
        )
        self.assertEqual(len(target.hosts), 20)
        self.assertIn("+17 more", target.describe())

    def test_duplicate_hosts_are_collapsed(self):
        hosts = _normalise_hosts(
            [{"hostname": "vm1"}, {"hostname": " vm1 "}, {"hostname": "vm2"}, {"hostname": ""}], 22
        )
        self.assertEqual([h["hostname"] for h in hosts], ["vm1", "vm2"])

    def test_per_host_port_overrides_the_default(self):
        hosts = _normalise_hosts([{"hostname": "vm1", "ssh_port": 2222}, {"hostname": "vm2"}], 22)
        self.assertEqual(hosts[0]["ssh_port"], 2222)
        self.assertEqual(hosts[1]["ssh_port"], 22)

    def test_an_empty_inventory_is_refused(self):
        with self.assertRaises(LinuxApplyError):
            make_target(hosts=[])

    def test_a_secret_without_hosts_cannot_be_saved(self):
        with self.assertRaises(frappe.ValidationError):
            make_linux_secret(title="Linux Rotation Invalid Secret", hosts=[])

    # ------------------------------------------------------------------
    # The automation credential
    # ------------------------------------------------------------------

    def test_the_ansible_user_may_not_be_the_rotated_account(self):
        # Rotating the account Ansible logs in as would work exactly once.
        with self.assertRaises(LinuxApplyError):
            make_target(ansible_user="svc_account")

    def test_that_rule_is_enforced_at_save_time_too(self):
        with self.assertRaises(frappe.ValidationError):
            make_linux_secret(title="Linux Rotation Invalid Secret", ansible_user="svc_account")

    def test_key_auth_requires_a_key(self):
        with self.assertRaises(LinuxApplyError):
            make_target(auth_method=KEY_AUTH, ssh_private_key="")

    def test_password_auth_requires_a_password(self):
        with self.assertRaises(LinuxApplyError):
            make_target(auth_method=PASSWORD_AUTH, ssh_private_key=None, ansible_password="")

    def test_an_unknown_auth_method_is_refused(self):
        with self.assertRaises(LinuxApplyError):
            make_target(auth_method="Kerberos")

    def test_a_saved_secret_resolves_into_a_target(self):
        doc = make_linux_secret(
            title="Linux Rotation Bulk Secret",
            hosts=[{"hostname": "vm1.example"}, {"hostname": "vm2.example", "ssh_port": 2222}],
        )
        target = build_linux_target(doc)

        self.assertEqual(target.username, "svc_account")
        self.assertEqual(target.ansible_user, "automation")
        self.assertEqual({h["hostname"] for h in target.hosts}, {"vm1.example", "vm2.example"})

    # ------------------------------------------------------------------
    # Hashing — ansible.builtin.user will not take plaintext
    # ------------------------------------------------------------------

    def test_password_is_hashed_as_sha512_crypt(self):
        from passlib.hash import sha512_crypt

        hashed = hash_password("SomePassword123!")
        self.assertTrue(hashed.startswith("$6$"))
        self.assertTrue(sha512_crypt.verify("SomePassword123!", hashed))

    def test_the_hash_is_salted(self):
        self.assertNotEqual(hash_password("same"), hash_password("same"))

    # ------------------------------------------------------------------
    # Nothing sensitive on a command line or in a description
    # ------------------------------------------------------------------

    def test_describe_names_hosts_without_leaking_credentials(self):
        target = make_target(ansible_password="SuperSecret", auth_method=PASSWORD_AUTH, ssh_private_key=None)
        described = target.describe()

        self.assertIn("vm1.example", described)
        self.assertNotIn("SuperSecret", described)

    def test_connection_secrets_live_in_the_inventory_not_the_argv(self):
        import tempfile

        workdir = tempfile.mkdtemp()
        try:
            target = make_target(
                auth_method=PASSWORD_AUTH,
                ssh_private_key=None,
                ansible_password="SshSecret123",
                become_password="SudoSecret123",
            )
            inventory = _build_inventory(target, workdir)

            # Present in the 0600 inventory file...
            self.assertIn("SshSecret123", inventory)
            self.assertIn("SudoSecret123", inventory)
            # ...and the environment carries none of it.
            self.assertNotIn("SshSecret123", json.dumps(_build_env(target, workdir)))
        finally:
            import shutil

            shutil.rmtree(workdir, ignore_errors=True)

    def test_the_private_key_file_is_not_world_readable(self):
        import shutil
        import tempfile

        workdir = tempfile.mkdtemp()
        try:
            _build_inventory(make_target(), workdir)
            mode = os.stat(os.path.join(workdir, "id_key")).st_mode & 0o777
            self.assertEqual(mode, 0o600)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    def test_host_key_checking_is_on_by_default(self):
        env = _build_env(make_target(), "/tmp")
        self.assertEqual(env["ANSIBLE_HOST_KEY_CHECKING"], "True")

    def test_host_key_checking_can_be_turned_off_deliberately(self):
        env = _build_env(make_target(strict_host_key_checking=False), "/tmp")
        self.assertEqual(env["ANSIBLE_HOST_KEY_CHECKING"], "False")

    # ------------------------------------------------------------------
    # Reading Ansible's report
    # ------------------------------------------------------------------

    def _completed(self, stdout, stderr="", code=0):
        class Completed:
            pass

        c = Completed()
        c.stdout, c.stderr, c.returncode = stdout, stderr, code
        return c

    def test_a_clean_run_marks_every_host_ok(self):
        target = make_target(hosts=[{"hostname": "vm1"}, {"hostname": "vm2"}])
        report = {"stats": {"vm1": {"ok": 1, "failures": 0}, "vm2": {"ok": 1, "failures": 0}}, "plays": []}

        result = _parse_result(target, self._completed(json.dumps(report)))
        self.assertTrue(result.all_ok)

    def test_one_bad_host_makes_the_whole_run_a_failure(self):
        target = make_target(hosts=[{"hostname": "vm1"}, {"hostname": "vm2"}])
        report = {
            "stats": {"vm1": {"ok": 1, "failures": 0}, "vm2": {"ok": 0, "failures": 1}},
            "plays": [
                {
                    "tasks": [
                        {"hosts": {"vm2": {"failed": True, "msg": "sudo: a password is required"}}}
                    ]
                }
            ],
        }

        result = _parse_result(target, self._completed(json.dumps(report)))

        self.assertFalse(result.all_ok)
        self.assertEqual([o.hostname for o in result.failed], ["vm2"])
        self.assertEqual([o.hostname for o in result.succeeded], ["vm1"])
        self.assertIn("sudo", result.summary())

    def test_an_unreachable_host_is_a_failure(self):
        target = make_target(hosts=[{"hostname": "vm1"}])
        report = {"stats": {"vm1": {"ok": 0, "unreachable": 1}}, "plays": []}

        self.assertFalse(_parse_result(target, self._completed(json.dumps(report))).all_ok)

    def test_unparseable_output_is_reported_rather_than_assumed_fine(self):
        target = make_target()
        with self.assertRaises(LinuxApplyError):
            _parse_result(target, self._completed("not json at all", stderr="ERROR! bad inventory"))

    def test_contacting_no_hosts_is_not_treated_as_success(self):
        target = make_target()
        with self.assertRaises(LinuxApplyError):
            _parse_result(target, self._completed(json.dumps({"stats": {}})))

    def test_summary_counts_only_the_failures(self):
        result = RunResult(
            outcomes=[
                HostOutcome("vm1", True),
                HostOutcome("vm2", False, "connection refused"),
                HostOutcome("vm3", False, "permission denied"),
            ]
        )
        self.assertIn("2 of 3", result.summary())
