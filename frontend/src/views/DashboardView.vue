<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50/20">
    <!-- Header -->
    <header class="flex h-10.5 items-center justify-between border-b bg-white px-5 py-2.5 shrink-0">
      <div class="flex items-center gap-2 min-w-0 flex-1">
        <!-- Mobile Sidebar Trigger -->
        <Button
          class="size-7 sm:hidden flex items-center justify-center p-0 mr-1 focus:outline-none shrink-0"
          variant="ghost"
          @click="mobileSidebarOpened = true"
        >
          <template #icon>
            <FeatherIcon name="menu" class="w-4.5 h-4.5 text-ink-gray-9" />
          </template>
        </Button>
        <h1 class="text-lg font-medium text-gray-900 truncate">Dashboard</h1>
      </div>
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          iconLeft="refresh-ccw"
          label="Refresh"
          @click="() => { stats.reload(); score.reload() }"
        />
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-y-auto p-5">
      <!-- Stat cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div v-for="stat in statCards" :key="stat.label"
             class="bg-surface-white rounded-lg shadow-sm border border-outline-gray-2 p-5 hover:shadow-md transition-shadow flex flex-col justify-center">
          <p class="text-sm font-medium text-ink-gray-5 mb-1">{{ stat.label }}</p>
          <p class="text-3xl font-semibold text-ink-gray-9">{{ stat.value }}</p>
        </div>
      </div>

      <!-- Security Score -->
      <div class="bg-surface-white rounded-lg shadow-sm border border-outline-gray-2 p-6 mb-8">
        <h2 class="text-base font-medium text-ink-gray-9 mb-4">Security Score</h2>
        <div class="flex flex-col sm:flex-row items-center sm:items-start gap-6">
          <div class="relative w-24 h-24 shrink-0">
            <svg class="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" stroke="#e5e7eb" stroke-width="8" fill="none" />
              <circle cx="50" cy="50" r="42" :stroke="scoreColor" stroke-width="8" fill="none"
                      stroke-linecap="round" :stroke-dasharray="`${(securityScore?.score || 0) * 2.64} 264`" />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-2xl font-bold text-gray-900">{{ securityScore?.score || 0 }}</span>
            </div>
          </div>
          <div class="flex-1 w-full mt-4 sm:mt-0">
            <div v-for="s in securityScore?.suggestions || []" :key="s" class="flex items-start gap-2 mb-3">
              <FeatherIcon name="alert-circle" class="w-4 h-4 mt-0.5 text-yellow-500 shrink-0" />
              <p class="text-sm text-gray-700 leading-tight">{{ s }}</p>
            </div>
            <div v-if="!securityScore?.suggestions?.length" class="flex items-center gap-2">
              <FeatherIcon name="check-circle" class="w-4 h-4 text-green-500" />
              <p class="text-sm text-gray-700">Your vault is in great shape! No critical security risks detected.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Secrets -->
      <div class="bg-surface-white rounded-lg shadow-sm border border-outline-gray-2 p-0 overflow-hidden mb-4">
        <div class="px-5 py-4 border-b border-outline-gray-2">
          <h2 class="text-base font-medium text-ink-gray-9">Recently Accessed</h2>
        </div>
        <div v-if="recentSecrets.length" class="divide-y divide-outline-gray-2">
          <router-link v-for="s in recentSecrets" :key="s.name" :to="`/secrets?secret=${s.name}`"
                       class="flex items-center py-3 px-5 hover:bg-surface-gray-2 transition-colors">
            <div class="w-8 h-8 rounded bg-surface-gray-2 border border-outline-gray-2 flex items-center justify-center mr-3 shrink-0">
              <FeatherIcon :name="typeIcons[s.secret_type] || 'file'" class="w-4 h-4 text-ink-gray-5" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-ink-gray-9 truncate">{{ s.title }}</p>
              <p class="text-xs text-ink-gray-5 truncate">{{ s.secret_type }}</p>
            </div>
            <FeatherIcon name="chevron-right" class="w-4 h-4 text-ink-gray-4 ml-2 shrink-0" />
          </router-link>
        </div>
        <div v-else class="p-8">
          <EmptyState icon="clock" title="No recent activity" description="Access a secret to see it here" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon, Button } from 'frappe-ui'
import { useVaultStats, useSecurityScore } from '../composables/vault'
import { mobileSidebarOpened } from '../composables/sidebar'
import EmptyState from '../components/EmptyState.vue'

const stats = useVaultStats()
const score = useSecurityScore()

const securityScore = computed(() => score.data)
const recentSecrets = computed(() => stats.data?.recent_secrets || [])

const statCards = computed(() => [
  { label: 'Total Secrets', value: stats.data?.total_secrets || 0, icon: 'key', bgColor: 'bg-blue-100', iconColor: 'text-blue-600' },
  { label: 'Favorites', value: stats.data?.favorites || 0, icon: 'star', bgColor: 'bg-yellow-100', iconColor: 'text-yellow-600' },
  { label: 'Weak Passwords', value: stats.data?.weak_passwords || 0, icon: 'alert-triangle', bgColor: 'bg-red-100', iconColor: 'text-red-600' },
  { label: 'Types', value: Object.keys(stats.data?.secrets_by_type || {}).length, icon: 'layers', bgColor: 'bg-purple-100', iconColor: 'text-purple-600' },
])

const typeIcons = { Password: 'key', 'API Key': 'code', Note: 'file-text', 'SSH Key': 'terminal', Certificate: 'shield', 'Credit Card': 'credit-card', Database: 'database' }

const scoreColor = computed(() => {
  const s = securityScore.value?.score || 0
  if (s >= 80) return '#10b981'
  if (s >= 60) return '#3b82f6'
  if (s >= 40) return '#f59e0b'
  return '#ef4444'
})
</script>
