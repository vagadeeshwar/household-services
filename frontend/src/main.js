// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

// Import Bootstrap and Bootstrap Icons CSS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

// Import Bootstrap JavaScript with Popper.js
import 'bootstrap/dist/js/bootstrap.bundle.min.js'


// main.js
import Loading from '@/components/shared/Loading.vue'
import Toast from '@/components/shared/Toast.vue'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import FormNavigationGuard from '@/components/shared/FormNavigationGuard.vue'

// Register global components
app.component('Loading', Loading)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)
app.component('FormNavigationGuard', FormNavigationGuard)

// Configure axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

// Add token if it exists
const token = localStorage.getItem('token')
if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Handle 401 responses globally
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            store.dispatch('auth/logout')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

const app = createApp(App)

app.use(router)
app.use(store)

app.mount('#app')