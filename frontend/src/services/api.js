import axios from 'axios'
import { jwtDecode } from 'jwt-decode'
import store from '@/store'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// Request interceptor - Adds auth token if exists
api.interceptors.request.use(
  async (config) => {
    const token = store.getters['auth/token']
    if (token) {
      try {
        const decodedToken = jwtDecode(token)
        const currentTime = Date.now() / 1000

        if (decodedToken.exp < currentTime) {
          await store.dispatch('auth/logout')
          router.push('/login')
          return Promise.reject('Session expired')
        }

        config.headers.Authorization = `Bearer ${token}`
      } catch (error) {
        console.error('Token validation error:', error)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response interceptor - Handles common errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (!error.response) {
      window.showToast({
        type: 'error',
        title: 'Network Error',
        message: 'Please check your internet connection',
      })
      return Promise.reject(error)
    }

    const { status, data } = error.response

    // Handle 401 Unauthorized
    if (status === 401) {
      await store.dispatch('auth/logout')
      router.push('/login')
      window.showToast({
        type: 'error',
        title: 'Session Expired/Unauthorized',
        message: 'Please login again',
      })
    }

    // Handle validation errors
    if (status === 422 && data.errors) {
      const firstError = Object.values(data.errors)[0]
      window.showToast({
        type: 'error',
        title: 'Validation Error',
        message: Array.isArray(firstError) ? firstError[0] : firstError,
      })
    }

    // Handle forbidden access
    if (status === 403) {
      window.showToast({
        type: 'error',
        title: 'Access Denied',
        message: data.message || 'You do not have permission to perform this action',
      })
    }

    // Handle not found
    if (status === 404) {
      router.push('/not-found')
    }

    // Handle server errors
    if (status >= 500) {
      window.showToast({
        type: 'error',
        title: 'Server Error',
        message: data.message || 'An unexpected error occurred. Please try again later.',
      })
    }

    return Promise.reject(error)
  },
)

export default api
