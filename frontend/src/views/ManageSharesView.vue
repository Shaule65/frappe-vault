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
        <Badge variant="subtle" theme="blue" size="sm" class="ml-1 font-medium shrink-0">
          {{ filteredList.length }} {{ filteredList.length === 1 ? 'active share' : 'active shares' }}
        </Badge>
      </div>
      <!-- Header Actions -->
      <div class="flex items-center gap-2">
        <Button
          variant="solid"
          size="sm"
          class="shadow-sm font-semibold"
          @click="openShareDialog"
        >
          <template #prefix><FeatherIcon name="user-plus" class="w-3.5 h-3.5" /></template>
          <span>Share Item</span>
        </Button>
      </div>
    </header>

    <ViewControlsBar>
      <template #left>
        <div class="m-1 min-w-36">
          <TextInput
            v-model="titleQuery"
            placeholder="Title"
            class="w-full"
          />
        </div>
      </template>
      <template #right>
        <!-- Bulk Delete Button -->
        <Button
          v-if="selectedShares.size > 0"
          variant="solid"
          theme="red"
          class="h-8 px-3 text-sm focus:outline-none"
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
        <div v-for="i in 5" :key="i" class="h-16 bg-gray-100 rounded-lg animate-pulse" />
      </div>

      <!-- ListView Table of shares -->
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
              @click="handleRowClick(row)"
            >
              <ListRowItem :item="item" :align="column.align" class="overflow-hidden">
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
                      <span class="font-semibold text-ink-gray-9 hover:text-indigo-600  cursor-pointer text-base truncate block leading-normal transition-colors">{{ item.title }}</span>
                    </div>
                  </div>

                  <!-- Type column -->
                  <span v-else-if="column.key === 'secret_type'" class="text-base text-ink-gray-9">
                    {{ row.shared_doctype === 'Vault Folder' ? 'Folder' : item }}
                  </span>

                  <!-- Shared By column -->
                  <span v-else-if="column.key === 'shared_by'" class="text-base text-ink-gray-6 truncate">{{ item }}</span>

                  <!-- Shared With column -->
                  <span v-else-if="column.key === 'shared_with'" class="text-base text-ink-gray-9 font-semibold truncate">{{ item }}</span>

                  <!-- Target Type column -->
                  <div v-else-if="column.key === 'share_type'">
                    <Badge variant="subtle" theme="gray" size="sm">
                      {{ item }}
                    </Badge>
                  </div>

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

                  <!-- Actions column (Revoke) -->
                  <div v-else-if="column.key === 'actions'" class="flex justify-end w-full" @click.stop>
                    <Button
                      v-if="!row.is_revoked"
                      variant="ghost"
                      theme="red"
                      size="sm"
                      class="h-7.5 px-2 text-ink-red-3 hover:text-ink-red-4 hover:bg-red-50 rounded focus:outline-none"
                      @click="confirmRevokeShare(row)"
                      tooltip="Revoke Share"
                    >
                      <template #icon>
                        <FeatherIcon name="trash-2" class="w-3.5 h-3.5" />
                      </template>
                    </Button>
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
            rowCount: filteredList.length,
            totalCount: totalCount,
          }"
          @loadMore="pageLength += 20"
        />
      </template>

      <!-- Empty state -->
      <EmptyState v-else icon="users" title="No shares found" description="Active shared secrets or folders will appear in this board" />
    </div>

    <!-- Admin Share Secret/Folder Dialog -->
    <Dialog
      v-model="showShareDialog"
      :options="{
        title: 'Share a Secret or Folder',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="space-y-4 pt-2">
          <!-- Shared DocType Selector -->
          <div>
            <label class="block text-sm text-ink-gray-5 mb-1.5">Item Type</label>
            <div class="flex gap-1.5 p-1 bg-surface-gray-2 rounded-lg">
              <button
                v-for="doctype in ['Vault Secret', 'Vault Folder']"
                :key="doctype"
                type="button"
                class="flex-1 py-1.5 text-xs font-medium rounded-md transition-all duration-200 focus:outline-none"
                :class="newShareDoctype === doctype ? 'bg-white text-ink-gray-9 shadow-sm' : 'text-ink-gray-6 hover:text-ink-gray-9'"
                @click="() => { newShareDoctype = doctype; newShareItem = '' }"
              >
                {{ doctype === 'Vault Secret' ? 'Secret' : 'Folder' }}
              </button>
            </div>
          </div>

          <!-- Item Selector -->
          <FormControl
            :label="`Select ${newShareDoctype === 'Vault Secret' ? 'Secret' : 'Folder'}`"
            type="select"
            v-model="newShareItem"
            :options="shareItemOptions"
          />

          <!-- Share Type Selection -->
          <div>
            <label class="block text-sm text-ink-gray-5 mb-1.5">Share With</label>
            <div class="flex gap-1.5 p-1 bg-surface-gray-2 rounded-lg">
              <button
                v-for="t in ['User', 'Group', 'Role']"
                :key="t"
                type="button"
                class="flex-1 py-1.5 text-xs font-medium rounded-md transition-all duration-200 focus:outline-none"
                :class="newShareType === t ? 'bg-white text-ink-gray-9 shadow-sm' : 'text-ink-gray-6 hover:text-ink-gray-9'"
                @click="() => { newShareType = t; newShareRecipient = '' }"
              >
                {{ t }}
              </button>
            </div>
          </div>

          <!-- Recipient Selection -->
          <FormControl
            :label="`Select ${newShareType}`"
            type="select"
            v-model="newShareRecipient"
            :options="recipientOptions"
          />

          <!-- Permission Level Selection -->
          <FormControl
            label="Permission Level"
            type="select"
            v-model="newSharePermission"
            :options="[
              { label: 'View Only', value: 'View Only' },
              { label: 'View & Copy', value: 'View & Copy' },
              { label: 'Edit', value: 'Edit' },
              { label: 'Full Control', value: 'Full Control' }
            ]"
          />

          <!-- Optional Expiration Date -->
          <FormControl
            label="Expires On (Optional)"
            type="datetime-local"
            v-model="newShareExpiresOn"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" label="Cancel" @click="showShareDialog = false" class="text-ink-gray-7 focus:outline-none" />
        <Button
          variant="solid"
          label="Share"
          :loading="isSharing"
          :disabled="!newShareItem || !newShareRecipient"
          @click="handleShareSecret"
          class="font-semibold shadow-sm focus:outline-none"
        />
      </template>
    </Dialog>

    <!-- Revoke Confirmation Dialog -->
    <Dialog
      v-model="showRevokeConfirm"
      :options="{
        title: 'Revoke Share Access',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="pt-2">
          <p class="text-sm text-ink-gray-7">
            Are you sure you want to revoke share access for
            <span class="font-bold text-ink-gray-9">{{ shareToRevoke?.shared_with }}</span> on {{ shareToRevoke?.shared_doctype === 'Vault Folder' ? 'folder' : 'secret' }}
            <span class="font-bold text-ink-gray-9">"{{ shareToRevoke?.title?.title || shareToRevoke?.title }}"</span>?
          </p>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 px-4 pb-4">
          <Button variant="ghost" label="Cancel" @click="showRevokeConfirm = false" class="text-ink-gray-7 focus:outline-none" />
          <Button
            variant="solid"
            theme="red"
            label="Revoke Access"
            :loading="unshareResource.loading"
            @click="handleRevokeShare"
            class="px-4 font-semibold shadow-sm focus:outline-none"
          />
        </div>
      </template>
    </Dialog>

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
          Are you sure you want to permanently delete the <span class="font-semibold text-ink-gray-9">{{ selectedShares.size }}</span> selected sharing log records? This action cannot be undone.
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
import { mobileSidebarOpened } from '../composables/sidebar'
import RefreshIcon from '../components/RefreshIcon.vue'
import { Badge, Button, TextInput, FeatherIcon, FormControl, ListView, ListHeader, ListHeaderItem, ListRows, ListRow, ListRowItem, ListFooter, Dialog, Breadcrumbs, toast } from 'frappe-ui'
import { useSharedWithMe, useShareSecret, useUnshare, useShareOptions, useSecrets, useFolders, useBulkDeleteShares } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'

