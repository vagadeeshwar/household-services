import { ref } from 'vue'

export function useLoading() {
  const isLoading = ref(false)
  const loadingMessage = ref('')

  const showLoading = (message = '') => {
    loadingMessage.value = message
    isLoading.value = true
  }

  const hideLoading = () => {
    isLoading.value = false
    loadingMessage.value = ''
  }

  // Helper for async operations
  const withLoading = async (promise, message = '') => {
    showLoading(message)
    try {
      return await promise
    } finally {
      hideLoading()
    }
  }

  return {
    isLoading,
    loadingMessage,
    showLoading,
    hideLoading,
    withLoading,
  }
}
