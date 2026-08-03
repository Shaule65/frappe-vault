<template>
  <div class="min-h-screen w-full bg-surface-base text-ink-gray-9 flex flex-col items-center justify-center p-4 overflow-y-auto">
    <div class="w-full max-w-sm my-auto">

      <!-- Passphrase Screen -->
      <div v-if="!secret && needsPassphrase" class="w-full space-y-4">
        <!-- App Vault Logo Header -->
        <div class="flex flex-col items-center text-center mb-1">
          <img
            :src="logoUrl"
            alt="Frappe Vault Logo"
            class="h-10 w-10 object-contain mb-2.5"
          />
          <h1 class="text-xl font-semibold text-ink-gray-9 tracking-tight">Passphrase Required</h1>
          <p class="text-xs text-ink-gray-5 mt-0.5 font-normal">Enter the passphrase to unlock and reveal this secret.</p>
        </div>

        <div class="space-y-3.5">
          <div>
            <label class="block text-xs font-medium text-ink-gray-5 mb-1.5">Passphrase</label>
            <TextInput
              v-model="passphrase"
              type="password"
              placeholder="••••••••"
              autofocus
              class="w-full"
              @keyup.enter="openLink"
            />
            <p v-if="errorMessage" class="text-xs text-ink-red-3 font-medium mt-1">{{ errorMessage }}</p>
          </div>

          <Button
            variant="solid"
            class="w-full font-medium !py-2.5 shadow-2xs"
            :loading="consume.loading"
            @click="openLink"
            label="Unlock Secret"
          />
        </div>
      </div>

      <!-- Expired / Error Card Container (App Logo + ! Alert Icon INSIDE the Box Card) -->
      <div v-else-if="errorMessage" class="w-full min-w-0 bg-surface-base rounded-2xl border border-outline-gray-1 p-6 shadow-2xs text-center space-y-3">
        <!-- Vault App Logo inside the card -->
        <img
          :src="logoUrl"
          alt="Frappe Vault Logo"
          class="h-9 w-9 object-contain mx-auto mb-1"
        />
        <!-- Soft Red Alert Circle Badge -->
        <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-surface-red-1 text-ink-red-3">
          <AlertCircleIcon class="h-5 w-5" />
        </div>
        <div class="space-y-1">
          <h2 class="text-base font-semibold text-ink-gray-9">Unable to Open Link</h2>
          <p class="text-xs text-ink-gray-5 font-normal leading-relaxed">
            {{ errorMessage }}
          </p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="flex flex-col items-center justify-center py-6 space-y-3 text-center">
        <img
          :src="logoUrl"
          alt="Frappe Vault Logo"
          class="h-10 w-10 object-contain"
        />
        <LoaderIcon class="h-6 w-6 animate-spin text-ink-gray-5" />
      </div>

      <!-- Secret Unlocked View (Single Unified Box Card Container) -->
      <div v-else-if="secret" class="space-y-4">
        <!-- Unified Box Card Container -->
        <div class="w-full min-w-0 bg-surface-base rounded-2xl border border-outline-gray-1 shadow-2xs overflow-hidden divide-y divide-outline-gray-1">

          <!-- Header Section inside the box card -->
          <div class="py-4 px-5 text-center bg-surface-gray-2">
            <!-- App Vault Logo inside unlocked card -->
            <img
              :src="logoUrl"
              alt="Frappe Vault Logo"
              class="h-8 w-8 object-contain mx-auto mb-2"
            />
            <span class="inline-flex items-center rounded bg-surface-gray-3 border border-outline-gray-1 px-2.5 py-0.5 text-xs font-medium text-ink-gray-9 mb-1.5">
              {{ secret.secret_type }}
            </span>
            <h2 class="text-base font-semibold text-ink-gray-9 tracking-tight leading-snug">{{ secret.title }}</h2>
            <p class="text-xs text-ink-gray-5 mt-0.5 font-normal">Shared One-Time Secret</p>
          </div>

          <!-- Secret Field Rows inside the box card -->
          <SecretValueDisplay v-if="secret.url" label="URL" :value="secret.url" />
          <SecretValueDisplay v-if="secret.username" label="Username" :value="secret.username" />
          <SecretValueDisplay v-if="secret.email" label="Email" :value="secret.email" />
          <SecretValueDisplay
            v-for="item in decryptedValues"
            :key="item.label"
            :label="item.label"
            :value="item.value"
            sensitive
          />
          <SecretValueDisplay v-if="secret.notes" label="Notes" :value="secret.notes" multiline />
        </div>

        <p class="text-center text-xs text-ink-gray-4 font-normal">
          This one-time link may not remain accessible after viewing.
        </p>
      </div>

      <!-- Footer Disclaimer -->
      <div class="text-center text-xs text-ink-gray-4 pt-4">
        Powered by <span class="font-medium text-ink-gray-7">Frappe Vault</span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { TextInput, Button } from 'frappe-ui'
import LoaderIcon from '~icons/lucide/loader-2'
import AlertCircleIcon from '~icons/lucide/alert-circle'
import { useRoute } from 'vue-router'
import { useConsumeOneTimeLink } from '../composables/vault'
import SecretValueDisplay from '../components/SecretValueDisplay.vue'

const route = useRoute()
const consume = useConsumeOneTimeLink()

const logoUrl = ref('/assets/frappe_vault/images/vault-icon.svg')
const passphrase = ref('')
const needsPassphrase = ref(false)
const secret = ref(null)
const errorMessage = ref('')
const loading = ref(true)

const token = computed(() => route.params.token)

const decryptedValues = computed(() => {
  const data = secret.value?.decrypted || {}
  return Object.entries(data)
    .filter(([, value]) => value)
    .map(([key, value]) => ({
      label: key.replaceAll('_', ' ').replace(/\b\w/g, (char) => char.toUpperCase()),
      value,
    }))
})

async function openLink() {
  errorMessage.value = ''
  loading.value = true
  try {
    const result = await consume.submit({
      token: token.value,
      passphrase: passphrase.value || undefined,
    })
    secret.value = result
    needsPassphrase.value = false
  } catch (error) {
    const message = error?.messages?.[0] || error?.message || 'This link has expired or been consumed'
    if (message.toLowerCase().includes('passphrase')) {
      needsPassphrase.value = true
      errorMessage.value = passphrase.value ? 'Invalid passphrase. Please try again.' : ''
    } else {
      errorMessage.value = message
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (token.value) {
    openLink()
  }
})
</script>
