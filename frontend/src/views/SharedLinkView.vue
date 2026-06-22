<template>
  <div class="min-h-screen w-full bg-gray-50">
    <div class="mx-auto flex min-h-screen w-full max-w-2xl flex-col justify-center px-6 py-10">
      <div class="mb-6 flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white">
          <FeatherIcon name="lock" class="h-5 w-5" />
        </div>
        <div>
          <h1 class="text-xl font-semibold text-gray-900">Shared Vault Secret</h1>
          <p class="text-sm text-gray-500">This link can only be opened within its view and expiry limits.</p>
        </div>
      </div>

      <div class="rounded-lg border bg-white p-5 shadow-sm">
        <div v-if="!secret && !errorMessage" class="space-y-4">
          <div v-if="needsPassphrase">
            <TextInput v-model="passphrase" type="password" placeholder="Enter passphrase" autofocus @keyup.enter="openLink" />
          </div>
          <button
            class="inline-flex h-9 items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="consume.loading"
            @click="openLink"
          >
            {{ consume.loading ? 'Opening...' : 'Open Secret' }}
          </button>
        </div>

        <div v-else-if="errorMessage" class="flex items-start gap-3 rounded-md border border-red-200 bg-red-50 p-4">
          <FeatherIcon name="alert-circle" class="mt-0.5 h-5 w-5 text-red-600" />
          <div>
            <p class="text-sm font-medium text-red-900">Unable to open this link</p>
            <p class="mt-1 text-sm text-red-700">{{ errorMessage }}</p>
          </div>
        </div>

        <div v-else class="space-y-5">
          <div>
            <p class="text-sm text-gray-500">{{ secret.secret_type }}</p>
            <h2 class="text-lg font-semibold text-gray-900">{{ secret.title }}</h2>
          </div>

          <div class="grid gap-3">
            <SecretValue v-if="secret.url" label="URL" :value="secret.url" />
            <SecretValue v-if="secret.username" label="Username" :value="secret.username" />
            <SecretValue v-if="secret.email" label="Email" :value="secret.email" />
            <SecretValue
              v-for="item in decryptedValues"
              :key="item.label"
              :label="item.label"
              :value="item.value"
              sensitive
            />
            <SecretValue v-if="secret.notes" label="Notes" :value="secret.notes" multiline />
          </div>

          <p class="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
            Save what you need now. This link may not work again after the allowed views are used.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { FeatherIcon, TextInput, Button } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { useConsumeOneTimeLink } from '../composables/vault'

const route = useRoute()
const consume = useConsumeOneTimeLink()
const passphrase = ref('')
const needsPassphrase = ref(true)
const secret = ref(null)
const errorMessage = ref('')

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
  try {
    const result = await consume.submit({
      token: token.value,
      passphrase: passphrase.value || undefined,
    })
    secret.value = result
  } catch (error) {
    const message = error?.messages?.[0] || error?.message || 'The link is expired, already consumed, or the passphrase is wrong.'
    errorMessage.value = message
  }
}
</script>

<script>
export default {
  components: {
    SecretValue: {
      props: {
        label: String,
        value: [String, Number],
        sensitive: Boolean,
        multiline: Boolean,
      },
      data() {
        return { visible: !this.sensitive }
      },
      computed: {
        displayValue() {
          if (this.visible) return this.value
          return '••••••••••••'
        },
      },
      template: `
        <div class="rounded-md border border-gray-200 p-3">
          <div class="mb-1 flex items-center justify-between gap-3">
            <span class="text-xs font-medium uppercase text-gray-500">{{ label }}</span>
            <button
              v-if="sensitive"
              class="text-xs font-medium text-blue-600 hover:text-blue-700"
              @click="visible = !visible"
            >
              {{ visible ? 'Hide' : 'Show' }}
            </button>
          </div>
          <pre
            v-if="multiline || String(value).includes('\\n')"
            class="custom-scrollbar max-h-56 overflow-auto whitespace-pre-wrap break-words text-sm text-gray-900"
          >{{ displayValue }}</pre>
          <p v-else class="break-all text-sm text-gray-900">{{ displayValue }}</p>
        </div>
      `,
    },
  },
}
</script>
