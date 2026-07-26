/**
 * Attachment utility functions for parsing, cleaning, and extracting file metadata.
 */

export function cleanUrl(url) {
  if (typeof url !== 'string') return ''
  return url.trim().replace(/^["'\[\]\s]+|["'\[\]\s]+$/g, '')
}

export function parseAttachments(val) {
  if (!val) return []
  let res = []
  if (Array.isArray(val)) {
    res = val
  } else if (typeof val === 'string') {
    let str = val.trim()
    if (!str) return []
    try {
      let parsed = JSON.parse(str)
      while (typeof parsed === 'string' && (parsed.startsWith('[') || parsed.startsWith('"'))) {
        parsed = JSON.parse(parsed)
      }
      if (Array.isArray(parsed)) {
        res = parsed
      } else if (typeof parsed === 'string') {
        res = [parsed]
      }
    } catch (e) {
      res = str.split(/[\n,]+/)
    }
  }

  return res
    .map(cleanUrl)
    .filter(s => s && s.length > 2 && (s.startsWith('/') || s.startsWith('http') || s.includes('.')))
}

export function isImageUrl(url) {
  if (!url) return false
  const cleaned = cleanUrl(url)
  return /\.(jpeg|jpg|gif|png|svg|webp)$/i.test(cleaned)
}

export function getFileName(url) {
  if (!url) return ''
  const cleaned = cleanUrl(url)
  return cleaned.split('/').pop() || cleaned
}
