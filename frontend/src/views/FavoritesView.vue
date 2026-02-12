<template>
  <div class="flex-1 overflow-auto p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Favorites</h1>
      <p class="text-gray-500 mt-1">Your starred secrets for quick access</p>
    </div>

    <!-- Loading -->
    <div v-if="secrets.loading && !secrets.data" class="text-center py-12">
      <LoadingText />
    </div>

    <!-- List -->
    <div v-else-if="favoriteSecrets.length" class="space-y-2">
      <SecretRow
        v-for="secret in favoriteSecrets"
        :key="secret.name"
        :secret="secret"
        @click="selectedSecret = secret.name"
        @toggle-favorite="handleToggleFavorite"
      />
    </div>

    <!-- Empty state -->
    <EmptyState
      v-else
      icon="star"
      title="No favorites yet"
      description="Star your frequently used secrets for quick access"
    >
      <template #actions>
        <Button variant="subtle" @click="$router.push('/secrets')">
          Browse Secrets
        </Button>
      </template>
    </EmptyState>

    <!-- Secret Panel -->
    <SecretPanel
      v-if="selectedSecret"
      :name="selectedSecret"
      @close="selectedSecret = null"
      @updated="secrets.reload()"
      @deleted="handleSecretDeleted"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button, LoadingText } from 'frappe-ui'
import { useSecrets, useToggleFavorite } from '@/data/vault'
import SecretRow from '@/components/SecretRow.vue'
import SecretPanel from '@/components/SecretPanel.vue'
import EmptyState from '@/components/EmptyState.vue'

const selectedSecret = ref(null)

const secrets = useSecrets({ favorites_only: true })
const toggleFavorite = useToggleFavorite()

const favoriteSecrets = computed(() => secrets.data?.secrets || [])

async function handleToggleFavorite(secret) {
  await toggleFavorite.submit({ name: secret.name })
  secrets.reload()
}

function handleSecretDeleted() {
  selectedSecret.value = null
  secrets.reload()
}
</script>
