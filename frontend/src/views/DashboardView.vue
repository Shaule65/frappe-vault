<template>
  <div class="flex-1 overflow-auto p-6">
    <div class="flex items-center gap-2 mb-6">
      <Button
        class="size-7 sm:hidden flex items-center justify-center p-0 mr-1 focus:outline-none shrink-0"
        variant="ghost"
        @click="mobileSidebarOpened = true"
      >
        <template #icon>
          <FeatherIcon name="menu" class="w-4.5 h-4.5 text-ink-gray-9" />
        </template>
      </Button>
      <h1 class="text-2xl font-semibold text-gray-900">Dashboard</h1>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="stat in statCards" :key="stat.label"
           class="bg-white rounded-xl border p-5 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="stat.bgColor">
            <FeatherIcon :name="stat.icon" class="w-5 h-5" :class="stat.iconColor" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
        <p class="text-sm text-gray-500">{{ stat.label }}</p>
      </div>
    </div>

    <!-- Security Score -->
    <div class="bg-white rounded-xl border p-6 mb-8">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Security Score</h2>
      <div class="flex items-center gap-6">
        <div class="relative w-24 h-24">
          <svg class="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="42" stroke="#e5e7eb" stroke-width="8" fill="none" />
            <circle cx="50" cy="50" r="42" :stroke="scoreColor" stroke-width="8" fill="none"
                    stroke-linecap="round" :stroke-dasharray="`${(securityScore?.score || 0) * 2.64} 264`" />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-2xl font-bold">{{ securityScore?.score || 0 }}</span>
          </div>
        </div>
        <div class="flex-1">
          <div v-for="s in securityScore?.suggestions || []" :key="s" class="flex items-center gap-2 mb-2">
            <FeatherIcon name="alert-circle" class="w-4 h-4 text-yellow-500" />
            <p class="text-sm text-gray-600">{{ s }}</p>
          </div>
          <p v-if="!securityScore?.suggestions?.length" class="text-sm text-green-600">
            <FeatherIcon name="check-circle" class="w-4 h-4 inline" /> Your vault is in great shape!
          </p>
        </div>
      </div>
    </div>

    <!-- Recent Secrets -->
    <div class="bg-white rounded-xl border p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Recently Accessed</h2>
      <div v-if="recentSecrets.length" class="divide-y">
        <router-link v-for="s in recentSecrets" :key="s.name" :to="`/secrets?secret=${s.name}`"
                     class="flex items-center py-3 hover:bg-gray-50 rounded px-2 -mx-2 transition-colors">
          <FeatherIcon :name="typeIcons[s.secret_type] || 'file'" class="w-4 h-4 text-gray-400 mr-3" />
          <span class="flex-1 text-sm font-medium">{{ s.title }}</span>
          <span class="text-xs text-gray-400">{{ s.secret_type }}</span>
        </router-link>
      </div>
      <EmptyState v-else icon="clock" title="No recent activity" description="Access a secret to see it here" />
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
