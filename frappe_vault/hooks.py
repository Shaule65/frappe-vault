app_name = "frappe_vault"
app_title = "Frappe Vault"
app_publisher = "Frappe Vault"
app_description = "Password and secrets management for the Frappe ecosystem"
app_email = "hello@example.com"
app_license = "MIT"
app_logo_url = "/assets/frappe_vault/images/vault-logo.svg"
app_home = "/vault"
required_apps = ["frappe"]

# Apps Screen
add_to_apps_screen = [
	{
		"name": "frappe_vault",
		"logo": app_logo_url,
		"title": "Frappe Vault",
		"route": app_home,
	}
]

# Includes in <head>
# app_include_css = "/assets/frappe_vault/css/frappe_vault.css"
# app_include_js = "/assets/frappe_vault/js/frappe_vault.js"

# Fixtures
fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Vault User", "Vault Manager", "Vault Admin"]]],
	}
]

# Website Route Rules — serve Vue SPA
website_route_rules = [
	{"from_route": "/vault/<path:app_path>", "to_route": "vault"},
	{"from_route": "/vault", "to_route": "vault"},
]

# Installation
after_install = "frappe_vault.setup.install.after_install"

# Document Events
doc_events = {
	"Vault Secret": {
		"after_insert": "frappe_vault.services.audit_service.log_secret_created",
		"on_update": "frappe_vault.services.audit_service.log_secret_updated",
		"on_trash": "frappe_vault.services.audit_service.log_secret_deleted",
	},
	"Vault Share": {
		"after_insert": "frappe_vault.services.audit_service.log_share_created",
		"on_trash": "frappe_vault.services.audit_service.log_share_removed",
	},
}

# Scheduled Tasks
scheduler_events = {
	"daily": [
		"frappe_vault.background_jobs.password_expiry.check_password_expiry",
	],
	"weekly": [
		"frappe_vault.background_jobs.security_scan.run_security_scan",
		"frappe_vault.background_jobs.log_cleanup.cleanup_old_logs",
	],
	"hourly": [
		"frappe_vault.background_jobs.link_cleanup.cleanup_expired_links",
	],
}

# Permissions — row-level filtering
permission_query_conditions = {
	"Vault Secret": "frappe_vault.utils.permissions.get_secret_permission_query",
}

has_permission = {
	"Vault Secret": "frappe_vault.utils.permissions.has_secret_permission",
}