const router = useRouter()
const shared = useSharedWithMe()
const secretsResource = useSecrets({ limit: 150 })
const foldersResource = useFolders()
const shareOptionsResource = useShareOptions()

const shareResource = useShareSecret()
const unshareResource = useUnshare()
const bulkDeleteResource = useBulkDeleteShares()

const titleQuery = ref('')
const selectedShares = ref(new Set())
const showBulkDeleteDialog = ref(false)
const bulkDeleteLoading = ref(false)
const pageLength = ref(20)

// Form Dialog state
const showShareDialog = ref(false)
const newShareDoctype = ref('Vault Secret')
const newShareItem = ref('')
const newShareType = ref('User')
const newShareRecipient = ref('')
const newSharePermission = ref('View Only')
const newShareExpiresOn = ref('')
const isSharing = ref(false)

// Revoke dialog state
const showRevokeConfirm = ref(false)
const shareToRevoke = ref(null)

const list = computed(() => shared.data?.shared || [])
const totalCount = computed(() => shared.data?.total || 0)

watch(pageLength, (newLength) => {
  shared.submit({
    limit: newLength,
  })
}, { immediate: true })
const breadcrumbs = computed(() => {
  return [
    { label: 'Manage Shares', route: '/manage-shares' },
    { label: 'List' }
  ]
})
const secretsList = computed(() => secretsResource.data?.secrets || [])
const foldersList = computed(() => foldersResource.data || [])
const shareOptions = computed(() => shareOptionsResource.data || { users: [], groups: [], roles: [] })

