<template>
  <div class="flex-1 overflow-auto p-6">
    <h1 class="text-xl font-semibold text-gray-900 mb-4">Favorites</h1>
    <div v-if="secrets.loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-16 bg-gray-100 rounded-lg animate-pulse" />
    </div>
    <div v-else-if="list.length" class="bg-white rounded-xl border divide-y">
      <div v-for="s in list" :key="s.name" class="flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer">
        <FeatherIcon name="star" class="w-4 h-4 text-yellow-500 fill-yellow-500 mr-3" />
        <div class="flex-1"><p class="text-sm font-medium">{{ s.title }}</p><p class="text-xs text-gray-500">{{ s.secret_type }}</p></div>
      </div>
    </div>
    <EmptyState v-else icon="star" title="No favorites yet" description="Star your most-used secrets for quick access" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useSecrets } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'
const secrets = useSecrets({ favorites_only: 1 })
const list = computed(() => secrets.data?.secrets || [])
</script>
