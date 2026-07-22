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
      <!-- Header Actions -->
      <div class="flex items-center gap-2">
        <Button
          variant="solid"
          size="sm"
          class="shadow-sm font-semibold"
          iconLeft="lucide-user-plus"
          label="Share Item"
          @click="openShareDialog"
        />
      </div>
    </header>

    <ViewControlsBar>
      <template #left>
        <TextInput
          v-model="titleQuery"
          placeholder="Title"
          class="w-44 shrink-0"
        />
      </template>
      <template #right>
        <Button 
          v-if="selectedShares.size === 1 && canRevokeSelected"
          iconLeft="lucide-user-minus"
          label="Revoke Access"
          @click="showBulkRevokeConfirm = true"
        />
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

      <!-- ListView Table of shares -->
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
                    <div v-if="row.shared_doctype === 'Vault Folder'" class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-outline-gray-1 shadow-sm bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
                       <FeatherIcon name="folder" class="w-4 h-4" />
                    </div>
                    <SecretTypeIcon v-else :type="item.secret_type" />
                    <span class="min-w-0 flex-1 font-medium text-ink-gray-9 cursor-pointer text-base truncate block leading-normal">{{ item.title }}</span>
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
                  <Badge v-else-if="column.key === 'share_type'" variant="subtle" theme="gray" size="sm">
                    {{ item }}
                  </Badge>

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
          <ListSelectBanner>
            <template #actions="{ unselectAll }">
              <Dropdown
                :options="[
                  ...(canRevokeSelected ? [{
                    label: 'Revoke Access',
                    icon: 'lucide-user-minus',
                    onClick: () => { showBulkRevokeConfirm = true }
                  }] : []),
                  {
                    label: 'Delete Logs',
                    icon: 'trash-2',
                    onClick: () => { showBulkDeleteDialog = true }
                  }
                ]"
              >
                <Button variant="ghost" icon="more-horizontal" class="text-ink-gray-7" />
              </Dropdown>
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
            <label class="block text-p-sm-medium text-ink-gray-7 mb-1.5">Item Type</label>
            <TabButtons
              v-model="newShareDoctype"
              :options="[
                { label: 'Secret', value: 'Vault Secret', class: 'flex-1 !justify-center', onClick: () => { newShareItem = '' } },
                { label: 'Folder', value: 'Vault Folder', class: 'flex-1 !justify-center', onClick: () => { newShareItem = '' } }
              ]"
              class="w-full !flex"
            />
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
            <label class="block text-p-sm-medium text-ink-gray-7 mb-1.5">Share With</label>
            <TabButtons
              v-model="newShareType"
              :options="[
                { label: 'User', value: 'User', class: 'flex-1 !justify-center', onClick: () => { newShareRecipient = '' } },
                { label: 'Role', value: 'Role', class: 'flex-1 !justify-center', onClick: () => { newShareRecipient = '' } }
              ]"
              class="w-full !flex"
            />
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
            type="datetime"
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

    <!-- Bulk Revoke Confirmation Dialog -->
    <Dialog
      v-model="showBulkRevokeConfirm"
      :options="{
        title: 'Revoke Selected Shares',
        size: 'sm',
      }"
    >
      <template #body-content>
        <p class="text-sm text-ink-gray-7 pt-2">
          Are you sure you want to revoke access for the <span class="font-semibold text-ink-gray-9">{{ selectedShares.size }}</span> selected sharing records? The recipients will immediately lose access.
        </p>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 px-4 pb-4">
          <Button variant="ghost" label="Cancel" @click="showBulkRevokeConfirm = false" class="text-ink-gray-7 focus:outline-none" />
          <Button
            variant="solid"
            theme="red"
            label="Revoke Access"
            :loading="bulkRevokeLoading"
            @click="handleBulkRevoke"
            class="px-4 font-semibold shadow-sm focus:outline-none"
          />
        </div>
      </template>
    </Dialog>

    <!-- Bulk Delete Confirmation Dialog -->
    <Dialog
      v-model="showBulkDeleteDialog"
      :options="{
        title: 'Delete Selected Logs',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="pt-2 flex flex-col gap-3">
          <p class="text-sm text-ink-gray-7">
            Are you sure you want to permanently delete the <span class="font-semibold text-ink-gray-9">{{ selectedShares.size }}</span> selected sharing logs? This action cannot be undone.
          </p>
          <div v-if="hasActiveSharesSelected" class="bg-surface-red-2 text-ink-red-4 text-sm p-3 rounded-md flex items-start gap-2 border border-outline-red-1">
            <FeatherIcon name="alert-triangle" class="w-4 h-4 mt-0.5 shrink-0" />
            <p>You have selected active shares. Deleting these logs will <b>immediately revoke access</b> for the recipients.</p>
          </div>
        </div>
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
import { Badge, Button, TextInput, FeatherIcon, FormControl, ListView, ListHeader, ListHeaderItem, ListRows, ListRow, ListRowItem, ListSelectBanner, ListFooter, Dialog, Breadcrumbs, toast, TabButtons, Dropdown } from 'frappe-ui'
import { mobileSidebarOpened, useSharedWithMe, useShareSecret, useUnshare, useShareOptions, useSecrets, useFolders, useBulkDeleteShares } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'
import SecretTypeIcon from '../components/SecretTypeIcon.vue'
import { permissionTheme, formatDateTime as formatTime } from '../composables/constants'

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
const showBulkRevokeConfirm = ref(false)
const bulkRevokeLoading = ref(false)
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
const totalCount = computed(() => shared.data?.total || filteredList.value.length || 0)

