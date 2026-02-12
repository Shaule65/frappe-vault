<template>
  <div class="space-y-1">
    <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
      <div
        class="h-full transition-all duration-300 rounded-full"
        :class="strengthClass"
        :style="{ width: `${strengthPercent}%` }"
      />
    </div>
    <p class="text-xs" :class="textClass">{{ strengthLabel }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  password: String,
})

const strength = computed(() => {
  const pwd = props.password || ''
  let score = 0

  if (pwd.length >= 8) score += 1
  if (pwd.length >= 12) score += 1
  if (pwd.length >= 16) score += 1
  if (/[a-z]/.test(pwd)) score += 1
  if (/[A-Z]/.test(pwd)) score += 1
  if (/[0-9]/.test(pwd)) score += 1
  if (/[^a-zA-Z0-9]/.test(pwd)) score += 1

  if (score <= 2) return 'weak'
  if (score <= 4) return 'fair'
  if (score <= 5) return 'good'
  if (score <= 6) return 'strong'
  return 'very-strong'
})

const strengthPercent = computed(() => {
  const map = {
    weak: 20,
    fair: 40,
    good: 60,
    strong: 80,
    'very-strong': 100,
  }
  return map[strength.value] || 0
})

const strengthClass = computed(() => {
  const map = {
    weak: 'bg-red-500',
    fair: 'bg-orange-500',
    good: 'bg-yellow-500',
    strong: 'bg-green-500',
    'very-strong': 'bg-green-600',
  }
  return map[strength.value] || 'bg-gray-300'
})

const textClass = computed(() => {
  const map = {
    weak: 'text-red-600',
    fair: 'text-orange-600',
    good: 'text-yellow-600',
    strong: 'text-green-600',
    'very-strong': 'text-green-700',
  }
  return map[strength.value] || 'text-gray-500'
})

const strengthLabel = computed(() => {
  const map = {
    weak: 'Weak password',
    fair: 'Fair password',
    good: 'Good password',
    strong: 'Strong password',
    'very-strong': 'Very strong password',
  }
  return map[strength.value] || ''
})
</script>
