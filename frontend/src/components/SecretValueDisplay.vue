<template>
  <div class="rounded-md border border-outline-gray-1 p-3 bg-surface-elevation-1">
    <div class="mb-1 flex items-center justify-between gap-3">
      <span class="text-xs font-medium uppercase text-ink-gray-5">{{ label }}</span>
      <Button
        v-if="sensitive"
        variant="ghost"
        class="!p-1 h-auto !text-xs !font-medium text-blue-600 hover:text-blue-700"
        @click="visible = !visible"
      >
        {{ visible ? 'Hide' : 'Show' }}
      </Button>
    </div>
    <pre
      v-if="multiline || String(value).includes('\n')"
      class="custom-scrollbar max-h-56 overflow-auto whitespace-pre-wrap break-words text-sm text-ink-gray-9 font-mono"
    >{{ displayValue }}</pre>
    <p v-else class="break-all text-sm text-ink-gray-9">{{ displayValue }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button } from 'frappe-ui'

const props = defineProps({
  label: String,
  value: [String, Number],
  sensitive: Boolean,
  multiline: Boolean,
})

const visible = ref(!props.sensitive)
const displayValue = computed(() => {
  if (visible.value) return props.value
  return '••••••••••••'
})
</script>
