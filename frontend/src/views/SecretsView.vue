<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-surface-base">
    <!-- Header -->
    <header class="flex h-10.5 items-center justify-between border-b border-outline-gray-1 bg-surface-base px-5 py-2.5 shrink-0">
      <div class="flex items-center gap-2 min-w-0 flex-1">
        <!-- Mobile Sidebar Trigger -->
        <Button
          class="sm:hidden mr-1 shrink-0"
          variant="ghost"
          icon="lucide-menu"
          @click="mobileSidebarOpened = true"
        />

        <Breadcrumbs :items="breadcrumbs" class="min-w-0" />
      </div>
      <div class="flex items-center gap-2">
        <Button variant="solid" iconLeft="plus" label="Create" @click="showNewDialog = true" />
      </div>
    </header>

    <!-- View Controls Bar -->
    <div class="view-controls-bar flex items-center justify-between gap-2 px-5 py-4 relative z-10">
      <!-- Quick Filters (Left side) -->
      <div class="flex flex-1 items-center gap-2.5 overflow-x-auto h-9">
        <TextInput
          v-model="titleQuery"
          placeholder="Title"
          class="w-44 shrink-0"
        />

        <Select
          v-model="activeFilters.secret_type"
          :options="typeFilterOptions"
          placeholder="Type"
        />

        <Select
          v-model="activeFilters.folder"
          :options="folderFilterOptions"
          placeholder="Folder"
        />
      </div>

      <!-- Divider -->
      <div class="-ml-2 h-[70%] border-l" />

      <!-- Controls (Right side) -->
      <div class="flex items-center gap-2">
        <!-- Refresh -->
        <Button
          :tooltip="'Refresh'"
          :icon="RefreshIcon"
          :loading="secrets.loading"
          @click="refreshSecrets()"
        />

        <!-- Filter Panel -->
        <FilterPanel
          :fields="filterableFields.data || []"
          @update="onFilterUpdate"
        />

        <!-- Sort Panel -->
        <SortPanel
          :fields="sortOptions.data || []"
          @update="onSortUpdate"
        />

        <!-- Column Panel -->
        <ColumnPanel
          :defaultColumns="defaultColumns"
          :allFields="filterableFields.data || []"
          @update="onColumnsUpdate"
        />

        <!-- More Options -->
        <Dropdown :options="moreOptions">
          <template #default>
            <Button :tooltip="'More Options'" icon="more-horizontal" />
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- Secret list -->
    <div class="flex-1 flex flex-col overflow-hidden relative">
      <!-- Loading state -->
      <div v-if="secrets.loading && !secrets.data" class="p-6 space-y-3">
        <div v-for="i in 5" :key="i" class="h-16 bg-surface-gray-3 rounded-lg animate-pulse" />
      </div>

      <!-- Secrets list view -->
      <template v-else-if="secretsList.length">
        <ListView
          class="flex-1 flex flex-col overflow-hidden bg-surface-base"
          :columns="columns"
          :rows="paginatedRows"
          row-key="name"
          v-model:selections="selectedSecrets"
          :options="{
            selectable: true,
            showTooltip: true,
            resizeColumn: true,
            onRowClick: (row) => router.push({ name: 'SecretDetail', params: { name: row.name } }),
          }"
        >
          <ListHeader class="sm:mx-5 mx-3 shrink-0 relative">
            <ListHeaderItem
              v-for="column in columns"
              :key="column.key"
              :item="column"
            />
          </ListHeader>
          <ListRows class="sm:mx-5 mx-3">
            <ListRow
              v-for="row in paginatedRows"
              :key="row.name"
              v-slot="{ column, item }"
              :row="row"
              @click="router.push({ name: 'SecretDetail', params: { name: row.name } })"
            >
              <ListRowItem :item="item" :align="column.align" class="overflow-hidden">
                <template #default>
                  <!-- Title column -->
                  <div v-if="column.key === 'title'" class="flex items-center gap-3 py-1">
                    <SecretTypeIcon :type="item.secret_type" />
                    <span class="min-w-0 font-medium text-ink-gray-9 hover:text-ink-blue-3 cursor-pointer text-base truncate block leading-normal transition-colors">{{ item.title }}</span>
                  </div>

                  <!-- Type column -->
                  <span v-else-if="column.key === 'secret_type'" class="text-base text-ink-gray-9">{{ item }}</span>

                  <!-- Folder column -->
                  <div v-else-if="column.key === 'folder'" class="flex items-center gap-1.5 text-base text-ink-gray-9">
                    <template v-if="item">
                      <FeatherIcon name="folder" class="w-3.5 h-3.5 text-ink-gray-5 shrink-0" />
                      <span class="truncate">{{ item }}</span>
                    </template>
                    <span class="text-base text-ink-gray-4" v-else>—</span>
                  </div>

                  <!-- Strength column -->
                  <StrengthBadge v-else-if="column.key === 'password_strength' && item" :strength="item" size="sm" />
                  <span v-else-if="column.key === 'password_strength'" class="text-base text-ink-gray-4">—</span>

                  <!-- Modified column -->
                  <span v-else-if="column.key === 'modified'" class="text-base text-ink-gray-6">{{ item.formatted }}</span>

                  <!-- Actions column -->
                  <div v-else-if="column.key === '_actions'" class="flex items-center justify-end gap-1.5" @click.stop>
                    <Button
                      variant="ghost"
                      class="!p-1.5 h-auto text-ink-gray-5 hover:text-ink-gray-9"
                      @click.stop="handleToggleFavorite(row)"
                    >
                      <FeatherIcon
                        name="star"
                        class="w-4 h-4"
                        :class="row.is_favorite ? 'text-ink-yellow-3 fill-current' : 'text-ink-gray-4'"
                      />
                    </Button>
                  </div>

                  <!-- Dynamic columns (fallback) -->
                  <span v-else class="text-base text-ink-gray-7 truncate">{{ item ?? '—' }}</span>
                </template>
              </ListRowItem>
            </ListRow>
          </ListRows>
          <ListSelectBanner>
            <template #actions="{ unselectAll }">
              <Button
                variant="solid"
                theme="red"
                iconLeft="trash-2"
                label="Delete"
                @click="showDeleteDialog = true"
              />
            </template>
          </ListSelectBanner>
        </ListView>

        <!-- Pagination Footer -->
        <ListFooter
          v-model="pageLength"
          class="border-t border-outline-gray-1 px-5 py-2 bg-surface-base shrink-0"
          :options="{
            rowCount: paginatedRows.length,
            totalCount: totalCount,
          }"
          @loadMore="pageLength += 20"
        />
      </template>

      <!-- Empty state -->
      <EmptyState v-else icon="key" title="No secrets found" :description="hasActiveFilters ? 'Try adjusting your filters' : 'Create your first secret to get started'">
        <template #actions>
          <div class="flex items-center gap-2">
            <Button variant="solid" @click="showNewDialog = true">Create</Button>
            <Button
              v-if="!hasActiveFilters && !stats.data?.has_demo_data"
              variant="outline"
              iconLeft="lucide-sparkles"
              label="Load Demo Data"
              :loading="generateDemo.loading"
              @click="handleGenerateDemo"
            />
          </div>
        </template>
      </EmptyState>
    </div>

    <!-- Delete Secret Dialog -->
    <Dialog
      v-model="showDeleteDialog"
      :title="'Delete Secret'"
      size="sm"
    >
      <template #default>
        <div class="space-y-3 px-4 pb-6">
          <p class="text-sm text-ink-gray-6 mt-1 leading-normal" v-if="selectedSecrets.size === 1">
            Are you sure you want to permanently delete <strong>this secret</strong>? This action cannot be undone.
          </p>
          <p class="text-sm text-ink-gray-6 mt-1 leading-normal" v-else>
            Are you sure you want to permanently delete <strong>{{ selectedSecrets.size }} secrets</strong>? This action cannot be undone.
          </p>
          <div v-if="deleteError" class="text-sm text-ink-red-3 bg-surface-red-2 p-3 rounded-lg border border-outline-red-1">
            {{ deleteError }}
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 px-4 pb-4">
          <Button variant="outline" @click="showDeleteDialog = false">
            Cancel
          </Button>
          <Button variant="solid" theme="red" @click="handleDeleteSecret" :loading="deleteResource.loading">
            Delete
          </Button>
        </div>
      </template>
    </Dialog>

    <!-- New Secret Dialog -->
    <NewSecretDialog v-model="showNewDialog" :initial-folder="activeFilters.folder" @created="handleCreated" />

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import RefreshIcon from '../components/RefreshIcon.vue'
import FilterPanel from '../components/FilterPanel.vue'
import SortPanel from '../components/SortPanel.vue'
import ColumnPanel from '../components/ColumnPanel.vue'
import {
  Button,
  Dialog,
  TextInput,
  Dropdown,
  FeatherIcon,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRows,
  ListRow,
  ListRowItem,
  ListSelectBanner,
  ListFooter,
  Breadcrumbs,
  Select,
} from 'frappe-ui'
import {
  mobileSidebarOpened,
  useSecrets,
  useFolders,
  useToggleFavorite,
  useGenerateDemoData,
  useVaultStats,
  useBulkDeleteSecrets,
  useFilterableFields,
  useSortOptions,
} from '../composables/vault'
import { typeFilterOptions, formatDate as formatTime } from '../composables/constants'
import EmptyState from '../components/EmptyState.vue'
import NewSecretDialog from '../components/NewSecretDialog.vue'
import SecretTypeIcon from '../components/SecretTypeIcon.vue'
import StrengthBadge from '../components/StrengthBadge.vue'

