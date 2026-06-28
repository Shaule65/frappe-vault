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

export const actionColors = {
  Created: 'bg-green-100 text-green-600',
  Deleted: 'bg-red-100 text-red-600',
  Shared: 'bg-blue-100 text-blue-600',
  Unshared: 'bg-orange-100 text-orange-600',
  Updated: 'bg-purple-100 text-purple-600',
  Copied: 'bg-teal-100 text-teal-600',
  Generated: 'bg-yellow-100 text-yellow-600',
  Viewed: 'bg-surface-gray-3 text-ink-gray-6',
}
