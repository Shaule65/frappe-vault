<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Header -->
    <div class="bg-white border-b px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900">{{ pageTitle }}</h1>
          <p class="text-sm text-gray-500 mt-0.5">{{ totalCount }} secrets</p>
        </div>
        <Button variant="solid" @click="showNewDialog = true">
          <template #prefix><FeatherIcon name="plus" class="w-4 h-4" /></template>
          Add Secret
        </Button>
      </div>

      <!-- Filters toolbar -->
      <div class="flex items-center gap-3 mt-4">
        <div class="flex-1 max-w-md">
          <TextInput v-model="searchQuery" type="search" placeholder="Search secrets..." :debounce="300">
            <template #prefix>
              <FeatherIcon name="search" class="w-4 h-4 text-gray-400" />
            </template>
          </TextInput>
        </div>

        <Dropdown :options="typeFilterOptions">
          <template #default>
            <Button variant="outline">
              <FeatherIcon name="filter" class="w-4 h-4" />
              <span>{{ activeFilters.secret_type || 'All Types' }}</span>
            </Button>
          </template>
        </Dropdown>

        <Dropdown :options="folderFilterOptions">
          <template #default>
            <Button variant="outline">
              <FeatherIcon name="folder" class="w-4 h-4" />
              <span>{{ activeFilters.folder || 'All Folders' }}</span>
            </Button>
          </template>
        </Dropdown>

        <Button v-if="hasActiveFilters" variant="ghost" @click="clearFilters">Clear</Button>
      </div>
    </div>

    <!-- Secret list -->
    <div class="flex-1 overflow-auto">
      <!-- Loading state -->
      <div v-if="secrets.loading && !secrets.data" class="p-6 space-y-3">
        <div v-for="i in 5" :key="i" class="h-16 bg-gray-100 rounded-lg animate-pulse" />
      </div>

      <!-- Secret rows -->
      <div v-else-if="secretsList.length" class="divide-y">
        <div
          v-for="secret in secretsList"
          :key="secret.name"
          class="flex items-center px-6 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
          @click="selectedSecret = secret.name"
        >
          <!-- Type icon -->
          <div class="w-10 h-10 rounded-lg flex items-center justify-center mr-4"
               :class="typeColors[secret.secret_type] || 'bg-gray-100 text-gray-600'">
            <FeatherIcon :name="typeIcons[secret.secret_type] || 'file'" class="w-5 h-5" />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900 truncate">{{ secret.title }}</p>
            <p class="text-sm text-gray-500 truncate">
              {{ secret.username || secret.url || secret.secret_type }}
            </p>
          </div>

          <!-- Favorite star -->
          <button
            class="mr-3 p-1 rounded hover:bg-gray-200 transition-colors"
            @click.stop="handleToggleFavorite(secret)"
          >
            <FeatherIcon
              name="star"
              class="w-4 h-4"
              :class="secret.is_favorite ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'"
            />
          </button>

          <!-- Strength badge -->
          <Badge
            v-if="secret.password_strength"
            :theme="strengthTheme[secret.password_strength]"
            variant="subtle"
          >
            {{ secret.password_strength }}
          </Badge>

          <!-- Timestamp -->
          <span class="text-xs text-gray-400 ml-4 whitespace-nowrap">
            {{ formatTime(secret.modified) }}
          </span>
        </div>
      </div>

      <!-- Empty state -->
      <EmptyState v-else icon="key" title="No secrets found" :description="hasActiveFilters ? 'Try adjusting your filters' : 'Create your first secret to get started'">
        <template #actions>
          <Button variant="solid" @click="showNewDialog = true">Add Secret</Button>
        </template>
      </EmptyState>
    </div>

    <!-- New Secret Dialog -->
    <NewSecretDialog v-model="showNewDialog" @created="handleCreated" />

    <!-- Detail Panel -->
    <SecretDetailPanel v-if="selectedSecret" :name="selectedSecret" @close="selectedSecret = null" @updated="secrets.reload()" @deleted="handleDeleted" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Button, TextInput, Dropdown, Badge, FeatherIcon } from 'frappe-ui'
import { useSecrets, useFolders, useToggleFavorite } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'
import NewSecretDialog from '../components/NewSecretDialog.vue'
import SecretDetailPanel from '../components/SecretDetailPanel.vue'

const route = useRoute()
const searchQuery = ref('')
const selectedSecret = ref(null)
const showNewDialog = ref(false)
const activeFilters = ref({ secret_type: '', folder: '' })

const secrets = useSecrets()
const foldersResource = useFolders()
const toggleFav = useToggleFavorite()

const secretsList = computed(() => secrets.data?.secrets || [])
const totalCount = computed(() => secrets.data?.total || 0)
const hasActiveFilters = computed(() => searchQuery.value || activeFilters.value.secret_type || activeFilters.value.folder)
const pageTitle = computed(() => activeFilters.value.folder ? `Folder: ${activeFilters.value.folder}` : 'All Secrets')

const typeIcons = { Password: 'key', 'API Key': 'code', Note: 'file-text', 'SSH Key': 'terminal', Certificate: 'shield', 'Credit Card': 'credit-card', Database: 'database', Other: 'file' }
const typeColors = { Password: 'bg-blue-100 text-blue-600', 'API Key': 'bg-purple-100 text-purple-600', Note: 'bg-green-100 text-green-600', 'SSH Key': 'bg-orange-100 text-orange-600', Certificate: 'bg-teal-100 text-teal-600', 'Credit Card': 'bg-yellow-100 text-yellow-600', Database: 'bg-red-100 text-red-600' }
const strengthTheme = { weak: 'red', fair: 'orange', good: 'blue', strong: 'green', excellent: 'green' }

const typeFilterOptions = [
  { label: 'All Types', onClick: () => (activeFilters.value.secret_type = '') },
  ...['Password', 'API Key', 'Note', 'SSH Key', 'Certificate', 'Credit Card', 'Database'].map(t => ({ label: t, onClick: () => (activeFilters.value.secret_type = t) })),
]

const folderFilterOptions = computed(() => {
  const opts = [{ label: 'All Folders', onClick: () => (activeFilters.value.folder = '') }]
  for (const f of foldersResource.data || []) {
    opts.push({ label: f.folder_name, onClick: () => (activeFilters.value.folder = f.name) })
  }
  return opts
})

function clearFilters() { searchQuery.value = ''; activeFilters.value = { secret_type: '', folder: '' } }
function formatTime(dt) { if (!dt) return ''; const d = new Date(dt); return d.toLocaleDateString() }
async function handleToggleFavorite(s) { await toggleFav.submit({ name: s.name }); secrets.reload() }
function handleCreated(r) { showNewDialog.value = false; secrets.reload(); selectedSecret.value = r.name }
function handleDeleted() { selectedSecret.value = null; secrets.reload() }

watch([searchQuery, activeFilters], () => {
  secrets.submit({
    search: searchQuery.value || undefined,
    secret_type: activeFilters.value.secret_type || undefined,
    folder: activeFilters.value.folder || undefined,
  })
}, { deep: true })

watch(() => route.query.folder, (newFolder) => {
  activeFilters.value.folder = newFolder || ''
})

onMounted(() => {
  if (route.query.folder) activeFilters.value.folder = route.query.folder
})

</script>
