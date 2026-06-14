# -*- coding: utf-8 -*-
import frappe
from frappe_vault.services.secret_service import get_secrets, toggle_favorite, get_vault_stats, get_secret
from frappe_vault.services.sharing_service import share_secret

def run():
    print("--- STARTING PER-USER FAVORITES AND COUNT VERIFICATION ---")

    # Set user to Administrator
    frappe.set_user("Administrator")
    
    # 1. Clean up old test data
    test_secret_name = "test_favorite_secret"
    if frappe.db.exists("Vault Secret", test_secret_name):
        frappe.delete_doc("Vault Secret", test_secret_name, force=True)
    
    frappe.db.sql("DELETE FROM `tabVault Favorite` WHERE secret = 'test_favorite_secret'")
    frappe.db.sql("DELETE FROM `tabVault Favorite` WHERE user = 'chandayogesh123@gmail.com'")
    frappe.db.sql("DELETE FROM `tabVault Share` WHERE shared_name = 'test_favorite_secret'")
    frappe.db.commit()

    # Get standard user's initial count of visible secrets
    standard_user = "chandayogesh123@gmail.com"
    frappe.set_user(standard_user)
    initial_secrets_count = len(frappe.get_list("Vault Secret", pluck="name"))
    initial_favorites_count = len(frappe.get_all("Vault Favorite", filters={"user": standard_user}, pluck="secret"))

    # 2. Create a test secret owned by Administrator
    frappe.set_user("Administrator")
    secret = frappe.get_doc({
        "doctype": "Vault Secret",
        "name": test_secret_name,
        "title": "Test Favorite Secret",
        "secret_type": "Password",
        "password": "supersecretpassword",
        "owner": "Administrator"
    }).insert(ignore_permissions=True)
    print(f"Created test secret: {secret.name}")

    # 3. Share the secret with standard user
    share_res = share_secret(
        shared_name=secret.name,
        shared_doctype="Vault Secret",
        share_type="User",
        user=standard_user,
        permission_level="View Only"
    )
    print(f"Shared secret with standard user: {share_res['name']}")

    # 4. Favorite the secret as Administrator
    frappe.set_user("Administrator")
    toggle_res = toggle_favorite(secret.name)
    assert toggle_res["is_favorite"] == 1, "Admin should have favorited the secret!"
    print("PASSED: Admin successfully favorited the secret.")

    # 5. Check if standard user sees it as favorite (should be 0 change from initial)
    frappe.set_user(standard_user)
    fav_check_std = get_secret(secret.name)["is_favorite"]
    assert fav_check_std == 0, "Standard user should NOT see shared secret as favorite when only Admin favorited it!"
    print("PASSED: Favorites isolation verified — standard user is unaffected by Admin's favorite.")

    # 6. Favorite the secret as standard user
    toggle_res_std = toggle_favorite(secret.name)
    assert toggle_res_std["is_favorite"] == 1, "Standard user should have favorited the secret!"
    print("PASSED: Standard user successfully favorited the secret.")

    # 7. Unfavorite as Administrator
    frappe.set_user("Administrator")
    toggle_res_unfav = toggle_favorite(secret.name)
    assert toggle_res_unfav["is_favorite"] == 0, "Admin should have unfavorited the secret!"
    print("PASSED: Admin successfully unfavorited the secret.")

    # 8. Check if standard user still has it as favorite (should be 1)
    frappe.set_user(standard_user)
    fav_check_std_2 = get_secret(secret.name)["is_favorite"]
    assert fav_check_std_2 == 1, "Standard user should still see shared secret as favorite after Admin unfavorited it!"
    print("PASSED: Favorites isolation verified — standard user remains favorited.")

    # 9. Verify Stats and Count Leak checks
    stats_std = get_vault_stats()
    print(f"Stats for standard user: {stats_std}")
    assert stats_std["total_secrets"] == initial_secrets_count + 1, f"Standard user should see {initial_secrets_count + 1} visible secrets, but got {stats_std['total_secrets']}"
    assert stats_std["favorites"] == initial_favorites_count + 1, f"Standard user should have {initial_favorites_count + 1} favorites, but got {stats_std['favorites']}"
    print("PASSED: Count checks and stats respect permissions perfectly.")

    # 10. Clean up
    frappe.set_user("Administrator")
    frappe.delete_doc("Vault Secret", secret.name, force=True)
    frappe.db.sql("DELETE FROM `tabVault Favorite` WHERE secret = 'test_favorite_secret'")
    frappe.db.sql("DELETE FROM `tabVault Share` WHERE shared_name = 'test_favorite_secret'")
    frappe.db.commit()

    print("--- ALL VERIFICATION TESTS PASSED ---")
