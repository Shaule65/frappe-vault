<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Header -->
    <div class="bg-white border-b px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900">All Secrets</h1>
          <p class="text-sm text-gray-500 mt-0.5">
            {{ secrets.data?.total || 0 }} secrets
          </p>
        </div>
        <Button variant="solid" theme="green" @click="showNewDialog = true">
          <template #prefix><FeatherIcon name="plus" class="w-4 h-4" /></template>
          Add Secret
        </Button>
      </div>

      <!-- Filters -->
      <div class="flex items-center gap-3 mt-4">
        <div class="flex-1 max-w-md">
          <TextInput
            v-model="searchQuery"
            type="search"
            placeholder="Search secrets..."
            :debounce="300"
          >
            <template #prefix>
              <FeatherIcon name="search" class="w-4 h-4 text-gray-400" />
            </template>
          </TextInput>
        </div>

        <Dropdown :options="typeFilterOptions">
          <template #default="{ open }">
            <Button variant="outline" :class="{ 'border-vault-500': filters.secret_type }">
              <FeatherIcon name="filter" class="w-4 h-4" />
              <span>{{ filters.secret_type || 'All Types' }}</span>
              <FeatherIcon name="chevron-down" class="w-4 h-4" />
            </Button>
          </template>
        </Dropdown>

        <Dropdown :options="categoryFilterOptions">
          <template #default="{ open }">
            <Button variant="outline" :class="{ 'border-vault-500': filters.category }">
              <FeatherIcon name="folder" class="w-4 h-4" />
              <span>{{ filters.category || 'All Categories' }}</span>
              <FeatherIcon name="chevron-down" class="w-4 h-4" />
            </Button>
          </template>
        </Dropdown>

        <Button
          v-if="hasFilters"
          variant="ghost"
          @click="clearFilters"
        >
          Clear filters
        </Button>
      </div>
    </div>

    <!-- List -->
    <div class="flex-1 overflow-auto p-6">
      <div v-if="secrets.loading && !secrets.data" class="text-center py-12">
        <LoadingText />
      </div>

      <div v-else-if="secretsList.length" class="space-y-2">
        <SecretRow
          v-for="secret in secretsList"
          :key="secret.name"
          :secret="secret"
          @click="openSecret(secret)"
          @toggle-favorite="handleToggleFavorite"
        />
      </div>

      <EmptyState
        v-else
        icon="key"
        title="No secrets found"
        :description="hasFilters ? 'Try adjusting your filters' : 'Create your first secret to get started'"
      >
        <template #actions>
          <Button variant="solid" theme="green" @click="showNewDialog = true">
            Add Secret
          </Button>
        </template>
      </EmptyState>
    </div>

    <!-- New Secret Dialog -->
    <NewSecretDialog
      v-model="showNewDialog"
      @created="handleSecretCreated"
    />

    <!-- Secret Detail Panel -->
    <SecretPanel
      v-if="selectedSecret"
      :name="selectedSecret"
      @close="selectedSecret = null"
      @updated="secrets.reload()"
      @deleted="handleSecretDeleted"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Button,
  TextInput,
  Dropdown,
  FeatherIcon,
  LoadingText,
} from 'frappe-ui'
import { useSecrets, useCategories, useToggleFavorite } from '@/data/vault'
import SecretRow from '@/components/SecretRow.vue'
import SecretPanel from '@/components/SecretPanel.vue'
import NewSecretDialog from '@/components/NewSecretDialog.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const selectedSecret = ref(null)
const showNewDialog = ref(false)

const filters = ref({
  secret_type: '',
  category: '',
})

const secrets = useSecrets()
const categories = useCategories()
const toggleFavorite = useToggleFavorite()

const secretsList = computed(() => secrets.data?.secrets || [])

const hasFilters = computed(() => {
  return searchQuery.value || filters.value.secret_type || filters.value.category
})

const typeFilterOptions = [
  { label: 'All Types', onClick: () => (filters.value.secret_type = '') },
  { label: 'Password', onClick: () => (filters.value.secret_type = 'Password') },
  { label: 'API Key', onClick: () => (filters.value.secret_type = 'API Key') },
  { label: 'Note', onClick: () => (filters.value.secret_type = 'Note') },
  { label: 'Card', onClick: () => (filters.value.secret_type = 'Card') },
  { label: 'SSH Key', onClick: () => (filters.value.secret_type = 'SSH Key') },
]

const categoryFilterOptions = computed(() => {
  const opts = [{ label: 'All Categories', onClick: () => (filters.value.category = '') }]
  for (const cat of categories.data || []) {
    opts.push({
      label: cat.category_name,
      onClick: () => (filters.value.category = cat.name),
    })
  }
  return opts
})

function clearFilters() {
  searchQuery.value = ''
  filters.value.secret_type = ''
  filters.value.category = ''
}

function openSecret(secret) {
  selectedSecret.value = secret.name
}

async function handleToggleFavorite(secret) {
  await toggleFavorite.submit({ name: secret.name })
  secrets.reload()
}

function handleSecretCreated(result) {
  showNewDialog.value = false
  secrets.reload()
  selectedSecret.value = result.name
}

function handleSecretDeleted() {
  selectedSecret.value = null
  secrets.reload()
}

// Watch for filter changes
watch(
  [searchQuery, filters],
  () => {
    secrets.submit({
      search: searchQuery.value || undefined,
      secret_type: filters.value.secret_type || undefined,
      category: filters.value.category || undefined,
    })
  },
  { deep: true }
)

// Handle URL params
onMounted(() => {
  if (route.query.category) {
    filters.value.category = route.query.category
  }
  if (route.query.new) {
    showNewDialog.value = true
  }
})
</script>
