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

setConfig('resourceFetcher', frappeRequest)

app.use(FrappeUI)
app.use(resourcesPlugin)
app.use(pageMetaPlugin)
app.use(router)

app.mount('#app')
