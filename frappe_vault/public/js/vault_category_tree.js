// Vault Category Tree View Script
// Follows Frappe Desk UI patterns and guidelines

frappe.treeview_settings["Vault Category"] = {
    breadcrumb: "Frappe Vault",
    title: __("Vault Categories"),
    
    get_tree_root: false,
    root_label: __("All Categories"),
    
    get_tree_nodes: "frappe_vault.frappe_vault.doctype.vault_category.vault_category.get_children",
    add_tree_node: "frappe_vault.frappe_vault.doctype.vault_category.vault_category.add_node",
    
    filters: [],
    
    // Fields for new category dialog
    fields: [
        {
            fieldtype: "Data",
            fieldname: "category_name",
            label: __("Category Name"),
            reqd: 1,
            description: __("Name of the category")
        },
        {
            fieldtype: "Check",
            fieldname: "is_group",
            label: __("Is Group"),
            description: __("Check if this category can have sub-categories")
        },
        {
            fieldtype: "Column Break"
        },
        {
            fieldtype: "Icon",
            fieldname: "icon",
            label: __("Icon")
        },
        {
            fieldtype: "Color",
            fieldname: "color",
            label: __("Color"),
            description: __("Color for visual identification")
        }
    ],
    
    onload(treeview) {
        // Add primary action
        treeview.page.set_primary_action(
            __("New Category"),
            () => treeview.new_node(),
            "add"
        );
        
        // Add inner buttons
        treeview.page.add_inner_button(__("New Secret"), () => {
            frappe.new_doc("Vault Secret");
        });
        
        treeview.page.add_inner_button(__("Vault Dashboard"), () => {
            frappe.set_route("vault");
        });
    },
    
    // Custom rendering for tree nodes
    onrender(node) {
        if (!node.data) return;
        
        const $label = $(node.parent).find(".tree-label").first();
        
        // Apply custom color
        if (node.data.color) {
            $label.css({
                "border-left": `3px solid ${node.data.color}`,
                "padding-left": "8px"
            });
        }
        
        // Add secret count if available
        if (node.data.secret_count !== undefined) {
            $label.append(`
                <span class="text-muted small ml-2">(${node.data.secret_count})</span>
            `);
        }
    },
    
    // Toolbar buttons for tree nodes
    toolbar: [
        {
            label: __("View Secrets"),
            click(node) {
                frappe.route_options = { category: node.data.value };
                frappe.set_route("List", "Vault Secret");
            },
            btnClass: "btn-default btn-xs"
        }
    ],
    
    // Menu items when right-clicking nodes
    menu_items: [
        {
            group: __("Actions"),
            items: [
                {
                    label: __("New Sub-category"),
                    action(node, tree) {
                        tree.new_node();
                    },
                    condition: node => node.data.is_group || !node.data.value
                },
                {
                    label: __("View Secrets"),
                    action(node) {
                        frappe.route_options = { category: node.data.value };
                        frappe.set_route("List", "Vault Secret");
                    }
                },
                {
                    label: __("Delete"),
                    action(node, tree) {
                        frappe.confirm(
                            __("Are you sure you want to delete this category?"),
                            () => {
                                frappe.call({
                                    method: "frappe.client.delete",
                                    args: { doctype: "Vault Category", name: node.data.value },
                                    callback() {
                                        tree.load();
                                    }
                                });
                            }
                        );
                    },
                    condition: node => node.data.value
                }
            ]
        }
    ]
};
