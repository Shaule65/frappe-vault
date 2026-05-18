<template>
  <div class="flex-1 overflow-auto p-6">
    <h1 class="text-xl font-semibold text-gray-900 mb-4">Shared With Me</h1>
    <div v-if="shared.loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-16 bg-gray-100 rounded-lg animate-pulse" />
    </div>
    <div v-else-if="list.length" class="bg-white rounded-xl border divide-y">
      <div v-for="s in list" :key="s.share_name" class="flex items-center px-4 py-3 hover:bg-gray-50">
        <FeatherIcon name="share-2" class="w-4 h-4 text-blue-500 mr-3" />
        <div class="flex-1"><p class="text-sm font-medium">{{ s.title }}</p><p class="text-xs text-gray-500">{{ s.permission_level }} · from {{ s.shared_by }}</p></div>
        <Badge variant="subtle">{{ s.secret_type }}</Badge>
      </div>
    </div>
    <EmptyState v-else icon="users" title="Nothing shared with you" description="When someone shares a secret with you, it will appear here" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon, Badge } from 'frappe-ui'
import { useSharedWithMe } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'
const shared = useSharedWithMe()
const list = computed(() => shared.data?.shared || [])
</script>
