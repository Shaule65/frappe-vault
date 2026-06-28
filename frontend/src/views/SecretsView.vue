<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-surface-base">
    <!-- Header -->
    <header class="flex h-10.5 items-center justify-between border-b border-outline-gray-2 bg-surface-base px-5 py-2.5 shrink-0">
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

    <!-- View Controls Bar (matching CRM ViewControls.vue line 132-237) -->
    <div class="flex items-center justify-between gap-2 px-5 py-4">
      <!-- Quick Filters (Left side - matching CRM quick filter fields) -->
      <div class="flex flex-1 items-center gap-2.5 overflow-x-auto h-9">
        <!-- Title Quick Filter -->
        <div class="w-44 shrink-0">
          <TextInput
            v-model="titleQuery"
            placeholder="Title"
            class="w-full"
          />
        </div>

        <!-- Type Quick Filter Dropdown -->
        <Select
          v-model="activeFilters.secret_type"
          :options="typeFilterOptions"
          placeholder="Type"
        />

        <!-- Folder Quick Filter Dropdown -->
        <Select
          v-model="activeFilters.folder"
          :options="folderFilterOptions"
          placeholder="Folder"
        />
      </div>

      <!-- Divider (matching CRM: -ml-2 h-[70%] border-l) -->
      <div class="-ml-2 h-[70%] border-l" />

      <!-- Controls (Right side - matching CRM ViewControls right side) -->
      <div class="flex items-center gap-2">
        <!-- Refresh Button (matching CRM: icon only with tooltip) -->
        <Button
          :tooltip="'Refresh'"
          :icon="RefreshIcon"
          :loading="secrets.loading"
          @click="refreshSecrets()"
        />

        <!-- Filter Button (matching CRM Filter.vue - Button with iconLeft + label) -->
        <Dropdown :options="combinedFilterOptions">
          <template #default="{ open }">
            <div class="flex items-center">
              <Button
                :label="'Filter'"
                :iconLeft="FilterIcon"
                :class="activeFilterCount ? 'rounded-r-none' : ''"
                @click="open"
              >
                <template v-if="activeFilterCount" #suffix>
                  <div
                    class="flex h-5 w-5 items-center justify-center rounded-[5px] bg-surface-elevation-1 pt-px text-xs font-medium text-ink-gray-8 shadow-sm"
                  >
                    {{ activeFilterCount }}
                  </div>
                </template>
              </Button>
              <Button
                v-if="activeFilterCount"
                :tooltip="'Clear Filters'"
                class="rounded-l-none border-l"
                icon="x"
                variant="ghost"
                @click.stop="clearFilters()"
              />
            </div>
          </template>
        </Dropdown>

        <!-- Sort Button (matching CRM SortBy.vue - Button with iconLeft + label) -->
        <Dropdown :options="sortDropdownOptions">
          <template #default="{ open }">
            <Button label="Sort" @click="open">
              <template #prefix>
                <SortIcon class="h-4" />
              </template>
            </Button>
          </template>
        </Dropdown>

        <!-- Columns Button (matching CRM ColumnSettings.vue - Button with iconLeft + label) -->
        <Dropdown :options="columnsDropdownOptions">
          <template #default="{ open }">
            <Button label="Columns" @click="open">
              <template #prefix>
                <ColumnsIcon class="h-4" />
              </template>
            </Button>
          </template>
        </Dropdown>

        <!-- More Dropdown (matching CRM: icon-only button with tooltip) -->
        <Dropdown :options="moreOptions">
          <template #default>
            <Button :tooltip="'More Options'" icon="more-horizontal" />
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- Secret list -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Loading state -->
      <div v-if="secrets.loading && !secrets.data" class="p-6 space-y-3">
        <div v-for="i in 5" :key="i" class="h-16 bg-surface-gray-3 rounded-lg animate-pulse" />
      </div>

      <!-- Secrets list view -->
      <template v-else-if="secretsList.length">
        <ListView
          class="flex-1 flex flex-col overflow-hidden bg-surface-base"
          :columns="columns"
          :rows="formattedRows"
          row-key="name"
          :options="{
            selectable: true,
            showTooltip: true,
            resizeColumn: true,
            onRowClick: (row) => router.push({ name: 'SecretDetail', params: { name: row.name } }),
          }"
        >
          <ListHeader class="sm:mx-5 mx-3 shrink-0">
            <ListHeaderItem
              v-for="column in columns"
              :key="column.key"
              :item="column"
            />
          </ListHeader>
          <ListRows class="sm:mx-5 mx-3">
            <ListRow
              v-for="row in formattedRows"
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
                    <div class="min-w-0">
                      <span class="font-semibold text-ink-gray-9 hover:text-indigo-600 cursor-pointer text-base truncate block leading-normal transition-colors">{{ item.title }}</span>
                    </div>
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
                  <div v-else-if="column.key === 'password_strength'">
                    <StrengthBadge v-if="item" :strength="item" size="sm" />
                    <span class="text-base text-ink-gray-4" v-else>—</span>
                  </div>

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
                        :class="row.is_favorite ? 'text-yellow-500 fill-yellow-500' : 'text-ink-gray-3'"
                      />
                    </Button>
                    <Dropdown :options="getRowActions(row)">
                      <template #default="{ open }">
                        <Button variant="ghost" icon="lucide-more-horizontal" :class="{ 'bg-surface-gray-2': open }" />
                      </template>
                    </Dropdown>
                  </div>
                </template>
              </ListRowItem>
            </ListRow>
          </ListRows>
        </ListView>

        <!-- Pagination Footer -->
        <ListFooter
          v-model="pageLength"
          class="border-t border-outline-gray-2 px-5 py-2 bg-surface-base shrink-0"
          :options="{
            rowCount: secretsList.length,
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

    <!-- New Secret Dialog -->
    <NewSecretDialog v-model="showNewDialog" :initial-folder="activeFilters.folder" @created="handleCreated" />

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SortIcon from '../components/SortIcon.vue'
import ColumnsIcon from '../components/ColumnsIcon.vue'
import FilterIcon from '../components/FilterIcon.vue'
import RefreshIcon from '../components/RefreshIcon.vue'
import {
  Button,
  TextInput,
  Dropdown,
  Badge,
  FeatherIcon,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRows,
  ListRow,
  Breadcrumbs,
  Select,
} from 'frappe-ui'
import { mobileSidebarOpened, useSecrets, useFolders, useToggleFavorite, useGenerateDemoData, useVaultStats } from '../composables/vault'
import { SECRET_TYPES } from '../composables/constants'
import EmptyState from '../components/EmptyState.vue'
import NewSecretDialog from '../components/NewSecretDialog.vue'
import SecretTypeIcon from '../components/SecretTypeIcon.vue'
import StrengthBadge from '../components/StrengthBadge.vue'