const shareItemOptions = computed(() => {
  const options = [{ label: 'Choose item to share...', value: '' }]
  if (newShareDoctype.value === 'Vault Secret') {
    secretsList.value.forEach(s => {
      options.push({ label: `${s.title} (${s.secret_type})`, value: s.name })
    })
  } else {
    foldersList.value.forEach(f => {
      options.push({ label: f.folder_name, value: f.name })
    })
  }
  return options
})

const recipientOptions = computed(() => {
  const list = newShareType.value === 'User' 
    ? shareOptions.value.users 
    : newShareType.value === 'Group' 
      ? shareOptions.value.groups 
      : shareOptions.value.roles
  return [{ label: 'Choose recipient...', value: '' }, ...list]
})

const filteredList = computed(() => {
  let result = list.value
  if (titleQuery.value.trim()) {
    const q = titleQuery.value.toLowerCase().trim()
    result = result.filter(item => 
      (item.title && item.title.toLowerCase().includes(q)) || 
      (item.shared_by && item.shared_by.toLowerCase().includes(q)) ||
      (item.user && item.user.toLowerCase().includes(q)) ||
      (item.group && item.group.toLowerCase().includes(q)) ||
      (item.frappe_role && item.frappe_role.toLowerCase().includes(q))
    )
  }
  return result
})

const typeIcons = { Password: 'key', 'API Key': 'code', Note: 'file-text', 'SSH Key': 'terminal', Certificate: 'shield', 'Credit Card': 'credit-card', Database: 'database', Other: 'file' }
const typeColors = { Password: 'bg-blue-100 text-blue-600', 'API Key': 'bg-purple-100 text-purple-600', Note: 'bg-green-100 text-green-600', 'SSH Key': 'bg-orange-100 text-orange-600', Certificate: 'bg-teal-100 text-teal-600', 'Credit Card': 'bg-yellow-100 text-yellow-600', Database: 'bg-red-100 text-red-600' }
const permissionTheme = { 'View Only': 'gray', 'View & Copy': 'blue', 'Edit': 'orange', 'Full Control': 'green', 'Revoked': 'red' }

