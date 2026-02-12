import { reactive } from 'vue'
import { call } from 'frappe-ui'

// Get CSRF token
const getCsrfToken = () => {
  return window.csrf_token || window.frappe?.boot?.csrf_token || ''
}

export const session = reactive({
  user: null,
  isLoggedIn: false,
  initialized: false,
  fullName: '',
  userImage: '',

  async init() {
    if (this.initialized) return

    try {
      const user = await call('frappe.auth.get_logged_user')
      if (user && user !== 'Guest') {
        this.user = user
        this.isLoggedIn = true
        await this.fetchUserInfo()
      }
    } catch (e) {
      console.error('Session init failed:', e)
      this.isLoggedIn = false
    }

    this.initialized = true
  },

  async fetchUserInfo() {
    try {
      const info = await call('frappe.client.get', {
        doctype: 'User',
        name: this.user,
      })
      this.fullName = info.full_name
      this.userImage = info.user_image
    } catch (e) {
      console.error('Failed to fetch user info:', e)
    }
  },

  async login(email, password) {
    try {
      await call('login', { usr: email, pwd: password })
      this.user = email
      this.isLoggedIn = true
      await this.fetchUserInfo()
      // Refresh to get new CSRF token
      window.location.reload()
      return { success: true }
    } catch (e) {
      return { success: false, error: e.message || 'Login failed' }
    }
  },

  async logout() {
    try {
      await call('logout')
      this.user = null
      this.isLoggedIn = false
      window.location.reload()
    } catch (e) {
      console.error('Logout failed:', e)
    }
  },
})

// Initialize session on load
session.init()
