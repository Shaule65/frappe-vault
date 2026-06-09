<template>
  <aside
    class="h-full border-r bg-surface-menu-bar flex flex-col justify-between transition-all duration-300 ease-in-out select-none shrink-0"
    :class="isSidebarCollapsed ? 'w-12' : 'w-[220px]'"
  >
    <!-- Brand & User Dropdown at the Top -->
    <div class="p-2 border-b border-gray-100/50">
      <Popover placement="bottom-start" trigger="click" class="w-full">
        <template #target="{ open, togglePopover }">
          <button
            class="flex h-12 items-center rounded-md py-2 duration-200 ease-in-out w-full focus:outline-none"
            :class="
              isSidebarCollapsed
                ? 'w-auto px-0 justify-center mx-auto'
                : open
                  ? 'px-2 bg-surface-white shadow-sm border border-gray-100/30'
                  : 'px-2 hover:bg-surface-gray-3'
            "
            @click.prevent="togglePopover()"
          >
            <div class="flex items-center w-full" :class="isSidebarCollapsed ? 'justify-center gap-0' : 'px-1 gap-3'">
              <Tooltip text="Frappe Vault" placement="right" :disabled="!isSidebarCollapsed">
                <div class="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center shrink-0 shadow-sm border border-blue-700/10">
                  <FeatherIcon name="lock" class="w-4 h-4 text-white" />
                </div>
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

            <!-- Settings -->
            <button
              class="w-full flex h-8 items-center gap-2 rounded px-2.5 hover:bg-surface-gray-2 text-ink-gray-8 text-left focus:outline-none"
              @click="() => { router.push('/settings'); close() }"
            >
              <FeatherIcon name="settings" class="w-4 h-4 text-ink-gray-7" />
              <span class="text-sm font-medium">Settings</span>
            </button>

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
    <nav class="flex-1 py-3 space-y-0.5 overflow-y-auto custom-scrollbar">
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
          <Button variant="ghost" size="sm" class="h-6 w-6 p-0 hover:bg-surface-gray-2 rounded" @click="$emit('create-folder')">
            <FeatherIcon name="plus" class="w-3.5 h-3.5 text-ink-gray-7" />
          </Button>
        </div>
        <div class="flex flex-col items-center mb-2" v-else>
          <div class="w-full border-b border-gray-100/50 my-1" />
          <Tooltip text="Create Folder" placement="right">
            <Button variant="ghost" size="sm" class="h-8 w-8 p-0 hover:bg-surface-gray-2 rounded" @click="$emit('create-folder')">
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
        </SidebarLink>
      </div>
    </nav>

    <!-- Bottom Controls -->
    <div class="m-2 flex flex-col gap-1">
      <!-- Collapse toggle button -->
      <SidebarLink
        :label="isSidebarCollapsed ? 'Expand' : 'Collapse'"
        :isCollapsed="isSidebarCollapsed"
        :icon="isSidebarCollapsed ? 'chevrons-right' : 'chevrons-left'"
        class="text-ink-gray-7 hover:text-ink-gray-9 hover:bg-surface-gray-2"
        @click="isSidebarCollapsed = !isSidebarCollapsed"
      />
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
  </aside>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Badge, Button, Popover, FeatherIcon, Tooltip, Dialog } from 'frappe-ui'
import { useVaultStats, useFolders } from '../composables/vault'
import SidebarLink from './SidebarLink.vue'
import LayoutDashboard from '~icons/lucide/layout-dashboard'

const route = useRoute()
const router = useRouter()
const stats = useVaultStats()
const foldersResource = useFolders()

defineEmits(['create-folder'])

// LocalStorage collapsed state syncing
const isSidebarCollapsed = ref(localStorage.getItem('isSidebarCollapsed') === 'true')
watch(isSidebarCollapsed, (val) => {
  localStorage.setItem('isSidebarCollapsed', String(val))
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

const navItems = computed(() => [
  { name: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, to: '/' },
  { name: 'secrets', label: 'All Secrets', icon: 'key', to: '/secrets', count: stats.data?.total_secrets },
  { name: 'favorites', label: 'Favorites', icon: 'star', to: '/favorites', count: stats.data?.favorites },
])

const handleLogout = () => {
  window.location.href = '/logout'
}
</script>
