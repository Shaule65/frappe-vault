<template>
  <div class="w-full min-w-0 py-3.5 px-4 space-y-1">
    <div class="flex items-center justify-between gap-2">
      <span class="text-[11px] font-medium uppercase tracking-wider text-ink-gray-5">{{ label }}</span>
      <div class="flex items-center gap-1 shrink-0">
        <!-- Copy Button -->
        <Button
          variant="ghost"
          size="sm"
          class="!p-1.5 h-auto text-ink-gray-5 hover:text-ink-gray-9 focus:outline-none"
          :icon="copied ? 'lucide-check' : 'lucide-copy'"
          :class="{ 'text-ink-green-3': copied }"
          :title="copied ? 'Copied!' : 'Copy to clipboard'"
          @click="copyToClipboard"
        />
        <!-- Toggle Mask / Eye Icon -->
        <Button
          v-if="sensitive"
          variant="ghost"
          size="sm"
          class="!p-1.5 h-auto text-ink-gray-5 hover:text-ink-gray-9 focus:outline-none"
          :icon="visible ? 'lucide-eye-off' : 'lucide-eye'"
          :title="visible ? 'Hide value' : 'Show value'"
          @click="visible = !visible"
        />
      </div>
    </div>

    <pre
      v-if="multiline || String(value).includes('\n')"
      class="custom-scrollbar max-h-60 overflow-auto whitespace-pre-wrap break-all font-mono text-sm leading-relaxed text-ink-gray-9 font-normal"
    >{{ displayValue }}</pre>

    <p
      v-else
      class="break-all font-mono text-sm select-all"
      :class="visible ? 'text-ink-gray-9 font-normal' : 'text-ink-gray-5 tracking-wider font-normal'"
    >{{ displayValue }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button } from 'frappe-ui'
import { useClipboard } from '../composables/clipboard'

const props = defineProps({
  label: String,
  value: [String, Number],
  sensitive: Boolean,
  multiline: Boolean,
})

const visible = ref(!props.sensitive)
const clipboard = useClipboard()

const copied = computed(() => clipboard.copied.value)

const displayValue = computed(() => {
  if (visible.value) return props.value
  return '••••••••••••••••'
})

function copyToClipboard() {
  if (!props.value) return
  clipboard.copy(String(props.value))
}
</script>
