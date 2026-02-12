<template>
  <div class="h-screen flex bg-gray-50" v-if="isLoggedIn">
    <Sidebar />
    <main class="flex-1 flex flex-col overflow-hidden">
      <router-view />
    </main>
  </div>
  <LoginView v-else />
</template>

<script setup>
import { computed } from 'vue'
import { session } from './data/session'
import Sidebar from './components/Sidebar.vue'
import LoginView from './views/LoginView.vue'

const isLoggedIn = computed(() => {
  return session.isLoggedIn
})
</script>
