// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

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