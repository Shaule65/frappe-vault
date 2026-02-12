// Vault Settings Form Script
frappe.ui.form.on("Vault Settings", {
    refresh: function(frm) {
        // Add Lock Vault button
        frm.add_custom_button(__("Lock Vault Now"), function() {
            frappe_vault.lock_vault();
        });
        
        // Add info about session status
        frappe_vault.check_session(function(session) {
            if (session.required) {
                if (session.valid) {
                    frm.dashboard.add_indicator(__("Vault Unlocked"), "green");
                    if (session.expires_at) {
                        frm.dashboard.add_comment(
                            __("Session expires at: {0}", [frappe.datetime.str_to_user(session.expires_at)])
                        );
                    }
                } else {
                    frm.dashboard.add_indicator(__("Vault Locked"), "red");
                }
            } else {
                frm.dashboard.add_indicator(__("Master Password Disabled"), "grey");
            }
        });
    },

    enabled: function(frm) {
        if (frm.doc.enabled && !frm.doc.master_password) {
            frappe.show_alert({
                message: __("Please set a master password"),
                indicator: "orange"
            }, 5);
        }
    }
});
