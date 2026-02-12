<template>
  <div class="flex-1 overflow-auto p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Password Generator</h1>
      <p class="text-gray-500 mt-1">Generate strong, secure passwords</p>
    </div>

    <div class="max-w-2xl">
      <!-- Generated password display -->
      <div class="vault-card p-6 mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="flex-1 relative">
            <input
              :value="generatedPassword"
              :type="showPassword ? 'text' : 'password'"
              readonly
              class="w-full px-4 py-3 text-lg font-mono bg-gray-50 border rounded-lg"
              placeholder="Click generate to create a password"
            />
          </div>
          <Button variant="ghost" @click="showPassword = !showPassword">
            <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-5 h-5" />
          </Button>
          <Button variant="ghost" @click="copyPassword" :disabled="!generatedPassword">
            <FeatherIcon :name="copied ? 'check' : 'copy'" class="w-5 h-5" :class="copied ? 'text-green-500' : ''" />
          </Button>
        </div>

        <PasswordStrengthBar v-if="generatedPassword" :password="generatedPassword" class="mb-4" />

        <Button
          variant="solid"
          theme="green"
          class="w-full"
          @click="generate"
          :loading="passwordGenerator.loading"
        >
          <template #prefix>
            <FeatherIcon name="refresh-cw" class="w-4 h-4" />
          </template>
          Generate Password
        </Button>
      </div>

      <!-- Options -->
      <div class="vault-card p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Options</h3>

        <div class="space-y-6">
          <!-- Length slider -->
          <div>
            <div class="flex justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">Password Length</label>
              <span class="text-sm font-mono text-vault-600">{{ options.length }}</span>
            </div>
            <input
              type="range"
              v-model.number="options.length"
              min="8"
              max="64"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-vault-500"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>8</span>
              <span>64</span>
            </div>
          </div>

          <!-- Character options -->
          <div class="space-y-3">
            <label class="text-sm font-medium text-gray-700">Include Characters</label>
            
            <div class="grid grid-cols-2 gap-3">
              <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  v-model="options.use_uppercase"
                  class="rounded border-gray-300 text-vault-600 focus:ring-vault-500"
                />
                <div>
                  <span class="text-sm font-medium text-gray-700">Uppercase</span>
                  <span class="text-xs text-gray-400 ml-2">A-Z</span>
                </div>
              </label>

              <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  v-model="options.use_lowercase"
                  class="rounded border-gray-300 text-vault-600 focus:ring-vault-500"
                />
                <div>
                  <span class="text-sm font-medium text-gray-700">Lowercase</span>
                  <span class="text-xs text-gray-400 ml-2">a-z</span>
                </div>
              </label>

              <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  v-model="options.use_digits"
                  class="rounded border-gray-300 text-vault-600 focus:ring-vault-500"
                />
                <div>
                  <span class="text-sm font-medium text-gray-700">Numbers</span>
                  <span class="text-xs text-gray-400 ml-2">0-9</span>
                </div>
              </label>

              <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  v-model="options.use_special"
                  class="rounded border-gray-300 text-vault-600 focus:ring-vault-500"
                />
                <div>
                  <span class="text-sm font-medium text-gray-700">Symbols</span>
                  <span class="text-xs text-gray-400 ml-2">!@#$%</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Additional options -->
          <label class="flex items-center gap-3">
            <input
              type="checkbox"
              v-model="options.exclude_ambiguous"
              class="rounded border-gray-300 text-vault-600 focus:ring-vault-500"
            />
            <div>
              <span class="text-sm font-medium text-gray-700">Exclude ambiguous characters</span>
              <span class="text-xs text-gray-400 block">Avoids l, 1, I, O, 0 etc.</span>
            </div>
          </label>
        </div>
      </div>

      <!-- Password history -->
      <div v-if="history.length" class="vault-card p-6 mt-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Recent Passwords</h3>
          <Button variant="ghost" size="sm" @click="history = []">Clear</Button>
        </div>
        <div class="space-y-2">
          <div
            v-for="(pwd, idx) in history"
            :key="idx"
            class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg group"
          >
            <code class="flex-1 text-sm font-mono text-gray-600 truncate">
              {{ pwd }}
            </code>
            <Button
              variant="ghost"
              size="sm"
              class="opacity-0 group-hover:opacity-100"
              @click="copyHistoryPassword(pwd)"
            >
              <FeatherIcon name="copy" class="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import { usePasswordGenerator } from '@/data/vault'
import PasswordStrengthBar from '@/components/PasswordStrengthBar.vue'

const passwordGenerator = usePasswordGenerator()

const generatedPassword = ref('')
const showPassword = ref(true)
const copied = ref(false)
const history = ref([])

const options = reactive({
  length: 20,
  use_uppercase: true,
  use_lowercase: true,
  use_digits: true,
  use_special: true,
  exclude_ambiguous: false,
})

async function generate() {
  const result = await passwordGenerator.submit(options)
  if (result?.password) {
    generatedPassword.value = result.password
    // Add to history (max 5)
    history.value.unshift(result.password)
    if (history.value.length > 5) {
      history.value.pop()
    }
  }
}

function copyPassword() {
  if (generatedPassword.value) {
    navigator.clipboard.writeText(generatedPassword.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}

function copyHistoryPassword(pwd) {
  navigator.clipboard.writeText(pwd)
}

// Generate initial password
generate()
</script>
