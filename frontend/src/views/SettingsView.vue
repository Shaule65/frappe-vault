<template>
  <div class="flex-1 overflow-auto p-6">
    <h1 class="text-xl font-semibold text-gray-900 mb-6">Settings</h1>
    <div class="max-w-2xl space-y-6">
      <div class="bg-white rounded-xl border p-6">
        <h2 class="text-lg font-medium mb-4">Master Password</h2>
        <p class="text-sm text-gray-500 mb-4">Enable a master password to add an extra layer of protection when viewing or copying secrets.</p>
        <Button variant="outline" @click="window.open('/app/vault-settings', '_blank')">
          <FeatherIcon name="settings" class="w-4 h-4" /> Configure in Desk
        </Button>
      </div>

      <div class="bg-white rounded-xl border p-6">
        <h2 class="text-lg font-medium mb-4">Password Policy</h2>
        <p class="text-sm text-gray-500 mb-4">Set organization-wide password requirements and rotation policies.</p>
        <Button variant="outline" @click="window.open('/app/vault-policy', '_blank')">
          <FeatherIcon name="shield" class="w-4 h-4" /> Manage Policies
        </Button>
      </div>

      <div class="bg-white rounded-xl border p-6">
        <h2 class="text-lg font-medium mb-4">Import / Export</h2>
        <p class="text-sm text-gray-500 mb-4">Import secrets from other password managers or export your vault.</p>
        <div class="flex gap-3">
          <Button variant="outline"><FeatherIcon name="upload" class="w-4 h-4" /> Import</Button>
          <Button variant="outline"><FeatherIcon name="download" class="w-4 h-4" /> Export</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, FeatherIcon } from 'frappe-ui'
</script>
