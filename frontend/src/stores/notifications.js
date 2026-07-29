import { createResource } from 'frappe-ui'
import { computed, ref } from 'vue'

export const visible = ref(false)

export const notifications = createResource({
  url: 'frappe_vault.api.notifications.get_notifications',
  initialData: [],
})

export const unreadNotificationsCount = computed(
  () => notifications.data?.filter((n) => !n.read).length || 0,
)

// Load notifications on first access (deferred, not auto)
let _loaded = false
export function ensureLoaded() {
  if (!_loaded) {
    _loaded = true
    notifications.reload()
  }
}

export function toggleNotificationPanel() {
  visible.value = !visible.value
  if (visible.value) {
    notifications.reload()
  }
}

export const mark_as_read = createResource({
  url: 'frappe_vault.api.notifications.mark_as_read',
  onSuccess: () => {
    notifications.reload()
  },
})

export function markDocAsRead(docname) {
  mark_as_read.submit({ docname })
  visible.value = false
}

export function markAllAsRead() {
  mark_as_read.submit({ mark_all: true })
}

export const delete_notification = createResource({
  url: 'frappe_vault.api.notifications.delete_notification',
  onSuccess: () => {
    notifications.reload()
  },
})

export const clear_all_notifications = createResource({
  url: 'frappe_vault.api.notifications.clear_all_notifications',
  onSuccess: () => {
    notifications.reload()
  },
})

export function deleteNotification(docname) {
  delete_notification.submit({ docname })
}

export function clearAllNotifications() {
  clear_all_notifications.submit()
}
