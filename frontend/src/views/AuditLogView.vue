<template>
  <div class="flex-1 overflow-auto p-6">
    <h1 class="text-xl font-semibold text-gray-900 mb-4">Audit Log</h1>
    <div v-if="logs.loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-12 bg-gray-100 rounded animate-pulse" />
    </div>
    <div v-else-if="logList.length" class="bg-white rounded-xl border divide-y">
      <div v-for="log in logList" :key="log.name" class="flex items-center px-4 py-3">
        <div class="w-8 h-8 rounded-full flex items-center justify-center mr-3" :class="actionColors[log.action] || 'bg-gray-100'">
          <FeatherIcon :name="actionIcons[log.action] || 'activity'" class="w-4 h-4" />
        </div>
        <div class="flex-1">
          <p class="text-sm">
            <span class="font-medium">{{ log.user }}</span>
            {{ log.action.toLowerCase() }}
            <span v-if="getSecretLabel(log)" class="font-medium text-gray-900">{{ getSecretLabel(log) }}</span>
          </p>
          <p class="text-xs text-gray-400">{{ formatTime(log.timestamp) }} · {{ log.ip_address }}</p>
        </div>
      </div>
    </div>
    <EmptyState v-else icon="activity" title="No audit logs" description="Activity will be tracked here" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useAuditLogs } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'

const logs = useAuditLogs()
const logList = computed(() => logs.data?.logs || [])

const actionIcons = { Viewed: 'eye', Created: 'plus-circle', Updated: 'edit', Deleted: 'trash-2', Shared: 'share', Copied: 'copy', Generated: 'refresh-cw' }
const actionColors = { Created: 'bg-green-100', Deleted: 'bg-red-100', Shared: 'bg-blue-100', Viewed: 'bg-gray-100' }

function getSecretLabel(log) {
  if (log.secret) {
    return log.secret
  }
  if (log.details) {
    try {
      const detailsObj = typeof log.details === 'string' ? JSON.parse(log.details) : log.details
      if (detailsObj.title && detailsObj.deleted_secret_name) {
        return `${detailsObj.title} (${detailsObj.deleted_secret_name})`
      }
      if (detailsObj.title) {
        return detailsObj.title
      }
      if (detailsObj.deleted_secret_name) {
        return detailsObj.deleted_secret_name
      }
    } catch (e) {
      console.error('Failed to parse log details:', e)
    }
  }
  return ''
}

function formatTime(dt) { return dt ? new Date(dt).toLocaleString() : '' }
</script>
