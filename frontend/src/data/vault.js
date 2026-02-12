import { createResource, createListResource } from 'frappe-ui'

// Stats for dashboard
export function useStats() {
  return createResource({
    url: 'frappe_vault.api.get_stats',
    auto: true,
    cache: 'vault-stats',
  })
}

// Get all secrets with optional filters
export function useSecrets(options = {}) {
  return createResource({
    url: 'frappe_vault.api.get_secrets',
    params: options,
    auto: true,
    cache: 'vault-secrets',
  })
}

// Get single secret with decrypted data
export function useSecret(name) {
  return createResource({
    url: 'frappe_vault.api.get_secret',
    params: { name },
    auto: !!name,
  })
}

// Create new secret
export function useCreateSecret() {
  return createResource({
    url: 'frappe_vault.api.create_secret',
    auto: false,
  })
}

// Update secret
export function useUpdateSecret() {
  return createResource({
    url: 'frappe_vault.api.update_secret',
    auto: false,
  })
}

// Delete secret
export function useDeleteSecret() {
  return createResource({
    url: 'frappe_vault.api.delete_secret',
    auto: false,
  })
}

// Toggle favorite
export function useToggleFavorite() {
  return createResource({
    url: 'frappe_vault.api.toggle_favorite',
    auto: false,
  })
}

// Get categories
export function useCategories() {
  return createResource({
    url: 'frappe_vault.api.get_categories',
    auto: true,
    cache: 'vault-categories',
  })
}

// Password generator
export function usePasswordGenerator() {
  return createResource({
    url: 'frappe_vault.api.generate_password',
    auto: false,
  })
}

// Security score
export function useSecurityScore() {
  return createResource({
    url: 'frappe_vault.api.get_security_score',
    auto: true,
    cache: 'vault-security-score',
  })
}
