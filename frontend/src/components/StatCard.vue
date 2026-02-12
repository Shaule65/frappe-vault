<template>
  <div class="vault-card p-4">
    <div class="flex items-center gap-3">
      <div
        class="w-10 h-10 rounded-lg flex items-center justify-center"
        :class="bgColorClass"
      >
        <FeatherIcon :name="icon" class="w-5 h-5" :class="textColorClass" />
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ title }}</p>
        <p class="text-2xl font-bold" :class="textColorClass">
          {{ value }}{{ suffix }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  title: String,
  value: [String, Number],
  suffix: { type: String, default: '' },
  icon: String,
  color: { type: String, default: 'gray' },
})

const colorMap = {
  blue: { bg: 'bg-blue-100', text: 'text-blue-600' },
  green: { bg: 'bg-green-100', text: 'text-green-600' },
  yellow: { bg: 'bg-yellow-100', text: 'text-yellow-600' },
  orange: { bg: 'bg-orange-100', text: 'text-orange-600' },
  red: { bg: 'bg-red-100', text: 'text-red-600' },
  purple: { bg: 'bg-purple-100', text: 'text-purple-600' },
  gray: { bg: 'bg-gray-100', text: 'text-gray-600' },
}

const bgColorClass = computed(() => colorMap[props.color]?.bg || colorMap.gray.bg)
const textColorClass = computed(() => colorMap[props.color]?.text || colorMap.gray.text)
</script>
