<template>
  <div
    class="secret-type-icon"
    :class="typeClass"
  >
    <FeatherIcon :name="iconName" class="w-4 h-4" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  type: String,
})

const typeConfig = {
  Password: { icon: 'key', class: 'secret-type-password' },
  'API Key': { icon: 'code', class: 'secret-type-api-key' },
  Note: { icon: 'file-text', class: 'secret-type-note' },
  Card: { icon: 'credit-card', class: 'secret-type-card' },
  'SSH Key': { icon: 'terminal', class: 'secret-type-ssh-key' },
}

const config = computed(() => typeConfig[props.type] || typeConfig.Password)
const iconName = computed(() => config.value.icon)
const typeClass = computed(() => config.value.class)
</script>
