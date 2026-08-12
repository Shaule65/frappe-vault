"""Notification service — handles creating and reading Notification Logs for Frappe Vault."""

import frappe
from frappe import _


def send_vault_notification(
    for_user: str,
    subject: str,
    email_content: str = "",
    notification_type: str = "Share",
    document_type: str = "Vault Secret",
    document_name: str = None,
    from_user: str = None,
):
    """Create a Notification Log record so notifications appear in Frappe Desk and Vault frontend.

    Args:
        for_user: User receiving the notification
        subject: Title/summary of notification
        email_content: Additional details
        notification_type: Type ("Share", "Alert", "Mention", etc.)
        document_type: Target DocType ("Vault Secret", "Vault Share", etc.)
        document_name: Target document name
        from_user: Sender user (defaults to current session user)
    """
    if not for_user or for_user == "Guest":
        return None

    if not from_user:
        from_user = frappe.session.user if frappe.session and frappe.session.user else "Administrator"

    try:
        notification = frappe.get_doc(
            {
                "doctype": "Notification Log",
                "subject": subject,
                "email_content": email_content or subject,
                "for_user": for_user,
                "from_user": from_user,
                "type": notification_type,
                "document_type": document_type,
                "document_name": document_name,
                "read": 0,
            }
        )
        notification.insert(ignore_permissions=True)

        # Real-time push notification
        frappe.publish_realtime("vault_notification", user=for_user)

        return notification.name
    except Exception as e:
        frappe.log_error(
            f"Failed to create Vault notification for {for_user}: {str(e)}", "Vault Notification"
        )
        return None


def get_vault_admins() -> list:
    """Return list of user IDs who have Vault Admin role."""
    roles = ["Vault Admin"]
    user_roles = frappe.get_all(
        "Has Role", filters={"role": ["in", roles], "parenttype": "User"}, pluck="parent"
    )
    # Exclude current session user and system users
    admins = set(user_roles) - {frappe.session.user, "Guest"}
    return list(admins)


def notify_vault_admins(
    subject: str, email_content: str, document_type: str = "Vault Secret", document_name: str = None
):
    """Send notification to all Vault Admins except current actor."""
    admins = get_vault_admins()
    for admin_user in admins:
        send_vault_notification(
            for_user=admin_user,
            subject=subject,
            email_content=email_content,
            notification_type="Alert",
            document_type=document_type,
            document_name=document_name,
            from_user=frappe.session.user,
        )


def get_user_notifications(limit: int = 20) -> dict:
    """Fetch notifications for current user with unread count."""
    user = frappe.session.user
    if not user or user == "Guest":
        return {"notifications": [], "unread_count": 0}

    logs = frappe.get_all(
        "Notification Log",
        filters={"for_user": user},
        fields=[
            "name",
            "subject",
            "email_content",
            "type",
            "document_type",
            "document_name",
            "read",
            "from_user",
            "creation",
        ],
        order_by="creation desc",
        limit=int(limit),
    )

    user_names = {}
    from_users = {log["from_user"] for log in logs if log.get("from_user")}
    if from_users:
        user_docs = frappe.get_all(
            "User", filters={"name": ["in", list(from_users)]}, fields=["name", "full_name"]
        )
        for u in user_docs:
            user_names[u["name"]] = u.get("full_name") or u["name"]

    for log in logs:
        log["from_user_full_name"] = user_names.get(log.get("from_user"), log.get("from_user") or "System")
        log["creation"] = str(log["creation"])

    unread_count = frappe.db.count("Notification Log", filters={"for_user": user, "read": 0})

    return {"notifications": logs, "unread_count": unread_count}


def mark_notification_as_read(docname: str) -> dict:
    """Mark a notification as read."""
    if not docname:
        return {"success": False}

    doc = frappe.get_doc("Notification Log", docname)
    if doc.for_user != frappe.session.user and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    doc.read = 1
    doc.save(ignore_permissions=True)
    return {"success": True, "name": docname}


def mark_all_notifications_as_read() -> dict:
    """Mark all notifications as read for current user."""
    user = frappe.session.user
    unread_docs = frappe.get_all("Notification Log", filters={"for_user": user, "read": 0}, pluck="name")
    if unread_docs:
        frappe.db.set_value(
            "Notification Log", {"name": ["in", unread_docs]}, "read", 1, update_modified=False
        )
        frappe.db.commit()  # nosemgrep
    return {"success": True, "marked_count": len(unread_docs)}
