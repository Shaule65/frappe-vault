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

    
    <ViewControlsBar>
      <template #left>
        <!-- Title Quick Filter -->
        <TextInput
          v-model="titleQuery"
          placeholder="Title"
          class="w-44 shrink-0"
        />
      </template>
      <template #right>
        <!-- Bulk Delete Button -->
        <Button
          v-if="selectedShares.size > 0"
          variant="solid"
          theme="red"
          class="h-8 px-3 text-sm focus:outline-none font-medium"
          @click="showBulkDeleteDialog = true"
        >
          Delete Logs ({{ selectedShares.size }})
        </Button>

        <!-- Refresh Button -->
        <Button
          :tooltip="'Refresh'"
          :icon="RefreshIcon"
          :loading="shared.loading"
          @click="shared.reload()"
        />
      </template>
    </ViewControlsBar>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Loading state -->
      <div v-if="shared.loading && !shared.data" class="p-6 space-y-3">
        <div v-for="i in 5" :key="i" class="h-16 bg-surface-gray-3 rounded-lg animate-pulse" />
      </div>

      <!-- Shared secrets list view -->
      <template v-else-if="filteredList.length">
        <ListView
          v-model:selections="selectedShares"
          class="flex-1 flex flex-col overflow-hidden bg-surface-base"
          :columns="columns"
          :rows="paginatedRows"
          row-key="name"
          :options="{
            selectable: true,
            showTooltip: true,
            resizeColumn: true,
            onRowClick: (row) => handleRowClick(row),
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
              v-for="row in paginatedRows"
              :key="row.name"
              v-slot="{ column, item }"
              :row="row"
              @click="handleRowClick(row)"
            >
              <ListRowItem :item="item" :align="column.align" class="overflow-hidden">
                <template #default>
                  <!-- Title column -->
                  <div v-if="column.key === 'title'" class="flex items-center gap-3 py-1 min-w-0">
                    <div v-if="row.shared_doctype === 'Vault Folder'" class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-outline-gray-1 shadow-sm bg-indigo-50 text-indigo-600">
                       <FeatherIcon name="folder" class="w-4 h-4" />
                    </div>
                    <SecretTypeIcon v-else :type="item.secret_type" />
                    <span class="min-w-0 flex-1 font-semibold text-ink-gray-9 hover:text-indigo-600 cursor-pointer text-base truncate block leading-normal transition-colors">{{ item.title }}</span>
                  </div>

                  <!-- Type column -->
                  <span v-else-if="column.key === 'secret_type'" class="text-base text-ink-gray-9">
                    {{ row.shared_doctype === 'Vault Folder' ? 'Folder' : item }}
                  </span>

                  <!-- Shared By column -->
                  <span v-else-if="column.key === 'shared_by'" class="text-base text-ink-gray-6 truncate">{{ item }}</span>

                  <!-- Permission column -->
                  <Badge
                    v-else-if="column.key === 'permission_level'"
                    :theme="permissionTheme[item] || 'gray'"
                    variant="subtle"
                  >
                    {{ item }}
                  </Badge>

                  <!-- Expires On column -->
                  <span v-else-if="column.key === 'expires_on'" class="text-base text-ink-gray-6">{{ item }}</span>
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
      <EmptyState v-else icon="users" title="Nothing shared with you" description="When someone shares a secret with you, it will appear here" />
    </div>

    <!-- Bulk Delete Confirmation Dialog -->
    <Dialog
      v-model="showBulkDeleteDialog"
      :options="{
        title: 'Delete Sharing Logs',
        size: 'sm',
      }"
    >
      <template #body-content>
        <p class="text-sm text-ink-gray-7 pt-2">
          Are you sure you want to delete the <span class="font-semibold text-ink-gray-9">{{ selectedShares.size }}</span> selected sharing log records from your list?
        </p>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 px-4 pb-4">
          <Button variant="ghost" label="Cancel" @click="showBulkDeleteDialog = false" class="text-ink-gray-7 focus:outline-none" />
          <Button
            variant="solid"
            theme="red"
            label="Delete Logs"
            :loading="bulkDeleteLoading"
            @click="handleBulkDelete"
            class="px-4 font-semibold shadow-sm focus:outline-none"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import ViewControlsBar from '../components/ViewControlsBar.vue'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import RefreshIcon from '../components/RefreshIcon.vue'
