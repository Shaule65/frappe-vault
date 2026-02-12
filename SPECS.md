
Prompt for Coding Agent: Project "Frappe Vault"

**Objective**

Build a Frappe-based password and secrets management application inspired by Zoho Vault. The app should allow users to securely store, share, and manage sensitive credentials within their Frappe/ERPNext environment.

**1. Core Data Models (DocTypes)**

-   **Vault Secret:**
    -   Fields:  `title`,  `secret_type`  (Password, API Key, Note),  `url`,  `username`,  `password`  (encrypted),  `notes`,  `category`.
    -   Features: Toggle visibility for password, "Copy to Clipboard" buttons.
-   **Vault Category:**  Simple tree-based DocType to organize secrets (e.g., Social Media, Server SSH, Banking).
-   **Vault Access Log:**  A Read-only DocType to track who accessed/viewed which secret and when.

**2. Security Requirements (Critical)**

-   **Encryption:**  Use Frappe’s built-in  `password`  field type or  `aes_encrypt`  for sensitive data.
-   **Master Password:**  Implement a mechanism where a user must enter a session-based "Master Password" to decrypt and view secrets.
-   **Role-Based Access (RBAC):**  Use Frappe’s standard Permission Manager. Only owners or shared users can see specific secrets.

**3. Key Features to Implement**

-   **Secret Sharing:**  A "Share" feature (using a child table or DocShare) to give specific Users or Roles access to a secret without making it public.
-   **Password Generator:**  A utility function/UI component to generate strong, random passwords.
-   **Dashboard:**  A custom Workspace showing "Recently Used," "Favorites," and "Security Score" (based on password age/strength).

**4. Technical Stack Constraints**

-   **Framework:**  Frappe Framework (v15+ preferred).
-   **UI:**  Use standard Desk UI for the backend; create a clean, minimalist Custom Page for the "Vault View."
-   **API:**  Ensure all secrets are accessible via REST API (for potential future browser extensions).

**Deliverables**

1.  A new Frappe App named  `frappe_vault`.
2.  All necessary DocTypes and Modules.
3.  Client-side scripts for the "Copy to Clipboard" and "Password Masking" functionality.
4.  A basic README on how to install and set the encryption key.

----------

**start by defining the DocType schema for 'Vault Secret' first**