<template>
  <aside class="w-[480px] border-l bg-white flex flex-col fixed right-0 top-0 h-full z-20 shadow-xl">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b">
      <h2 class="font-semibold text-lg text-gray-900 truncate">{{ secretData?.title }}</h2>
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="handleDelete" theme="red">
          <FeatherIcon name="trash-2" class="w-4 h-4" />
        </Button>
        <Button variant="ghost" @click="$emit('close')">
          <FeatherIcon name="x" class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b">
      <button v-for="tab in tabs" :key="tab.name" class="flex-1 px-4 py-2.5 text-sm font-medium transition-colors"
        :class="activeTab === tab.name ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'"
        @click="activeTab = tab.name">
        {{ tab.label }}
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-auto p-4">
      <!-- Details Tab -->
      <div v-if="activeTab === 'details'" class="space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <p class="text-xs text-gray-500 mb-1">Type</p>
            <Badge>{{ secretData?.secret_type }}</Badge>
          </div>
          <div v-if="secretData?.folder">
            <p class="text-xs text-gray-500 mb-1">Folder</p>
            <p class="text-sm">{{ secretData.folder }}</p>
          </div>
        </div>

        <div v-if="secretData?.url">
          <p class="text-xs text-gray-500 mb-1">URL</p>
          <a :href="secretData.url" target="_blank" class="text-sm text-blue-600 hover:underline">{{ secretData.url }}</a>
        </div>

        <div v-if="secretData?.username">
          <p class="text-xs text-gray-500 mb-1">Username</p>
          <div class="flex items-center gap-2">
            <p class="text-sm font-mono">{{ secretData.username }}</p>
            <Button variant="ghost" size="sm" @click="copyField(secretData.username, 'username')">
              <FeatherIcon name="copy" class="w-3 h-3" />
            </Button>
          </div>
        </div>

        <!-- Password field with reveal -->
        <div v-if="secretData?.secret_type === 'Password'">
          <p class="text-xs text-gray-500 mb-1">Password</p>
          <div class="flex items-center gap-2 bg-gray-50 rounded-lg p-2">
            <p class="flex-1 text-sm font-mono">{{ showPassword ? decryptedData?.password : '••••••••••••' }}</p>
            <Button variant="ghost" size="sm" @click="togglePassword">
              <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-3 h-3" />
            </Button>
            <Button variant="ghost" size="sm" @click="copyPassword">
              <FeatherIcon name="copy" class="w-3 h-3" />
            </Button>
          </div>
          <div v-if="clipboard.copied.value" class="text-xs text-green-600 mt-1">
            Copied! Auto-clearing in {{ clipboard.countdown.value }}s
          </div>
        </div>

        <div v-if="secretData?.notes" class="mt-4">
          <p class="text-xs text-gray-500 mb-1">Notes</p>
          <div class="text-sm prose prose-sm max-w-none" v-html="secretData.notes" />
        </div>

        <div v-if="secretData?.password_strength" class="mt-4">
          <p class="text-xs text-gray-500 mb-1">Strength</p>
          <PasswordStrength :level="secretData.password_strength" />
        </div>
      </div>

      <!-- Activity Tab -->
      <div v-else-if="activeTab === 'activity'" class="space-y-3">
        <div v-if="activity.loading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="h-12 bg-gray-100 rounded animate-pulse" />
        </div>
        <div v-else-if="activityList.length" v-for="item in activityList" :key="item.name" class="flex items-start gap-3">
          <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
            <FeatherIcon :name="actionIcons[item.action] || 'activity'" class="w-4 h-4 text-gray-500" />
          </div>
          <div>
            <p class="text-sm"><span class="font-medium">{{ item.user }}</span> {{ item.action.toLowerCase() }} this secret</p>
            <p class="text-xs text-gray-400">{{ formatTime(item.timestamp) }}</p>
          </div>
        </div>
        <EmptyState v-else icon="activity" title="No activity yet" />
      </div>

      <!-- Sharing Tab -->
      <div v-else-if="activeTab === 'sharing'" class="space-y-3">
        <Button variant="outline" class="w-full" @click="showShareDialog = true">
          <FeatherIcon name="user-plus" class="w-4 h-4" />
          Share Secret
        </Button>
        <p class="text-xs text-gray-500">Sharing functionality coming soon.</p>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button, Badge, FeatherIcon } from 'frappe-ui'
import { useSecret, useDecryptSecret, useSecretActivity, useDeleteSecret } from '../composables/vault'
import { useClipboard } from '../composables/clipboard'
import EmptyState from './EmptyState.vue'
import PasswordStrength from './PasswordStrength.vue'

const props = defineProps({ name: { type: String, required: true } })
const emit = defineEmits(['close', 'updated', 'deleted'])

const activeTab = ref('details')
const showPassword = ref(false)
const showShareDialog = ref(false)

const secret = useSecret(props.name)
const decryptResource = useDecryptSecret()
const activity = useSecretActivity(props.name)
const deleteResource = useDeleteSecret()
const clipboard = useClipboard()

const secretData = computed(() => secret.data)
const decryptedData = computed(() => decryptResource.data?.decrypted)
const activityList = computed(() => activity.data || [])

const tabs = [
  { name: 'details', label: 'Details' },
  { name: 'activity', label: 'Activity' },
  { name: 'sharing', label: 'Sharing' },
]

const actionIcons = { Viewed: 'eye', Created: 'plus', Updated: 'edit', Deleted: 'trash', Shared: 'share', Copied: 'copy' }

watch(() => props.name, (n) => {
  if (n) { secret.submit({ name: n }); activity.submit({ secret_name: n }); showPassword.value = false }
})

async function togglePassword() {
  if (!showPassword.value && !decryptedData.value) {
    await decryptResource.submit({ name: props.name })
  }
  showPassword.value = !showPassword.value
}

async function copyPassword() {
  if (!decryptedData.value) await decryptResource.submit({ name: props.name })
  if (decryptedData.value?.password) clipboard.copy(decryptedData.value.password)
}

function copyField(value) { clipboard.copy(value) }

function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleString()
}

async function handleDelete() {
  if (confirm('Are you sure you want to delete this secret?')) {
    await deleteResource.submit({ name: props.name })
    emit('deleted')
  }
}
</script>
