import frappe


def after_install():
    """Run after app installation."""
    create_default_categories()
    create_vault_roles()


def create_default_categories():
    """Create default vault categories."""
    categories = [
        {"category_name": "General", "is_group": 1},
        {"category_name": "Social Media", "parent_vault_category": "General", "is_group": 0},
        {"category_name": "Banking", "parent_vault_category": "General", "is_group": 0},
        {"category_name": "Server SSH", "parent_vault_category": "General", "is_group": 0},
        {"category_name": "API Keys", "parent_vault_category": "General", "is_group": 0},
        {"category_name": "Work", "is_group": 1},
        {"category_name": "Personal", "is_group": 1},
    ]
    
    for cat in categories:
        if not frappe.db.exists("Vault Category", cat.get("category_name")):
            doc = frappe.get_doc({
                "doctype": "Vault Category",
                **cat
            })
            doc.insert(ignore_permissions=True)
    
    frappe.db.commit()


def create_vault_roles():
    """Create vault-specific roles if they don't exist."""
    roles = [
        {"role_name": "Vault User", "desk_access": 1},
        {"role_name": "Vault Manager", "desk_access": 1},
    ]
    
    for role in roles:
        if not frappe.db.exists("Role", role.get("role_name")):
            doc = frappe.get_doc({
                "doctype": "Role",
                **role
            })
            doc.insert(ignore_permissions=True)
    
    frappe.db.commit()
