<template>
  <Sidebar
    v-model:collapsed="isSidebarCollapsed"
    :disable-collapse="isMobile"
    :header="sidebarConfig.header"
    :sections="sidebarConfig.sections"
    class="select-none"
  >

    <!-- Sidebar item slot — handles badges on nav items and custom folder rows -->
    <template #sidebar-item="{ item, isCollapsed }">
      <!-- Section Header row with + icon -->
      <div
        v-if="item.isHeader"
        class="flex items-center justify-between px-2 pt-3 pb-1 mt-2 select-none"
      >
        <span
          v-if="!isCollapsed"
          class="text-xs font-semibold text-ink-gray-4 tracking-wider uppercase transition-opacity duration-200 truncate"
        >
          {{ item.label }}
        </span>
        <Tooltip text="Create Folder" placement="right">
          <button
            class="flex items-center justify-center w-5 h-5 rounded hover:bg-surface-gray-3 text-ink-gray-6 hover:text-ink-gray-8 transition-colors shrink-0"
            :class="{ 'mx-auto': isCollapsed }"
            @click.prevent.stop="openCreateFolderDialog"
          >
            <FeatherIcon name="plus" class="w-3.5 h-3.5" />
          </button>
        </Tooltip>
      </div>

      <!-- Folder items: colored dot icon + context menu -->
      <SidebarItem
        v-else-if="item.folder"
        :label="item.label"
        :to="item.to"
        :isActive="item.isActive"
        class="group"
      >
        <template #icon>
          <div class="flex items-center justify-center w-4 h-4">
            <div
              class="w-2.5 h-2.5 rounded-full shrink-0 border border-black/5"
              :style="{ backgroundColor: item.color || '#6b7280' }"
            />
          </div>
        </template>
        <template #suffix>
          <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-150" @click.prevent.stop>
            <Dropdown :options="getFolderOptions(item.folder)">
              <template #default="{ open }">
                <Button
                  variant="ghost"
                  icon="lucide-more-horizontal"
                  class="!p-0.5 h-auto text-ink-gray-6"
                  :class="{ 'bg-surface-gray-3': open }"
                />
              </template>
            </Dropdown>
          </div>
        </template>
      </SidebarItem>

      <!-- Standard nav items: badge count suffix -->
      <SidebarItem
        v-else
        :label="item.label"
        :icon="item.icon"
        :to="item.to"
        :isActive="item.isActive"
      >
        <template v-if="item.count" #suffix>
          <Badge :label="String(item.count)" variant="subtle" theme="gray" />
        </template>
      </SidebarItem>
    </template>

    <!-- Footer items slot (holds dialogs since Sidebar has no default slot) -->
    <template #footer-items="{ isCollapsed }">
      <SidebarItem
        v-if="stats.data?.has_demo_data"
        label="Clear Demo Data"
        class="hover:!bg-red-100/80 !text-red-600 transition-colors cursor-pointer font-medium"
        @click="showClearDemoConfirm = true"
      >
        <template #icon>
          <BrushCleaningIcon class="size-4 text-red-600 shrink-0" />
        </template>
      </SidebarItem>
      <SidebarItem
        v-else-if="stats.data?.total_secrets === 0 && !generateDemo.loading"
        label="Load Demo Data"
        class="hover:!bg-blue-100/80 !text-blue-600 transition-colors cursor-pointer font-medium"
        @click="handleGenerateDemo"
      >
        <template #icon>
          <SparklesIcon class="size-4 text-blue-600 shrink-0" />
        </template>
      </SidebarItem>

      <!-- Clear Demo Data Confirmation Dialog -->
      <Dialog
        v-model="showClearDemoConfirm"
        :options="{ title: 'Clear Demo Data', size: 'sm' }"
      >
        <template #body-content>
          <p class="text-sm text-ink-gray-7 leading-relaxed">
            Are you sure you want to remove all demo folders and secrets? Any changes made to demo secrets will be lost.
          </p>
        </template>
        <template #actions>
          <div class="flex justify-end gap-2">
            <Button variant="ghost" label="Cancel" @click="showClearDemoConfirm = false" />
            <Button
              variant="solid"
              theme="red"
              label="Clear Demo Data"
              :loading="clearDemo.loading"
              @click="handleClearDemo"
            />
          </div>
        </template>
      </Dialog>

      <!-- Dialogs (rendered inside #footer-items slot since Sidebar has no default slot) -->
      <!-- About Dialog -->
      <Dialog
        v-model="showAboutModal"
        size="sm"
        bare
      >
        <template #default="{ close }">
          <div class="bg-surface-elevation-1 rounded-2xl p-6 shadow-xl border border-outline-gray-1 text-ink-gray-9">
            <!-- App Logo and Title -->
            <div class="flex flex-col items-center justify-center pb-3">
              <img :src="sidebarConfig.header.logo" class="size-12 object-contain rounded-xl shadow-sm" />
              <h3 class="mt-3 text-lg font-semibold text-ink-gray-9">Frappe Vault</h3>
            </div>

            <!-- Top Divider -->
            <div class="border-t border-outline-gray-1 my-2" />

            <!-- Links List -->
            <div class="flex flex-col py-1 space-y-0.5">
              <a
                v-for="link in aboutLinks"
                :key="link.label"
                :href="link.href"
                target="_blank"
                class="flex items-center gap-3 p-2 rounded-sm text-sm text-ink-gray-8 hover:bg-surface-gray-2 transition-colors"
              >
                <component :is="link.icon" class="size-4 text-ink-gray-6 shrink-0" />
                <span class="font-medium">{{ link.label }}</span>
              </a>
            </div>

            <!-- Bottom Divider -->
            <div class="border-t border-outline-gray-1 my-2" />

            <!-- Footer -->
            <div class="text-center text-xs text-ink-gray-5 pt-1">
              ©lubus solutions and contributors
            </div>
          </div>
        </template>
      </Dialog>

      <!-- Create Folder Dialog -->
      <Dialog
        v-model="showCreateFolderDialog"
        :options="{ title: 'New Folder', size: 'sm' }"
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
        :options="{ title: 'Edit Folder', size: 'sm' }"
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

      <!-- Delete Folder Dialog -->
      <Dialog
        v-model="showDeleteFolderDialog"
        :options="{ title: 'Delete Folder', size: 'sm' }"
      >
        <template #body-content>
          <div class="space-y-2">
            <p class="text-sm text-ink-gray-7" v-if="loadingCount">Analyzing folder secrets...</p>
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
    </template>
  </Sidebar>
</template>

<script setup>
import { ref, computed, reactive, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Badge, Button, FeatherIcon, Tooltip, Dialog, Dropdown, FormControl, Sidebar, SidebarItem, createResource } from 'frappe-ui'
import { useVaultStats, useFolders, useCreateFolder, useDeleteFolder, useUpdateFolder, useFolderSecrets, useGenerateDemoData, useClearDemoData } from '../composables/vault'
import LayoutDashboard from '~icons/lucide/layout-dashboard'
import GlobeIcon from '~icons/lucide/globe'
import HelpCircleIcon from '~icons/lucide/help-circle'
import BookOpenIcon from '~icons/lucide/book-open'
import BugIcon from '~icons/lucide/bug'
import HeadphonesIcon from '~icons/lucide/headphones'
import BrushCleaningIcon from '~icons/lucide/brush-cleaning'
import SparklesIcon from '~icons/lucide/sparkles'

const props = defineProps({
  isMobile: { type: Boolean, default: false }
})

const route = useRoute()
const router = useRouter()
const stats = useVaultStats()
const foldersResource = useFolders()
const generateDemo = useGenerateDemoData()
const clearDemo = useClearDemoData()
const showClearDemoConfirm = ref(false)

const appsResource = createResource({
  url: 'frappe.apps.get_apps',
  cache: 'apps',
  auto: true,
  transform: (data) => {
    let _apps = [
      {
        label: 'Desk',
        icon: { render: () => h('img', { src: '/assets/frappe/images/framework.png', class: 'size-6 object-contain rounded-xs' }) },
        onClick: () => { window.location.href = '/app' }
      }
    ]
    if (Array.isArray(data)) {
      data.forEach((app) => {
        if (app.name === 'frappe_vault' || app.name === 'frappe') return
        _apps.push({
          label: app.title || app.name,
          icon: { render: () => h('img', { src: app.logo || '/assets/frappe/images/framework.png', class: 'size-6 object-contain rounded-xs' }) },
          onClick: () => { window.location.href = app.route || `/${app.name}` }
        })
      })
    }
    return _apps
  }
})

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

    if (route.query.folder === folderToDelete.value.name || route.name === 'SecretDetail') {
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

async function handleGenerateDemo() {
  try {
    await generateDemo.submit()
    stats.reload()
    foldersResource.reload()
    if (route.name === 'SecretDetail') {
      router.push('/')
    }
  } catch (err) {
    console.error(err)
  }
}

async function handleClearDemo() {
  try {
    await clearDemo.submit()
    showClearDemoConfirm.value = false
    stats.reload()
    foldersResource.reload()
    router.push('/')
  } catch (err) {
    console.error(err)
  }
}

// Persist collapsed state in localStorage
const _isSidebarCollapsed = ref(localStorage.getItem('isSidebarCollapsed') === 'true')
const isSidebarCollapsed = computed({
  get: () => props.isMobile ? false : _isSidebarCollapsed.value,
  set: (val) => {
    _isSidebarCollapsed.value = val
    localStorage.setItem('isSidebarCollapsed', String(val))
  }
})

const showAboutModal = ref(false)

const aboutLinks = [
  { label: 'Website', href: 'https://frappe.io', icon: GlobeIcon },
  { label: 'GitHub Repository', href: 'https://github.com/frappe/frappe-vault', icon: HelpCircleIcon },
  { label: 'Documentation', href: 'https://github.com/frappe/frappe-vault#readme', icon: BookOpenIcon },
  { label: 'Report an Issue', href: 'https://github.com/frappe/frappe-vault/issues', icon: BugIcon },
  { label: 'Contact Support', href: 'https://t.me/frappeframework', icon: HeadphonesIcon },
]

const folders = computed(() => foldersResource.data || [])

const userName = computed(() => {
  if (window.frappe?.boot?.user) {
    if (typeof window.frappe.boot.user === 'object') {
      return window.frappe.boot.user.full_name || window.frappe.boot.user.name || 'User'
    }
    return window.frappe.boot.user
  }
  if (window.frappe?.session?.user_fullname) return window.frappe.session.user_fullname
  if (window.frappe?.user?.full_name) return window.frappe.user.full_name
  return window.frappe?.session?.user || 'User'
})

const isAdmin = computed(() => {
  if (stats.data?.is_admin) return true
  const user = window.frappe?.session?.user || window.frappe?.boot?.user?.name || ''
  if (user === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  return roles.includes('Vault Admin') || roles.includes('System Manager')
})

// Single reactive sidebar config — mirrors the frappe-ui docs pattern
function checkActive(to) {
  if (!to) return false
  const pathStr = typeof to === 'string' ? to : to.path || ''
  if (!pathStr) return false

  if (pathStr.includes('?')) {
    const [path, queryString] = pathStr.split('?')
    const currentSearch = window.location.search || ''
    return route.path === path && currentSearch.includes(queryString)
  }

  if (pathStr === '/') {
    return route.path === '/'
  }

  if (pathStr === '/secrets') {
    if (route.query.folder || route.query.category) {
      return false
    }
    return route.path === '/secrets' || route.path.startsWith('/secrets/')
  }

  return route.path === pathStr || route.path.startsWith(pathStr + '/')
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme')
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark'
  document.documentElement.setAttribute('data-theme', newTheme)
}

const sidebarConfig = reactive({
  header: computed(() => ({
    title: 'Vault',
    logo: '/assets/frappe_vault/images/vault-icon.svg',
    subtitle: userName.value,
    menuItems: [
      {
        group: '',
        hideLabel: true,
        options: [
          {
            icon: 'lucide-layout-grid',
            label: 'Apps',
            submenu: appsResource.data || [
              {
                label: 'Desk',
                  icon: { render: () => h('img', { src: '/assets/frappe/images/framework.png', class: 'size-4 object-contain rounded-xs' }) },
                onClick: () => { window.location.href = '/app' }
              }
            ]
          },
          {
            label: 'Toggle Theme',
            icon: 'lucide-moon',
            onClick: toggleTheme
          },
          {
            icon: 'lucide-info',
            label: 'About',
            onClick: () => { showAboutModal.value = true }
          }
        ]
      },
      {
        group: '',
        hideLabel: true,
        options: [
          {
            icon: 'lucide-log-out',
            label: 'Log out',
            onClick: () => { window.location.href = '/logout' }
          }
        ]
      }
    ],
  })),
  sections: computed(() => [
    {
      label: '',
      items: [
        { label: 'Dashboard', icon: LayoutDashboard, to: '/', isActive: checkActive('/') },
        { label: 'Secrets', icon: 'lucide-key-round', to: '/secrets', count: stats.data?.total_secrets, isActive: checkActive('/secrets') },
        { label: 'Favorites', icon: 'lucide-star', to: '/favorites', count: stats.data?.favorites, isActive: checkActive('/favorites') },
        {
          label: isAdmin.value ? 'Shares' : 'Shared with Me',
          icon: 'lucide-share-2',
          to: isAdmin.value ? '/manage-shares' : '/shared',
          isActive: checkActive(isAdmin.value ? '/manage-shares' : '/shared'),
        },
      ],
    },
    {
      label: '',
      items: [
        { isHeader: true, label: 'Folders' },
        ...folders.value.map((folder) => {
          const toUrl = `/secrets?folder=${folder.name}`
          return {
            label: folder.folder_name,
            to: toUrl,
            isActive: checkActive(toUrl),
            color: folder.color,
            folder,
          }
        }),
      ],
    },
  ]),
})
</script>
