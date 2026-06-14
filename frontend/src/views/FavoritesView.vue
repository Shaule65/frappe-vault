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
        <Badge variant="subtle" theme="yellow" size="sm" class="ml-1 font-medium shrink-0">
          {{ totalCount }} {{ totalCount === 1 ? 'favorite' : 'favorites' }}
        </Badge>
      </div>
    </header>

    
    <ViewControlsBar>
      <template #left>
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
      </template>
      <template #right>
        <!-- Refresh Button -->
        <Button
          :tooltip="'Refresh'"
          :icon="RefreshIcon"
          :loading="secrets.loading"
          @click="refreshSecrets()"
        />

        <!-- Sort Button -->
        <Dropdown :options="sortDropdownOptions">
          <template #default="{ open }">
            <Button label="Sort" @click="open">
              <template #prefix>
                <SortIcon class="h-4" />
              </template>
            </Button>
          </template>
        </Dropdown>

        <!-- Columns Button -->
        <Dropdown :options="columnsDropdownOptions">
          <template #default="{ open }">
            <Button label="Columns" @click="open">
              <template #prefix>
                <ColumnsIcon class="h-4" />
              </template>
            </Button>
          </template>
        </Dropdown>

        <!-- Clear Button -->
        <Button
          v-if="titleQuery || activeFilters.secret_type || currentSort !== 'modified desc'"
          variant="ghost"
          class="h-8 px-2 text-sm text-ink-gray-6 hover:text-ink-gray-9 focus:outline-none font-medium"
          @click="clearFilters()"
        >
          Clear
        </Button>
      </template>
    </ViewControlsBar>

    <!-- Favorite list -->
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
          <ListHeader class="border-b sm:mx-5 mx-3 bg-gray-50/50 shrink-0">
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
              class="cursor-pointer hover:bg-surface-gray-1 transition-colors h-[48px]"
              @click="router.push({ name: 'SecretDetail', params: { name: row.name } })"
            >
              <ListRowItem :item="item" :align="column.align" class="overflow-hidden text-base font-normal text-ink-gray-7 h-full flex items-center">
                <template #default>
                  <!-- Title column -->
                  <div v-if="column.key === 'title'" class="flex items-center gap-3 py-1 min-w-0">
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
                        class="w-4 h-4 text-yellow-500 fill-yellow-500"
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
      <EmptyState v-else icon="star" title="No favorites yet" description="Star your most-used secrets for quick access" />
    </div>
  </div>
</template>

<script setup>
import ViewControlsBar from '../components/ViewControlsBar.vue'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { mobileSidebarOpened } from '../composables/sidebar'
import SortIcon from '../components/SortIcon.vue'
import ColumnsIcon from '../components/ColumnsIcon.vue'
import RefreshIcon from '../components/RefreshIcon.vue'
import { Badge, Button, Dropdown, FeatherIcon, TextInput, ListView, ListHeader, ListHeaderItem, ListRows, ListRow, ListRowItem, ListFooter, Breadcrumbs } from 'frappe-ui'
import { useSecrets, useFolders, useToggleFavorite } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'

const router = useRouter()
const titleQuery = ref('')
const activeFilters = ref({ secret_type: '' })
const currentSort = ref('modified desc')
const pageLength = ref(20)

const visibleColumns = ref({
  secret_type: true,
  folder: true,
  password_strength: true,
  modified: true,
})

const secrets = useSecrets({ favorites_only: 1 })
const foldersResource = useFolders()
const toggleFav = useToggleFavorite()

const secretsList = computed(() => secrets.data?.secrets || [])
const totalCount = computed(() => secrets.data?.total || 0)
const breadcrumbs = computed(() => {
  return [
    { label: 'Favorites', route: '/favorites' },
    { label: 'List' }
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

function refreshSecrets() {
  secrets.submit({
    title: titleQuery.value || undefined,
    secret_type: activeFilters.value.secret_type || undefined,
    favorites_only: 1,
    limit: pageLength.value,
    order_by: currentSort.value,
  })
}

function clearFilters() {
  titleQuery.value = ''
  activeFilters.value = { secret_type: '' }
  currentSort.value = 'modified desc'
  pageLength.value = 20
}

function formatTime(dt) { if (!dt) return ''; const d = new Date(dt); return d.toLocaleDateString() }
async function handleToggleFavorite(s) { await toggleFav.submit({ name: s.name }); refreshSecrets() }

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
    favorites_only: 1, // Hardcoded for favorites list!
    limit: pageLength.value,
    order_by: currentSort.value,
  })
}, { deep: true, immediate: true })

</script>
