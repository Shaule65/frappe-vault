<template>
  <div class="flex items-center gap-2">
    <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
      <div class="h-full rounded-full transition-all duration-300" :class="barColor" :style="{ width: barWidth }" />
    </div>
    <Badge :theme="badgeTheme" variant="subtle" class="capitalize">{{ level }}</Badge>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'

const props = defineProps({ level: { type: String, default: 'weak' } })

const config = { weak: { width: '20%', color: 'bg-red-500', theme: 'red' }, fair: { width: '40%', color: 'bg-orange-500', theme: 'orange' }, good: { width: '60%', color: 'bg-blue-500', theme: 'blue' }, strong: { width: '80%', color: 'bg-green-500', theme: 'green' }, excellent: { width: '100%', color: 'bg-emerald-500', theme: 'green' } }

const barWidth = computed(() => config[props.level]?.width || '0%')
const barColor = computed(() => config[props.level]?.color || 'bg-gray-400')
const badgeTheme = computed(() => config[props.level]?.theme || 'gray')
</script>
