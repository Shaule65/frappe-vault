// Vault Settings Form Script
// Follows Frappe Desk UI patterns and guidelines

frappe.ui.form.on("Vault Settings", {
    validate(frm) {
        if (frm.doc.default_password_length && frm.doc.default_password_length < 4) {
            frappe.msgprint({
                title: __("Validation Error"),
                message: __("Default password length must be at least 4"),
                indicator: "red"
            });
            frappe.validated = false;
        }
    }
});