import { Badge, Button, TextInput, FeatherIcon, ListView, ListHeader, ListHeaderItem, ListRows, ListRow, ListRowItem, ListSelectBanner, ListFooter, Dialog, Breadcrumbs, toast } from 'frappe-ui'
import { mobileSidebarOpened, useSharedWithMe, useBulkDeleteShares } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'
import SecretTypeIcon from '../components/SecretTypeIcon.vue'
import { permissionTheme, formatDateTime as formatTime } from '../composables/constants'

const router = useRouter()
const shared = useSharedWithMe()
const bulkDeleteResource = useBulkDeleteShares()

const titleQuery = ref('')
const selectedShares = ref(new Set())
const showBulkDeleteDialog = ref(false)
const bulkDeleteLoading = ref(false)
const pageLength = ref(20)

const list = computed(() => shared.data?.shared || [])
const totalCount = computed(() => shared.data?.total || filteredList.value.length || 0)

watch(pageLength, (newLength) => {
  shared.submit({
    limit: newLength,
  })
}, { immediate: true })
const breadcrumbs = computed(() => [{ label: 'Shared with Me' }])

const filteredList = computed(() => {
  let result = list.value
  if (titleQuery.value.trim()) {
    const q = titleQuery.value.toLowerCase().trim()
    result = result.filter(item => 
      (item.title && item.title.toLowerCase().includes(q)) || 
      (item.shared_by && item.shared_by.toLowerCase().includes(q))
    )
  }
})

const columns = ref([
  { label: 'Title', key: 'title', width: '18rem' },
  { label: 'Type', key: 'secret_type', width: '10rem' },
  { label: 'Shared By', key: 'shared_by', width: '14rem' },
  { label: 'Permission', key: 'permission_level', width: '11rem' },
  { label: 'Expires On', key: 'expires_on', width: '11rem' }
])

const formattedRows = computed(() => {
  return filteredList.value.map(s => {
    return {
      name: s.share_name, // Unique share ID as row key to avoid duplicates
      secret_name: s.shared_name, // Actual secret/folder ID
      shared_doctype: s.shared_doctype,
      title: {
        title: s.title || (s.shared_doctype === 'Vault Folder' ? 'Deleted Folder' : 'Deleted Secret'),
        secret_type: s.secret_type || 'Other',
      },
      secret_type: s.secret_type || 'Other',
      shared_by: s.shared_by || 'Unknown',
      permission_level: s.is_revoked ? 'Revoked' : (s.permission_level || 'View Only'),
      expires_on: s.expires_on ? formatTime(s.expires_on) : 'Never',
      is_revoked: s.is_revoked,
    }
  })
})

const paginatedRows = computed(() => formattedRows.value.slice(0, pageLength.value))

function handleRowClick(row) {
  if (row.is_revoked) {
    toast.error('This share has been revoked and is no longer accessible')
    return
  }
  if (row.shared_doctype === 'Vault Folder') {
    router.push({ path: '/secrets', query: { folder: row.secret_name } })
  } else {
    router.push({ name: 'SecretDetail', params: { name: row.secret_name } })
  }
}

async function handleBulkDelete() {
  if (selectedShares.value.size === 0) return
  bulkDeleteLoading.value = true
  try {
    await bulkDeleteResource.submit({
      share_names: Array.from(selectedShares.value)
    })
    toast.success('Selected logs deleted successfully')
    selectedShares.value.clear()
    shared.reload()
    showBulkDeleteDialog.value = false
  } catch (err) {
    toast.error(err.message || 'Failed to delete logs')
  } finally {
    bulkDeleteLoading.value = false
  }
}

</script>
