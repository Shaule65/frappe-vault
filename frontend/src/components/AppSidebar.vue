<template>
  <aside
    class="h-full border-r bg-surface-menu-bar flex flex-col justify-between transition-all duration-300 ease-in-out select-none shrink-0"
    :class="isSidebarCollapsed ? 'w-12' : 'w-[220px]'"
  >
    <!-- Brand & User Dropdown at the Top -->
    <div class="p-2">
      <Popover placement="bottom-start" trigger="click" class="w-full">
        <template #target="{ isOpen, togglePopover }">
          <button
            class="flex h-12 items-center rounded-md py-2 duration-200 ease-in-out w-full focus:outline-none focus:ring-0 focus-visible:ring-0 focus-visible:outline-none"
            :class="
              isSidebarCollapsed
                ? 'w-auto px-0 justify-center mx-auto'
                : isOpen
                  ? 'px-2 bg-surface-white shadow-sm'
                  : 'px-2 hover:bg-surface-gray-3'
            "
            @click.prevent="togglePopover()"
          >
            <div class="flex items-center w-full" :class="isSidebarCollapsed ? 'justify-center gap-0' : 'pl-0'">
              <Tooltip text="Frappe Vault" placement="right" :disabled="!isSidebarCollapsed">
                <!-- Same SVG as /assets/frappe_vault/images/vault-logo.svg -->
                <svg width="32" height="32" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" class="rounded-xl shrink-0 shadow-sm">
                  <rect width="48" height="48" rx="12" :fill="`url(#vaultGrad-${isMobile ? 'mobile' : 'desktop'})`"/>
                  <path d="M24 12C18.48 12 14 16.48 14 22V26H12V36H36V26H34V22C34 16.48 29.52 12 24 12ZM18 22C18 18.69 20.69 16 24 16C27.31 16 30 18.69 30 22V26H18V22ZM24 32C22.9 32 22 31.1 22 30C22 28.9 22.9 28 24 28C25.1 28 26 28.9 26 30C26 31.1 25.1 32 24 32Z" fill="white"/>
                  <defs>
                    <linearGradient :id="`vaultGrad-${isMobile ? 'mobile' : 'desktop'}`" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#2563EB"/>
                      <stop offset="1" stop-color="#4338CA"/>
                    </linearGradient>
                  </defs>
                </svg>
              </Tooltip>
              <div
                class="flex flex-1 flex-col text-left duration-200 ease-in-out truncate"
                :class="
                  isSidebarCollapsed
                    ? 'ml-0 w-0 overflow-hidden opacity-0'
                    : 'ml-2 w-auto opacity-100'
                "
              >
                <div class="text-sm font-semibold leading-none text-ink-gray-9 truncate">
                  Frappe Vault
                </div>
                <div class="mt-1.5 text-xs leading-none text-ink-gray-7 truncate">
                  {{ userName }}
                </div>
              </div>
              <div
                v-if="!isSidebarCollapsed"
                class="duration-200 ease-in-out shrink-0"
              >
                <FeatherIcon
                  name="chevron-down"
                  class="w-4 h-4 text-ink-gray-5"
                  aria-hidden="true"
                />
              </div>
            </div>
          </button>
        </template>
        <template #body="{ close }">
          <div class="flex flex-col rounded-lg border border-outline-gray-2 bg-surface-white p-1 text-sm text-ink-gray-8 shadow-xl min-w-[180px] mt-1">
            <!-- Apps popover switcher -->
            <Popover placement="right-start" trigger="hover">
              <template #target="{ togglePopover }">
                <button
                  class="w-full flex h-8 items-center justify-between rounded px-2.5 hover:bg-surface-gray-2 text-ink-gray-8 text-left focus:outline-none"
                  @click.prevent="togglePopover()"
                >
                  <div class="flex gap-2 items-center">
                    <FeatherIcon name="grid" class="w-4 h-4 text-ink-gray-7" />
                    <span class="text-sm font-medium">Apps</span>
                  </div>
                  <FeatherIcon name="chevron-right" class="w-4 h-4 text-ink-gray-5" />
                </button>
              </template>
              <template #body>
                <div class="flex flex-col rounded-lg border border-outline-gray-2 bg-surface-white p-1.5 text-sm text-ink-gray-8 shadow-xl min-w-32">
                  <a href="/app" class="flex items-center gap-2 rounded p-1.5 hover:bg-surface-gray-2">
                    <img class="w-6 h-6 shrink-0" :src="'/assets/frappe/images/framework.png'" />
                    <span class="text-sm">Desk</span>
                  </a>
                  <a href="/crm" class="flex items-center gap-2 rounded p-1.5 hover:bg-surface-gray-2">
                    <img class="w-6 h-6 shrink-0" :src="'/assets/crm/images/crm-logo.svg'" onerror="this.src='/assets/frappe/images/framework.png'" />
                    <span class="text-sm">CRM</span>
                  </a>
                </div>
              </template>
            </Popover>



            <!-- About -->
            <button
              class="w-full flex h-8 items-center gap-2 rounded px-2.5 hover:bg-surface-gray-2 text-ink-gray-8 text-left focus:outline-none"
              @click="() => { showAboutModal = true; close() }"
            >
              <FeatherIcon name="info" class="w-4 h-4 text-ink-gray-7" />
              <span class="text-sm font-medium">About</span>
            </button>

            <div class="border-t border-gray-100 my-1" />

            <!-- Logout -->
            <button
              class="w-full flex h-8 items-center gap-2 rounded px-2.5 hover:bg-surface-red-2 text-ink-red-3 hover:text-ink-red-4 text-left focus:outline-none"
              @click="handleLogout"
            >
              <FeatherIcon name="log-out" class="w-4 h-4" />
              <span class="text-sm font-medium">Logout</span>
            </button>
          </div>
        </template>
      </Popover>
    </div>

    <!-- Primary Navigation -->
    <nav class="flex-1 flex flex-col py-3 space-y-0.5 overflow-y-auto custom-scrollbar">
      <SidebarLink
        v-for="item in navItems"
        :key="item.name"
        :to="item.to"
        :icon="item.icon"
        :label="item.label"
        :isCollapsed="isSidebarCollapsed"
      >
        <template #right v-if="item.count && !isSidebarCollapsed">
          <Badge :label="String(item.count)" variant="subtle" theme="gray" />
        </template>
      </SidebarLink>

      <!-- Folders Section -->
      <div class="pt-3 mt-3 border-t border-gray-100/50">
        <div class="flex items-center justify-between px-4 mb-2" v-if="!isSidebarCollapsed">
          <p class="text-xs font-semibold text-ink-gray-4 uppercase tracking-wider pl-1">Folders</p>
          <Button variant="ghost" size="sm" class="h-6 w-6 p-0 hover:bg-surface-gray-2 rounded" @click="openCreateFolderDialog">
            <FeatherIcon name="plus" class="w-3.5 h-3.5 text-ink-gray-7" />
          </Button>
        </div>
        <div class="flex flex-col items-center mb-2" v-else>
          <div class="w-full border-b border-gray-100/50 my-1" />
          <Tooltip text="Create Folder" placement="right">
            <Button variant="ghost" size="sm" class="h-8 w-8 p-0 hover:bg-surface-gray-2 rounded" @click="openCreateFolderDialog">
              <FeatherIcon name="plus" class="w-4 h-4 text-ink-gray-7" />
            </Button>
          </Tooltip>
        </div>

        <SidebarLink
          v-for="folder in folders"
          :key="folder.name"
          :to="`/secrets?folder=${folder.name}`"
          :label="folder.folder_name"
          :isCollapsed="isSidebarCollapsed"
        >
          <template #icon>
            <div class="flex items-center justify-center w-4 h-4">
              <div
                class="w-2.5 h-2.5 rounded-full shrink-0 border border-black/5"
                :style="{ backgroundColor: folder.color || '#6b7280' }"
              />
            </div>
          </template>
          <template #right>
            <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-150" @click.prevent.stop>
              <Dropdown :options="getFolderOptions(folder)">
                <template #default="{ open }">
                  <button
                    class="p-0.5 rounded hover:bg-surface-gray-3 text-ink-gray-6 focus:outline-none"
                    :class="{ 'bg-surface-gray-3': open }"
                  >
                    <FeatherIcon name="more-horizontal" class="w-3.5 h-3.5" />
                  </button>
                </template>
              </Dropdown>
            </div>
          </template>
        </SidebarLink>
      </div>
    </nav>

    <!-- Bottom Controls -->
    <div v-if="!isMobile" class="my-2 flex flex-col gap-1">
      <!-- Collapse toggle button -->
      <SidebarLink
        :label="isSidebarCollapsed ? 'Expand' : 'Collapse'"
        :isCollapsed="isSidebarCollapsed"
        class="text-ink-gray-7 hover:text-ink-gray-9 hover:bg-surface-gray-2"
        @click="isSidebarCollapsed = !isSidebarCollapsed"
      >
        <template #icon>
          <span class="grid h-4 w-4 flex-shrink-0 place-items-center">
            <CollapseSidebar
              class="h-4 w-4 text-ink-gray-7 duration-300 ease-in-out"
              :class="{ '[transform:rotateY(180deg)]': isSidebarCollapsed }"
            />
          </span>
        </template>
      </SidebarLink>
    </div>

    <!-- About Dialog -->
    <Dialog
      v-model="showAboutModal"
      :options="{
        title: 'About Frappe Vault',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="space-y-3 text-sm text-ink-gray-7 leading-relaxed">
          <p>
            Frappe Vault is a secure, modern password and secrets manager built specifically for the Frappe ecosystem.
          </p>
          <div class="border-t border-gray-100 pt-3 flex flex-col gap-1">
            <div>
              <span class="font-medium text-ink-gray-9">App Version:</span> 0.0.1 (dev)
            </div>
            <div>
              <span class="font-medium text-ink-gray-9">Framework Version:</span> 16.18.2
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Create Folder Dialog -->
    <Dialog
      v-model="showCreateFolderDialog"
      :options="{
        title: 'New Folder',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            label="Folder Name"
            v-model="newFolderName"
            placeholder="e.g. Work, Personal"
            @keyup.enter="handleCreateFolder"
          />
          <div>
            <label class="block text-xs text-ink-gray-5 mb-1.5 font-medium">Folder Color</label>
            <div class="flex items-center gap-2">
              <button
                v-for="color in curatedColors"
                :key="color"
                class="w-6 h-6 rounded-full border border-black/10 flex items-center justify-center focus:outline-none transition-transform"
                :style="{ backgroundColor: color }"
                :class="{ 'scale-110 ring-2 ring-indigo-500 ring-offset-2': newFolderColor === color }"
                @click="newFolderColor = color"
              >
                <FeatherIcon v-if="newFolderColor === color" name="check" class="w-3.5 h-3.5 text-white" />
              </button>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="showCreateFolderDialog = false" />
          <Button
            variant="solid"
            label="Create"
            :loading="createFolderResource.loading"
            :disabled="!newFolderName.trim()"
            @click="handleCreateFolder"
          />
        </div>
      </template>
    </Dialog>

    <!-- Edit Folder Dialog -->
    <Dialog
      v-model="showEditFolderDialog"
      :options="{
        title: 'Edit Folder',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            label="Folder Name"
            v-model="editFolderName"
            placeholder="e.g. Work, Personal"
            @keyup.enter="handleEditFolder"
          />
          <div>
            <label class="block text-xs text-ink-gray-5 mb-1.5 font-medium">Folder Color</label>
            <div class="flex items-center gap-2">
              <button
                v-for="color in curatedColors"
                :key="color"
                class="w-6 h-6 rounded-full border border-black/10 flex items-center justify-center focus:outline-none transition-transform"
                :style="{ backgroundColor: color }"
                :class="{ 'scale-110 ring-2 ring-indigo-500 ring-offset-2': editFolderColor === color }"
                @click="editFolderColor = color"
              >
                <FeatherIcon v-if="editFolderColor === color" name="check" class="w-3.5 h-3.5 text-white" />
              </button>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="showEditFolderDialog = false" />
          <Button
            variant="solid"
            label="Save"
            :loading="updateFolderResource.loading"
            :disabled="!editFolderName.trim()"
            @click="handleEditFolder"
          />
        </div>
      </template>
    </Dialog>

    <!-- Delete Folder Warning Dialog -->
    <Dialog
      v-model="showDeleteFolderDialog"
      :options="{
        title: 'Delete Folder',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="space-y-2">
          <p class="text-sm text-ink-gray-7" v-if="loadingCount">
            Analyzing folder secrets...
          </p>
          <template v-else>
            <div class="space-y-3" v-if="deleteSecretsCount > 0">
              <div class="p-3 bg-red-50 border border-red-100 rounded-lg text-ink-red-3 flex items-start gap-2.5">
                <FeatherIcon name="alert-triangle" class="w-5 h-5 shrink-0 mt-0.5" />
                <div class="text-sm">
                  <p class="font-semibold text-ink-red-4">Warning: Contains Secrets</p>
                  <p class="mt-1 leading-relaxed">
                    This folder contains <span class="font-bold">{{ deleteSecretsCount }}</span> {{ deleteSecretsCount === 1 ? 'secret' : 'secrets' }}. Deleting this folder will <span class="font-bold">permanently delete the folder and all secrets stored inside it</span>!
                  </p>
                </div>
              </div>
              <p class="text-sm text-ink-gray-7 pl-1">
                Are you sure you want to proceed with deleting the folder <span class="font-semibold text-ink-gray-9">"{{ folderToDelete?.folder_name }}"</span>?
              </p>
            </div>
            <div class="space-y-2" v-else>
              <p class="text-sm text-ink-gray-7">
                Are you sure you want to delete the empty folder <span class="font-semibold text-ink-gray-9">"{{ folderToDelete?.folder_name }}"</span>?
              </p>
            </div>
          </template>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="showDeleteFolderDialog = false" />
          <Button
            variant="solid"
            theme="red"
            label="Delete"
            :loading="deleteFolderResource.loading"
            :disabled="loadingCount"
            @click="handleDeleteFolder"
          />
        </div>
      </template>
    </Dialog>
  </aside>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Badge, Button, Popover, FeatherIcon, Tooltip, Dialog, Dropdown, FormControl } from 'frappe-ui'
