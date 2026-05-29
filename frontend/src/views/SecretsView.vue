<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50/20">
    <!-- Header -->
    <header class="flex h-14 items-center justify-between border-b bg-white px-5 py-3 shrink-0">
      <div class="flex items-center gap-2">
        <h1 class="text-lg font-semibold text-ink-gray-9">{{ pageTitle }}</h1>
        <Badge variant="subtle" theme="gray" size="sm" class="ml-1 font-medium">
          {{ totalCount }} {{ totalCount === 1 ? 'secret' : 'secrets' }}
        </Badge>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="solid" iconLeft="plus" label="Create" @click="showNewDialog = true" />
      </div>
    </header>

    <!-- View Controls Bar (Exactly copies CRM quick filters, Sort, Columns, and alignment) -->
    <div class="bg-white border-b px-5 py-3 flex items-center justify-between gap-4 shrink-0">
      <!-- Quick Filters (Left side) -->
      <div class="flex flex-1 items-center gap-2 overflow-x-auto no-scrollbar">
        <!-- Title Quick Filter -->
        <div class="min-w-[130px] max-w-[160px]">
          <TextInput
            v-model="titleQuery"
            placeholder="Title"
            class="w-full text-sm h-8"
          />
        </div>

 

        <!-- Type Quick Filter Dropdown -->
        <Dropdown :options="typeFilterOptions">
          <template #default="{ open }">
            <button
              class="flex h-8 items-center justify-between rounded border border-gray-200 bg-gray-50/30 px-3 py-1.5 text-sm text-ink-gray-7 hover:bg-gray-50 focus:outline-none min-w-[120px]"
              :class="{ 'bg-gray-100 border-gray-300 font-medium text-ink-gray-9': open || activeFilters.secret_type }"
            >
              <span class="truncate">{{ activeFilters.secret_type || 'Type' }}</span>
              <FeatherIcon name="chevron-down" class="w-3.5 h-3.5 text-ink-gray-4 ml-2 shrink-0" />
            </button>
          </template>
        </Dropdown>

        <!-- Folder Quick Filter Dropdown -->
        <Dropdown :options="folderFilterOptions">
          <template #default="{ open }">
            <button
              class="flex h-8 items-center justify-between rounded border border-gray-200 bg-gray-50/30 px-3 py-1.5 text-sm text-ink-gray-7 hover:bg-gray-50 focus:outline-none min-w-[120px]"
              :class="{ 'bg-gray-100 border-gray-300 font-medium text-ink-gray-9': open || activeFilters.folder }"
            >
              <span class="truncate">{{ activeFilters.folder ? (foldersResource.data?.find(f => f.name === activeFilters.folder)?.folder_name || 'Folder') : 'Folder' }}</span>
              <FeatherIcon name="chevron-down" class="w-3.5 h-3.5 text-ink-gray-4 ml-2 shrink-0" />
            </button>
          </template>
        </Dropdown>
      </div>

      <!-- Controls & Dropdowns (Right side) -->
      <div class="flex items-center gap-1.5 shrink-0">
        <!-- Refresh Button -->
        <Button
          class="h-8 w-8 p-0 flex items-center justify-center focus:outline-none hover:bg-gray-50 border border-gray-200 rounded"
          variant="outline"
          @click="secrets.reload()"
          tooltip="Refresh"
        >
          <template #icon>
            <FeatherIcon name="refresh-cw" class="w-3.5 h-3.5 text-ink-gray-7" :class="{ 'animate-spin': secrets.loading }" />
          </template>
        </Button>

        <!-- Filter Button -->
        <Dropdown :options="combinedFilterOptions">
          <template #default="{ open }">
            <Button
              variant="outline"
              class="h-8 px-3 text-sm focus:outline-none text-ink-gray-7"
              :class="{ 'bg-surface-gray-2 border-gray-300': open || activeFilters.favorites_only }"
            >
              <template #prefix><FeatherIcon name="filter" class="w-3.5 h-3.5 text-ink-gray-5 mr-1" /></template>
              <span>Filter</span>
            </Button>
          </template>
        </Dropdown>

        <!-- Sort Button -->
        <Dropdown :options="sortDropdownOptions">
          <template #default="{ open }">
            <Button
              variant="outline"
              class="h-8 px-3 text-sm focus:outline-none text-ink-gray-7"
              :class="{ 'bg-surface-gray-2 border-gray-300': open }"
            >
              <template #prefix><FeatherIcon name="bar-chart-2" class="w-3.5 h-3.5 text-ink-gray-5 rotate-90 mr-1" /></template>
              <span>Sort</span>
            </Button>
          </template>
        </Dropdown>

        <!-- Columns Button -->
        <Dropdown :options="columnsDropdownOptions">
          <template #default="{ open }">
            <Button
              variant="outline"
              class="h-8 px-3 text-sm focus:outline-none text-ink-gray-7"
              :class="{ 'bg-surface-gray-2 border-gray-300': open }"
            >
              <template #prefix><FeatherIcon name="columns" class="w-3.5 h-3.5 text-ink-gray-5 mr-1" /></template>
              <span>Columns</span>
            </Button>
          </template>
        </Dropdown>

        <!-- More Dropdown -->
        <Dropdown :options="moreOptions">
          <template #default="{ open }">
            <Button
              variant="outline"
              class="h-8 w-8 p-0 flex items-center justify-center focus:outline-none"
              :class="{ 'bg-surface-gray-2': open }"
            >
              <template #icon>
                <FeatherIcon name="more-horizontal" class="w-3.5 h-3.5 text-ink-gray-5" />
              </template>
            </Button>
          </template>
        </Dropdown>

        <!-- Clear Button -->
        <Button
          v-if="hasActiveFilters || currentSort !== 'modified desc'"
          variant="ghost"
          class="h-8 px-2 text-sm text-ink-gray-6 hover:text-ink-gray-9 focus:outline-none font-medium"
          @click="clearFilters"
        >
          Clear
        </Button>
      </div>
    </div>

    <!-- Secret list -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Loading state -->
      <div v-if="secrets.loading && !secrets.data" class="p-6 space-y-3">
        <div v-for="i in 5" :key="i" class="h-16 bg-gray-100 rounded-lg animate-pulse" />
      </div>

      <!-- Secrets list view -->
      <template v-else-if="secretsList.length">
        <ListView
          class="flex-1 flex flex-col overflow-hidden bg-white"
          :columns="columns"
          :rows="formattedRows"
          row-key="name"
          :options="{
            selectable: false,
            showTooltip: true,
            resizeColumn: true,
            onRowClick: (row) => router.push({ name: 'SecretDetail', params: { name: row.name } }),
          }"
        >
          <ListHeader class="border-b px-5 py-2.5 bg-gray-50/50 shrink-0">
            <ListHeaderItem
              v-for="column in columns"
              :key="column.key"
              :item="column"
            />
          </ListHeader>
          <ListRows>
            <ListRow
              v-for="row in formattedRows"
              :key="row.name"
              v-slot="{ column, item }"
              :row="row"
              class="cursor-pointer hover:bg-surface-gray-1 transition-colors h-[48px]"
              @click="router.push({ name: 'SecretDetail', params: { name: row.name } })"
            >
              <ListRowItem :item="item" :align="column.align" class="text-sm font-normal text-ink-gray-7 h-full flex items-center">
                <template #default>
                  <!-- Title column -->
                  <div v-if="column.key === 'title'" class="flex items-center gap-3 py-1">
                    <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-gray-100 shadow-sm"
                         :class="typeColors[item.secret_type] || 'bg-gray-100 text-gray-600'">
                       <FeatherIcon :name="typeIcons[item.secret_type] || 'file'" class="w-4 h-4" />
                    </div>
                    <div class="min-w-0">
                      <span class="font-semibold text-ink-gray-9 hover:text-indigo-600 hover:underline cursor-pointer text-base truncate block leading-normal transition-colors">{{ item.title }}</span>
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
                    <Badge
                      v-if="item"
                      :theme="strengthTheme[item]"
                      variant="subtle"
                    >
                      {{ item }}
                    </Badge>
                    <span class="text-base text-ink-gray-4" v-else>—</span>
                  </div>

                  <!-- Modified column -->
                  <span v-else-if="column.key === 'modified'" class="text-base text-ink-gray-6">{{ item.formatted }}</span>

                  <!-- Actions column -->
                  <div v-else-if="column.key === '_actions'" class="flex items-center justify-end gap-1.5" @click.stop>
                    <button
                      class="p-1.5 rounded hover:bg-surface-gray-2 text-ink-gray-5 hover:text-ink-gray-9 transition-colors focus:outline-none"
                      @click.stop="handleToggleFavorite(row)"
                    >
                      <FeatherIcon
                        name="star"
                        class="w-4 h-4"
                        :class="row.is_favorite ? 'text-yellow-500 fill-yellow-500' : 'text-ink-gray-3'"
                      />
                    </button>
                    <Dropdown :options="getRowActions(row)">
                      <template #default="{ open }">
                        <Button variant="ghost" class="h-7 w-7 p-0 focus:outline-none" :class="{ 'bg-surface-gray-2': open }">
                          <template #icon>
                            <FeatherIcon name="more-horizontal" class="w-4 h-4 text-ink-gray-5" />
                          </template>
                        </Button>
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
          class="border-t px-5 py-2 bg-white shrink-0"
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
          <Button variant="solid" @click="showNewDialog = true">Add Secret</Button>
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
  ListRowItem,
  ListFooter,
} from 'frappe-ui'
import { useSecrets, useFolders, useToggleFavorite } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'
import NewSecretDialog from '../components/NewSecretDialog.vue'

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

