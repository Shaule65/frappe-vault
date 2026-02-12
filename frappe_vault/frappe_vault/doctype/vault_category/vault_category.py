"""Vault Category DocType controller."""

import frappe
from frappe.utils.nestedset import NestedSet


class VaultCategory(NestedSet):
    """Controller for Vault Category - a tree-based DocType for organizing secrets."""
    
    nsm_parent_field = "parent_vault_category"
    
    def validate(self):
        """Validate the category."""
        if self.category_name:
            self.category_name = self.category_name.strip()
    
    def on_update(self):
        """Handle post-update tasks."""
        super().on_update()
    
    def on_trash(self):
        """Handle deletion - check for linked secrets."""
        # Check if any secrets are using this category
        secrets_count = frappe.db.count("Vault Secret", {"category": self.name})
        if secrets_count > 0:
            frappe.throw(
                f"Cannot delete category '{self.name}' as it has {secrets_count} secret(s) linked to it. "
                "Please move or delete the secrets first."
            )
        super().on_trash()


@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False):
    """Get children for tree view.
    
    Args:
        doctype: The DocType name
        parent: Parent category name
        is_root: Whether this is the root level
        
    Returns:
        list of category dicts
    """
    filters = {}
    
    if parent and not is_root:
        filters["parent_vault_category"] = parent
    else:
        filters["parent_vault_category"] = ("is", "not set")
    
    categories = frappe.get_all(
        "Vault Category",
        filters=filters,
        fields=["name as value", "category_name", "is_group", "icon", "color", "parent_vault_category"],
        order_by="category_name"
    )
    
    # Add secrets count for each category
    for cat in categories:
        cat["expandable"] = cat.get("is_group", 0)
        secrets_count = frappe.db.count("Vault Secret", {"category": cat["value"]})
        cat["secrets_count"] = secrets_count
    
    return categories


@frappe.whitelist()
def add_node():
    """Add a new category node.
    
    Returns:
        The created category document
    """
    from frappe.desk.treeview import make_tree_args
    
    args = frappe.form_dict
    args = make_tree_args(**args)
    
    if args.get("is_root"):
        args["parent_vault_category"] = None
    
    doc = frappe.get_doc({
        "doctype": "Vault Category",
        "category_name": args.get("category_name"),
        "parent_vault_category": args.get("parent"),
        "is_group": args.get("is_group", 0),
        "icon": args.get("icon"),
        "color": args.get("color"),
    })
    doc.insert()
    
    return doc
