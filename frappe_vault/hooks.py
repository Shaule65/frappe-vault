app_name = "frappe_vault"
app_title = "Frappe Vault"
app_publisher = "Frappe Vault"
app_description = "A Frappe-based password and secrets management application"
app_email = "hello@example.com"
app_license = "MIT"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "frappe_vault",
		"logo": "/assets/frappe_vault/images/vault-logo.svg",
		"title": "Frappe Vault",
		"route": "/vault",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/frappe_vault/css/frappe_vault.css"
app_include_js = "/assets/frappe_vault/js/frappe_vault.js"

# include js, css files in header of web template
# web_include_css = "/assets/frappe_vault/css/frappe_vault.css"
# web_include_js = "/assets/frappe_vault/js/frappe_vault.js"

# include custom scss in every website theme (without signing in)
# website_theme_scss = "frappe_vault/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Vault Secret": "public/js/vault_secret.js",
    "Vault Settings": "public/js/vault_settings.js"
}

doctype_list_js = {
    "Vault Secret": "public/js/vault_secret_list.js"
}

doctype_tree_js = {
    "Vault Category": "public/js/vault_category_tree.js"
}

# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "frappe_vault/public/icons.svg"

# Fixtures
# --------
fixtures = ["Role"]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Website Route Rules
# --------------------
# Route all /vault/* paths to the vault SPA
website_route_rules = [
	{"from_route": "/vault/<path:app_path>", "to_route": "vault"},
]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "frappe_vault.utils.jinja_methods",
# 	"filters": "frappe_vault.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "frappe_vault.install.before_install"
after_install = "frappe_vault.setup.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "frappe_vault.uninstall.before_uninstall"
# after_uninstall = "frappe_vault.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/configurations required by the app
# boot_session = "frappe_vault.boot.boot_session"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "frappe_vault.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Vault Secret": {
        "after_insert": "frappe_vault.frappe_vault.doctype.vault_secret.vault_secret.log_access",
        "on_update": "frappe_vault.frappe_vault.doctype.vault_secret.vault_secret.log_access",
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"frappe_vault.tasks.check_password_expiry"
	],
	"weekly": [
		"frappe_vault.tasks.cleanup_old_access_logs"
	],
}

# Testing
# -------

# before_tests = "frappe_vault.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "frappe_vault.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "frappe_vault.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["frappe_vault.utils.before_request"]
# after_request = ["frappe_vault.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_vault.utils.before_job"]
# after_job = ["frappe_vault.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"frappe_vault.auth.validate"
# ]

# Automatically update python controller files for doctype when editing json
# Recomended enabling this for developer mode only! Set via bench config.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
