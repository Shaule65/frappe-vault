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
    </header>

    
    <ViewControlsBar>
      <template #left>
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
                  <div v-if="column.key === 'title'" class="flex items-center gap-3 py-1 min-w-0">
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
                        class="w-4 h-4 text-yellow-500 fill-yellow-500"
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
      <EmptyState v-else icon="star" title="No favorites yet" description="Star your most-used secrets for quick access" />
    </div>
  </div>
</template>

<script setup>
import ViewControlsBar from '../components/ViewControlsBar.vue'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import SortIcon from '../components/SortIcon.vue'
import ColumnsIcon from '../components/ColumnsIcon.vue'
import RefreshIcon from '../components/RefreshIcon.vue'
import { Badge, Button, Dropdown, FeatherIcon, TextInput, ListView, ListHeader, ListHeaderItem, ListRows, ListRow, ListRowItem, ListFooter, Breadcrumbs, Select } from 'frappe-ui'
import { mobileSidebarOpened, useSecrets, useFolders, useToggleFavorite } from '../composables/vault'
import { SECRET_TYPES } from '../composables/constants'
import EmptyState from '../components/EmptyState.vue'
import SecretTypeIcon from '../components/SecretTypeIcon.vue'
import StrengthBadge from '../components/StrengthBadge.vue'

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
const breadcrumbs = computed(() => [{ label: 'Favorites' }])


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
