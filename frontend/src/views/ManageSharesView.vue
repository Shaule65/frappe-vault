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
                    <div v-if="row.shared_doctype === 'Vault Folder'" class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-outline-gray-1 shadow-2xs bg-surface-gray-3 text-ink-gray-7">
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
                  <div v-else-if="column.key === 'shared_with'" class="flex items-center gap-2 min-w-0">
                    <Button
                      v-if="row.share_type === 'Role'"
                      variant="subtle"
                      theme="gray"
                      size="sm"
                      title="Click to view assigned role members"
                      @click.stop="openRoleUsersModal(item, row)"
                    >
                      <template #prefix>
                        <FeatherIcon name="shield" class="w-3.5 h-3.5" />
                      </template>
                      {{ item }}
                    </Button>
                    <Button
                      v-else-if="row.share_type === 'UserGroup' || row.user_count > 1"
                      variant="subtle"
                      theme="gray"
                      size="sm"
                      title="Click to view shared users"
                      @click.stop="openUserGroupModal(row)"
                    >
                      <template #prefix>
                        <FeatherIcon name="users" class="w-3.5 h-3.5" />
                      </template>
                      {{ row.user || (row.user_count ? row.user_count + ' Users' : 'Users') }}
                    </Button>
                    <span v-else class="text-base text-ink-gray-9 font-semibold truncate">{{ row.user || item }}</span>
                  </div>

                  <!-- Target Type column -->
                  <Badge v-else-if="column.key === 'share_type'" variant="subtle" theme="gray" size="sm">
                    {{ item === 'UserGroup' ? 'User' : item }}
                  </Badge>

                  <!-- Permission column -->
                  <div v-else-if="column.key === 'permission_level'" class="flex items-center gap-1.5" @click.stop>
                    <Dropdown
                      v-if="!row.is_revoked"
                      :options="permissionOptionsList.map(p => ({
                        label: p,
                        onClick: () => handleUpdateSharePermission(row.name, p)
                      }))"
                    >
                      <Badge
                        :theme="permissionTheme[item] || 'gray'"
                        variant="subtle"
                        size="sm"
                        class="cursor-pointer hover:opacity-80 transition-opacity"
                        title="Click to update permission level"
                      >
                        {{ item }} ▾
                      </Badge>
                    </Dropdown>
                    <Badge
                      v-else
                      :theme="permissionTheme[item] || 'gray'"
                      variant="subtle"
                      size="sm"
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

          <!-- Grouped MultiSelect Item Selector (Grouped by Folder Name) -->
          <div class="space-y-1.5">
            <label class="block text-p-sm-medium text-ink-gray-7">
              Select {{ newShareDoctype === 'Vault Secret' ? 'Secrets' : 'Folders' }}
            </label>
            <MultiSelect
              v-model="selectedItems"
              :options="groupedItemOptions"
              :placeholder="`Select ${newShareDoctype === 'Vault Secret' ? 'secrets' : 'folders'} to share…`"
              class="w-full"
            >
              <template #item-prefix="{ item }">
                <SecretTypeIcon v-if="item.secret_type" :type="item.secret_type" class="w-6 h-6 !w-6 !h-6 shrink-0" />
              </template>
            </MultiSelect>
          </div>

          <!-- Share Type Selection -->
          <div>
            <label class="block text-p-sm-medium text-ink-gray-7 mb-1.5">Share With</label>
            <TabButtons
              v-model="newShareType"
              :options="[
                { label: 'User', value: 'User', class: 'flex-1 !justify-center', onClick: () => { newShareRecipient = ''; selectedUserEmails = [] } },
                { label: 'Role', value: 'Role', class: 'flex-1 !justify-center', onClick: () => { newShareRecipient = ''; selectedUserEmails = [] } }
              ]"
              class="w-full !flex"
            />
          </div>

          <!-- Recipient Selection: MultiSelect Component vs Single Role Select -->
          <div v-if="newShareType === 'User'" class="space-y-1.5">
            <label class="block text-p-sm-medium text-ink-gray-7">Select Users</label>
            <MultiSelect
              v-model="selectedUserEmails"
              :options="userMembers"
              placeholder="Select users to share with…"
              class="w-full"
            >
              <template #prefix>
                <div v-if="visibleSelected.length" class="flex -space-x-1.5">
                  <Avatar
                    v-for="m in visibleSelected"
                    :key="m.value"
                    :image="m.image"
                    :label="m.label"
                    size="sm"
                  />
                  <span
                    v-if="overflowCount > 0"
                    class="z-10 grid size-5 place-items-center rounded-full bg-surface-gray-3 text-p-xs-medium text-ink-gray-7"
                  >
                    +{{ overflowCount }}
                  </span>
                </div>
                <FeatherIcon v-else name="users" class="w-4 h-4 text-ink-gray-5" />
              </template>

              <template #summary="{ selectedOptions, summary }">
                <template v-if="selectedOptions.length">
                  {{ selectedOptions.map((o) => o.label).join(', ') }}
                </template>
                <template v-else>{{ summary }}</template>
              </template>

              <template #item-prefix="{ item }">
                <Avatar :image="item.image" :label="item.label" size="sm" />
              </template>

              <template #item-label="{ item }">
                <div class="min-w-0 flex items-center justify-between w-full">
                  <div class="truncate font-medium text-ink-gray-9 text-xs">{{ item.label }}</div>
                  <div class="truncate text-[11px] text-ink-gray-5 font-mono ml-2">{{ item.value }}</div>
                </div>
              </template>
            </MultiSelect>
          </div>

          <!-- Role Selection: MultiSelect Component -->
          <div v-else class="space-y-1.5">
            <label class="block text-p-sm-medium text-ink-gray-7">Select Roles</label>
            <MultiSelect
              v-model="selectedRoles"
              :options="roleMembers"
              placeholder="Select roles to share with…"
              class="w-full"
            >
              <template #prefix>
                <div v-if="visibleSelectedRoles.length" class="flex -space-x-1.5">
                  <span
                    v-for="r in visibleSelectedRoles"
                    :key="r.value"
                    class="z-10 inline-flex items-center justify-center px-1.5 py-0.5 rounded bg-surface-blue-2 text-ink-blue-link text-xs font-medium border border-outline-blue-1"
                  >
                    {{ r.label }}
                  </span>
                  <span
                    v-if="overflowRoleCount > 0"
                    class="z-10 grid size-5 place-items-center rounded-full bg-surface-gray-3 text-p-xs-medium text-ink-gray-7"
                  >
                    +{{ overflowRoleCount }}
                  </span>
                </div>
                <FeatherIcon v-else name="shield" class="w-4 h-4 text-ink-gray-5" />
              </template>

              <template #summary="{ selectedOptions, summary }">
                <template v-if="selectedOptions.length">
                  {{ selectedOptions.map((o) => o.label).join(', ') }}
                </template>
                <template v-else>{{ summary }}</template>
              </template>

              <template #item-label="{ item }">
                <div class="min-w-0 flex items-center justify-between w-full">
                  <div class="truncate font-medium text-ink-gray-9 text-xs">{{ item.label }}</div>
                </div>
              </template>
            </MultiSelect>
          </div>

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
          :disabled="(selectedItems.length === 0 && !newShareItem) || (newShareType === 'User' ? selectedUserEmails.length === 0 : selectedRoles.length === 0)"
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
    <!-- Role Users Modal -->
    <Dialog v-model="showRoleUsersModal" :options="{ title: selectedRoleName ? `People with ${selectedRoleName} Role` : 'People with Access', size: 'lg' }">
      <template #body-content>
        <div class="flex flex-col gap-4 py-1">
          <TextInput
            v-model="roleMemberSearchQuery"
            type="text"
            placeholder="Search members by name or email…"
            iconLeft="search"
            class="w-full"
          />

          <div class="space-y-4">
            <!-- Active Members Section -->
            <div>
              <h4 class="text-xs font-bold text-ink-gray-5 uppercase tracking-wider mb-2">
                Active Members ({{ activeRoleUsersList.length }})
              </h4>

              <div v-if="roleUsersResource.loading" class="py-6 flex flex-col items-center justify-center space-y-2">
                <FeatherIcon name="loader" class="w-5 h-5 animate-spin text-ink-gray-5" />
                <span class="text-xs text-ink-gray-5">Loading members...</span>
              </div>

              <div v-else-if="activeRoleUsersList.length" class="flex flex-col max-h-56 overflow-y-auto divide-y divide-outline-gray-1 bg-surface-base border border-outline-gray-1 rounded-xl">
                <div
                  v-for="u in activeRoleUsersList"
                  :key="u.user"
                  class="flex items-center justify-between gap-3 p-2.5 hover:bg-surface-gray-1 transition-colors"
                >
                  <div class="flex items-center gap-3 min-w-0 flex-1">
                    <Avatar :label="u.full_name || u.user" size="md" />
                    <div class="min-w-0">
                      <div class="text-sm font-medium text-ink-gray-9 truncate">
                        {{ u.full_name || u.user }}
                      </div>
                      <div class="truncate text-xs text-ink-gray-5">
                        {{ u.user }}
                      </div>
                    </div>
                  </div>

                  <!-- Permission Level Selector -->
                  <FormControl
                    type="select"
                    :modelValue="getUserPermissionLevel(u)"
                    :options="[
                      { label: 'View Only', value: 'View Only' },
                      { label: 'View & Copy', value: 'View & Copy' },
                      { label: 'Edit', value: 'Edit' },
                      { label: 'Full Control', value: 'Full Control' }
                    ]"
                    class="!w-36 text-xs shrink-0"
                    @update:modelValue="(val) => handleUpdateUserPermission(u, val)"
                    @change="(val) => handleUpdateUserPermission(u, val)"
                  />

                  <!-- Three-Dot Menu -->
                  <Dropdown
                    :options="[
                      {
                        label: 'Revoke Access',
                        icon: 'lucide-user-minus',
                        theme: 'red',
                        onClick: () => handleRevokeRoleMember(u)
                      }
                    ]"
                  >
                    <template #default="{ open }">
                      <Button variant="ghost" icon="lucide-more-vertical" class="!p-1.5 text-ink-gray-5 hover:text-ink-gray-9 focus:outline-none" />
                    </template>
                  </Dropdown>
                </div>
              </div>
              <p v-else class="text-xs text-ink-gray-5 italic py-4 text-center">No active members.</p>
            </div>

            <!-- Revoked / Removed Members Section -->
            <div v-if="revokedRoleUsersList.length">
              <h4 class="text-xs font-bold text-ink-gray-5 uppercase tracking-wider mb-2">
                Revoked / Removed Members ({{ revokedRoleUsersList.length }})
              </h4>

              <div class="flex flex-col max-h-44 overflow-y-auto divide-y divide-outline-gray-1 bg-surface-gray-2 border border-outline-gray-1 rounded-xl">
                <div
                  v-for="u in revokedRoleUsersList"
                  :key="u.user"
                  class="flex items-center justify-between gap-3 p-2.5 hover:bg-surface-gray-1 transition-colors"
                >
                  <div class="flex items-center gap-3 min-w-0 flex-1">
                    <Avatar :label="u.full_name || u.user" size="md" class="opacity-60" />
                    <div class="min-w-0">
                      <div class="text-sm font-medium text-ink-gray-7 truncate flex items-center gap-2">
                        <span>{{ u.full_name || u.user }}</span>
                        <Badge variant="subtle" theme="red" size="sm">Revoked</Badge>
                      </div>
                      <div class="truncate text-xs text-ink-gray-5">
                        {{ u.user }}
                      </div>
                    </div>
                  </div>

                  <!-- Re-grant Access Button -->
                  <Button
                    variant="subtle"
                    theme="blue"
                    label="Re-grant Access"
                    icon="lucide-user-plus"
                    size="sm"
                    class="shrink-0 font-medium"
                    @click="handleRegrantRoleMember(u)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button
            variant="solid"
            label="Save Changes"
            :loading="isSavingRoleMembers"
            @click="handleSaveRoleMemberPermissions"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import ViewControlsBar from '../components/ViewControlsBar.vue'
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import RefreshIcon from '../components/RefreshIcon.vue'
import { Badge, Button, TextInput, FeatherIcon, FormControl, ListView, ListHeader, ListHeaderItem, ListRows, ListRow, ListRowItem, ListSelectBanner, ListFooter, Dialog, Breadcrumbs, toast, TabButtons, Dropdown, Avatar, MultiSelect, Autocomplete } from 'frappe-ui'
import { mobileSidebarOpened, useSharedWithMe, useShareSecret, useUnshare, useShareOptions, useSecrets, useFolders, useBulkDeleteShares, useRoleUsers, useUpdateSharePermission, useVaultStats, useSaveRoleMemberPermission } from '../composables/vault'
import EmptyState from '../components/EmptyState.vue'
import SecretTypeIcon from '../components/SecretTypeIcon.vue'
import { permissionTheme, formatDateTime as formatTime } from '../composables/constants'

