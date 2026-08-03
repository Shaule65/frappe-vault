"""Hourly one-time link cleanup."""

import frappe
from frappe.utils import now_datetime


def cleanup_expired_links():
    """Mark expired one-time links as consumed."""
    frappe.db.sql(
        """
        UPDATE `tabVault One Time Link`
        SET is_consumed = 1
        WHERE is_consumed = 0
        AND (expires_at < %s OR view_count >= max_views)
    """,
        (now_datetime(),),
    )
    frappe.db.commit()  # nosemgrep
