# -*- coding: utf-8 -*-
import frappe

def migrate_favorites():
    print("--- STARTING FAVORITES MIGRATION ---")
    
    # 1. Find all secrets with is_favorite = 1
    secrets = frappe.get_all("Vault Secret", filters={"is_favorite": 1}, fields=["name", "owner"])
    
    migrated_count = 0
    for s in secrets:
        # Create Vault Favorite if it doesn't exist for the owner
        if not frappe.db.exists("Vault Favorite", {"user": s.owner, "secret": s.name}):
            fav = frappe.get_doc({
                "doctype": "Vault Favorite",
                "user": s.owner,
                "secret": s.name,
                "owner": s.owner
            })
            fav.insert(ignore_permissions=True)
            migrated_count += 1
            print(f"Migrated favorite: Secret {s.name} for User {s.owner}")
            
    frappe.db.commit()
    print(f"--- MIGRATION COMPLETED: Migrated {migrated_count} records ---")