const router = useRouter()
const stats = useVaultStats()

onMounted(() => {
  const user = window.frappe?.session?.user || window.frappe?.boot?.user?.name || ''
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  const isAdmin = user === 'Administrator' || roles.includes('Vault Admin') || roles.includes('System Manager') || stats.data?.is_admin
  if (!isAdmin) {
    router.replace('/shared')
  }
})
const shared = useSharedWithMe()
const secretsResource = useSecrets({ limit: 150 })
const foldersResource = useFolders()
const shareOptionsResource = useShareOptions()

const shareResource = useShareSecret()
const unshareResource = useUnshare()
const bulkDeleteResource = useBulkDeleteShares()
const roleUsersResource = useRoleUsers()
const saveRoleMemberPermResource = useSaveRoleMemberPermission()
const updateSharePermResource = useUpdateSharePermission()

const showRoleUsersModal = ref(false)
const selectedRoleName = ref('')
const selectedRoleItem = ref(null)
const roleMemberSearchQuery = ref('')
const revokedUserIds = ref(new Set())
const userPermissionOverrides = ref({})
const isSavingRoleMembers = ref(false)

const roleUsersList = computed(() => roleUsersResource.data || [])
const filteredRoleUsersList = computed(() => {
  if (!roleMemberSearchQuery.value.trim()) return roleUsersList.value
  const q = roleMemberSearchQuery.value.toLowerCase().trim()
  return roleUsersList.value.filter(u =>
    (u.full_name && u.full_name.toLowerCase().includes(q)) ||
    (u.user && u.user.toLowerCase().includes(q))
  )
})

