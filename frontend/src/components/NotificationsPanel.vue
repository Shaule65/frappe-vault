<!-- eslint-disable vue/no-v-html -->
<template>
  <div
    v-if="visible"
    ref="target"
    class="absolute top-0 z-50 h-screen w-[350px] min-w-[350px] max-w-[350px] left-[calc(100%+1px)] bg-surface-base border-r border-outline-gray-1 shadow-2xl transition-all duration-300 ease-in-out"
  >
    <div class="flex h-screen flex-col text-ink-gray-9 bg-surface-base">
      <!-- Header -->
      <div
        class="z-20 flex items-center justify-between border-b border-outline-gray-1 bg-surface-base px-5 py-2.5 shrink-0"
      >
        <div class="text-base font-medium text-ink-gray-9">Notifications</div>
        <div class="flex items-center gap-1">
          <Button
            v-if="unreadNotificationsCount > 0"
            tooltip="Mark all as read"
            icon="lucide-check-check"
            variant="ghost"
            size="sm"
            @click="handleMarkAllAsRead"
          />
          <Button
            v-if="notifications.data?.length > 0"
            tooltip="Clear all notifications"
            icon="lucide-trash-2"
            variant="ghost"
            size="sm"
            @click="handleClearAll"
          />
          <Button
            tooltip="Close"
            icon="lucide-x"
            variant="ghost"
            size="sm"
            @click="() => toggleNotificationPanel()"
          />
        </div>
      </div>

      <!-- Notifications List -->
      <div
        v-if="notifications.data?.length"
        class="divide-y divide-outline-gray-1 overflow-y-auto text-base flex-1 custom-scrollbar"
      >
        <div
          v-for="n in notifications.data"
          :key="n.name"
          class="flex cursor-pointer items-start gap-2.5 px-4 py-3 hover:bg-surface-gray-2 transition-colors relative group"
          :class="[!n.read ? 'bg-surface-blue-1/30 dark:bg-blue-950/20' : '']"
          @click="handleNotificationClick(n)"
        >
          <div class="mt-1 flex items-center gap-2">
            <div
              class="size-[5px] rounded-full shrink-0"
              :class="[n.read ? 'bg-transparent' : 'bg-blue-500']"
            />
            <div class="flex h-7 w-7 items-center justify-center rounded-full bg-surface-gray-2 text-xs font-medium text-ink-gray-7 shrink-0">
              {{ getInitials(n.from_user?.full_name) }}
            </div>
          </div>

          <div class="flex-1 min-w-0 pr-6">
            <div
              v-if="n.notification_text"
              class="mb-1 space-x-1 leading-5 text-xs text-ink-gray-7"
              v-html="n.notification_text"
            />
            <div v-else class="mb-1 space-x-1 leading-5 text-xs text-ink-gray-7">
              <span class="font-medium text-ink-gray-9">
                {{ n.from_user?.full_name }}
              </span>
              <span>{{ n.subject }}</span>
            </div>
            <div class="text-[11px] text-ink-gray-5">
              {{ timeAgo(n.creation) }}
            </div>
          </div>

          <!-- Hover Action: Delete Single Notification -->
          <button
            class="absolute right-2.5 top-2.5 opacity-0 group-hover:opacity-100 transition-all p-1 text-ink-gray-6 hover:text-red-600 hover:bg-surface-gray-3 rounded-md border border-transparent hover:border-outline-gray-2"
            title="Delete notification"
            @click.stop="handleDeleteNotification(n.name)"
          >
            <FeatherIcon name="trash-2" class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else
        class="flex flex-1 flex-col items-center justify-center p-6 text-center"
      >
        <FeatherIcon name="bell-off" class="w-8 h-8 text-ink-gray-4 mb-3" />
        <p class="text-sm font-medium text-ink-gray-9">No New Notifications</p>
        <p class="text-xs text-ink-gray-5 mt-1">You have no new notifications</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Button, FeatherIcon } from 'frappe-ui'
import { onClickOutside } from '@vueuse/core'
import {
  visible,
  notifications,
  unreadNotificationsCount,
  toggleNotificationPanel,
  markDocAsRead,
  markAllAsRead,
  deleteNotification,
  clearAllNotifications,
  ensureLoaded,
} from '../stores/notifications'

const router = useRouter()
const target = ref(null)

onClickOutside(
  target,
  (event) => {
    if (visible.value) {
      toggleNotificationPanel()
    }
  },
  {
    ignore: ['#notifications-btn', '.notifications-btn-trigger'],
  },
)

// Real-time socket listener
const app = getCurrentInstance()
const $socket = app?.appContext?.config?.globalProperties?.$socket

onMounted(() => {
  ensureLoaded()
  if ($socket) {
    $socket.on('vault_notification', () => {
      notifications.reload()
    })
  }
})

onBeforeUnmount(() => {
  if ($socket) {
    $socket.off('vault_notification')
  }
})

function getInitials(name) {
  if (!name) return 'S'
  const parts = name.trim().split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return parts[0].substring(0, 2).toUpperCase()
}

function timeAgo(timestamp) {
  if (!timestamp) return ''
  try {
    const d = new Date(timestamp)
    const now = new Date()
    const diffMs = now - d
    const diffMins = Math.floor(diffMs / (1000 * 60))
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return `${diffDays}d ago`
    return d.toLocaleDateString()
  } catch (e) {
    return timestamp
  }
}

function handleNotificationClick(item) {
  markDocAsRead(item.name)

  if (item.route_path) {
    router.push(item.route_path)
  } else if (item.document_type === 'Vault Secret' && item.document_name) {
    router.push(`/secrets?secret=${item.document_name}`)
  } else if (item.document_type === 'Vault Share' || item.type === 'Share') {
    router.push('/shared')
  }
}

function handleMarkAllAsRead() {
  markAllAsRead()
}

function handleDeleteNotification(docname) {
  deleteNotification(docname)
}

function handleClearAll() {
  clearAllNotifications()
}
</script>