import { useVaultStats, useFolders, useCreateFolder, useDeleteFolder, useUpdateFolder, useFolderSecrets } from '../composables/vault'
import SidebarLink from './SidebarLink.vue'
import CollapseSidebar from './CollapseSidebar.vue'
import LayoutDashboard from '~icons/lucide/layout-dashboard'

const props = defineProps({
  isMobile: { type: Boolean, default: false }
})

const route = useRoute()
const router = useRouter()
const stats = useVaultStats()
const foldersResource = useFolders()

const createFolderResource = useCreateFolder()
const deleteFolderResource = useDeleteFolder()
const updateFolderResource = useUpdateFolder()
const folderSecretsResource = useFolderSecrets()

const showCreateFolderDialog = ref(false)
const newFolderName = ref('')
const newFolderColor = ref('#3b82f6')

const showEditFolderDialog = ref(false)
const folderToEdit = ref(null)
const editFolderName = ref('')
const editFolderColor = ref('#3b82f6')

const showDeleteFolderDialog = ref(false)
const folderToDelete = ref(null)
const deleteSecretsCount = ref(0)
const loadingCount = ref(false)

const curatedColors = [
  '#3b82f6', // Blue
  '#10b981', // Green
  '#f97316', // Orange
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#ef4444', // Red
]

