import { createApp } from 'vue'
import {
  FrappeUI,
  setConfig,
  frappeRequest,
  resourcesPlugin,
  pageMetaPlugin,
} from 'frappe-ui'
import App from './App.vue'
import router from './router'
import './index.css'

const app = createApp(App)

// Get CSRF token from window (set by Jinja template)
const getCsrfToken = () => {
  return window.csrf_token || window.frappe?.boot?.csrf_token || ''
}

// Configure Frappe UI with custom fetcher that includes CSRF token
setConfig('resourceFetcher', (options) => {
  // Ensure headers exist
  options.headers = options.headers || {}
  // Add CSRF token to headers
  const token = getCsrfToken()
  if (token) {
    options.headers['X-Frappe-CSRF-Token'] = token
  }
  return frappeRequest(options)
})

// Disable socket.io (we don't need realtime for vault)
setConfig('socketio', false)

// Register plugins
app.use(FrappeUI)
app.use(resourcesPlugin)
app.use(pageMetaPlugin)
app.use(router)

app.mount('#app')
