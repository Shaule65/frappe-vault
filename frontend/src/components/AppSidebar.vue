<template>
  <aside
    class="h-full border-r bg-surface-menu-bar flex flex-col justify-between transition-all duration-300 ease-in-out select-none shrink-0"
    :class="isSidebarCollapsed ? 'w-12' : 'w-[220px]'"
  >
    <!-- Brand Header -->
    <div class="p-2 border-b border-gray-100/50">
      <div
        class="flex items-center gap-3 duration-300 ease-in-out"
        :class="isSidebarCollapsed ? 'justify-center py-1' : 'px-2 py-1.5'"
      >
        <Tooltip text="Frappe Vault" placement="right" :disabled="!isSidebarCollapsed">
          <div class="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center shrink-0 shadow-sm border border-blue-700/10">
            <FeatherIcon name="lock" class="w-4 h-4 text-white" />
          </div>
        </Tooltip>
        <span
          v-if="!isSidebarCollapsed"
          class="font-semibold text-ink-gray-9 text-base truncate transition-all duration-300"
        >
          Frappe Vault
        </span>
      </div>
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

    <!-- Bottom Controls & User Menu -->
    <div class="m-2 flex flex-col gap-1">
      <!-- Collapse toggle button -->
      <SidebarLink
        :label="isSidebarCollapsed ? 'Expand' : 'Collapse'"
        :isCollapsed="isSidebarCollapsed"
        :icon="isSidebarCollapsed ? 'chevrons-right' : 'chevrons-left'"
        class="text-ink-gray-7 hover:text-ink-gray-9 hover:bg-surface-gray-2"
        @click="isSidebarCollapsed = !isSidebarCollapsed"
      />

      <!-- User profile selector -->
      <Dropdown :options="userMenuOptions">
        <template #default="{ open }">
          <button
            class="flex h-12 items-center rounded-md py-2 duration-200 ease-in-out w-full focus:outline-none"
            :class="
              isSidebarCollapsed
                ? 'w-auto px-0 justify-center mx-auto'
                : open
                  ? 'px-2 bg-surface-white shadow-sm border border-gray-100/30'
                  : 'px-2 hover:bg-surface-gray-3'
            "
          >
            <Avatar :label="userName" size="sm" class="shrink-0 border border-gray-200/50 shadow-sm" />
            <div
              class="flex flex-1 flex-col text-left duration-200 ease-in-out truncate"
              :class="
                isSidebarCollapsed
                  ? 'ml-0 w-0 overflow-hidden opacity-0'
                  : 'ml-2 w-auto opacity-100'
              "
            >
              <div class="text-sm font-medium leading-none text-ink-gray-9 truncate">
                {{ userName }}
              </div>
              <div class="mt-1.5 text-xs leading-none text-ink-gray-7 truncate">
                Secret Manager
              </div>
            </div>
            <div
              class="duration-200 ease-in-out"
              :class="
                isSidebarCollapsed
                  ? 'ml-0 w-0 overflow-hidden opacity-0'
                  : 'ml-2 w-auto opacity-100'
              "
            >
              <FeatherIcon
                name="chevron-up"
                class="w-4 h-4 text-ink-gray-5"
                aria-hidden="true"
              />
            </div>
          </button>
        </template>
      </Dropdown>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Avatar, Badge, Button, Dropdown, FeatherIcon, Tooltip } from 'frappe-ui'
import { useVaultStats, useFolders } from '../composables/vault'
import SidebarLink from './SidebarLink.vue'

const route = useRoute()
const stats = useVaultStats()
const foldersResource = useFolders()

defineEmits(['create-folder'])

// LocalStorage collapsed state syncing
const isSidebarCollapsed = ref(localStorage.getItem('isSidebarCollapsed') === 'true')
watch(isSidebarCollapsed, (val) => {
  localStorage.setItem('isSidebarCollapsed', String(val))
})

const folders = computed(() => foldersResource.data || [])
const userName = computed(() => {
  if (window.frappe?.boot?.user?.full_name) return window.frappe.boot.user.full_name
  return window.frappe?.session?.user || 'User'
})

const navItems = computed(() => [
  { name: 'dashboard', label: 'Dashboard', icon: 'home', to: '/' },
  { name: 'secrets', label: 'All Secrets', icon: 'key', to: '/secrets', count: stats.data?.total_secrets },
  { name: 'favorites', label: 'Favorites', icon: 'star', to: '/favorites', count: stats.data?.favorites },
  { name: 'shared', label: 'Shared With Me', icon: 'users', to: '/shared' },
  { name: 'generator', label: 'Generator', icon: 'refresh-cw', to: '/generator' },
  { name: 'audit', label: 'Audit Log', icon: 'activity', to: '/audit' },
  { name: 'settings', label: 'Settings', icon: 'settings', to: '/settings' },
])

const userMenuOptions = [
  { label: 'Go to Desk', icon: 'external-link', onClick: () => window.open('/app', '_blank') },
  { label: 'Logout', icon: 'log-out', onClick: () => {
      fetch('/api/method/logout', { method: 'POST' }).then(() => { window.location.replace('/login') })
    } 
  },
]
</script>