function openCreateFolderDialog() {
  newFolderName.value = ''
  newFolderColor.value = '#3b82f6'
  showCreateFolderDialog.value = true
}

async function handleCreateFolder() {
  if (!newFolderName.value.trim()) return
  try {
    await createFolderResource.submit({
      folder_name: newFolderName.value.trim(),
      color: newFolderColor.value,
    })
    showCreateFolderDialog.value = false
    foldersResource.reload()
    stats.reload()
  } catch (err) {
    console.error(err)
  }
}

function getFolderOptions(folder) {
  return [
    {
      label: 'Edit Folder',
      icon: 'edit-2',
      onClick: () => {
        folderToEdit.value = folder
        editFolderName.value = folder.folder_name
        editFolderColor.value = folder.color || '#3b82f6'
        showEditFolderDialog.value = true
      }
    },
    {
      label: 'Delete Folder',
      icon: 'trash-2',
      onClick: () => openDeleteFolderDialog(folder)
    }
  ]
}

function openDeleteFolderDialog(folder) {
  folderToDelete.value = folder
  deleteSecretsCount.value = 0
  loadingCount.value = true
  showDeleteFolderDialog.value = true

  folderSecretsResource.submit({ folder_name: folder.name }).then((res) => {
    deleteSecretsCount.value = res.total || 0
    loadingCount.value = false
  }).catch(() => {
    loadingCount.value = false
  })
}

