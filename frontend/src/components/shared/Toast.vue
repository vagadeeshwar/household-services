# src/components/shared/Toast.vue
<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast show"
      :class="toastClasses(toast)"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="toast-header" :class="headerClasses(toast)">
        <i :class="['bi', iconClass(toast.type), 'me-2']"></i>
        <strong class="me-auto">{{ toast.title }}</strong>
        <small>{{ timeAgo(toast.timestamp) }}</small>
        <button type="button" class="btn-close" @click="removeToast(toast.id)"></button>
      </div>
      <div class="toast-body" :class="{ 'text-white': toast.type }">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import moment from 'moment'

export default {
  name: 'Toast',
  setup() {
    const toasts = ref([])
    let nextId = 1

    const toastClasses = (toast) => {
      if (!toast.type) return ''
      return {
        'bg-success': toast.type === 'success',
        'bg-danger': toast.type === 'danger',
        'bg-warning': toast.type === 'warning',
        'bg-info': toast.type === 'info',
      }
    }

    const headerClasses = (toast) => {
      if (!toast.type) return ''
      return {
        'text-white': ['success', 'danger'].includes(toast.type),
        'border-0': !!toast.type,
      }
    }

    const iconClass = (type) => {
      switch (type) {
        case 'success':
          return 'bi-check-circle-fill'
        case 'danger':
          return 'bi-x-circle-fill'
        case 'warning':
          return 'bi-exclamation-triangle-fill'
        case 'info':
          return 'bi-info-circle-fill'
        default:
          return 'bi-bell-fill'
      }
    }

    const timeAgo = (timestamp) => moment(timestamp).fromNow()

    const addToast = (toast) => {
      const id = nextId++
      const newToast = {
        id,
        timestamp: new Date(),
        title: toast.title || 'Notification',
        type: toast.type,
        message: toast.message,
      }

      toasts.value.push(newToast)

      // Auto remove after duration
      setTimeout(() => {
        removeToast(id)
      }, toast.duration || 5000)
    }

    const removeToast = (id) => {
      const index = toasts.value.findIndex((t) => t.id === id)
      if (index > -1) {
        toasts.value.splice(index, 1)
      }
    }

    // Expose the addToast method globally
    onMounted(() => {
      window.showToast = addToast
    })

    return {
      toasts,
      toastClasses,
      headerClasses,
      iconClass,
      timeAgo,
      removeToast,
    }
  },
}
</script>

<style scoped>
.toast-container {
  z-index: 1050;
  max-width: 350px;
}

.toast {
  opacity: 1;
  margin-bottom: 0.5rem;
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.1);
}

.toast-header {
  padding: 0.75rem 1rem;
}

.toast-body {
  padding: 1rem;
}

/* Animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
