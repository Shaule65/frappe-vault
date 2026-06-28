<template>
  <div class="flex items-center gap-2">
    <div class="flex-1 h-2 bg-surface-gray-3 rounded-full overflow-hidden">
      <div class="h-full rounded-full transition-all duration-300" :class="[barColor, barWidthClass]" />
    </div>
    <StrengthBadge :strength="level" size="sm" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StrengthBadge from './StrengthBadge.vue'

const props = defineProps({ level: { type: String, default: 'weak' } })

const config = {
  weak: { widthClass: 'w-1/5', color: 'bg-red-500' },
  fair: { widthClass: 'w-2/5', color: 'bg-orange-500' },
  good: { widthClass: 'w-3/5', color: 'bg-blue-500' },
  strong: { widthClass: 'w-4/5', color: 'bg-green-500' },
  excellent: { widthClass: 'w-full', color: 'bg-emerald-500' },
}

const barWidthClass = computed(() => config[props.level]?.widthClass || 'w-0')
const barColor = computed(() => config[props.level]?.color || 'bg-surface-gray-4')
</script>
