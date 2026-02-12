<template>
  <div>
    <div class="flex justify-between text-sm mb-1">
      <span class="text-gray-600">{{ label }}</span>
      <span class="font-medium" :class="textClass">{{ value }} / {{ total }}</span>
    </div>
    <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-300"
        :class="bgClass"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  value: Number,
  total: Number,
  color: { type: String, default: 'gray' },
})

const percentage = computed(() => {
  if (!props.total) return 0
  return Math.round((props.value / props.total) * 100)
})

const colorMap = {
  green: { bg: 'bg-green-500', text: 'text-green-600' },
  yellow: { bg: 'bg-yellow-500', text: 'text-yellow-600' },
  orange: { bg: 'bg-orange-500', text: 'text-orange-600' },
  red: { bg: 'bg-red-500', text: 'text-red-600' },
  gray: { bg: 'bg-gray-500', text: 'text-gray-600' },
}

const bgClass = computed(() => colorMap[props.color]?.bg || colorMap.gray.bg)
const textClass = computed(() => colorMap[props.color]?.text || colorMap.gray.text)
</script>