const route = useRoute()
const router = useRouter()
const titleQuery = ref('')
const selectedSecret = ref(null)
const showNewDialog = ref(false)
const activeFilters = ref({ secret_type: '', folder: route.query.folder || '', favorites_only: false })
const pageLength = ref(20)
const currentSort = ref('modified desc')

const visibleColumns = ref({
  secret_type: true,
  folder: true,
  password_strength: true,
  modified: true,
})

const secrets = useSecrets()
const foldersResource = useFolders()
const toggleFav = useToggleFavorite()
const stats = useVaultStats()
const generateDemo = useGenerateDemoData()

async function handleGenerateDemo() {
  try {
    await generateDemo.submit()
    secrets.reload()
    stats.reload()
  } catch (err) {
    console.error(err)
  }
}

const secretsList = computed(() => secrets.data?.secrets || [])
const totalCount = computed(() => secrets.data?.total || 0)
const hasActiveFilters = computed(() => titleQuery.value || activeFilters.value.secret_type || activeFilters.value.folder || activeFilters.value.favorites_only)
const activeFilterCount = computed(() => [
  titleQuery.value,
  activeFilters.value.secret_type,
  activeFilters.value.folder,
  activeFilters.value.favorites_only,
].filter(Boolean).length)
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


const sortOptions = [
  { label: 'Last Modified (Newest)', value: 'modified desc' },
  { label: 'Last Modified (Oldest)', value: 'modified asc' },
  { label: 'Title (A-Z)', value: 'title asc' },
  { label: 'Title (Z-A)', value: 'title desc' },
  { label: 'Last Accessed', value: 'last_accessed desc' },
]

const sortDropdownOptions = computed(() => {
  return sortOptions.map(opt => ({
    label: opt.label,
    onClick: () => {
      currentSort.value = opt.value
    }
  }))
})

