import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import App from '@/App.vue'
import { router } from '@/router'
import { useAuthStore } from '@/stores/auth'

import '@/styles/main.css'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const app = createApp(App)
app.use(pinia)
app.use(router)

const authStore = useAuthStore()
if (authStore.token) {
  authStore.fetchMe().catch(() => authStore.clear())
}

app.mount('#app')