const columns = ref([
  { label: 'Title', key: 'title', width: '18rem' },
  { label: 'Type', key: 'secret_type', width: '8rem' },
  { label: 'Shared By', key: 'shared_by', width: '12rem' },
  { label: 'Shared With', key: 'shared_with', width: '14rem' },
  { label: 'Target Type', key: 'share_type', width: '8rem' },
  { label: 'Permission', key: 'permission_level', width: '10rem' },
  { label: 'Expires On', key: 'expires_on', width: '10rem' },
  { label: '', key: 'actions', width: '4rem', align: 'right' }
])

const formattedRows = computed(() => {
  return filteredList.value.map(s => {
    let sharedWithLabel = ''
    if (s.share_type === 'User') {
      sharedWithLabel = s.user
    } else if (s.share_type === 'Group') {
      sharedWithLabel = s.group
    } else if (s.share_type === 'Role') {
      sharedWithLabel = s.frappe_role
    }
    return {
      name: s.share_name, // Unique Vault Share ID as row key
      secret_name: s.shared_name, // Actual secret/folder ID
      shared_doctype: s.shared_doctype,
      title: {
        title: s.title || (s.shared_doctype === 'Vault Folder' ? 'Deleted Folder' : 'Deleted Secret'),
        secret_type: s.secret_type || 'Other',
      },
      secret_type: s.secret_type || 'Other',
      shared_by: s.shared_by || 'Unknown',
      shared_with: sharedWithLabel || 'Everyone',
      share_type: s.share_type || 'User',
      permission_level: s.is_revoked ? 'Revoked' : (s.permission_level || 'View Only'),
      expires_on: s.expires_on ? formatTime(s.expires_on) : 'Never',
      is_revoked: s.is_revoked,
    }
  })
})

function handleRowClick(row) {
  if (row.shared_doctype === 'Vault Folder') {
    router.push({ path: '/secrets', query: { folder: row.secret_name } })
  } else {
    router.push({ name: 'SecretDetail', params: { name: row.secret_name } })
  }
}

function openShareDialog() {
  newShareDoctype.value = 'Vault Secret'
  newShareItem.value = ''
  newShareType.value = 'User'
  newShareRecipient.value = ''
  newSharePermission.value = 'View Only'
  newShareExpiresOn.value = ''
  showShareDialog.value = true
  
  secretsResource.fetch()
  foldersResource.fetch()
  shareOptionsResource.fetch()
}

async function handleShareSecret() {
  if (!newShareItem.value) {
    toast.error(`Please select a ${newShareDoctype.value === 'Vault Secret' ? 'secret' : 'folder'} to share`)
    return
  }
  if (!newShareRecipient.value) {
    toast.error('Please select a recipient')
    return
  }

  isSharing.value = true
  try {
    await shareResource.submit({
      shared_name: newShareItem.value,
      shared_doctype: newShareDoctype.value,
      share_type: newShareType.value,
      user: newShareType.value === 'User' ? newShareRecipient.value : undefined,
      group: newShareType.value === 'Group' ? newShareRecipient.value : undefined,
      frappe_role: newShareType.value === 'Role' ? newShareRecipient.value : undefined,
      permission_level: newSharePermission.value,
      expires_on: newShareExpiresOn.value || undefined,
    })

    toast.success('Access shared successfully')
    showShareDialog.value = false
    shared.reload()
  } catch (err) {
    console.error(err)
    toast.error(err.messages?.[0] || err.message || 'Failed to share access')
  } finally {
    isSharing.value = false
  }
}

function confirmRevokeShare(row) {
  shareToRevoke.value = row
  showRevokeConfirm.value = true
}

async function handleRevokeShare() {
  if (!shareToRevoke.value) return
  
  try {
    await unshareResource.submit({ share_name: shareToRevoke.value.name })
    toast.success(`Revoked access for ${shareToRevoke.value.shared_with}`)
    showRevokeConfirm.value = false
    shareToRevoke.value = null
    shared.reload()
  } catch (err) {
    console.error(err)
    toast.error(err.message || 'Failed to revoke access')
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
