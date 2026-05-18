/**
 * Clipboard utility with auto-clear.
 */
import { ref } from 'vue'

export function useClipboard(clearAfterMs = 30000) {
  const copied = ref(false)
  const countdown = ref(0)
  let timer = null
  let countdownTimer = null

  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text)
      copied.value = true
      countdown.value = Math.ceil(clearAfterMs / 1000)

      // Clear clipboard after timeout
      clearTimeout(timer)
      clearInterval(countdownTimer)

      countdownTimer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) clearInterval(countdownTimer)
      }, 1000)

      timer = setTimeout(async () => {
        try {
          await navigator.clipboard.writeText('')
        } catch (e) {
          // Clipboard clear may fail if tab is not focused
        }
        copied.value = false
        countdown.value = 0
      }, clearAfterMs)

      return true
    } catch (e) {
      console.error('Clipboard copy failed:', e)
      return false
    }
  }

  return { copy, copied, countdown }
}
