<template>
  <div
    class="vault-card p-4 cursor-pointer hover:border-vault-200 transition-colors"
    @click="$emit('click', secret)"
  >
    <div class="flex items-center gap-4">
      <!-- Type icon -->
      <SecretTypeIcon :type="secret.secret_type" />

      <!-- Main content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <h3 class="font-medium text-gray-900 truncate">{{ secret.title }}</h3>
          <FeatherIcon
            v-if="secret.is_favorite"
            name="star"
            class="w-4 h-4 text-yellow-400 fill-yellow-400"
          />
        </div>
        <div class="flex items-center gap-3 mt-1 text-sm text-gray-500">
          <span>{{ secret.secret_type }}</span>
          <span v-if="secret.username">• {{ secret.username }}</span>
          <span v-if="secret.url" class="truncate max-w-[200px]">• {{ secret.url }}</span>
        </div>
      </div>

      <!-- Strength indicator -->
      <div v-if="secret.password_strength" class="hidden sm:flex items-center gap-2">
        <StrengthBadge :strength="secret.password_strength" />
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-1" @click.stop>
        <Button
          variant="ghost"
          size="sm"
          :icon="secret.is_favorite ? 'star' : 'star'"
          :class="secret.is_favorite ? 'text-yellow-400' : 'text-gray-400'"
          @click="$emit('toggle-favorite', secret)"
        />
        <Dropdown :options="actions">
          <Button variant="ghost" size="sm">
            <FeatherIcon name="more-vertical" class="w-4 h-4 text-gray-400" />
          </Button>
        </Dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Button, Dropdown, FeatherIcon } from 'frappe-ui'
import SecretTypeIcon from './SecretTypeIcon.vue'
import StrengthBadge from './StrengthBadge.vue'

const props = defineProps({
  secret: Object,
})

const emit = defineEmits(['click', 'toggle-favorite', 'copy-password'])

const actions = computed(() => [
  {
    label: 'Copy Username',
    icon: 'user',
    onClick: () => copyToClipboard(props.secret.username),
  },
  {
    label: 'Copy Password',
    icon: 'key',
    onClick: () => emit('copy-password', props.secret),
  },
  {
    label: 'Open URL',
    icon: 'external-link',
    onClick: () => window.open(props.secret.url, '_blank'),
    condition: () => !!props.secret.url,
  },
].filter(a => !a.condition || a.condition()))

function copyToClipboard(text) {
  if (!text) return
  navigator.clipboard.writeText(text)
}
</script>