watch(() => roleUsersResource.data, (data) => {
  if (data && Array.isArray(data)) {
    const rev = new Set()
    const perms = {}
    data.forEach(u => {
      if (u.is_revoked) rev.add(u.user)
      if (u.permission_level) perms[u.user] = u.permission_level
    })
    revokedUserIds.value = rev
    userPermissionOverrides.value = perms
  }
})

const activeRoleUsersList = computed(() => {
  return filteredRoleUsersList.value.filter(u => !revokedUserIds.value.has(u.user))
})

const revokedRoleUsersList = computed(() => {
  return filteredRoleUsersList.value.filter(u => revokedUserIds.value.has(u.user))
})

const permissionOptionsList = ['View Only', 'View & Copy', 'Edit', 'Full Control']

function openRoleUsersModal(roleName, row) {
  if (!roleName) return
  selectedRoleName.value = roleName
  selectedRoleItem.value = row || null
  roleMemberSearchQuery.value = ''
  revokedUserIds.value = new Set()
  userPermissionOverrides.value = {}
  showRoleUsersModal.value = true
  roleUsersResource.submit({
    role_name: roleName,
    shared_name: row?.secret_name || row?.shared_name || undefined,
    shared_doctype: row?.shared_doctype || 'Vault Secret'
  })
}

