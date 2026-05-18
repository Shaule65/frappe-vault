<template>
  <div class="h-screen flex bg-gray-50">
    <AppSidebar />
    <main class="flex-1 flex flex-col overflow-hidden">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import AppSidebar from './components/AppSidebar.vue'
</script>
