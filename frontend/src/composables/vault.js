/**
 * Composables for Frappe Vault data fetching.
 * Uses createResource from frappe-ui.
 */
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

export const mobileSidebarOpened = ref(false)

// --- Secrets ---
export function useSecrets(initialFilters = {}) {
  return createResource({
    url: 'frappe_vault.api.secrets.list',
    params: initialFilters,
    auto: false,
  })
}

export function useSecret(name) {
  return createResource({
    url: 'frappe_vault.api.secrets.get',
    params: { name },
    auto: !!name,
  })
}

export function useDecryptSecret() {
  return createResource({
    url: 'frappe_vault.api.secrets.decrypt',
    makeParams: ({ name }) => ({ name }),
  })
}

export function useCreateSecret() {
  return createResource({
    url: 'frappe_vault.api.secrets.create',
  })
}

export function useUpdateSecret() {
  return createResource({
    url: 'frappe_vault.api.secrets.update',
  })
}

export function useDeleteSecret() {
  return createResource({
    url: 'frappe_vault.api.secrets.delete',
  })
}

export function useToggleFavorite() {
  return createResource({
    url: 'frappe_vault.api.secrets.toggle_favorite',
  })
}

export function useVaultStats() {
  return createResource({
    url: 'frappe_vault.api.secrets.stats',
    auto: true,
    cache: 'vault-stats',
  })
}

// --- Folders ---
export function useFolders() {
  return createResource({
    url: 'frappe_vault.api.folders.get_all',
    auto: true,
    cache: 'vault-folders',
  })
}

export function useFolderSecrets() {
  return createResource({
    url: 'frappe_vault.api.folders.get_folder_secrets',
    makeParams: ({ folder_name }) => ({ folder_name, limit: 1 }),
  })
}

export function useCreateFolder() {
  return createResource({
    url: 'frappe_vault.api.folders.create',
  })
}

export function useDeleteFolder() {
  return createResource({
    url: 'frappe_vault.api.folders.delete',
  })
}

export function useUpdateFolder() {
  return createResource({
    url: 'frappe_vault.api.folders.update',
  })
}

// --- Sharing ---
export function useShareSecret() {
  return createResource({
    url: 'frappe_vault.api.sharing.share',
  })
}

export function useUnshare() {
  return createResource({
    url: 'frappe_vault.api.sharing.unshare',
  })
}

export function useSharedWithMe() {
  return createResource({
    url: 'frappe_vault.api.sharing.shared_with_me',
    auto: true,
    cache: 'vault-shared',
  })
}

export function useShareOptions() {
  return createResource({
    url: 'frappe_vault.api.sharing.get_share_options',
    auto: true,
    cache: 'vault-share-options',
  })
}

export function useSecretShares(secretName) {
  return createResource({
    url: 'frappe_vault.api.sharing.get_shares',
    params: { secret_name: secretName },
    auto: !!secretName,
  })
}

export function useBulkDeleteShares() {
  return createResource({
    url: 'frappe_vault.api.sharing.bulk_delete_shares',
  })
}

export function useCreateOneTimeLink() {
  return createResource({
    url: 'frappe_vault.api.sharing.create_one_time_link',
  })
}

export function useConsumeOneTimeLink() {
  return createResource({
    url: 'frappe_vault.api.sharing.consume_link',
  })
}

// --- Generator ---
export function useGeneratePassword() {
  return createResource({
    url: 'frappe_vault.api.generator.generate',
  })
}

export function useCheckStrength() {
  return createResource({
    url: 'frappe_vault.api.generator.check_strength',
  })
}

export function useCheckBreach() {
  return createResource({
    url: 'frappe_vault.api.generator.check_breach',
  })
}

// --- Security ---
export function useSecurityScore() {
  return createResource({
    url: 'frappe_vault.services.security_service.calculate_security_score',
    auto: true,
    cache: 'vault-security-score',
  })
}

// --- Audit ---
export function useAuditLogs(initialParams = {}) {
  return createResource({
    url: 'frappe_vault.api.audit.get_logs',
    params: initialParams,
    auto: true,
  })
}

export function useSecretActivity(secretName) {
  return createResource({
    url: 'frappe_vault.api.audit.get_secret_activity',
    params: { secret_name: secretName },
    auto: !!secretName,
  })
}

export function useVerifyMasterPassword() {
  return createResource({
    url: 'frappe_vault.vault.doctype.vault_settings.vault_settings.verify_master_password',
  })
}

// --- Demo Data ---
export function useGenerateDemoData() {
  return createResource({
    url: 'frappe_vault.api.demo.generate_demo_data',
  })
}

export function useClearDemoData() {
  return createResource({
    url: 'frappe_vault.api.demo.clear_demo_data',
  })
}