const secretsList = computed(() => secrets.data?.secrets || [])
const totalCount = computed(() => secrets.data?.total || 0)
const hasActiveFilters = computed(() => titleQuery.value || activeFilters.value.secret_type || activeFilters.value.folder || activeFilters.value.favorites_only)
const pageTitle = computed(() => activeFilters.value.folder ? `Folder: ${foldersResource.data?.find(f => f.name === activeFilters.value.folder)?.folder_name || 'Folder'}` : 'All Secrets')

const typeIcons = { Password: 'key', 'API Key': 'code', Note: 'file-text', 'SSH Key': 'terminal', Certificate: 'shield', 'Credit Card': 'credit-card', Database: 'database', Other: 'file' }
const typeColors = { Password: 'bg-blue-100 text-blue-600', 'API Key': 'bg-purple-100 text-purple-600', Note: 'bg-green-100 text-green-600', 'SSH Key': 'bg-orange-100 text-orange-600', Certificate: 'bg-teal-100 text-teal-600', 'Credit Card': 'bg-yellow-100 text-yellow-600', Database: 'bg-red-100 text-red-600' }
const strengthTheme = { weak: 'red', fair: 'orange', good: 'blue', strong: 'green', excellent: 'green' }

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

const columns = computed(() => {
  const cols = [
    {
      label: 'Title',
      key: 'title',
      width: '260px',
    }
  ]

  if (visibleColumns.value.secret_type) {
    cols.push({
      label: 'Type',
      key: 'secret_type',
      width: '120px',
    })
  }

  if (visibleColumns.value.folder) {
    cols.push({
      label: 'Folder',
      key: 'folder',
      width: '130px',
    })
  }

  if (visibleColumns.value.password_strength) {
    cols.push({
      label: 'Strength',
      key: 'password_strength',
      width: '120px',
    })
  }

  if (visibleColumns.value.modified) {
    cols.push({
      label: 'Last Modified',
      key: 'modified',
      width: '140px',
    })
  }

  cols.push({
    label: '',
    key: '_actions',
    width: '90px',
    align: 'right',
  })

  return cols
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
          onClick: () => { secrets.reload() }
        }
      ]
    }
  ]
})

function clearFilters() {
  titleQuery.value = ''
  activeFilters.value = { secret_type: '', folder: '', favorites_only: false }
  currentSort.value = 'modified desc'
}

function formatTime(dt) { if (!dt) return ''; const d = new Date(dt); return d.toLocaleDateString() }
async function handleToggleFavorite(s) { await toggleFav.submit({ name: s.name }); secrets.reload() }
function handleCreated(r) { showNewDialog.value = false; secrets.reload(); router.push({ name: 'SecretDetail', params: { name: r.name } }) }
function handleDeleted() { secrets.reload() }

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
})

</script>