const route = useRoute()
const router = useRouter()
const titleQuery = ref('')
const selectedSecret = ref(null)
const showNewDialog = ref(false)
const selectedSecrets = ref(new Set())
const activeFilters = ref({ secret_type: '', folder: route.query.folder || '', favorites_only: false })
const panelFilters = ref({})
const pageLength = ref(20)
const currentSort = ref('modified desc')
const showDeleteDialog = ref(false)
const deleteError = ref('')
const secretToDelete = ref(null)

const defaultColumns = [
  { label: 'Type', key: 'secret_type', width: '10rem' },
  { label: 'Folder', key: 'folder', width: '11rem' },
  { label: 'Strength', key: 'password_strength', width: '10rem' },
  { label: 'Last Modified', key: 'modified', width: '12rem' },
]

const activeColumnDefs = ref([...defaultColumns])

const secrets = useSecrets()
const foldersResource = useFolders()
const toggleFav = useToggleFavorite()
const stats = useVaultStats()
const generateDemo = useGenerateDemoData()
const deleteResource = useBulkDeleteSecrets()
const filterableFields = useFilterableFields()
const sortOptions = useSortOptions()

async function handleGenerateDemo() {
  try {
    await generateDemo.submit()
    secrets.reload()
    stats.reload()
  } catch (err) {
  }
}

