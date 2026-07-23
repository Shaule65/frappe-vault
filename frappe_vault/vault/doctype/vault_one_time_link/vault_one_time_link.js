// Vault One Time Link Form Script

frappe.ui.form.on("Vault One Time Link", {
    refresh(frm) {
        // Clear cached Submit primary action unconditionally
        frm.page.clear_primary_action();

        if (!frm.is_new() && frm.doc.share_url) {
            // Primary action button to copy shareable link
            frm.add_custom_button(__("Copy Shareable Link"), function() {
                frappe.utils.copy_to_clipboard(frm.doc.share_url);
            }).addClass("btn-primary");

            // Render inline Copy button inside the share_url field
            frm.events.render_inline_copy_button(frm);
        }

        if (frm.is_dirty()) {
            frm.page.set_primary_action(__("Save"), function() {
                frm.save();
            });
        }
    },

    render_inline_copy_button(frm) {
        const field = frm.get_field("share_url");
        if (!field || !field.$wrapper) return;

        field.$wrapper.find(".copy-link-btn").remove();

        const $controlInput = field.$wrapper.find(".control-input");
        if (!$controlInput.length) return;

        $controlInput.css("position", "relative");

        const $copyBtn = $(`
            <button class="btn btn-xs btn-default copy-link-btn" type="button" title="${__("Copy Link")}" style="position: absolute; right: 8px; top: 50%; transform: translateY(-50%); z-index: 5; display: inline-flex; items-center; justify-content: center; padding: 3px 6px;">
                <svg class="icon icon-sm" style="width: 14px; height: 14px; fill: currentColor;"><use href="#icon-clipboard"></use></svg>
            </button>
        `);

        $copyBtn.on("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            frappe.utils.copy_to_clipboard(frm.doc.share_url);
        });

        $controlInput.append($copyBtn);
    }
});
