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
    </header>

    
    <ViewControlsBar class="z-10">
      <template #left>
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
      </template>
      <template #right>
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

        <!-- Clear -->
        <Button
          v-if="titleQuery || activeFilters.secret_type || currentSort !== 'modified desc' || Object.keys(panelFilters).length"
          variant="ghost"
          class="h-8 px-2 text-sm text-ink-gray-6 hover:text-ink-gray-9 focus:outline-none font-medium"
          @click="clearFilters()"
        >
          Clear
        </Button>
      </template>
    </ViewControlsBar>

    <!-- Bookmark list -->
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
                  <div v-if="column.key === 'title'" class="flex items-center gap-3 py-1 min-w-0">
                    <SecretTypeIcon :type="item.secret_type" />
                    <span class="min-w-0 font-medium text-ink-gray-9 cursor-pointer text-base truncate block leading-normal">{{ item.title }}</span>
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
                      @click.stop="handleToggleBookmark(row)"
                    >
                      <FeatherIcon
                        name="bookmark"
                        class="w-4 h-4 text-ink-yellow-3 fill-current"
                      />
                    </Button>
                  </div>

                  <!-- Dynamic columns (fallback) -->
                  <span v-else class="text-base text-ink-gray-7 truncate">{{ item ?? '—' }}</span>
                </template>
              </ListRowItem>
            </ListRow>
          </ListRows>
          <ListSelectBanner />
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
      <EmptyState v-else icon="bookmark" title="No bookmarks yet" description="Bookmark your most-used secrets for quick access" />
    </div>
  </div>
</template>

<script setup>
import ViewControlsBar from '../components/ViewControlsBar.vue'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import RefreshIcon from '../components/RefreshIcon.vue'
import FilterPanel from '../components/FilterPanel.vue'
import SortPanel from '../components/SortPanel.vue'
import ColumnPanel from '../components/ColumnPanel.vue'
import { Button, FeatherIcon, TextInput, ListView, ListHeader, ListHeaderItem, ListRows, ListRow, ListRowItem, ListSelectBanner, ListFooter, Breadcrumbs, Select } from 'frappe-ui'
import { mobileSidebarOpened, useSecrets, useFolders, useToggleBookmark, useFilterableFields, useSortOptions } from '../composables/vault'
import { typeFilterOptions, formatDate as formatTime } from '../composables/constants'
import EmptyState from '../components/EmptyState.vue'
import SecretTypeIcon from '../components/SecretTypeIcon.vue'
import StrengthBadge from '../components/StrengthBadge.vue'

const router = useRouter()
const titleQuery = ref('')
const activeFilters = ref({ secret_type: '' })
const panelFilters = ref({})
const currentSort = ref('modified desc')
const pageLength = ref(20)

const defaultColumns = [
  { label: 'Type', key: 'secret_type', width: '10rem' },
  { label: 'Folder', key: 'folder', width: '11rem' },
  { label: 'Strength', key: 'password_strength', width: '10rem' },
  { label: 'Last Modified', key: 'modified', width: '12rem' },
]

const activeColumnDefs = ref([...defaultColumns])

const secrets = useSecrets({ bookmarks_only: 1 })
const foldersResource = useFolders()
const toggleBook = useToggleBookmark()
const filterableFields = useFilterableFields()
const sortOptions = useSortOptions()

const secretsList = computed(() => secrets.data?.secrets || [])
const totalCount = computed(() => secrets.data?.total || secretsList.value.length || 0)
const breadcrumbs = computed(() => [{ label: 'Bookmarks' }])

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
    bookmarks_only: 1,
    limit: pageLength.value,
    order_by: currentSort.value,
  }
  for (const [key, val] of Object.entries(panelFilters.value)) {
    if (val !== undefined && val !== '') {
      filters[key] = val
    }
  }
  secrets.submit(filters)
}

function clearFilters() {
  titleQuery.value = ''
  activeFilters.value = { secret_type: '' }
  panelFilters.value = {}
  currentSort.value = 'modified desc'
  pageLength.value = 20
}

async function handleToggleBookmark(s) { await toggleBook.submit({ name: s.name }); refreshSecrets() }


watch([titleQuery, activeFilters, pageLength, currentSort, panelFilters], () => {
  const filters = {
    title: titleQuery.value || undefined,
    secret_type: activeFilters.value.secret_type || undefined,
    bookmarks_only: 1,
    limit: pageLength.value,
    order_by: currentSort.value,
  }
  for (const [key, val] of Object.entries(panelFilters.value)) {
    if (val !== undefined && val !== '') {
      filters[key] = val
    }
  }
  secrets.submit(filters)
}, { deep: true, immediate: true })

</script>
