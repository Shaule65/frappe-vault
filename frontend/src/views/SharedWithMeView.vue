<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50/20">
    <!-- Header -->
    <header class="flex h-14 items-center justify-between border-b bg-white px-5 py-3 shrink-0">
      <div class="flex items-center gap-2">
        <h1 class="text-lg font-semibold text-ink-gray-9">Shared with Me</h1>
        <Badge variant="subtle" theme="blue" size="sm" class="ml-1 font-medium">
          {{ filteredList.length }} {{ filteredList.length === 1 ? 'item' : 'items' }}
        </Badge>
      </div>
    </header>

    <!-- View Controls Bar -->
    <div class="bg-white border-b px-5 py-3 flex items-center justify-between gap-4 shrink-0">
      <!-- Quick Filters (Left side) -->
      <div class="flex flex-1 items-center gap-2 overflow-x-auto no-scrollbar">
        <!-- Title Quick Filter -->
        <div class="min-w-[180px] max-w-[240px]">
          <TextInput
            v-model="titleQuery"
            placeholder="Search shared items..."
            class="w-full text-sm h-8"
          />
        </div>
      </div>

      <!-- Controls & Dropdowns -->
      <div class="flex items-center gap-1.5 shrink-0">
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
          class="h-8 w-8 p-0 flex items-center justify-center focus:outline-none hover:bg-gray-50 border border-gray-200 rounded"
          variant="outline"
          @click="shared.reload()"
          tooltip="Refresh"
        >
          <template #icon>
            <FeatherIcon name="refresh-cw" class="w-3.5 h-3.5 text-ink-gray-7" :class="{ 'animate-spin': shared.loading }" />
          </template>
        </Button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Loading state -->
      <div v-if="shared.loading && !shared.data" class="p-6 space-y-3">
        <div v-for="i in 5" :key="i" class="h-16 bg-gray-100 rounded-lg animate-pulse" />
      </div>

      <!-- Shared secrets list view -->
      <template v-else-if="filteredList.length">
        <ListView
          v-model:selections="selectedShares"
          class="flex-1 flex flex-col overflow-hidden bg-white"
          :columns="columns"
          :rows="formattedRows"
          row-key="name"
          :options="{
            selectable: true,
            showTooltip: true,
            resizeColumn: true,
            onRowClick: (row) => handleRowClick(row),
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
              @click="handleRowClick(row)"
            >
              <ListRowItem :item="item" :align="column.align" class="text-sm font-normal text-ink-gray-7 h-full flex items-center">
                <template #default>
                  <!-- Title column -->
                  <div v-if="column.key === 'title'" class="flex items-center gap-3 py-1 min-w-0">
                    <div v-if="row.shared_doctype === 'Vault Folder'" class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-gray-100 shadow-sm bg-indigo-50 text-indigo-600">
                       <FeatherIcon name="folder" class="w-4 h-4" />
                    </div>
                    <div v-else class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-gray-100 shadow-sm"
                         :class="typeColors[item.secret_type] || 'bg-gray-100 text-gray-600'">
                       <FeatherIcon :name="typeIcons[item.secret_type] || 'file'" class="w-4 h-4" />
                    </div>
                    <div class="min-w-0 flex-1 truncate">
                      <span class="font-semibold text-ink-gray-9 hover:text-indigo-600 hover:underline cursor-pointer text-base truncate block leading-normal transition-colors">{{ item.title }}</span>
                    </div>
                  </div>

                  <!-- Type column -->
                  <span v-else-if="column.key === 'secret_type'" class="text-base text-ink-gray-9">
                    {{ row.shared_doctype === 'Vault Folder' ? 'Folder' : item }}
                  </span>

                  <!-- Shared By column -->
                  <span v-else-if="column.key === 'shared_by'" class="text-base text-ink-gray-6 truncate">{{ item }}</span>

                  <!-- Permission column -->
                  <div v-else-if="column.key === 'permission_level'">
                    <Badge
                      :theme="permissionTheme[item] || 'gray'"
                      variant="subtle"
                    >
                      {{ item }}
                    </Badge>
                  </div>

                  <!-- Expires On column -->
                  <span v-else-if="column.key === 'expires_on'" class="text-base text-ink-gray-6">{{ item }}</span>
                </template>
              </ListRowItem>
            </ListRow>
          </ListRows>
        </ListView>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Badge, Button, TextInput, FeatherIcon, ListView, ListHeader, ListHeaderItem, ListRows, ListRow, ListRowItem, Dialog, toast } from 'frappe-ui'
import { useSharedWithMe, useBulkDeleteShares } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'

const router = useRouter()
const shared = useSharedWithMe()
const bulkDeleteResource = useBulkDeleteShares()

const titleQuery = ref('')
const selectedShares = ref(new Set())
const showBulkDeleteDialog = ref(false)
const bulkDeleteLoading = ref(false)

const list = computed(() => shared.data?.shared || [])

const filteredList = computed(() => {
  let result = list.value
  if (titleQuery.value.trim()) {
    const q = titleQuery.value.toLowerCase().trim()
    result = result.filter(item => 
      (item.title && item.title.toLowerCase().includes(q)) || 
      (item.shared_by && item.shared_by.toLowerCase().includes(q))
    )
  }
  return result
})

const typeIcons = { Password: 'key', 'API Key': 'code', Note: 'file-text', 'SSH Key': 'terminal', Certificate: 'shield', 'Credit Card': 'credit-card', Database: 'database', Other: 'file' }
const typeColors = { Password: 'bg-blue-100 text-blue-600', 'API Key': 'bg-purple-100 text-purple-600', Note: 'bg-green-100 text-green-600', 'SSH Key': 'bg-orange-100 text-orange-600', Certificate: 'bg-teal-100 text-teal-600', 'Credit Card': 'bg-yellow-100 text-yellow-600', Database: 'bg-red-100 text-red-600' }
const permissionTheme = { 'View Only': 'gray', 'View & Copy': 'blue', 'Edit': 'orange', 'Full Control': 'green', 'Revoked': 'red' }

const columns = computed(() => [
  { label: 'Title', key: 'title', width: '240px' },
  { label: 'Type', key: 'secret_type', width: '120px' },
  { label: 'Shared By', key: 'shared_by', width: '180px' },
  { label: 'Permission', key: 'permission_level', width: '130px' },
  { label: 'Expires On', key: 'expires_on', width: '140px' }
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

function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
