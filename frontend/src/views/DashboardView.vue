<template>
  <div class="flex-1 overflow-auto p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-500 mt-1">Overview of your vault</p>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <StatCard
        title="Total Secrets"
        :value="stats.data?.total_secrets || 0"
        icon="key"
        color="blue"
      />
      <StatCard
        title="Favorites"
        :value="stats.data?.favorites_count || 0"
        icon="star"
        color="yellow"
      />
      <StatCard
        title="Categories"
        :value="stats.data?.categories_count || 0"
        icon="folder"
        color="purple"
      />
      <StatCard
        title="Security Score"
        :value="securityScore.data?.score || 0"
        suffix="%"
        icon="shield"
        :color="getScoreColor(securityScore.data?.score)"
      />
    </div>

    <!-- Security Overview -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Security breakdown -->
      <div class="vault-card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Security Overview</h3>
        <div v-if="securityScore.data" class="space-y-4">
          <SecurityMetric
            label="Strong Passwords"
            :value="securityScore.data?.strong_passwords || 0"
            :total="stats.data?.total_secrets || 0"
            color="green"
          />
          <SecurityMetric
            label="Weak Passwords"
            :value="securityScore.data?.weak_passwords || 0"
            :total="stats.data?.total_secrets || 0"
            color="red"
          />
          <SecurityMetric
            label="Old Passwords (90+ days)"
            :value="securityScore.data?.old_passwords || 0"
            :total="stats.data?.total_secrets || 0"
            color="orange"
          />
          <SecurityMetric
            label="Reused Passwords"
            :value="securityScore.data?.reused_passwords || 0"
            :total="stats.data?.total_secrets || 0"
            color="yellow"
          />
        </div>
        <LoadingText v-else />
      </div>

      <!-- Recent activity -->
      <div class="vault-card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Recently Accessed</h3>
        <div v-if="recentSecrets.length" class="space-y-3">
          <router-link
            v-for="secret in recentSecrets"
            :key="secret.name"
            :to="`/secrets/${secret.name}`"
            class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <SecretTypeIcon :type="secret.secret_type" />
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 truncate">{{ secret.title }}</p>
              <p class="text-sm text-gray-500">{{ formatDate(secret.last_accessed) }}</p>
            </div>
          </router-link>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          <FeatherIcon name="clock" class="w-8 h-8 mx-auto mb-2 text-gray-300" />
          <p>No recent activity</p>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="vault-card p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div class="flex flex-wrap gap-3">
        <Button variant="subtle" @click="$router.push('/secrets?new=1')">
          <template #prefix><FeatherIcon name="plus" class="w-4 h-4" /></template>
          Add Secret
        </Button>
        <Button variant="subtle" @click="$router.push('/generator')">
          <template #prefix><FeatherIcon name="refresh-cw" class="w-4 h-4" /></template>
          Generate Password
        </Button>
        <Button variant="subtle" @click="$router.push('/categories')">
          <template #prefix><FeatherIcon name="folder-plus" class="w-4 h-4" /></template>
          Manage Categories
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Button, FeatherIcon, LoadingText } from 'frappe-ui'
import { useStats, useSecurityScore, useSecrets } from '@/data/vault'
import StatCard from '@/components/StatCard.vue'
import SecurityMetric from '@/components/SecurityMetric.vue'
import SecretTypeIcon from '@/components/SecretTypeIcon.vue'

const stats = useStats()
const securityScore = useSecurityScore()
const secretsResource = useSecrets({ limit: 5 })

const recentSecrets = computed(() => {
  return (secretsResource.data?.secrets || []).slice(0, 5)
})

function getScoreColor(score) {
  if (!score) return 'gray'
  if (score >= 80) return 'green'
  if (score >= 60) return 'yellow'
  if (score >= 40) return 'orange'
  return 'red'
}

function formatDate(date) {
  if (!date) return 'Never'
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
