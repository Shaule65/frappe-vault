import { formatTime } from '../composables/constants'

export function parseDetails(details) {
  if (!details) return {}
  if (typeof details === 'object') return details
  try {
    return JSON.parse(details)
  } catch (e) {
    return {}
  }
}

export function getActivityText(item) {
  const details = parseDetails(item.details)
  switch (item.action) {
    case 'Created':
      return 'created this secret'
    case 'Updated':
      return 'updated this secret'
    case 'Deleted':
      return 'deleted this secret'
    case 'Viewed':
      return 'viewed this secret'
    case 'Copied': {
      const field = details.field || 'password'
      return `copied the ${field} field`
    }
    case 'Shared': {
      const recipient = details.recipient || 'Unknown'
      const permission = details.permission || 'View Only'
      const expiresOn = details.expires_on ? ` (expires ${formatTime(details.expires_on)})` : ''
      return `shared this secret with ${recipient} (${permission})${expiresOn}`
    }
    case 'Unshared': {
      const recipient = details.recipient || 'Unknown'
      return `revoked access for ${recipient}`
    }
    default:
      return `${item.action.toLowerCase()} this secret`
  }
}

export function getActionMainText(item) {
  switch (item.action) {
    case 'Created': return 'created this secret'
    case 'Updated': return 'updated this secret'
    case 'Deleted': return 'deleted this secret'
    case 'Viewed': return 'viewed this secret'
    case 'Copied': return 'copied secret credentials'
    case 'Shared': return 'shared access to this secret'
    case 'Unshared': return 'revoked secret access'
    default: return `${item.action.toLowerCase()} this secret`
  }
}

export function hasActivityDetails(item) {
  return ['Copied', 'Shared', 'Unshared'].includes(item.action)
}

export function getDetailIcon(item) {
  switch (item.action) {
    case 'Copied': return 'copy'
    case 'Shared': return 'share-2'
    case 'Unshared': return 'shield-off'
    default: return 'info'
  }
}

export function getActivityDetailText(item) {
  const details = parseDetails(item.details)
  switch (item.action) {
    case 'Copied': {
      const field = details.field || 'password'
      return `Field: ${field}`
    }
    case 'Shared': {
      const recipient = details.recipient || 'Unknown'
      const permission = details.permission || 'View Only'
      const expiresOn = details.expires_on ? ` • Expires ${formatTime(details.expires_on)}` : ''
      return `${recipient} (${permission})${expiresOn}`
    }
    case 'Unshared': {
      const recipient = details.recipient || 'Unknown'
      return `Recipient: ${recipient}`
    }
    default: return ''
  }
}
