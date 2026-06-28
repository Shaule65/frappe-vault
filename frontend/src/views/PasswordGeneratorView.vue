<template>
  <div class="flex-1 overflow-auto p-6">
    <h1 class="text-xl font-semibold text-ink-gray-9 mb-6">Password Generator</h1>

    <div class="max-w-xl">
      <div class="bg-surface-elevation-1 rounded-xl border border-outline-gray-2 p-6 mb-6">
        <!-- Generated password display -->
        <div class="bg-surface-gray-2 rounded-lg p-4 mb-4">
          <p class="font-mono text-lg text-ink-gray-9 break-all select-all">{{ generatedPassword || 'Click Generate' }}</p>
        </div>

        <div class="flex gap-3 mb-6">
          <Button variant="solid" class="flex-1" iconLeft="lucide-refresh-cw" label="Generate" @click="handleGenerate" :loading="generator.loading" />
          <Button variant="outline" iconLeft="lucide-copy" :label="clipboard.copied.value ? `Copied (${clipboard.countdown.value}s)` : 'Copy'" @click="handleCopy" :disabled="!generatedPassword" />
        </div>

        <!-- Strength indicator -->
        <div v-if="strength" class="mb-6">
          <PasswordStrength :level="strength.level" />
        </div>

        <!-- Options -->
        <div class="space-y-4">
          <div>
            <label class="text-sm font-medium text-ink-gray-7 mb-2 block">Length: {{ options.length }}</label>
            <input type="range" v-model.number="options.length" min="8" max="128" class="w-full accent-blue-600" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <Checkbox v-model="options.use_uppercase" label="Uppercase (A-Z)" />
            <Checkbox v-model="options.use_lowercase" label="Lowercase (a-z)" />
            <Checkbox v-model="options.use_digits" label="Numbers (0-9)" />
            <Checkbox v-model="options.use_special" label="Special (!@#$)" />
          </div>

          <Checkbox v-model="options.exclude_ambiguous" label="Exclude ambiguous (0OIl1)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Button, FeatherIcon, Checkbox } from 'frappe-ui'
import { useGeneratePassword } from '../composables/vault'
import { useClipboard } from '../composables/clipboard'
import PasswordStrength from '../components/PasswordStrength.vue'

const generator = useGeneratePassword()
const clipboard = useClipboard()

const options = reactive({ length: 20, use_uppercase: true, use_lowercase: true, use_digits: true, use_special: true, exclude_ambiguous: false })

const generatedPassword = computed(() => generator.data?.password || '')
const strength = computed(() => generator.data?.strength)

async function handleGenerate() { await generator.submit(options) }
function handleCopy() { if (generatedPassword.value) clipboard.copy(generatedPassword.value) }
</script>
