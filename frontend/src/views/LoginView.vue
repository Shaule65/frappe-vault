<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto vault-gradient rounded-2xl flex items-center justify-center mb-4">
          <FeatherIcon name="lock" class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-gray-900">Frappe Vault</h1>
        <p class="text-gray-500 mt-1">Secure password management</p>
      </div>

      <!-- Login form -->
      <div class="bg-white rounded-xl shadow-sm border p-8">
        <form @submit.prevent="handleLogin">
          <div class="space-y-4">
            <FormControl
              v-model="email"
              label="Email"
              type="email"
              placeholder="your@email.com"
              :required="true"
            />
            <FormControl
              v-model="password"
              label="Password"
              type="password"
              placeholder="••••••••"
              :required="true"
            />
          </div>

          <ErrorMessage v-if="error" :message="error" class="mt-4" />

          <Button
            type="submit"
            variant="solid"
            theme="green"
            class="w-full mt-6"
            :loading="loading"
          >
            Sign In
          </Button>
        </form>
      </div>

      <p class="text-center text-sm text-gray-500 mt-6">
        <a href="/app" class="text-vault-600 hover:underline">Go to Desk →</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FormControl, FeatherIcon, ErrorMessage } from 'frappe-ui'
import { session } from '@/data/session'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''

  const result = await session.login(email.value, password.value)

  if (!result.success) {
    error.value = result.error
  }

  loading.value = false
}
</script>
