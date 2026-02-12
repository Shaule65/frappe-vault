<template>
  <div class="flex-1 flex">
    <!-- Back to list -->
    <div class="flex-1 overflow-auto p-6">
      <Button variant="ghost" class="mb-4" @click="$router.push('/secrets')">
        <template #prefix><FeatherIcon name="arrow-left" class="w-4 h-4" /></template>
        Back to Secrets
      </Button>

      <SecretPanel
        v-if="name"
        :name="name"
        @close="$router.push('/secrets')"
        @deleted="$router.push('/secrets')"
      />
    </div>
  </div>
</template>

<script setup>
import { Button, FeatherIcon } from 'frappe-ui'
import SecretPanel from '@/components/SecretPanel.vue'

const props = defineProps({
  name: String,
})
</script>
