// Frappe Vault - Main JavaScript Utilities
// Follows Frappe Desk UI patterns and guidelines

frappe.provide("frappe_vault");

// Icon mapping for secret types (using Frappe SVG icons)
frappe_vault.SECRET_TYPE_ICONS = {
    "Password": "lock",
    "API Key": "key",
    "Note": "file",
    "SSH Key": "es-solid-code-block",
    "Certificate": "es-solid-certificate",
    "Other": "folder-normal"
};

// Password strength colors (Frappe standard indicator colors)
frappe_vault.STRENGTH_COLORS = {
    weak: "var(--red-500)",
    fair: "var(--orange-500)",
    good: "var(--yellow-500)",
    strong: "var(--green-500)",
    excellent: "var(--blue-500)"
};

frappe_vault.STRENGTH_INDICATORS = {
    weak: "red",
    fair: "orange",
    good: "yellow",
    strong: "green",
    excellent: "blue"
};

// Copy text to clipboard using modern API
frappe_vault.copy_to_clipboard = function(text, field_label) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            frappe.show_alert({
                message: __("{0} copied to clipboard", [field_label || __("Text")]),
                indicator: "green"
            });
        }).catch(() => {
            frappe_vault.fallback_copy(text, field_label);
        });
    } else {
        frappe_vault.fallback_copy(text, field_label);
    }
};

// Fallback copy method for older browsers
frappe_vault.fallback_copy = function(text, field_label) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.cssText = "position:fixed;left:-9999px;top:-9999px;";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand("copy");
        frappe.show_alert({
            message: __("{0} copied to clipboard", [field_label || __("Text")]),
            indicator: "green"
        });
    } catch (err) {
        frappe.show_alert({
            message: __("Failed to copy to clipboard"),
            indicator: "red"
        });
    }
    
    document.body.removeChild(textArea);
};

// Password Generator Dialog following Frappe UI patterns
frappe_vault.show_password_generator = function(callback) {
    const d = new frappe.ui.Dialog({
        title: __("Password Generator"),
        fields: [
            {
                fieldname: "length",
                fieldtype: "Int",
                label: __("Password Length"),
                default: 16,
                reqd: 1,
                description: __("Recommended: 16-32 characters")
            },
            {
                fieldtype: "Section Break",
                label: __("Character Options")
            },
            {
                fieldname: "use_uppercase",
                fieldtype: "Check",
                label: __("Uppercase (A-Z)"),
                default: 1
            },
            {
                fieldname: "use_lowercase",
                fieldtype: "Check",
                label: __("Lowercase (a-z)"),
                default: 1
            },
            {
                fieldtype: "Column Break"
            },
            {
                fieldname: "use_digits",
                fieldtype: "Check",
                label: __("Numbers (0-9)"),
                default: 1
            },
            {
                fieldname: "use_special",
                fieldtype: "Check",
                label: __("Symbols (!@#$...)"),
                default: 1
            },
            {
                fieldtype: "Section Break"
            },
            {
                fieldname: "exclude_ambiguous",
                fieldtype: "Check",
                label: __("Exclude ambiguous characters (0, O, l, 1, I)"),
                default: 0
            },
            {
                fieldtype: "Section Break",
                label: __("Generated Password")
            },
            {
                fieldname: "generated_password",
                fieldtype: "Data",
                label: __("Password"),
                read_only: 1
            },
            {
                fieldname: "strength_html",
                fieldtype: "HTML"
            }
        ],
        size: "small",
        primary_action_label: __("Use Password"),
        primary_action() {
            const password = d.get_value("generated_password");
            if (password && callback) {
                callback(password);
            }
            d.hide();
        },
        secondary_action_label: __("Regenerate"),
        secondary_action() {
            frappe_vault.generate_in_dialog(d);
        }
    });

    // Add copy button to footer
    d.$wrapper.find(".modal-footer").prepend(`
        <button type="button" class="btn btn-default btn-sm btn-copy-pwd mr-2">
            ${frappe.utils.icon("copy", "sm")} ${__("Copy")}
        </button>
    `);
    
    d.$wrapper.find(".btn-copy-pwd").on("click", () => {
        const password = d.get_value("generated_password");
        if (password) {
            frappe_vault.copy_to_clipboard(password, __("Password"));
        }
    });

    d.show();
    
    // Generate initial password
    frappe_vault.generate_in_dialog(d);
};

frappe_vault.generate_in_dialog = function(dialog) {
    frappe.xcall(
        "frappe_vault.api.generator.generate_password",
        {
            length: dialog.get_value("length") || 16,
            use_uppercase: dialog.get_value("use_uppercase") ? 1 : 0,
            use_lowercase: dialog.get_value("use_lowercase") ? 1 : 0,
            use_digits: dialog.get_value("use_digits") ? 1 : 0,
            use_special: dialog.get_value("use_special") ? 1 : 0,
            exclude_ambiguous: dialog.get_value("exclude_ambiguous") ? 1 : 0
        }
    ).then(result => {
        dialog.set_value("generated_password", result.password);
        frappe_vault.render_strength_indicator(dialog, result.strength);
    });
};

frappe_vault.render_strength_indicator = function(dialog, strength) {
    const color = frappe_vault.STRENGTH_COLORS[strength.level] || "var(--gray-500)";
    const percentage = strength.score;
    const label = __(strength.level.charAt(0).toUpperCase() + strength.level.slice(1));
    
    let html = `
        <div class="password-strength-container mt-3">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted">${__("Strength")}</span>
                <span style="color: ${color}; font-weight: 500;">${label}</span>
            </div>
            <div class="progress" style="height: 6px;">
                <div class="progress-bar" role="progressbar" 
                    style="width: ${percentage}%; background-color: ${color};"
                    aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
    `;
    
    if (strength.feedback && strength.feedback.length > 0) {
        html += `<div class="mt-2 small text-muted">`;
        strength.feedback.forEach(tip => {
            html += `<div>${frappe.utils.icon("info-circle", "xs")} ${__(tip)}</div>`;
        });
        html += `</div>`;
    }
    
    html += `</div>`;
    
    dialog.fields_dict.strength_html.$wrapper.html(html);
};

// Get icon for secret type (returns Frappe icon markup)
frappe_vault.get_type_icon = function(secret_type, size = "sm") {
    const icon_name = frappe_vault.SECRET_TYPE_ICONS[secret_type] || "folder-normal";
    return frappe.utils.icon(icon_name, size);
};

// Get indicator class for password strength
frappe_vault.get_strength_indicator = function(strength) {
    return frappe_vault.STRENGTH_INDICATORS[strength] || "grey";
};
