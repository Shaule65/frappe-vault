<template>
  <div class="space-y-1">
    <label class="text-sm font-medium text-gray-500">{{ label }}</label>
    <div class="flex items-center gap-2 p-3 bg-gray-50 rounded-lg group">
      <FeatherIcon :name="icon" class="w-4 h-4 text-gray-400 flex-shrink-0" />
      
      <div class="flex-1 min-w-0">
        <span
          v-if="masked && !isRevealed"
          class="font-mono text-gray-700"
        >
          ••••••••••••
        </span>
        <span
          v-else-if="linkable"
          class="text-vault-600 hover:underline cursor-pointer truncate block"
          @click="openLink"
        >
          {{ value }}
        </span>
        <span v-else class="font-mono text-gray-700 truncate block">
          {{ value }}
        </span>
      </div>

      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          v-if="masked"
          variant="ghost"
          size="sm"
          @click="isRevealed = !isRevealed"
        >
          <FeatherIcon :name="isRevealed ? 'eye-off' : 'eye'" class="w-4 h-4 text-gray-400" />
        </Button>
        <Button
          v-if="copyable"
          variant="ghost"
          size="sm"
          @click="copyValue"
        >
          <FeatherIcon :name="copied ? 'check' : 'copy'" class="w-4 h-4" :class="copied ? 'text-green-500' : 'text-gray-400'" />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  label: String,
  value: String,
  icon: { type: String, default: 'circle' },
  copyable: Boolean,
  masked: Boolean,
  linkable: Boolean,
})

const isRevealed = ref(false)
const copied = ref(false)

function copyValue() {
  navigator.clipboard.writeText(props.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

function openLink() {
  if (props.value) {
    let url = props.value
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url
    }
    window.open(url, '_blank')
  }
}
</script>
