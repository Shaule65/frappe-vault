<template>
  <Badge :variant="variant" :theme="theme">
    {{ label }}
  </Badge>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'

const props = defineProps({
  strength: String,
})

const strengthConfig = {
  'Very Strong': { theme: 'green', label: 'Very Strong' },
  Strong: { theme: 'green', label: 'Strong' },
  Good: { theme: 'blue', label: 'Good' },
  Fair: { theme: 'orange', label: 'Fair' },
  Weak: { theme: 'red', label: 'Weak' },
}

const config = computed(() => strengthConfig[props.strength] || { theme: 'gray', label: props.strength })
const theme = computed(() => config.value.theme)
const label = computed(() => config.value.label)
const variant = 'subtle'
</script>
