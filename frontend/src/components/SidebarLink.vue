<template>
  <router-link
    v-if="to"
    :to="to"
    class="flex h-7.5 cursor-pointer items-center rounded duration-200 ease-in-out focus:outline-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-outline-gray-3 mx-2 my-[1.5px]"
    :class="
      isActive
        ? 'bg-surface-selected shadow-sm text-ink-gray-9 font-medium'
        : 'hover:bg-surface-gray-2 text-ink-gray-8'
    "
  >
    <div
      class="flex w-full items-center justify-between duration-200 ease-in-out"
      :class="isCollapsed ? 'ml-[3px] p-1' : 'px-2 py-[7px]'"
    >
      <div class="flex items-center truncate">
        <Tooltip :text="label" placement="right" :disabled="!isCollapsed">
          <slot name="icon">
            <FeatherIcon
              v-if="icon"
              :name="icon"
              class="w-4 h-4 flex-shrink-0 transition-colors"
              :class="isActive ? 'text-ink-gray-9' : 'text-ink-gray-7'"
            />
          </slot>
        </Tooltip>
        <Tooltip
          :text="label"
          placement="right"
          :disabled="isCollapsed"
          :hoverDelay="1.5"
        >
          <span
            class="flex-1 flex-shrink-0 truncate text-sm duration-200 ease-in-out"
            :class="
              isCollapsed
                ? 'ml-0 w-0 overflow-hidden opacity-0'
                : 'ml-2 w-auto opacity-100'
            "
          >
            {{ label }}
          </span>
        </Tooltip>
      </div>
      <slot name="right" v-if="!isCollapsed" />
    </div>
  </router-link>
  <button
    v-else
    class="flex h-7.5 cursor-pointer items-center rounded duration-200 ease-in-out focus:outline-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-outline-gray-3 mx-2 my-[1.5px] text-left w-[calc(100%-16px)]"
    :class="
      isActive
        ? 'bg-surface-selected shadow-sm text-ink-gray-9 font-medium'
        : 'hover:bg-surface-gray-2 text-ink-gray-8'
    "
    @click="$emit('click')"
  >
    <div
      class="flex w-full items-center justify-between duration-200 ease-in-out"
      :class="isCollapsed ? 'ml-[3px] p-1' : 'px-2 py-[7px]'"
    >
      <div class="flex items-center truncate">
        <Tooltip :text="label" placement="right" :disabled="!isCollapsed">
          <slot name="icon">
            <FeatherIcon
              v-if="icon"
              :name="icon"
              class="w-4 h-4 flex-shrink-0 transition-colors text-ink-gray-8"
            />
          </slot>
        </Tooltip>
        <Tooltip
          :text="label"
          placement="right"
          :disabled="isCollapsed"
          :hoverDelay="1.5"
        >
          <span
            class="flex-1 flex-shrink-0 truncate text-sm duration-200 ease-in-out"
            :class="
              isCollapsed
                ? 'ml-0 w-0 overflow-hidden opacity-0'
                : 'ml-2 w-auto opacity-100'
            "
          >
            {{ label }}
          </span>
        </Tooltip>
      </div>
      <slot name="right" v-if="!isCollapsed" />
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Tooltip, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  icon: { type: String, default: null },
  label: { type: String, default: '' },
  to: { type: [Object, String], default: null },
  isCollapsed: { type: Boolean, default: false },
})

defineEmits(['click'])

const route = useRoute()

const isActive = computed(() => {
  if (!props.to) return false
  if (typeof props.to === 'string') {
    if (props.to.includes('?')) {
      const [path, queryString] = props.to.split('?')
      const fullPath = route.path + (window.location.search || '')
      return route.path === path && fullPath.includes(queryString)
    }
    if (props.to === '/') return route.path === '/'
    return route.path.startsWith(props.to)
  }
  return false
})
</script>
