// Vault Dashboard Page
// Follows Frappe Desk UI patterns and guidelines

frappe.pages["vault"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Vault"),
        single_column: true
    });

    wrapper.vault_page = new VaultPage(page);
};

frappe.pages["vault"].on_page_show = function(wrapper) {
    if (wrapper.vault_page) {
        wrapper.vault_page.refresh();
    }
};

class VaultPage {
    constructor(page) {
        this.page = page;
        this.current_category = null;
        this.search_query = "";
        this.favorites_only = false;
        this.current_type = null;
        
        this.setup_page();
        this.render();
        this.load_data();
    }

    setup_page() {
        // Primary action - New Secret
        this.page.set_primary_action(
            __("New Secret"),
            () => frappe.new_doc("Vault Secret"),
            "add"
        );

        // Secondary actions
        this.page.add_inner_button(__("Generate Password"), () => {
            frappe_vault.show_password_generator((password) => {
                frappe_vault.copy_to_clipboard(password, __("Password"));
            });
        });

        this.page.add_inner_button(__("Categories"), () => {
            frappe.set_route("Tree", "Vault Category");
        });

        this.page.add_inner_button(__("Access Logs"), () => {
            frappe.set_route("List", "Vault Access Log");
        });

        this.page.add_inner_button(__("Settings"), () => {
            frappe.set_route("Form", "Vault Settings");
        });

        // Lock vault button
        this.page.add_menu_item(__("Lock Vault"), () => {
            frappe_vault.lock_vault();
        });

        // Search field
        this.page.add_field({
            fieldname: "search",
            label: __("Search"),
            fieldtype: "Data",
            placeholder: __("Search secrets..."),
            change: () => {
                this.search_query = this.page.fields_dict.search.get_value() || "";
                this.load_secrets();
            }
        });

        // Category filter
        this.page.add_field({
            fieldname: "category",
            label: __("Category"),
            fieldtype: "Link",
            options: "Vault Category",
            change: () => {
                this.current_category = this.page.fields_dict.category.get_value();
                this.load_secrets();
            }
        });

        // Type filter
        this.page.add_field({
            fieldname: "secret_type",
            label: __("Type"),
            fieldtype: "Select",
            options: "\nPassword\nAPI Key\nNote\nSSH Key\nCertificate\nOther",
            change: () => {
                this.current_type = this.page.fields_dict.secret_type.get_value();
                this.load_secrets();
            }
        });

        // Favorites toggle
        this.page.add_field({
            fieldname: "favorites_only",
            label: __("Favorites Only"),
            fieldtype: "Check",
            change: () => {
                this.favorites_only = this.page.fields_dict.favorites_only.get_value();
                this.load_secrets();
            }
        });
    }

    render() {
        this.page.main.html(`
            <div class="vault-page-container">
                <!-- Stats Cards Row -->
                <div class="vault-stats-row frappe-card mb-4">
                    <div class="row">
                        <div class="col-sm-6 col-md-3">
                            <div class="vault-stat-item" data-filter="all">
                                <div class="stat-icon">${frappe.utils.icon("folder-normal", "lg")}</div>
                                <div class="stat-content">
                                    <div class="stat-number" id="stat-total">-</div>
                                    <div class="stat-label">${__("Total Secrets")}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-6 col-md-3">
                            <div class="vault-stat-item" data-filter="favorites">
                                <div class="stat-icon text-warning">${frappe.utils.icon("star", "lg")}</div>
                                <div class="stat-content">
                                    <div class="stat-number" id="stat-favorites">-</div>
                                    <div class="stat-label">${__("Favorites")}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-6 col-md-3">
                            <div class="vault-stat-item" data-filter="weak">
                                <div class="stat-icon text-danger">${frappe.utils.icon("alert", "lg")}</div>
                                <div class="stat-content">
                                    <div class="stat-number" id="stat-weak">-</div>
                                    <div class="stat-label">${__("Weak Passwords")}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-6 col-md-3">
                            <div class="vault-stat-item">
                                <div class="stat-icon text-primary">${frappe.utils.icon("clock", "lg")}</div>
                                <div class="stat-content">
                                    <div class="stat-number" id="stat-recent">-</div>
                                    <div class="stat-label">${__("Accessed Today")}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Secrets List -->
                <div class="vault-secrets-container">
                    <div class="vault-secrets-header d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0 text-muted">${__("Secrets")}</h5>
                        <div class="vault-view-toggle btn-group btn-group-sm">
                            <button class="btn btn-default active" data-view="grid">
                                ${frappe.utils.icon("grid", "sm")}
                            </button>
                            <button class="btn btn-default" data-view="list">
                                ${frappe.utils.icon("list", "sm")}
                            </button>
                        </div>
                    </div>
                    <div class="vault-secrets-list" id="secrets-list">
                        <div class="vault-loading text-center text-muted p-5">
                            <div class="spinner-border spinner-border-sm mb-2" role="status"></div>
                            <div>${__("Loading secrets...")}</div>
                        </div>
                    </div>
                </div>
            </div>
        `);

        this.bind_events();
    }

