<template>
  <Badge :variant="variant" :size="size" :theme="themeClass" class="capitalize">
    {{ strength || 'Unknown' }}
  </Badge>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'
import { strengthTheme } from '../composables/constants'

const props = defineProps({
  strength: {
    type: String,
    default: '',
  },
  variant: {
    type: String,
    default: 'subtle',
  },
  size: {
    type: String,
    default: 'sm',
  },
})

const themeClass = computed(() => {
  const key = (props.strength || '').toLowerCase()
  return strengthTheme[key] || 'gray'
})
</script>
