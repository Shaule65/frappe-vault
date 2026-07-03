import frappe

no_cache = 1
login_required = False


def get_context(context):
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()

    user_info = (
        frappe.db.get_value(
            "User",
            frappe.session.user,
            ["full_name", "user_image"],
            as_dict=True,
        )
        or {}
    )
    context.boot = frappe._dict(
        frappe=frappe._dict(
            csrf_token=csrf_token,
            boot=frappe._dict(
                user=frappe._dict(
                    name=frappe.session.user,
                    full_name=user_info.get("full_name") or frappe.session.user,
                    image=user_info.get("user_image"),
                    roles=frappe.get_roles(),
                ),
                site_name=frappe.local.site,
            ),
        ),
        csrf_token=csrf_token,
    )

    return context
