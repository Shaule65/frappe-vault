<template>
  <div class="flex items-center gap-2">
    <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" :class="colorClass">
      <FeatherIcon :name="iconName" class="w-4 h-4" />
    </div>
    <span v-if="showLabel" class="truncate font-normal">{{ label || type }}</span>
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
  showLabel: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: '',
  },
})

const iconName = computed(() => typeIcons[props.type] || 'file')
const colorClass = computed(() => typeColors[props.type] || 'bg-surface-gray-3 text-ink-gray-6')
</script>
