import frappe

no_cache = 1
login_required = False

def get_context(context):
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()  
    
    context.csrf_token = csrf_token
    
    user_info = frappe.db.get_value("User", frappe.session.user, ["full_name", "user_image"], as_dict=True) or {}
    context.boot = frappe._dict(
        user=frappe._dict(
            name=frappe.session.user,
            full_name=user_info.get("full_name") or frappe.session.user,
            image=user_info.get("user_image")
        ),
        site_name=frappe.local.site
    )
    
        # Check if we should use the dev server or built assets.
    # Automatically fallback to production assets if Vite dev server is offline.
    context.is_dev_mode = False
    if getattr(frappe.conf, "developer_mode", 0):
        import socket
        try:
            with socket.create_connection(("127.0.0.1", 8080), timeout=0.1):
                context.is_dev_mode = True
        except OSError:
            pass
    
    return context
