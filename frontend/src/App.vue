<template>
  <div class="h-screen flex bg-gray-50">
    <AppSidebar v-if="!isPublicRoute" />
    <main class="flex-1 flex flex-col overflow-hidden">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'

const route = useRoute()
const isPublicRoute = computed(() => {
  const browserPath = window.location.pathname || ''
  return route.meta.public || route.path.startsWith('/shared/') || browserPath.startsWith('/vault/shared/')
})

watchEffect(() => {
  const user = window.frappe?.boot?.user
  if (user === 'Guest' && !isPublicRoute.value) {
    window.location.href = `/login?redirect-to=${encodeURIComponent(window.location.pathname)}`
  }
})
</script>