async function handleEditFolder() {
  if (!editFolderName.value.trim() || !folderToEdit.value) return
  try {
    await updateFolderResource.submit({
      name: folderToEdit.value.name,
      folder_name: editFolderName.value.trim(),
      color: editFolderColor.value,
    })
    showEditFolderDialog.value = false
    folderToEdit.value = null
    foldersResource.reload()
  } catch (err) {
    console.error(err)
  }
}

async function handleDeleteFolder() {
  if (!folderToDelete.value) return
  try {
    await deleteFolderResource.submit({
      name: folderToDelete.value.name,
    })

    // Redirect if they are currently inside that folder's secrets list
    if (route.query.folder === folderToDelete.value.name) {
      router.push('/secrets')
    }

    showDeleteFolderDialog.value = false
    folderToDelete.value = null
    foldersResource.reload()
    stats.reload()
  } catch (err) {
    console.error(err)
  }
}

// LocalStorage collapsed state syncing
const _isSidebarCollapsed = ref(localStorage.getItem('isSidebarCollapsed') === 'true')
const isSidebarCollapsed = computed({
  get: () => props.isMobile ? false : _isSidebarCollapsed.value,
  set: (val) => {
    _isSidebarCollapsed.value = val
    localStorage.setItem('isSidebarCollapsed', String(val))
  }
})

