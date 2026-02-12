<template>
  <div class="flex-1 overflow-auto p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
      <p class="text-gray-500 mt-1">Configure your vault preferences</p>
    </div>

    <div class="max-w-2xl space-y-6">
      <!-- Account section -->
      <div class="vault-card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Account</h3>
        <div class="flex items-center gap-4">
          <Avatar :label="session.fullName || session.user" :image="session.userImage" size="xl" />
          <div>
            <p class="font-medium text-gray-900">{{ session.fullName || 'User' }}</p>
            <p class="text-sm text-gray-500">{{ session.user }}</p>
          </div>
        </div>
      </div>

      <!-- Security section -->
      <div class="vault-card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Security</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900">Auto-lock Timeout</p>
              <p class="text-sm text-gray-500">Lock vault after inactivity</p>
            </div>
            <select
              v-model="settings.autoLockTimeout"
              class="px-3 py-2 border rounded-lg bg-white"
            >
              <option value="5">5 minutes</option>
              <option value="15">15 minutes</option>
              <option value="30">30 minutes</option>
              <option value="60">1 hour</option>
              <option value="0">Never</option>
            </select>
          </div>

          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900">Clipboard Auto-clear</p>
              <p class="text-sm text-gray-500">Clear clipboard after copying passwords</p>
            </div>
            <select
              v-model="settings.clipboardTimeout"
              class="px-3 py-2 border rounded-lg bg-white"
            >
              <option value="30">30 seconds</option>
              <option value="60">1 minute</option>
              <option value="120">2 minutes</option>
              <option value="0">Never</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Export/Import section -->
      <div class="vault-card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Data</h3>
        <div class="space-y-3">
          <Button variant="outline" class="w-full justify-start" @click="exportSecrets">
            <template #prefix>
              <FeatherIcon name="download" class="w-4 h-4" />
            </template>
            Export Secrets (JSON)
          </Button>
          <Button variant="outline" class="w-full justify-start" @click="showImportDialog = true">
            <template #prefix>
              <FeatherIcon name="upload" class="w-4 h-4" />
            </template>
            Import Secrets
          </Button>
        </div>
        <p class="text-xs text-gray-400 mt-3">
          Note: Exported files do not include passwords for security reasons.
        </p>
      </div>

      <!-- Danger zone -->
      <div class="vault-card p-6 border-red-200">
        <h3 class="text-lg font-semibold text-red-600 mb-4">Danger Zone</h3>
        <Button variant="outline" theme="red" @click="showDeleteDialog = true">
          <template #prefix>
            <FeatherIcon name="trash-2" class="w-4 h-4" />
          </template>
          Delete All Secrets
        </Button>
      </div>

      <!-- Links -->
      <div class="vault-card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Links</h3>
        <div class="space-y-2">
          <a
            href="/app/vault-settings"
            target="_blank"
            class="flex items-center gap-2 text-vault-600 hover:underline"
          >
            <FeatherIcon name="settings" class="w-4 h-4" />
            Vault Settings (Desk)
          </a>
          <a
            href="/app"
            target="_blank"
            class="flex items-center gap-2 text-vault-600 hover:underline"
          >
            <FeatherIcon name="external-link" class="w-4 h-4" />
            Go to Frappe Desk
          </a>
        </div>
      </div>
    </div>

    <!-- Delete confirmation dialog -->
    <Dialog v-model="showDeleteDialog" :options="{ title: 'Delete All Secrets' }">
      <template #body-content>
        <div class="text-center py-4">
          <div class="w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
            <FeatherIcon name="alert-triangle" class="w-6 h-6 text-red-600" />
          </div>
          <p class="text-gray-600">
            This will permanently delete all your secrets. This action cannot be undone.
          </p>
          <p class="text-sm text-gray-400 mt-2">
            Type <strong>DELETE</strong> to confirm.
          </p>
          <input
            v-model="deleteConfirmation"
            type="text"
            class="mt-3 px-4 py-2 border rounded-lg w-full max-w-xs text-center"
            placeholder="Type DELETE"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showDeleteDialog = false">Cancel</Button>
        <Button
          variant="solid"
          theme="red"
          :disabled="deleteConfirmation !== 'DELETE'"
          @click="deleteAllSecrets"
        >
          Delete All
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Avatar, Button, Dialog, FeatherIcon } from 'frappe-ui'
import { call } from 'frappe-ui'
import { session } from '@/data/session'

const showImportDialog = ref(false)
const showDeleteDialog = ref(false)
const deleteConfirmation = ref('')

const settings = reactive({
  autoLockTimeout: '15',
  clipboardTimeout: '30',
})

async function exportSecrets() {
  try {
    const result = await call('frappe_vault.api.export_secrets', { format: 'json' })
    if (result?.content) {
      const blob = new Blob([result.content], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `vault-export-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
  } catch (e) {
    console.error('Export failed:', e)
  }
}

async function deleteAllSecrets() {
  // This would need a proper API endpoint
  showDeleteDialog.value = false
  deleteConfirmation.value = ''
}
</script>
