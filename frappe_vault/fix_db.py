import frappe

def fix_workspace():
    # 1. Re-create the module def temporarily so ORM doesn't crash if it tries to access it
    try:
        if not frappe.db.exists("Module Def", "Frappe Vault"):
            frappe.get_doc({
                "doctype": "Module Def",
                "module_name": "Frappe Vault",
                "app_name": "frappe_vault"
            }).insert(ignore_permissions=True)
            print("Temporarily created 'Frappe Vault' module to bypass validation")
    except Exception as e:
        print("Failed creating temp module:", e)

    # 2. Use Raw SQL to forcefully delete the Workspace
    try:
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = 'Frappe Vault'")
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = 'Frappe Vault'")
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = 'Frappe Vault'")
        frappe.db.sql("DELETE FROM `tabWorkspace Chart` WHERE parent = 'Frappe Vault'")
        print("Force deleted Workspace 'Frappe Vault' via SQL")
    except Exception as e:
        print("SQL delete workspace error:", e)

    # 3. Use Raw SQL to forcefully delete the old DocTypes
    try:
        for dt in ["Vault Category", "Vault Access Log"]:
            frappe.db.sql("DELETE FROM `tabDocType` WHERE name = %s", (dt,))
            frappe.db.sql("DELETE FROM `tabDocField` WHERE parent = %s", (dt,))
            frappe.db.sql("DROP TABLE IF EXISTS `tab{}`".format(dt))
            print(f"Force deleted DocType '{dt}' via SQL")
    except Exception as e:
        print("SQL delete doctype error:", e)

    # 4. Make sure 'Vault' module is created properly
    try:
        if not frappe.db.exists("Module Def", "Vault"):
            frappe.get_doc({
                "doctype": "Module Def",
                "module_name": "Vault",
                "app_name": "frappe_vault"
            }).insert(ignore_permissions=True)
            print("Created target 'Vault' module")
    except Exception:
        pass

    frappe.db.commit()
    print("Database cleanup complete!")
