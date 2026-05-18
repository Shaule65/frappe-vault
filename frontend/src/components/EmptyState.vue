<template>
  <div class="flex flex-col items-center justify-center h-64 text-center p-6">
    <FeatherIcon :name="icon" class="w-12 h-12 text-gray-300 mb-4" />
    <h3 class="font-medium text-gray-700 mb-1">{{ title }}</h3>
    <p class="text-sm text-gray-500 mb-4">{{ description }}</p>
    <slot name="actions" />
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
  icon: { type: String, default: 'inbox' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>