function openUserGroupModal(row) {
  if (!row) return
  selectedRoleName.value = ''
  selectedRoleItem.value = row
  roleMemberSearchQuery.value = ''
  revokedUserIds.value = new Set()
  userPermissionOverrides.value = {}
  showRoleUsersModal.value = true
  roleUsersResource.submit({
    shared_name: row.secret_name || row.shared_name,
    shared_doctype: row.shared_doctype || 'Vault Secret'
  })
}

function getUserPermissionLevel(userObj) {
  if (userPermissionOverrides.value && userPermissionOverrides.value[userObj.user]) {
    return userPermissionOverrides.value[userObj.user]
  }
  return userObj.permission_level || 'View Only'
}

function handleUpdateUserPermission(userObj, val) {
  let permValue = 'View Only'
  if (typeof val === 'string') {
    permValue = val
  } else if (val && typeof val === 'object') {
    if (val.target && val.target.value) {
      permValue = val.target.value
    } else if (val.value) {
      permValue = val.value
    }
  }
  userPermissionOverrides.value = {
    ...userPermissionOverrides.value,
    [userObj.user]: permValue
  }
}

function handleRevokeRoleMember(userObj) {
  const updatedSet = new Set(revokedUserIds.value)
  updatedSet.add(userObj.user)
  revokedUserIds.value = updatedSet
}