    bind_events() {
        // Stat card clicks for filtering
        this.page.main.find(".vault-stat-item").on("click", (e) => {
            const filter = $(e.currentTarget).data("filter");
            if (filter === "favorites") {
                this.page.fields_dict.favorites_only.set_value(1);
            } else if (filter === "weak") {
                // Navigate to list view with weak password filter
                frappe.route_options = { password_strength: "weak" };
                frappe.set_route("List", "Vault Secret");
            } else if (filter === "all") {
                this.page.fields_dict.favorites_only.set_value(0);
                this.page.fields_dict.category.set_value("");
                this.page.fields_dict.secret_type.set_value("");
            }
        });

        // View toggle
        this.page.main.find(".vault-view-toggle .btn").on("click", (e) => {
            const $btn = $(e.currentTarget);
            const view = $btn.data("view");
            
            this.page.main.find(".vault-view-toggle .btn").removeClass("active");
            $btn.addClass("active");
            
            this.current_view = view;
            this.render_secrets(this.last_secrets);
        });

        this.current_view = "grid";
    }

    async load_data() {
        await Promise.all([
            this.load_stats(),
            this.load_secrets()
        ]);
    }

    async load_stats() {
        try {
            const stats = await frappe.xcall(
                "frappe_vault.frappe_vault.doctype.vault_secret.vault_secret.get_vault_stats"
            );
            
            if (stats) {
                this.page.main.find("#stat-total").text(stats.total_secrets || 0);
                this.page.main.find("#stat-favorites").text(stats.favorites || 0);
                this.page.main.find("#stat-weak").text(stats.weak_passwords || 0);
                this.page.main.find("#stat-recent").text(stats.recent_secrets?.length || 0);
            }
        } catch (error) {
            console.error("Failed to load stats:", error);
        }
    }

    async load_secrets() {
        try {
            const result = await frappe.xcall("frappe_vault.api.get_secrets", {
                category: this.current_category || null,
                search: this.search_query || null,
                secret_type: this.current_type || null,
                favorites_only: this.favorites_only ? 1 : 0,
                limit: 50
            });
            
            if (result) {
                this.last_secrets = result.secrets;
                this.render_secrets(result.secrets);
            }
        } catch (error) {
            console.error("Failed to load secrets:", error);
            this.render_empty_state(__("Failed to load secrets. Please try again."));
        }
    }

    render_secrets(secrets) {
        const container = this.page.main.find("#secrets-list");
        
        if (!secrets || secrets.length === 0) {
            this.render_empty_state();
            return;
        }

        if (this.current_view === "list") {
            this.render_list_view(container, secrets);
        } else {
            this.render_grid_view(container, secrets);
        }
    }

    render_empty_state(message) {
        const container = this.page.main.find("#secrets-list");
        container.html(`
            <div class="vault-empty-state text-center p-5">
                <div class="empty-icon mb-3">${frappe.utils.icon("lock", "xl")}</div>
                <h5 class="text-muted">${message || __("No secrets found")}</h5>
                <p class="text-muted small">${__("Create your first secret to get started")}</p>
                <button class="btn btn-primary btn-sm" onclick="frappe.new_doc('Vault Secret')">
                    ${frappe.utils.icon("add", "xs")} ${__("Create Secret")}
                </button>
            </div>
        `);
    }

