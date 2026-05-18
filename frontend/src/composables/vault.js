/**
 * Composables for Frappe Vault data fetching.
 * Uses createResource / createListResource from frappe-ui.
 */
import { createResource, createListResource } from 'frappe-ui'
import { ref, reactive } from 'vue'

// --- Secrets ---
export function useSecrets(initialFilters = {}) {
  return createResource({
    url: 'frappe_vault.api.secrets.list',
    params: initialFilters,
    auto: true,
    cache: 'vault-secrets',
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

export function useCreateFolder() {
  return createResource({
    url: 'frappe_vault.api.folders.create',
  })
}

// --- Sharing ---
export function useShareSecret() {
  return createResource({
    url: 'frappe_vault.api.sharing.share',
  })
}

export function useSharedWithMe() {
  return createResource({
    url: 'frappe_vault.api.sharing.shared_with_me',
    auto: true,
    cache: 'vault-shared',
  })
}

export function useSecretShares(secretName) {
  return createResource({
    url: 'frappe_vault.api.sharing.get_shares',
    params: { secret_name: secretName },
    auto: !!secretName,
  })
}

export function useCreateOneTimeLink() {
  return createResource({
    url: 'frappe_vault.api.sharing.create_one_time_link',
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