function handleRegrantRoleMember(userObj) {
  const updatedSet = new Set(revokedUserIds.value)
  updatedSet.delete(userObj.user)
  revokedUserIds.value = updatedSet
}

async function handleSaveRoleMemberPermissions() {
  if (!selectedRoleItem.value) {
    toast.error('Share item reference missing')
    return
  }
  isSavingRoleMembers.value = true
  const targetSharedName = selectedRoleItem.value.shared_name || selectedRoleItem.value.secret_name || selectedRoleItem.value.name
  const targetDocType = selectedRoleItem.value.shared_doctype || 'Vault Secret'
  try {
    const users = roleUsersList.value || []
    for (const u of users) {
      const isRev = revokedUserIds.value.has(u.user)
      const permLevel = userPermissionOverrides.value[u.user] || u.permission_level || 'View Only'
      await saveRoleMemberPermResource.submit({
        shared_name: targetSharedName,
        shared_doctype: targetDocType,
        user: u.user,
        permission_level: permLevel,
        is_revoked: isRev,
      })
    }
    toast.success('Role member permissions saved successfully')
    showRoleUsersModal.value = false
    shared.reload()
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || 'Failed to save role member permissions')
  } finally {
    isSavingRoleMembers.value = false
  }
}

async function handleUpdateSharePermission(shareName, permissionLevel) {
  try {
    await updateSharePermResource.submit({
      share_name: shareName,
      permission_level: permissionLevel
    })
    toast.success(`Permission updated to ${permissionLevel}`)
    shared.reload()
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || 'Failed to update permission')
  }
}

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

const selectedUserEmails = ref([])
const selectedRoles = ref([])
const selectedItems = ref([])

