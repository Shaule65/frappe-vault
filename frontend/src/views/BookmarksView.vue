<template>
  <SecretListTemplate
    :fetchParams="{ bookmarks_only: 1 }"
    :breadcrumbs="breadcrumbs"
    :emptyState="{
      icon: 'bookmark',
      title: 'No bookmarks yet',
      description: 'Bookmark your most-used secrets for quick access',
      showDemoButton: false
    }"
    :showCreateButton="false"
    :showFolderFilter="false"
    :allowSelection="true"
    :allowDelete="false"
  />
</template>

<script setup>
import { computed } from 'vue'
import SecretListTemplate from '../components/SecretListTemplate.vue'

const breadcrumbs = computed(() => [{ label: 'Bookmarks' }])
</script>
