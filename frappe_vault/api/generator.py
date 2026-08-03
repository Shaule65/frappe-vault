"""Generator API — password generation and strength checking."""

import frappe


@frappe.whitelist()
def generate(
    length=16,
    use_uppercase=True,
    use_lowercase=True,
    use_digits=True,
    use_special=True,
    exclude_ambiguous=False,
):
    from frappe_vault.services.audit_service import log_password_generated
    from frappe_vault.services.generator_service import calculate_password_strength, generate_password

    pwd = generate_password(
        length=int(length),
        use_uppercase=frappe.utils.cint(use_uppercase),
        use_lowercase=frappe.utils.cint(use_lowercase),
        use_digits=frappe.utils.cint(use_digits),
        use_special=frappe.utils.cint(use_special),
        exclude_ambiguous=frappe.utils.cint(exclude_ambiguous),
    )
    strength = calculate_password_strength(pwd)
    log_password_generated()
    return {"password": pwd, "strength": strength}


@frappe.whitelist()
def check_strength(password):
    from frappe_vault.services.generator_service import calculate_password_strength

    return calculate_password_strength(password)


@frappe.whitelist()
def check_breach(password):
    from frappe_vault.services.security_service import check_password_breach

    return check_password_breach(password)