const groupedItemOptions = computed(() => {
  if (newShareDoctype.value === 'Vault Secret') {
    const folderGroups = {}
    secretsList.value.forEach(s => {
      let folderName = 'Root (No Folder)'
      if (s.folder_name) {
        folderName = s.folder_name
      } else if (s.folder) {
        const found = (foldersList.value || []).find(f => f.name === s.folder)
        if (found) folderName = found.folder_name
      }
      if (!folderGroups[folderName]) {
        folderGroups[folderName] = []
      }
      folderGroups[folderName].push({
        label: `${s.title} (${s.secret_type || 'General'})`,
        value: s.name,
        secret_type: s.secret_type || 'Other'
      })
    })
    return Object.keys(folderGroups).map(group => ({
      group,
      options: folderGroups[group],
    }))
  } else {
    return (foldersList.value || []).map(f => ({
      label: f.folder_name,
      value: f.name,
    }))
  }
})

const userMembers = computed(() => {
  const users = shareOptions.value.users || []
  return users.map(u => ({
    label: u.label || u.value,
    value: u.value,
    image: null,
  }))
})

const roleMembers = computed(() => {
  const roles = shareOptions.value.roles || []
  return roles.map(r => ({
    label: r.label || r.value,
    value: r.value,
  }))
})

const MAX_AVATARS = 3
const visibleSelected = computed(() =>
  selectedUserEmails.value
    .map((v) => userMembers.value.find((m) => m.value === v))
    .filter(Boolean)
    .slice(0, MAX_AVATARS)
)
const overflowCount = computed(() =>
  Math.max(0, selectedUserEmails.value.length - MAX_AVATARS)
)

const visibleSelectedRoles = computed(() =>
  selectedRoles.value
    .map((v) => roleMembers.value.find((m) => m.value === v))
    .filter(Boolean)
    .slice(0, MAX_AVATARS)
)
const overflowRoleCount = computed(() =>
  Math.max(0, selectedRoles.value.length - MAX_AVATARS)
)

function openShareDialog() {
  newShareDoctype.value = 'Vault Secret'
  newShareItem.value = ''
  selectedItems.value = []
  newShareType.value = 'User'
  newShareRecipient.value = ''
  selectedUserEmails.value = []
  selectedRoles.value = []
  newSharePermission.value = 'View Only'
  newShareExpiresOn.value = ''
  showShareDialog.value = true
  
  secretsResource.fetch()
  foldersResource.fetch()
  shareOptionsResource.fetch()
}

async function handleShareSecret() {
  if (selectedItems.value.length === 0 && !newShareItem.value) {
    toast.error(`Please select at least one ${newShareDoctype.value === 'Vault Secret' ? 'secret' : 'folder'} to share`)
    return
  }

  if (newShareType.value === 'User' && selectedUserEmails.value.length === 0) {
    toast.error('Please select at least one user')
    return
  }
  if (newShareType.value === 'Role' && selectedRoles.value.length === 0) {
    toast.error('Please select at least one role')
    return
  }

  const itemsToShare = selectedItems.value.length ? selectedItems.value : [newShareItem.value]

  isSharing.value = true
  try {
    if (newShareType.value === 'User') {
      for (const item of itemsToShare) {
        for (const email of selectedUserEmails.value) {
          await shareResource.submit({
            shared_name: item,
            shared_doctype: newShareDoctype.value,
            share_type: 'User',
            user: email,
            permission_level: newSharePermission.value,
            expires_on: newShareExpiresOn.value || undefined,
          })
        }
      }
      toast.success(`Shared successfully with ${selectedUserEmails.value.length} user(s)`)
    } else {
      for (const item of itemsToShare) {
        for (const role of selectedRoles.value) {
          await shareResource.submit({
            shared_name: item,
            shared_doctype: newShareDoctype.value,
            share_type: 'Role',
            frappe_role: role,
            permission_level: newSharePermission.value,
            expires_on: newShareExpiresOn.value || undefined,
          })
        }
      }
      toast.success(`Shared successfully with ${selectedRoles.value.length} role(s)`)
    }

    showShareDialog.value = false
    selectedItems.value = []
    selectedUserEmails.value = []
    selectedRoles.value = []
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
