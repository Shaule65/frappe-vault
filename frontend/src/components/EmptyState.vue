<template>
  <div class="flex flex-col items-center justify-center py-12 text-center">
    <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-4">
      <FeatherIcon :name="icon" class="w-6 h-6 text-gray-400" />
    </div>
    <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
    <p v-if="description" class="text-gray-500 mt-1 max-w-sm">{{ description }}</p>
    <div v-if="$slots.actions" class="mt-4">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
  icon: { type: String, default: 'inbox' },
  title: String,
  description: String,
})
</script>
