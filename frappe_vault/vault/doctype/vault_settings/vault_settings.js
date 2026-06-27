// Vault Settings Form Script
// Follows Frappe Desk UI patterns and guidelines

frappe.ui.form.on("Vault Settings", {
    refresh(frm) {
        // Clear existing custom buttons
        frm.clear_custom_buttons();
        
        // Add Lock Vault button using proper Frappe pattern
        frm.add_custom_button(__("Lock Vault"), async () => {
            await frappe_vault.lock_vault();
            frm.reload_doc();
        });

        // Add session status indicator
        frappe_vault.update_session_indicator(frm);
        
        // Add help section
        if (frm.doc.enabled && frm.doc.master_password) {
            frm.set_intro(__("Master password protection is enabled. Users will need to enter the master password to view or copy secrets."), "green");
        } else {
            frm.set_intro(__("Master password protection is disabled. Consider enabling it for additional security."), "yellow");
        }
    },

    enabled(frm) {
        if (frm.doc.enabled && !frm.doc.master_password) {
            frappe.show_alert({
                message: __("Please set a master password to enable vault protection"),
                indicator: "orange"
            });
            // Focus on master password field
            frm.scroll_to_field("master_password");
        }
    },

    validate(frm) {
        // Validation: if enabled, master password is required
        if (frm.doc.enabled && !frm.doc.master_password) {
            frappe.msgprint({
                title: __("Validation Error"),
                message: __("Master password is required when vault protection is enabled"),
                indicator: "red"
            });
            frappe.validated = false;
        }
        
        // Validate session timeout
        if (frm.doc.session_timeout && frm.doc.session_timeout < 1) {
            frappe.msgprint({
                title: __("Validation Error"),
                message: __("Session timeout must be at least 1 minute"),
                indicator: "red"
            });
            frappe.validated = false;
        }
    }
});

// Update session indicator on dashboard
frappe_vault.update_session_indicator = async function(frm) {
    try {
        const session = await frappe_vault.check_session();
        
        if (session.required) {
            if (session.valid) {
                frm.dashboard.add_indicator(__("Vault Unlocked"), "green");
                if (session.expires_at) {
                    const expires = frappe.datetime.str_to_user(session.expires_at);
                    frm.dashboard.add_comment(
                        __("Session expires: {0}", [expires]),
                        "green"
                    );
                }
            } else {
                frm.dashboard.add_indicator(__("Vault Locked"), "red");
            }
        } else {
            frm.dashboard.add_indicator(__("Master Password Disabled"), "grey");
        }
    } catch (error) {
        console.error("Failed to check session status:", error);
    }
};