watch(pageLength, (newLength) => {
  shared.submit({
    limit: newLength,
  })
}, { immediate: true })
const breadcrumbs = computed(() => [{ label: 'Shares' }])
const secretsList = computed(() => secretsResource.data?.secrets || [])
const foldersList = computed(() => foldersResource.data || [])
const shareOptions = computed(() => shareOptionsResource.data || { users: [], roles: [] })

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
      (item.frappe_role && item.frappe_role.toLowerCase().includes(q))
    )
  }
  return result
})

const columns = ref([
  { label: 'Title', key: 'title', width: '18rem' },
  { label: 'Type', key: 'secret_type', width: '8rem' },
  { label: 'Shared By', key: 'shared_by', width: '12rem' },
  { label: 'Shared With', key: 'shared_with', width: '14rem' },
  { label: 'Target Type', key: 'share_type', width: '8rem' },
  { label: 'Permission', key: 'permission_level', width: '10rem' },
  { label: 'Expires On', key: 'expires_on', width: '10rem' }
])

const formattedRows = computed(() => {
  return filteredList.value.map(s => {
    let sharedWithLabel = ''
    if (s.share_type === 'User') {
      sharedWithLabel = s.user
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

const paginatedRows = computed(() => formattedRows.value.slice(0, pageLength.value))

const canRevokeSelected = computed(() => {
  if (selectedShares.value.size === 0) return false
  return Array.from(selectedShares.value).every(name => {
    const doc = formattedRows.value.find(r => r.name === name)
    return doc && !doc.is_revoked
  })
})

const hasActiveSharesSelected = computed(() => {
  if (selectedShares.value.size === 0) return false
  return Array.from(selectedShares.value).some(name => {
    const doc = formattedRows.value.find(r => r.name === name)
    return doc && !doc.is_revoked
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
      frappe_role: newShareType.value === 'Role' ? newShareRecipient.value : undefined,
      permission_level: newSharePermission.value,
      expires_on: newShareExpiresOn.value || undefined,
    })

    toast.success('Access shared successfully')
    showShareDialog.value = false
    shared.reload()
  } catch (err) {
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

async function handleBulkRevoke() {
  if (selectedShares.value.size === 0) return
  bulkRevokeLoading.value = true
  try {
    const promises = Array.from(selectedShares.value).map((name) => {
      const doc = formattedRows.value.find(r => r.name === name)
      if (doc && !doc.is_revoked) {
        return unshareResource.submit({ share_name: name })
      }
      return Promise.resolve()
    })
    await Promise.all(promises)
    
    toast.success('Selected shares revoked successfully')
    selectedShares.value.clear()
    shared.reload()
    showBulkRevokeConfirm.value = false
  } catch (err) {
    toast.error(err.message || 'Failed to revoke shares')
  } finally {
    bulkRevokeLoading.value = false
  }
}

</script>