    render_grid_view(container, secrets) {
        let html = '<div class="row">';
        
        secrets.forEach(secret => {
            const icon = frappe_vault.get_type_icon(secret.secret_type);
            const strength_indicator = frappe_vault.get_strength_indicator(secret.password_strength);
            const favorite_icon = secret.is_favorite 
                ? `<span class="text-warning">${frappe.utils.icon("star", "xs")}</span>` 
                : "";
            
            html += `
                <div class="col-12 col-sm-6 col-lg-4 mb-3">
                    <div class="vault-secret-card frappe-card" data-name="${secret.name}">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div class="secret-title">
                                    ${favorite_icon}
                                    <span class="font-weight-bold">${frappe.utils.escape_html(secret.title)}</span>
                                </div>
                                <span class="badge badge-secondary">
                                    ${icon} ${__(secret.secret_type)}
                                </span>
                            </div>
                            <div class="secret-meta small text-muted">
                                ${secret.username ? `<div>${frappe.utils.icon("user", "xs")} ${frappe.utils.escape_html(secret.username)}</div>` : ""}
                                ${secret.url ? `<div class="text-truncate">${frappe.utils.icon("link", "xs")} <a href="${secret.url}" target="_blank" class="text-muted">${frappe.utils.escape_html(secret.url)}</a></div>` : ""}
                                ${secret.category ? `<div>${frappe.utils.icon("folder-normal", "xs")} ${frappe.utils.escape_html(secret.category)}</div>` : ""}
                            </div>
                            ${secret.password_strength ? `
                                <div class="mt-2">
                                    <span class="indicator-pill ${strength_indicator}">
                                        ${__(secret.password_strength)}
                                    </span>
                                </div>
                            ` : ""}
                            <div class="secret-actions mt-3 pt-2 border-top">
                                <button class="btn btn-xs btn-default btn-copy" data-name="${secret.name}" title="${__("Copy")}">
                                    ${frappe.utils.icon("copy", "xs")} ${__("Copy")}
                                </button>
                                <button class="btn btn-xs btn-default btn-view" data-name="${secret.name}" title="${__("View")}">
                                    ${frappe.utils.icon("file", "xs")} ${__("View")}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += "</div>";
        container.html(html);
        this.bind_secret_events(container);
    }

    render_list_view(container, secrets) {
        let html = '<div class="vault-list-view">';
        
        secrets.forEach(secret => {
            const icon = frappe_vault.get_type_icon(secret.secret_type, "sm");
            const strength_indicator = frappe_vault.get_strength_indicator(secret.password_strength);
            const favorite_icon = secret.is_favorite 
                ? `<span class="text-warning">${frappe.utils.icon("star", "sm")}</span>` 
                : "";
            
            html += `
                <div class="vault-list-item d-flex align-items-center" data-name="${secret.name}">
                    <div class="list-item-icon mr-3">${icon}</div>
                    <div class="list-item-content flex-grow-1">
                        <div class="list-item-title font-weight-bold">
                            ${favorite_icon} ${frappe.utils.escape_html(secret.title)}
                        </div>
                        <div class="list-item-meta small text-muted">
                            ${secret.username || ""} ${secret.category ? `• ${secret.category}` : ""}
                        </div>
                    </div>
                    ${secret.password_strength ? `
                        <span class="indicator-pill ${strength_indicator} mr-2">
                            ${__(secret.password_strength)}
                        </span>
                    ` : ""}
                    <div class="list-item-actions">
                        <button class="btn btn-xs btn-default btn-copy" data-name="${secret.name}">
                            ${frappe.utils.icon("copy", "xs")}
                        </button>
                        <button class="btn btn-xs btn-default btn-view" data-name="${secret.name}">
                            ${frappe.utils.icon("arrow-right", "xs")}
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += "</div>";
        container.html(html);
        this.bind_secret_events(container);
    }

    bind_secret_events(container) {
        // Copy button
        container.find(".btn-copy").on("click", (e) => {
            e.stopPropagation();
            const name = $(e.currentTarget).data("name");
            frappe_vault.reveal_password(name, (data) => {
                if (data.password) {
                    frappe_vault.copy_to_clipboard(data.password, __("Password"));
                } else if (data.api_secret) {
                    frappe_vault.copy_to_clipboard(data.api_secret, __("API Secret"));
                }
            });
        });

        // View button
        container.find(".btn-view").on("click", (e) => {
            e.stopPropagation();
            const name = $(e.currentTarget).data("name");
            frappe.set_route("Form", "Vault Secret", name);
        });

        // Card/row click
        container.find(".vault-secret-card, .vault-list-item").on("click", (e) => {
            const name = $(e.currentTarget).data("name");
            frappe.set_route("Form", "Vault Secret", name);
        });
    }

    refresh() {
        this.load_data();
    }
}
