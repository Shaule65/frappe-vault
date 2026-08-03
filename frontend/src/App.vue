<template>
  <div class="h-screen flex bg-surface-base overflow-hidden relative">
    <!-- Desktop Sidebar -->
    <AppSidebar v-if="!isPublicRoute" class="hidden sm:flex" />

    <!-- Mobile Drawer Sidebar -->
    <div
      v-if="!isPublicRoute && mobileSidebarOpened"
      class="fixed inset-0 z-50 flex sm:hidden"
    >
      <!-- Backdrop -->
      <div
        class="fixed inset-0 bg-black/70 transition-opacity"
        @click="mobileSidebarOpened = false"
      />
      <!-- Drawer Content -->
      <div class="relative w-[220px] h-full bg-surface-gray-2 shadow-xl flex flex-col shrink-0 animate-slide-in">
        <AppSidebar :is-mobile="true" />
      </div>
    </div>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col overflow-hidden min-w-0">
      <router-view />
    </main>

    <!-- Global Notifications Panel -->
    <NotificationsPanel />
  </div>
</template>

<script setup>
import { computed, watchEffect, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import NotificationsPanel from './components/NotificationsPanel.vue'
import { mobileSidebarOpened } from './composables/vault'

const route = useRoute()
const isPublicRoute = computed(() => {
  const browserPath = window.location.pathname || ''
  return route.meta.public || route.path.startsWith('/shared/') || browserPath.startsWith('/vault/shared/')
})

// Auto-close sidebar on route change on mobile
watchEffect(() => {
  if (route.path) {
    mobileSidebarOpened.value = false
  }
})

watchEffect(() => {
  const user = window.frappe?.boot?.user
  if (user === 'Guest' && !isPublicRoute.value) {
    window.location.href = `/login?redirect-to=${encodeURIComponent(window.location.pathname)}`
  }
})

// Set theme to prevent flashing as much as possible within Vue
const savedTheme = localStorage.getItem('theme') || 'light'
document.documentElement.setAttribute('data-theme', savedTheme)

onMounted(() => {
  const handleResize = () => {
    if (window.innerWidth >= 640 && mobileSidebarOpened.value) {
      mobileSidebarOpened.value = false
    }
  }
  window.addEventListener('resize', handleResize)

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
})
</script>

<style scoped>
@keyframes slide-in {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}
.animate-slide-in {
  animation: slide-in 0.2s ease-out forwards;
}
</style>
