import frappe
from frappe_vault.utils.permissions import get_secret_permission_query
from frappe_vault.services.secret_service import get_secrets

def run():
    user = "chandayogesh123@gmail.com"
    print("\n================ DIAGNOSTIC REPORT FOR USER: chandayogesh123@gmail.com ================")
    
    # 1. Check roles in database
    roles = frappe.get_roles(user)
    print(f"Active Roles in DB: {roles}")
    
    # 2. Check permission query generated
    query_cond = get_secret_permission_query(user)
    print(f"\nGenerated Permission Query SQL Condition:\n{query_cond}")
    
    # 3. Check what secrets get_secrets returns and the generated SQL
    frappe.set_user(user)
    has_perm = frappe.has_permission("Vault Secret", "read")
    print(f"\nDoes user have read permission in general? {has_perm}")
    
    secrets = frappe.get_list("Vault Secret", fields=["name", "title", "owner"])
    print(f"\nLast SQL Query Executed for frappe.get_list:\n{frappe.db.last_query}")
    
    print(f"\nSecrets fetched for yogesh (Count: {len(secrets)}):")
    for s in secrets:
        print(f" - {s.name} | Title: {s.title} | Owner: {s.owner}")
    
    print("===================================================================\n")
