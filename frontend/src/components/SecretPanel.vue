<template>
  <aside
    class="fixed inset-y-0 right-0 w-[500px] bg-white border-l shadow-xl flex flex-col z-50"
  >
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b">
      <h2 class="text-lg font-semibold text-gray-900">Secret Details</h2>
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="startEdit" v-if="!isEditing">
          <FeatherIcon name="edit-2" class="w-4 h-4" />
        </Button>
        <Dropdown :options="menuOptions">
          <Button variant="ghost">
            <FeatherIcon name="more-vertical" class="w-4 h-4" />
          </Button>
        </Dropdown>
        <Button variant="ghost" @click="$emit('close')">
          <FeatherIcon name="x" class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="secret.loading" class="flex-1 flex items-center justify-center">
      <LoadingText />
    </div>

    <!-- Content -->
    <div v-else-if="secret.data" class="flex-1 overflow-auto p-6 space-y-6">
      <!-- Title section -->
      <div class="flex items-start gap-4">
        <SecretTypeIcon :type="secret.data.secret_type" class="!w-12 !h-12" />
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <h3 class="text-xl font-semibold text-gray-900">
              {{ isEditing ? '' : secret.data.title }}
            </h3>
            <Button
              v-if="!isEditing"
              variant="ghost"
              size="sm"
              @click="toggleFavorite"
            >
              <FeatherIcon
                name="star"
                class="w-4 h-4"
                :class="secret.data.is_favorite ? 'text-yellow-400 fill-yellow-400' : 'text-gray-400'"
              />
            </Button>
          </div>
          <p class="text-sm text-gray-500">{{ secret.data.secret_type }}</p>
        </div>
      </div>

      <!-- Edit mode -->
      <div v-if="isEditing" class="space-y-4">
        <FormControl v-model="editForm.title" label="Title" :required="true" />
        <FormControl
          v-model="editForm.secret_type"
          label="Secret Type"
          type="select"
          :options="secretTypeOptions"
        />
        <FormControl v-model="editForm.url" label="URL" />
        <FormControl v-model="editForm.username" label="Username" />
        <div class="relative">
          <FormControl
            v-model="editForm.password"
            label="Password"
            :type="showPassword ? 'text' : 'password'"
          />
          <Button
            variant="ghost"
            size="sm"
            class="absolute right-2 top-7"
            @click="showPassword = !showPassword"
          >
            <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
          </Button>
        </div>
        <FormControl v-model="editForm.notes" label="Notes" type="textarea" :rows="3" />
      </div>

      <!-- View mode -->
      <template v-else>
        <!-- Credentials section -->
        <div class="space-y-4">
          <SecretField
            v-if="secret.data.url"
            label="URL"
            :value="secret.data.url"
            icon="globe"
            copyable
            linkable
          />

          <SecretField
            v-if="secret.data.username"
            label="Username"
            :value="secret.data.username"
            icon="user"
            copyable
          />

          <SecretField
            v-if="secret.data.password"
            label="Password"
            :value="secret.data.password"
            icon="key"
            copyable
            masked
          />

          <SecretField
            v-if="secret.data.api_key"
            label="API Key"
            :value="secret.data.api_key"
            icon="code"
            copyable
          />

          <SecretField
            v-if="secret.data.api_secret"
            label="API Secret"
            :value="secret.data.api_secret"
            icon="lock"
            copyable
            masked
          />
        </div>

        <!-- Notes -->
        <div v-if="secret.data.notes">
          <h4 class="text-sm font-medium text-gray-500 mb-2">Notes</h4>
          <div class="p-3 bg-gray-50 rounded-lg text-sm text-gray-700 whitespace-pre-wrap">
            {{ secret.data.notes }}
          </div>
        </div>

        <!-- Metadata -->
        <div class="pt-4 border-t space-y-3">
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">Password Strength</span>
            <StrengthBadge :strength="secret.data.password_strength" />
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">Last Accessed</span>
            <span class="text-gray-900">{{ formatDate(secret.data.last_accessed) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">Access Count</span>
            <span class="text-gray-900">{{ secret.data.access_count || 0 }} times</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">Password Changed</span>
            <span class="text-gray-900">{{ formatDate(secret.data.password_last_changed) }}</span>
          </div>
        </div>
      </template>
    </div>

    <!-- Footer -->
    <div class="p-4 border-t flex justify-end gap-2">
      <template v-if="isEditing">
        <Button variant="outline" @click="cancelEdit">Cancel</Button>
        <Button variant="solid" theme="green" @click="saveEdit" :loading="updateSecret.loading">
          Save Changes
        </Button>
      </template>
      <template v-else>
        <Button variant="subtle" @click="copyAllCredentials">
          <template #prefix><FeatherIcon name="copy" class="w-4 h-4" /></template>
          Copy All
        </Button>
        <Button v-if="secret.data?.url" variant="solid" @click="openUrl">
          <template #prefix><FeatherIcon name="external-link" class="w-4 h-4" /></template>
          Open URL
        </Button>
      </template>
    </div>

    <!-- Delete confirmation -->
    <Dialog v-model="showDeleteDialog" :options="{ title: 'Delete Secret' }">
      <template #body-content>
        <p class="text-gray-600">
          Are you sure you want to delete <strong>{{ secret.data?.title }}</strong>? This action cannot be undone.
        </p>
      </template>
      <template #actions>
        <Button variant="outline" @click="showDeleteDialog = false">Cancel</Button>
        <Button variant="solid" theme="red" @click="confirmDelete" :loading="deleteSecret.loading">
          Delete
        </Button>
      </template>
    </Dialog>
  </aside>
</template>

<script setup>
import { ref, watch, reactive } from 'vue'
import {
  Button,
  Dialog,
  Dropdown,
  FeatherIcon,
  FormControl,
  LoadingText,
} from 'frappe-ui'
import { useSecret, useUpdateSecret, useDeleteSecret, useToggleFavorite } from '@/data/vault'
import SecretTypeIcon from './SecretTypeIcon.vue'
import SecretField from './SecretField.vue'
import StrengthBadge from './StrengthBadge.vue'

const props = defineProps({
  name: String,
})

const emit = defineEmits(['close', 'updated', 'deleted'])

const secret = useSecret(props.name)
const updateSecret = useUpdateSecret()
const deleteSecret = useDeleteSecret()
const toggleFavoriteResource = useToggleFavorite()

const isEditing = ref(false)
const showPassword = ref(false)
const showDeleteDialog = ref(false)

const editForm = reactive({
  title: '',
  secret_type: '',
  url: '',
  username: '',
  password: '',
  notes: '',
})

const secretTypeOptions = [
  { label: 'Password', value: 'Password' },
  { label: 'API Key', value: 'API Key' },
  { label: 'Note', value: 'Note' },
  { label: 'Card', value: 'Card' },
  { label: 'SSH Key', value: 'SSH Key' },
]

const menuOptions = [
  { label: 'Edit', icon: 'edit-2', onClick: () => startEdit() },
  { label: 'Delete', icon: 'trash-2', onClick: () => (showDeleteDialog.value = true) },
]

// Watch for name changes
watch(() => props.name, (newName) => {
  if (newName) {
    secret.submit({ name: newName })
    isEditing.value = false
  }
}, { immediate: true })

function startEdit() {
  editForm.title = secret.data.title
  editForm.secret_type = secret.data.secret_type
  editForm.url = secret.data.url
  editForm.username = secret.data.username
  editForm.password = secret.data.password || ''
  editForm.notes = secret.data.notes
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  showPassword.value = false
}

async function saveEdit() {
  await updateSecret.submit({
    name: props.name,
    ...editForm,
  })
  isEditing.value = false
  secret.reload()
  emit('updated')
}

async function toggleFavorite() {
  await toggleFavoriteResource.submit({ name: props.name })
  secret.reload()
  emit('updated')
}

async function confirmDelete() {
  await deleteSecret.submit({ name: props.name })
  showDeleteDialog.value = false
  emit('deleted')
}

function openUrl() {
  if (secret.data?.url) {
    window.open(secret.data.url, '_blank')
  }
}

function copyAllCredentials() {
  const data = secret.data
  const parts = []
  if (data.username) parts.push(`Username: ${data.username}`)
  if (data.password) parts.push(`Password: ${data.password}`)
  if (data.api_key) parts.push(`API Key: ${data.api_key}`)
  if (data.api_secret) parts.push(`API Secret: ${data.api_secret}`)
  navigator.clipboard.writeText(parts.join('\n'))
}

function formatDate(date) {
  if (!date) return 'Never'
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>
