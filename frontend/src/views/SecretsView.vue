<template>
  <SecretListTemplate
    :fetchParams="{}"
    :breadcrumbs="breadcrumbs"
    :emptyState="{
      icon: 'key',
      title: 'No secrets found',
      description: 'Create your first secret to get started',
      showDemoButton: true
    }"
    :showCreateButton="true"
    :showFolderFilter="true"
    :allowSelection="true"
    :allowDelete="true"
  />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useFolders } from '../composables/vault'
import SecretListTemplate from '../components/SecretListTemplate.vue'

const route = useRoute()
const foldersResource = useFolders()

const breadcrumbs = computed(() => {
  if (route.query.folder) {
    const folderName = foldersResource.data?.find(f => f.name === route.query.folder)?.folder_name || 'Folder'
    return [
      { label: 'Secrets', route: '/secrets' },
      { label: folderName }
    ]
  }
  return [{ label: 'Secrets' }]
})
</script>
