# Frappe Vault — Technical Architecture & Agent Guide

> **Version**: 1.1.0
> **App Name**: `frappe_vault`
> **Target Framework**: Frappe Framework v15
> **Frontend Stack**: Vue 3 (Composition API), Frappe UI v5, TailwindCSS, Vite
> **License**: MIT

---

## 1. System Overview & Core Philosophy

**Frappe Vault** is a secure, multi-tenant secret and password management application built natively for the Frappe Framework. It provides encrypted storage for passwords, TOTP (2FA) seed keys, API keys, credit cards, SSH keys, and secure notes with granular row-level access control, role-based sharing, and real-time security auditing.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Frontend SPA (Vue 3 / Frappe UI)                   │
│          Route: /vault  (Served via www/vault.html template)            │
├─────────────────────────────────────────────────────────────────────────┤
│                     Whitelisted REST APIs (frappe_vault.api.*)          │
├─────────────────────────────────────────────────────────────────────────┤
│                    Services Layer (frappe_vault.services.*)            │
│    (Secret CRUD, Base32 TOTP, Sharing Engine, Security Scoring, Audit)  │
├─────────────────────────────────────────────────────────────────────────┤
│            Row-Level Permission Hooks (frappe_vault.utils.permissions)  │
├─────────────────────────────────────────────────────────────────────────┤
│               Frappe ORM & Encryption Core (Fernet / __Auth)            │
├─────────────────────────────────────────────────────────────────────────┤
│                       Database (MariaDB 10.6+)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Invariants
1. **Zero-Trust Attribute Access**: Fields of type `Password` (`password`, `totp_secret`, `api_secret`, `card_number`, `card_cvv`, `db_password`) are stored encrypted in Frappe's `__Auth` table. Accessing these attributes on `Document` instances MUST use safe lookups `doc.get("fieldname")` or `getattr(doc, "fieldname", None)` to prevent Python `AttributeError` crashes when documents are loaded without unpopulated auth attributes.
2. **Strict Base32 Modulo 8 Validation**: TOTP secret seeds must adhere strictly to RFC 4648 Base32 syntax (`[A-Z2-7]`, minimum length 8, valid unpadded string length `len % 8` in `(0, 2, 4, 5, 7)`). Equal signs (`=`) are only permitted at the end of the key for padding.
3. **Frappe UI Provider Context**: All frontend toast notifications (`toast.error()`, `toast.success()`) and dialog providers depend on wrapping the root template in `<FrappeUIProvider>` in [`frontend/src/App.vue`](file:///Users/yakshpurohit/frappe/my-bench/apps/frappe_vault/frontend/src/App.vue).
4. **Standard Desk Integration**: Frappe Vault operates cleanly alongside standard Frappe Desk (`/app`). System Managers and Vault Users navigate to Frappe Vault via the Desk App Switcher or desktop icon (`/vault`), preserving standard Desk landing routes.

---

## 2. Directory & Package Structure

```text
apps/frappe_vault/
├── ARCHITECTURE.md                  # Authoritative system documentation
├── pyproject.toml                   # Python package configuration
├── frappe_vault/                    # Backend Python package
│   ├── __init__.py                  # Application version (__version__ = "1.1.0")
│   ├── hooks.py                     # Frappe hooks (permission queries, doc events, routes)
│   ├── api/                         # Whitelisted API endpoints
│   │   ├── secrets.py               # Secret CRUD REST endpoints
│   │   ├── sharing.py               # User and Role share management API
│   │   ├── folders.py               # Folder hierarchy & share API
│   │   ├── dashboard.py             # Dashboard layout & chart data REST API
│   │   ├── generator.py             # Password generator API
│   │   ├── notifications.py         # In-app notifications API
│   │   ├── audit.py                 # Audit log query API
│   │   ├── demo.py                  # Demo data environment API
│   │   └── fields.py                # Secret category schema & custom field definitions
│   ├── services/                    # Core business logic layer
│   │   ├── secret_service.py        # Secret CRUD, TOTP generator, password strength
│   │   ├── sharing_service.py       # Sharing engine, role expansion, permission calculation
│   │   ├── dashboard_service.py     # Dashboard grid layout, trend calculations, metric aggregation
│   │   ├── security_service.py      # Per-user security score algorithm, weak password analysis
│   │   ├── audit_service.py         # Document event logger (after_insert, on_update, on_trash)
│   │   ├── notification_service.py  # Notification record creator
│   │   ├── generator_service.py     # Cryptographically secure password generation
│   │   ├── demo_service.py          # Demo data generator & teardown orchestration
│   │   └── demo_data_catalog.py     # Static catalog of realistic demo secrets and folders
│   ├── utils/                       # Permission query conditions & row-level hooks
│   │   └── permissions.py           # SQL permission queries and document permission checks
│   ├── vault/                       # DocType definitions
│   │   └── doctype/
│   │       ├── vault_secret/        # Primary Vault Secret DocType (JSON, PY, JS)
│   │       ├── vault_share/         # Access grant record DocType (User/Role permissions)
│   │       ├── vault_folder/        # Folder grouping DocType
│   │       ├── vault_bookmark/      # Per-user favorite bookmark DocType
│   │       ├── vault_audit_log/     # Immutable access and modification log DocType
│   │       ├── vault_one_time_link/ # Self-destructing secret share link DocType
│   │       └── vault_settings/      # System configuration & dashboard layout singleton
│   ├── setup/                       # Post-installation hooks
│   │   └── install.py               # Default role creation & System Manager role assignment
│   └── tests/                       # Automated test suite
│       ├── test_secret_service.py   # Secret CRUD, encryption, and TOTP unit tests
│       ├── test_sharing_service.py  # Direct user share and role expansion unit tests
│       ├── test_folders.py          # Folder hierarchy unit tests
│       ├── test_dashboard.py        # Dashboard metric unit tests
│       ├── test_notifications.py    # Notification engine unit tests
│       ├── test_one_time_link.py    # One-time link consumption unit tests
│       └── test_security.py         # Backend exploit simulation and security validation
└── frontend/                        # Frontend Vue 3 Single Page Application (SPA)
    ├── package.json                 # Frontend dependencies (frappe-ui, vue, tailwindcss, vite)
    ├── vite.config.js               # Vite build configuration (outputs to frappe_vault/public/frontend)
    └── src/                         # Vue 3 source files
        ├── App.vue                  # Root component (wrapped in FrappeUIProvider)
        ├── main.js                  # App bootstrap and router mount
        ├── router.js                # Client-side SPA routes
        ├── components/              # Reusable UI components & dialogs
        │   ├── AppSidebar.vue       # Main navigation sidebar, collapse state, version badge
        │   ├── TotpDialog.vue       # Live 30s TOTP passcode countdown & copy dialog
        │   ├── NewSecretDialog.vue  # Secret creation & edit modal
        │   ├── ManageFolderSharesDialog.vue # Folder share & role access manager
        │   ├── PeopleWithAccessModal.vue    # Secret share & role access manager
        │   ├── DashboardGrid.vue    # Draggable/resizable dashboard chart layout grid
        │   ├── DashboardItem.vue    # Security score widget, trend charts, number metrics
        │   ├── FilterPanel.vue      # Filter drawer for secret types and folders
        │   ├── SortPanel.vue        # Sorting controls
        │   ├── ColumnPanel.vue      # Custom list view column toggles
        │   └── SecretValueDisplay.vue # Masked/unmasked password toggle component
        ├── views/                   # SPA page views
        │   ├── DashboardView.vue    # Main dashboard view
        │   ├── SecretsView.vue      # Vault secrets list view
        │   ├── SecretDetailView.vue # Detailed secret viewer, edit form, notes, TOTP button
        │   ├── BookmarksView.vue    # Bookmarked secrets view
        │   ├── SharedWithMeView.vue # Secrets shared with the current user
        │   ├── ManageSharesView.vue # Admin/Owner share manager view
        │   ├── AuditLogView.vue     # Access audit log viewer
        │   └── SharedLinkView.vue   # Public one-time secret view page
        ├── composables/             # Vue 3 composables
        │   ├── vault.js             # API resources (useSecrets, useVaultStats, useSecurityScore)
        │   └── constants.js         # Secret type icons, color badges, date formatters
        └── stores/                  # Vue reactive state stores
            └── notifications.js     # Notification state & background polling
```

---

## 3. Data Models & DocTypes

### 3.1 `Vault Secret`
Primary entity storing secret credentials.
- **Fields**: `title`, `secret_type` (`Password`, `TOTP`, `API Key`, `Credit Card`, `SSH Key`, `Database`, `Secure Note`), `username`, `email`, `url`, `folder`, `password_strength`, `password_last_changed`, `last_accessed`, `access_count`, `notes`.
- **Encrypted Password Fields**: `password`, `totp_secret`, `api_secret`, `card_number`, `card_cvv`, `db_password`.
- **Warning: Plaintext Fields**: `ssh_private_key` and `certificate` are currently stored as plaintext `Text` fields in the database schema. This is a known risk (Schema change deferred).
- **Behavior**:
  - `validate_totp_secret()` automatically sanitizes (trims, uppercases) and verifies Base32 syntax (`[A-Z2-7]`, unpadded length >= 16, modulo 8 rule). Does NOT auto-pad missing `=` characters to ensure users provide valid raw keys.
  - Password strength is automatically calculated on insert/update using dictionary checks, length scoring, character diversity, and entropy evaluation.

### 3.2 `Vault Share`
Granular permission record granting access to specific users or roles.
- **Fields**:
  - `share_type`: `User` or `Role`
  - `user`: Link to `User` (when `share_type == 'User'`)
  - `frappe_role`: Link to `Role` (when `share_type == 'Role'`)
  - `shared_doctype`: `Vault Secret` or `Vault Folder`
  - `shared_name`: Name of the target document (`Vault Secret` or `Vault Folder`)
  - `permission_level`: `View Only`, `View & Copy`, `Edit`, `Full Control`
  - `expires_on`: Datetime after which access automatically expires
  - `is_revoked`: Check flag (1 if access is explicitly revoked)
  - `is_custom_override`: Check flag (1 if role member permission was manually changed)
  - `hidden_from_recipient`: Check flag (1 if the share should not appear in the recipient's dashboard)
  - `shared_by`: Link to `User` who created the share

### 3.3 `Vault Folder`
Group container for organizing secrets into categories (e.g. Work, Personal, Finance, Infrastructure).
- **Fields**: `folder_name`, `icon`, `color`, `parent_folder`, `owner`.

### 3.4 `Vault Audit Log`
Immutable audit log tracking every action performed on secrets and shares.
- **Fields**: `user`, `action` (`view`, `create`, `update`, `delete`, `share`, `revoke`, `copy_password`), `secret`, `secret_title`, `ip_address`, `user_agent`, `timestamp`.

### 3.5 `Vault Bookmark`
Per-user bookmark table mapping users to starred secrets.
- **Fields**: `user`, `secret`.

### 3.6 `Vault One Time Link`
Self-destructing secret share link accessible via unique token.
- **Fields**: `token`, `secret_data` (encrypted JSON payload), `passphrase_hash`, `max_views`, `view_count`, `expires_on`, `is_consumed`.

---

## 4. Permission Engine & Row-Level Security

Frappe Vault enforces strict **Row-Level Security (RLS)** using SQL query injection hooks configured in [`frappe_vault/hooks.py`](file:///Users/yakshpurohit/frappe/my-bench/apps/frappe_vault/frappe_vault/hooks.py#L77-L86):

```python
permission_query_conditions = {
    "Vault Secret": "frappe_vault.utils.permissions.get_secret_permission_query",
    "Vault Folder": "frappe_vault.utils.permissions.get_folder_permission_query",
}

has_permission = {
    "Vault Secret": "frappe_vault.utils.permissions.has_secret_permission",
    "Vault Folder": "frappe_vault.utils.permissions.has_folder_permission",
}
```

### Permission Levels & Hierarchy
1. **System Administrator / Vault Admin**: Has global unrestricted access to all secrets and settings.
2. **Owner**: The user who created the secret or folder has `Full Control`.
3. **Direct User Share (`Vault Share` where `user = session.user`)**: Access level determined by `permission_level` (`View Only`, `View & Copy`, `Edit`, `Full Control`).
4. **Role Share (`Vault Share` where `frappe_role IN (user_roles)`)**: All users possessing the target Frappe Role inherit the shared item access level.
5. **Folder Inheritance**: Secrets placed inside a shared `Vault Folder` automatically inherit the permissions granted on that folder.

---

## 5. Key Services & Domain Logic

### 5.1 Secret Service (`secret_service.py`)
- `get_secrets()`: Lists secrets matching filters (`search`, `folder`, `secret_type`, `bookmarks_only`) with dynamic presence flags (`has_password`, `has_totp`, etc.) and folder metadata.
- `get_secret(name, decrypt=False)`: Fetches a single secret. Sensitive encrypted attributes are only decrypted and returned when `decrypt=True` AND the user has `View & Copy`, `Edit`, or `Full Control` permissions.
- `bulk_move()` / `bulk_delete()`: Move or delete multiple secrets at once, respecting individual permissions.
- `get_totp_code(name)`: Validates the secret's Base32 TOTP key, applies necessary padding, generates the current 6-digit TOTP code via `pyotp.TOTP(secret).now()`, and returns the code with the remaining validity seconds in the 30-second time step.
- `get_vault_stats()`: Computes user-scoped statistics (`total_secrets`, `weak_passwords`, `bookmarks`, `secrets_by_type`, `recent_secrets`). For standard users, SQL queries accurately inspect owned secrets + `Vault Share` direct user shares + role shares + folder shares.

### 5.2 Sharing Service (`sharing_service.py`)
- `share_secret()` / `share_folder()`: Creates or updates a `Vault Share` record. Triggers in-app notification to recipients.
- `revoke_share()`: Sets `is_revoked = 1` on the target share record and updates audit logs. Only owners, original sharers, or Admins can revoke.
- `get_role_users(role)`: Expands a Frappe Role to list all active members possessing that role.
- `get_shares_for_secret()` / `get_shared_with_me()`: Retrieves and consolidates active and revoked shares.
- `save_role_member_permission()`: Manages custom role member overrides.
- `bulk_delete_shares()`: Permanently deletes shares (restricted to owners, sharers, admins).

### 5.3 Security Service (`security_service.py`)
- `calculate_security_score(user=None)`: Evaluates password health for the specified user (or session user). Calculates score out of 100 based on weak/fair password penalty (40%) and rotation staleness (>90 days penalty 30%).

---

## 6. Frontend Architecture & Reactivity

### 6.1 Entry Point & Component Wrapping
The SPA root component [`frontend/src/App.vue`](file:///Users/yakshpurohit/frappe/my-bench/apps/frappe_vault/frontend/src/App.vue#L2) wraps the application inside `<FrappeUIProvider>`:
```html
<template>
  <FrappeUIProvider>
    <div class="flex h-screen w-screen overflow-hidden bg-surface-base">
      <AppSidebar />
      <main class="flex-1 overflow-hidden">
        <router-view />
      </main>
    </div>
  </FrappeUIProvider>
</template>
```

### 6.2 Event-Driven Data Reactivity
To prevent requiring manual browser page refreshes (F5) when data changes across views:
- **`vault-demo-changed`**: Dispatched by `AppSidebar.vue` or `SecretsView.vue` whenever demo data is generated or cleared. `DashboardView.vue` and `SecretsView.vue` listen for this event and call `.reload()` on resources (`dashboardItems`, `scoreResource`, `secrets`, `stats`).
- **`vault-secret-updated`**: Triggered when secrets are edited, updating list views and sidebar stats in real-time.

### 6.3 TOTP Live Countdown Dialog (`TotpDialog.vue`)
Renders a live 6-digit TOTP passcode with a dynamic 30-second progress bar countdown:
- Computes `remainingSeconds` using `30 - (Math.floor(Date.now() / 1000) % 30)`.
- Automatically polls `frappe_vault.api.secrets.get_totp_code` when the countdown timer resets to 30.

---

## 7. Developer & Agent Guidelines for Modifying Code

When implementing fixes or adding features to `frappe_vault`, follow these non-negotiable repository conventions:

1. **Password Field Access**:
   - ❌ **DO NOT USE**: `doc.password` or `doc.totp_secret` directly without checking presence.
   - ✅ **ALWAYS USE**: `doc.get("password")` or `getattr(doc, "totp_secret", None)`.
2. **Base32 & Cryptographic Validation**:
   - All Base32 string processing must strip trailing `=`, uppercase characters, and check `len % 8` in `(0, 2, 4, 5, 7)`. Do not accept equal signs in the middle of seed keys.
3. **Frappe UI Guidelines**:
   - Use standard Frappe UI container layouts (`<div class="space-y-4">`) rather than raw `<form>` tags to conform with Frappe CRM patterns.
   - Catch API errors and iterate over `err.messages?.forEach(msg => toast.error(msg))`.
4. **Security & XSS**:
   - ❌ **DO NOT USE**: `v-html` for rendering user notes or titles.
   - ✅ **ALWAYS USE**: Safe Vue text interpolation `{{ secretData.notes }}`.
5. **Database Queries**:
   - When querying `tabVault Share`, use exact schema column names:
     - `shared_doctype` (NOT `document_type`)
     - `shared_name` (NOT `document_name`)
     - `user` (NOT `shared_with`)
     - `frappe_role` (NOT `shared_with`)
6. **SQL Sanitization**:
   - ❌ **DO NOT USE**: Frontend-provided `order_by` or `search` parameters directly in SQL or ORM queries without allowlisting or stripping wildcards.
   - ✅ **ALWAYS USE**: Parameterized queries (`%s`) instead of f-string interpolation for SQL, especially when injecting user-controlled data like Role names.
7. **Verification Workflow**:
   - Always run linters and unit tests after making changes:
     ```bash
     bench --site library.localhost run-tests --app frappe_vault
     ruff check . && ruff format --check .
     pre-commit run --all-files
     yarn --cwd frontend build
     ```
