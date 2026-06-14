<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50/20">
    <!-- Header -->
    <header class="flex h-10.5 items-center justify-between border-b bg-white px-5 py-2.5 shrink-0">
      <div class="flex items-center gap-2 min-w-0 flex-1">
        <!-- Mobile Sidebar Trigger -->
        <Button
          class="size-7 sm:hidden flex items-center justify-center p-0 mr-1 focus:outline-none shrink-0"
          variant="ghost"
          @click="mobileSidebarOpened = true"
        >
          <template #icon>
            <FeatherIcon name="menu" class="w-4.5 h-4.5 text-ink-gray-9" />
          </template>
        </Button>

        <Breadcrumbs :items="breadcrumbs" class="min-w-0" />
        <Badge variant="subtle" theme="gray" size="sm" class="ml-1 font-medium shrink-0">
          {{ totalCount }} {{ totalCount === 1 ? 'secret' : 'secrets' }}
        </Badge>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="solid" iconLeft="plus" label="Create" @click="showNewDialog = true" />
      </div>
    </header>

    <!-- View Controls Bar (matching CRM ViewControls.vue line 132-237) -->
    <div class="flex items-center justify-between gap-2 px-5 py-4">
      <!-- Quick Filters (Left side - matching CRM quick filter fields) -->
      <div class="flex flex-1 items-center overflow-x-auto -ml-1 h-9">
        <!-- Title Quick Filter -->
        <div class="m-1 min-w-36">
          <TextInput
            v-model="titleQuery"
            placeholder="Title"
            class="w-full"
          />
        </div>

        <!-- Type Quick Filter Dropdown -->
        <div class="m-1 min-w-36">
          <Dropdown :options="typeFilterOptions">
            <template #default="{ open }">
              <Button
                class="w-full"
                :label="activeFilters.secret_type || 'Type'"
                :iconRight="'chevron-down'"
              />
            </template>
          </Dropdown>
        </div>

        <!-- Folder Quick Filter Dropdown -->
        <div class="m-1 min-w-36">
          <Dropdown :options="folderFilterOptions">
            <template #default="{ open }">
              <Button
                class="w-full"
                :label="activeFilters.folder ? (foldersResource.data?.find(f => f.name === activeFilters.folder)?.folder_name || 'Folder') : 'Folder'"
                :iconRight="'chevron-down'"
              />
            </template>
          </Dropdown>
        </div>
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
                    class="flex h-5 w-5 items-center justify-center rounded-[5px] bg-surface-white pt-px text-xs font-medium text-ink-gray-8 shadow-sm"
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
                    <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-gray-100 shadow-sm"
                         :class="typeColors[item.secret_type] || 'bg-gray-100 text-gray-600'">
                       <FeatherIcon :name="typeIcons[item.secret_type] || 'file'" class="w-4 h-4" />
                    </div>
                    <div class="min-w-0">
                      <span class="font-semibold text-ink-gray-9 hover:text-indigo-600  cursor-pointer text-base truncate block leading-normal transition-colors">{{ item.title }}</span>
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
import { mobileSidebarOpened } from '../composables/sidebar'
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
  ListRowItem,
  ListFooter,
  Breadcrumbs,
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
const activeFilterCount = computed(() => [
  titleQuery.value,
  activeFilters.value.secret_type,
  activeFilters.value.folder,
  activeFilters.value.favorites_only,
].filter(Boolean).length)
const pageTitle = computed(() => activeFilters.value.folder ? `Folder: ${foldersResource.data?.find(f => f.name === activeFilters.value.folder)?.folder_name || 'Folder'}` : 'All Secrets')
const breadcrumbs = computed(() => {
  const folderName = activeFilters.value.folder
    ? (foldersResource.data?.find(f => f.name === activeFilters.value.folder)?.folder_name || 'Folder')
    : 'List'
  return [
    { label: 'Secrets', route: '/secrets' },
    { label: folderName }
  ]
})

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
      width: '18rem',
    }
  ]

  if (visibleColumns.value.secret_type) {
    cols.push({
      label: 'Type',
      key: 'secret_type',
      width: '10rem',
    })
  }

  if (visibleColumns.value.folder) {
    cols.push({
      label: 'Folder',
      key: 'folder',
      width: '11rem',
    })
  }

  if (visibleColumns.value.password_strength) {
    cols.push({
      label: 'Strength',
      key: 'password_strength',
      width: '10rem',
    })
  }

  if (visibleColumns.value.modified) {
    cols.push({
      label: 'Last Modified',
      key: 'modified',
      width: '12rem',
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