const columnsDropdownOptions = computed(() => {
  return [
    {
      group: 'Toggle Columns',
      items: [
        {
          label: 'Type',
          icon: visibleColumns.value.secret_type ? 'check' : '',
          onClick: () => { visibleColumns.value.secret_type = !visibleColumns.value.secret_type }
        },
        {
          label: 'Folder',
          icon: visibleColumns.value.folder ? 'check' : '',
          onClick: () => { visibleColumns.value.folder = !visibleColumns.value.folder }
        },
        {
          label: 'Strength',
          icon: visibleColumns.value.password_strength ? 'check' : '',
          onClick: () => { visibleColumns.value.password_strength = !visibleColumns.value.password_strength }
        },
        {
          label: 'Last Modified',
          icon: visibleColumns.value.modified ? 'check' : '',
          onClick: () => { visibleColumns.value.modified = !visibleColumns.value.modified }
        },
      ]
    }
  ]
})

const allColumns = ref([
  { label: 'Title', key: 'title', width: '18rem' },
  { label: 'Type', key: 'secret_type', width: '10rem' },
  { label: 'Folder', key: 'folder', width: '11rem' },
  { label: 'Strength', key: 'password_strength', width: '10rem' },
  { label: 'Last Modified', key: 'modified', width: '12rem' },
  { label: '', key: '_actions', width: '6rem', align: 'right' }
])

const columns = computed(() => {
  return allColumns.value.filter(col => {
    if (col.key === 'title' || col.key === '_actions') return true
    return visibleColumns.value[col.key]
  })
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

const typeFilterOptions = computed(() => [
  { label: 'All Types', value: '' },
  ...SECRET_TYPES.map(t => ({ label: t, value: t })),
])

const folderFilterOptions = computed(() => {
  const opts = [{ label: 'All Folders', value: '' }]
  for (const f of foldersResource.data || []) {
    opts.push({ label: f.folder_name, value: f.name })
  }
  return opts
})

const combinedFilterOptions = computed(() => {
  return [
    {
      group: 'Filters',
      items: [
        {
          label: 'Favorites Only',
          icon: activeFilters.value.favorites_only ? 'check' : '',
          onClick: () => { activeFilters.value.favorites_only = !activeFilters.value.favorites_only }
        },
      ]
    }
  ]
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

function refreshSecrets() {
  secrets.submit({
    title: titleQuery.value || undefined,
    secret_type: activeFilters.value.secret_type || undefined,
    folder: activeFilters.value.folder || undefined,
    favorites_only: activeFilters.value.favorites_only || undefined,
    limit: pageLength.value,
    order_by: currentSort.value,
  })
}

function clearFilters() {
  titleQuery.value = ''
  activeFilters.value = { secret_type: '', folder: '', favorites_only: false }
  currentSort.value = 'modified desc'
}

function formatTime(dt) { if (!dt) return ''; const d = new Date(dt); return d.toLocaleDateString() }
async function handleToggleFavorite(s) { await toggleFav.submit({ name: s.name }); refreshSecrets() }
function handleCreated(r) { showNewDialog.value = false; refreshSecrets(); router.push({ name: 'SecretDetail', params: { name: r.name } }) }
function handleDeleted() { refreshSecrets() }

function copyToClipboard(text) {
  if (!text) return
  navigator.clipboard.writeText(text)
}

function getRowActions(secret) {
  const actions = [
    {
      label: 'View Details',
      icon: 'eye',
      onClick: () => router.push({ name: 'SecretDetail', params: { name: secret.name } }),
    },
    {
      label: 'Copy Username',
      icon: 'copy',
      onClick: () => copyToClipboard(secret.username),
      condition: () => !!secret.username,
    },
    {
      label: 'Open URL',
      icon: 'external-link',
      onClick: () => window.open(secret.url, '_blank'),
      condition: () => !!secret.url,
    },
  ]
  return actions.filter(a => !a.condition || a.condition())
}

watch([titleQuery, activeFilters, pageLength, currentSort], () => {
  secrets.submit({
    title: titleQuery.value || undefined,
    secret_type: activeFilters.value.secret_type || undefined,
    folder: activeFilters.value.folder || undefined,
    favorites_only: activeFilters.value.favorites_only || undefined,
    limit: pageLength.value,
    order_by: currentSort.value,
  })
}, { deep: true, immediate: true })

watch(() => route.query.folder, (newFolder) => {
  activeFilters.value.folder = newFolder || ''
}, { immediate: true })

</script>
