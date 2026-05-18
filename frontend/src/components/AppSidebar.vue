<template>
  <aside class="w-60 bg-white border-r flex flex-col h-full">
    <!-- App Header -->
    <div class="p-4 border-b">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
          <FeatherIcon name="lock" class="w-5 h-5 text-white" />
        </div>
        <span class="font-semibold text-gray-900 text-base">Frappe Vault</span>
      </div>
    </div>

    <!-- Primary Navigation -->
    <nav class="flex-1 p-3 space-y-1 overflow-y-auto">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors"
        :class="isActive(item.to)
          ? 'bg-blue-50 text-blue-700 font-medium'
          : 'text-gray-700 hover:bg-gray-100'"
      >
        <FeatherIcon :name="item.icon" class="w-4 h-4" />
        <span class="flex-1">{{ item.label }}</span>
        <Badge v-if="item.count" :label="String(item.count)" variant="subtle" theme="gray" />
      </router-link>

      <!-- Folders Section -->
      <div class="pt-4 mt-4 border-t">
        <div class="flex items-center justify-between px-3 mb-2">
          <p class="text-xs font-medium text-gray-500 uppercase tracking-wider">Folders</p>
          <Button variant="ghost" size="sm" @click="$emit('create-folder')">
            <FeatherIcon name="plus" class="w-3 h-3" />
          </Button>
        </div>
        <router-link
          v-for="folder in folders"
          :key="folder.name"
          :to="`/secrets?folder=${folder.name}`"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <div class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: folder.color || '#6b7280' }" />
          <span>{{ folder.folder_name }}</span>
        </router-link>
      </div>
    </nav>

    <!-- User Menu -->
    <div class="p-3 border-t">
      <Dropdown :options="userMenuOptions">
        <template #default="{ open }">
          <button
            class="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
            :class="{ 'bg-gray-100': open }"
          >
            <Avatar :label="userName" size="sm" />
            <div class="flex-1 text-left min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ userName }}</p>
            </div>
            <FeatherIcon name="chevron-up" class="w-4 h-4 text-gray-400" />
          </button>
        </template>
      </Dropdown>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Avatar, Badge, Button, Dropdown, FeatherIcon } from 'frappe-ui'
import { useVaultStats, useFolders } from '../composables/vault'

const route = useRoute()
const stats = useVaultStats()
const foldersResource = useFolders()

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

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>
