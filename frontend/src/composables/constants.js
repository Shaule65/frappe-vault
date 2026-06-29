export const SECRET_TYPES = [
  'Password',
  'API Key',
  'Note',
  'SSH Key',
  'Certificate',
  'Credit Card',
  'Database',
  'Other',
]

export const secretTypeOptions = SECRET_TYPES.map(t => ({ label: t, value: t }))

export const typeIcons = {
  Password: 'key',
  'API Key': 'code',
  Note: 'file-text',
  'SSH Key': 'terminal',
  Certificate: 'shield',
  'Credit Card': 'credit-card',
  Database: 'database',
  Other: 'file',
}

export const typeColors = {
  Password: 'bg-blue-100 text-blue-600',
  'API Key': 'bg-purple-100 text-purple-600',
  Note: 'bg-green-100 text-green-600',
  'SSH Key': 'bg-orange-100 text-orange-600',
  Certificate: 'bg-teal-100 text-teal-600',
  'Credit Card': 'bg-yellow-100 text-yellow-600',
  Database: 'bg-red-100 text-red-600',
  Other: 'bg-surface-gray-3 text-ink-gray-6',
}

export const typeMeta = {
  Password: { icon: 'key', bg: 'bg-emerald-50 text-emerald-600 border-emerald-100', color: 'text-emerald-600' },
  'API Key': { icon: 'code', bg: 'bg-purple-50 text-purple-600 border-purple-100', color: 'text-purple-600' },
  Note: { icon: 'file-text', bg: 'bg-amber-50 text-amber-600 border-amber-100', color: 'text-amber-600' },
  'SSH Key': { icon: 'terminal', bg: 'bg-slate-50 text-slate-600 border-slate-100', color: 'text-slate-600' },
  Certificate: { icon: 'shield', bg: 'bg-indigo-50 text-indigo-600 border-indigo-100', color: 'text-indigo-600' },
  'Credit Card': { icon: 'credit-card', bg: 'bg-blue-50 text-blue-600 border-blue-100', color: 'text-blue-600' },
  Database: { icon: 'database', bg: 'bg-cyan-50 text-cyan-600 border-cyan-100', color: 'text-cyan-600' },
  Other: { icon: 'lock', bg: 'bg-pink-50 text-pink-600 border-pink-100', color: 'text-pink-600' },
}

export const strengthTheme = {
  weak: 'red',
  fair: 'orange',
  good: 'blue',
  strong: 'green',
  excellent: 'green',
}

export const permissionTheme = {
  'View Only': 'gray',
  'View & Copy': 'blue',
  'Edit': 'orange',
  'Full Control': 'green',
  'Revoked': 'red',
}

export const actionIcons = {
  Viewed: 'eye',
  Created: 'plus-circle',
  Updated: 'edit',
  Deleted: 'trash-2',
  Shared: 'share-2',
  Unshared: 'user-minus',
  Copied: 'copy',
  Generated: 'refresh-cw',
}

export const typeFilterOptions = [
  { label: 'All Types', value: '' },
  ...SECRET_TYPES.map(t => ({ label: t, value: t })),
]

export function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleDateString()
}

export function formatDateTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function formatRelativeTime(dt) {
  if (!dt) return ''
  const now = new Date()
  const date = new Date(dt)
  const seconds = Math.floor((now - date) / 1000)
  if (seconds < 60) return 'Just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes} min${minutes > 1 ? 's' : ''} ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`
  const weeks = Math.floor(days / 7)
  if (weeks < 4) return `${weeks} week${weeks > 1 ? 's' : ''} ago`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months} month${months > 1 ? 's' : ''} ago`
  const years = Math.floor(days / 365)
  return `${years} year${years > 1 ? 's' : ''} ago`
}
