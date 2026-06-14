<template>
  <aside class="w-60 bg-white border-r flex flex-col">
    <!-- Logo/Header -->
    <div class="p-4 border-b">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 vault-gradient rounded-lg flex items-center justify-center">
          <FeatherIcon name="lock" class="w-5 h-5 text-white" />
        </div>
        <span class="font-semibold text-gray-900">Frappe Vault</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-3 space-y-1 overflow-y-auto custom-scrollbar">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.to"
        class="nav-item"
        :class="{ 'nav-item-active': isActive(item.to) }"
      >
        <FeatherIcon :name="item.icon" class="w-4 h-4" />
        <span>{{ item.label }}</span>
        <Badge v-if="item.count" :label="item.count" variant="subtle" theme="gray" class="ml-auto" />
      </router-link>

      <!-- Categories section -->
      <div class="pt-4 mt-4 border-t">
        <p class="px-3 mb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
          Categories
        </p>
        <router-link
          v-for="cat in categories"
          :key="cat.name"
          :to="`/secrets?category=${cat.name}`"
          class="nav-item"
        >
          <div
            class="w-2.5 h-2.5 rounded-full"
            :style="{ backgroundColor: cat.color || '#6b7280' }"
          />
          <span>{{ cat.category_name }}</span>
        </router-link>
      </div>
    </nav>

    <!-- User menu -->
    <div class="p-3 border-t">
      <Dropdown :options="userMenuOptions">
        <template #default="{ open }">
          <button
            class="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
            :class="{ 'bg-gray-100': open }"
          >
            <Avatar :label="session.fullName || session.user" :image="session.userImage" size="sm" />
            <div class="flex-1 text-left min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ session.fullName || session.user }}
              </p>
            </div>
            <FeatherIcon name="chevron-down" class="w-4 h-4 text-gray-400" />
          </button>
        </template>
      </Dropdown>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Avatar, Badge, Dropdown, FeatherIcon } from 'frappe-ui'
import { session } from '@/data/session'
import { useCategories, useStats } from '@/data/vault'

const route = useRoute()
const router = useRouter()

const stats = useStats()
const categoriesResource = useCategories()

const categories = computed(() => categoriesResource.data || [])

const isAdmin = computed(() => {
  if (stats.data?.is_admin) return true
  const user = window.frappe?.session?.user || window.frappe?.boot?.user?.name || ''
  if (user === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  return roles.includes('Vault Admin') || roles.includes('System Manager')
})

const navItems = computed(() => [
  { name: 'dashboard', label: 'Dashboard', icon: 'home', to: '/' },
  {
    name: 'secrets',
    label: 'All Secrets',
    icon: 'key',
    to: '/secrets',
    count: stats.data?.total_secrets,
  },
  {
    name: 'favorites',
    label: 'Favorites',
    icon: 'star',
    to: '/favorites',
    count: stats.data?.favorites_count,
  },
  {
    name: 'shared',
    label: isAdmin.value ? 'Manage Shares' : 'Shared with Me',
    icon: 'share-2',
    to: isAdmin.value ? '/manage-shares' : '/shared',
  },
  { name: 'settings', label: 'Settings', icon: 'settings', to: '/settings' },
])

const userMenuOptions = [
  {
    label: 'Go to Desk',
    icon: 'external-link',
    onClick: () => window.open('/app', '_blank'),
  },
  {
    label: 'Logout',
    icon: 'log-out',
    onClick: () => {
      window.location.href = '/logout'
    },
  },
]

function isActive(path) {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>

<style scoped>
.nav-item {
  @apply flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-700 hover:bg-gray-100 transition-colors;
}

.nav-item-active {
  @apply bg-vault-50 text-vault-700 font-medium;
}
</style>
