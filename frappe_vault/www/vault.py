import frappe

no_cache = 1
login_required = False

def get_context(context):
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()  
    
    context.csrf_token = csrf_token
    context.boot = frappe._dict(
        user=frappe.session.user,
        site_name=frappe.local.site
    )
    
    # Check if we should use the dev server or built assets.
    # If developer_mode is 1, Frappe defaults to dev server for UI.
    context.is_dev_mode = getattr(frappe.conf, "developer_mode", 0)
    
    return context