const secretsList = computed(() => secrets.data?.secrets || [])
const totalCount = computed(() => secrets.data?.total || secretsList.value.length || 0)
const hasActiveFilters = computed(() =>
  titleQuery.value || activeFilters.value.secret_type || activeFilters.value.folder ||
  activeFilters.value.favorites_only || Object.keys(panelFilters.value).length > 0
)

const breadcrumbs = computed(() => {
  if (activeFilters.value.folder) {
    const folderName = foldersResource.data?.find(f => f.name === activeFilters.value.folder)?.folder_name || 'Folder'
    return [
      { label: 'Secrets', route: '/secrets' },
      { label: folderName }
    ]
  }
  return [{ label: 'Secrets' }]
})

// Fixed columns: title (always first) and _actions (always last)
const columns = computed(() => {
  const titleCol = { label: 'Title', key: 'title', width: '18rem' }
  const actionsCol = { label: '', key: '_actions', width: '6rem', align: 'right' }
  return [titleCol, ...activeColumnDefs.value, actionsCol]
})

const formattedRows = computed(() => {
  return secretsList.value.map(secret => {
    return {
      ...secret,
      name: secret.name,
      title: {
        title: secret.title,
        subtitle: secret.username || secret.email || secret.url || '',
        secret_type: secret.secret_type,
      },
      secret_type: secret.secret_type,
      folder: foldersResource.data?.find(f => f.name === secret.folder)?.folder_name || secret.folder || '',
      password_strength: secret.password_strength || '',
      modified: {
        raw: secret.modified,
        formatted: formatTime(secret.modified),
      },
      _actions: secret,
    }
  })
})

