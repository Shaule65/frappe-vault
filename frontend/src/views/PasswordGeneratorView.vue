<template>
  <div class="flex-1 overflow-auto p-6">
    <h1 class="text-xl font-semibold text-gray-900 mb-6">Password Generator</h1>

    <div class="max-w-xl">
      <div class="bg-white rounded-xl border p-6 mb-6">
        <!-- Generated password display -->
        <div class="bg-gray-50 rounded-lg p-4 mb-4">
          <p class="font-mono text-lg text-gray-900 break-all select-all">{{ generatedPassword || 'Click Generate' }}</p>
        </div>

        <div class="flex gap-3 mb-6">
          <Button variant="solid" class="flex-1" @click="handleGenerate" :loading="generator.loading">
            <FeatherIcon name="refresh-cw" class="w-4 h-4" /> Generate
          </Button>
          <Button variant="outline" @click="handleCopy" :disabled="!generatedPassword">
            <FeatherIcon name="copy" class="w-4 h-4" /> {{ clipboard.copied.value ? `Copied (${clipboard.countdown.value}s)` : 'Copy' }}
          </Button>
        </div>

        <!-- Strength indicator -->
        <div v-if="strength" class="mb-6">
          <PasswordStrength :level="strength.level" />
        </div>

        <!-- Options -->
        <div class="space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 mb-2 block">Length: {{ options.length }}</label>
            <input type="range" v-model.number="options.length" min="8" max="128" class="w-full accent-blue-600" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="options.use_uppercase" class="accent-blue-600" /> Uppercase (A-Z)
            </label>
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="options.use_lowercase" class="accent-blue-600" /> Lowercase (a-z)
            </label>
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="options.use_digits" class="accent-blue-600" /> Numbers (0-9)
            </label>
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="options.use_special" class="accent-blue-600" /> Special (!@#$)
            </label>
          </div>

          <label class="flex items-center gap-2 text-sm">
            <input type="checkbox" v-model="options.exclude_ambiguous" class="accent-blue-600" /> Exclude ambiguous (0OIl1)
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
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
