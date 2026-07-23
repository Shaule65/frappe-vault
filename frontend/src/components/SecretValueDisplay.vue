<template>
  <div class="w-full min-w-0 py-3.5 px-4 space-y-1">
    <div class="flex items-center justify-between gap-2">
      <span class="text-[11px] font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ label }}</span>
      <div class="flex items-center gap-1 shrink-0">
        <!-- Copy Button -->
        <Button
          variant="ghost"
          size="sm"
          class="!p-1.5 h-auto text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 focus:outline-none"
          :icon="copied ? 'lucide-check' : 'lucide-copy'"
          :class="{ 'text-green-600 dark:text-green-400': copied }"
          :title="copied ? 'Copied!' : 'Copy to clipboard'"
          @click="copyToClipboard"
        />
        <!-- Toggle Mask / Eye Icon -->
        <Button
          v-if="sensitive"
          variant="ghost"
          size="sm"
          class="!p-1.5 h-auto text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 focus:outline-none"
          :icon="visible ? 'lucide-eye-off' : 'lucide-eye'"
          :title="visible ? 'Hide value' : 'Show value'"
          @click="visible = !visible"
        />
      </div>
    </div>

    <pre
      v-if="multiline || String(value).includes('\n')"
      class="custom-scrollbar max-h-60 overflow-auto whitespace-pre-wrap break-all font-mono text-sm leading-relaxed text-gray-900 dark:text-gray-100 font-normal"
    >{{ displayValue }}</pre>
    
    <p
      v-else
      class="break-all font-mono text-sm select-all"
      :class="visible ? 'text-gray-900 font-normal dark:text-gray-100' : 'text-gray-400 tracking-wider font-normal dark:text-gray-500'"
    >{{ displayValue }}</p>
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
const copied = ref(false)

const displayValue = computed(() => {
  if (visible.value) return props.value
  return '••••••••••••••••'
})

function copyToClipboard() {
  if (!props.value) return
  navigator.clipboard.writeText(String(props.value))
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}
</script>
