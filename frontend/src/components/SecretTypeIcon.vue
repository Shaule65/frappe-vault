<template>
  <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" :class="colorClass">
    <FeatherIcon :name="iconName" class="w-4 h-4" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { typeIcons, typeColors } from '../composables/constants'

const props = defineProps({
  type: {
    type: String,
    default: 'Other',
  },
})

const iconName = computed(() => typeIcons[props.type] || 'file')
const colorClass = computed(() => typeColors[props.type] || 'bg-surface-gray-3 text-ink-gray-6')
</script>