const paginatedRows = computed(() => formattedRows.value.slice(0, pageLength.value))

const folderFilterOptions = computed(() => {
  const opts = [{ label: 'All Folders', value: '' }]
  for (const f of foldersResource.data || []) {
    opts.push({ label: f.folder_name, value: f.name })
  }
  return opts
})

const moreOptions = computed(() => {
  return [
    {
      group: 'Options',
      items: [
        {
          label: 'Create Secret',
          icon: 'plus',
          onClick: () => { showNewDialog.value = true }
        },
        {
          label: 'Refresh List',
          icon: 'refresh-cw',
          onClick: () => { refreshSecrets() }
        }
      ]
    }
  ]
})

function onFilterUpdate(filters) {
  panelFilters.value = filters
}

function onSortUpdate(orderBy) {
  currentSort.value = orderBy
}

function onColumnsUpdate(cols) {
  activeColumnDefs.value = cols
}

function refreshSecrets() {
  const filters = {
    title: titleQuery.value || undefined,
    secret_type: activeFilters.value.secret_type || undefined,
    folder: activeFilters.value.folder || undefined,
    favorites_only: activeFilters.value.favorites_only || undefined,
    limit: pageLength.value,
    order_by: currentSort.value,
    ...panelFilters.value,
  }
  secrets.submit(filters)
}

function clearFilters() {
  titleQuery.value = ''
  activeFilters.value = { secret_type: '', folder: '', favorites_only: false }
  panelFilters.value = {}
  currentSort.value = 'modified desc'
}

async function handleToggleFavorite(s) { await toggleFav.submit({ name: s.name }); refreshSecrets() }
function handleCreated(r) { showNewDialog.value = false; refreshSecrets(); router.push({ name: 'SecretDetail', params: { name: r.name } }) }

function parseFrappeError(error) {
  if (error?.message && !error.message.includes('Traceback')) {
    return error.message
  }
  if (Array.isArray(error?.messages) && error.messages.length) {
    const msg = error.messages[0]
    if (msg && !msg.includes('Traceback')) return msg
  }
  if (error?.exc) {
    const lines = error.exc.split('\n').map(l => l.trim()).filter(Boolean)
    const last = lines[lines.length - 1]
    if (last) return last.replace(/^frappe\.\w+\.\w+:\s*/, '')
  }
  return 'Failed to delete secret(s). Please try again.'
}

async function handleDeleteSecret() {
  if (!selectedSecrets.value || selectedSecrets.value.size === 0) return

  deleteError.value = ''
  try {
    const secret_names = Array.from(selectedSecrets.value).map((item) =>
      typeof item === 'object' && item !== null ? item.name : item
    )
    const res = await deleteResource.submit({ secret_names: JSON.stringify(secret_names) })

    if (res && res.deleted > 0) {
      showDeleteDialog.value = false
      selectedSecrets.value.clear()
      refreshSecrets()
      stats.reload()
    } else if (res && res.skipped > 0 && res.deleted === 0) {
      deleteError.value = `You don't have permission to delete the selected secret(s). Only the owner or someone with Full Control access can delete.`
    } else if (res && res.failed > 0) {
      deleteError.value = res.error || 'An unexpected error occurred while deleting.'
    }
  } catch (error) {
    deleteError.value = parseFrappeError(error)
  }
}

watch([titleQuery, activeFilters, pageLength, currentSort, panelFilters], () => {
  const filters = {
    title: titleQuery.value || undefined,
    secret_type: activeFilters.value.secret_type || undefined,
    folder: activeFilters.value.folder || undefined,
    favorites_only: activeFilters.value.favorites_only || undefined,
    limit: pageLength.value,
    order_by: currentSort.value,
  }
  // Merge panel filters into the API params
  for (const [key, val] of Object.entries(panelFilters.value)) {
    if (val !== undefined && val !== '') {
      filters[key] = val
    }
  }
  secrets.submit(filters)
}, { deep: true, immediate: true })

watch(() => route.query.folder, (newFolder) => {
  activeFilters.value.folder = newFolder || ''
}, { immediate: true })

</script>