const showAboutModal = ref(false)

const folders = computed(() => foldersResource.data || [])
const userName = computed(() => {
  if (window.frappe?.boot?.user) {
    if (typeof window.frappe.boot.user === 'object') {
      return window.frappe.boot.user.full_name || window.frappe.boot.user.name || 'User'
    }
    return window.frappe.boot.user
  }
  if (window.frappe?.session?.user_fullname) {
    return window.frappe.session.user_fullname
  }
  if (window.frappe?.user?.full_name) {
    return window.frappe.user.full_name
  }
  return window.frappe?.session?.user || 'User'
})

const isAdmin = computed(() => {
  if (stats.data?.is_admin) return true
  const user = window.frappe?.session?.user || window.frappe?.boot?.user?.name || ''
  if (user === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  return roles.includes('Vault Admin') || roles.includes('System Manager')
})

const navItems = computed(() => [
  { name: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, to: '/' },
  { name: 'secrets', label: 'All Secrets', icon: 'key', to: '/secrets', count: stats.data?.total_secrets },
  { name: 'favorites', label: 'Favorites', icon: 'star', to: '/favorites', count: stats.data?.favorites },
  { name: 'shared', label: isAdmin.value ? 'Manage Shares' : 'Shared with Me', icon: 'share-2', to: isAdmin.value ? '/manage-shares' : '/shared' },
])

const handleLogout = () => {
  window.location.href = '/logout'
}
</script>
