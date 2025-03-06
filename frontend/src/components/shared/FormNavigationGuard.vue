<template>
  <div class="modal fade" ref="modal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-exclamation-triangle-fill text-warning me-2"></i>
            Unsaved Changes
          </h5>
          <button type="button" class="btn-close" @click="handleStay"></button>
        </div>
        <div class="modal-body">
          {{ message }}
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="handleStay">Stay</button>
          <button type="button" class="btn btn-primary" @click="handleLeave">Leave</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import * as bootstrap from 'bootstrap'

export default {
  name: 'FormNavigationGuard',

  props: {
    when: {
      type: Boolean,
      required: true,
    },
    message: {
      type: String,
      default: 'You have unsaved changes. Are you sure you want to leave?',
    },
    onBeforeUnload: {
      type: Boolean,
      default: true,
    },
  },

  setup(props) {
    const router = useRouter()
    const modal = ref(null)
    const bsModal = ref(null)
    let nextNavigation = null
    let unregisterGuard = null
    let navigationCallback = null

    // Handle beforeunload event
    const handleBeforeUnload = (e) => {
      if (props.when) {
        e.preventDefault()
        e.returnValue = ''
      }
    }

    // Handle modal actions
    const handleLeave = () => {
      navigationCallback = () => {
        if (nextNavigation) {
          nextNavigation()
          nextNavigation = null
        }
      }
      bsModal.value?.hide()
    }

    const handleStay = () => {
      nextNavigation = null
      bsModal.value?.hide()
    }

    // Watch for changes in the when prop
    watch(
      () => props.when,
      (value) => {
        if (props.onBeforeUnload) {
          if (value) {
            window.addEventListener('beforeunload', handleBeforeUnload)
          } else {
            window.removeEventListener('beforeunload', handleBeforeUnload)
          }
        }
      },
      { immediate: true },
    )

    // Initialize modal and router guard
    onMounted(() => {
      if (modal.value) {
        // Setup modal event handlers
        modal.value.addEventListener('hidden.bs.modal', () => {
          if (navigationCallback) {
            navigationCallback()
            navigationCallback = null
          }
        })

        bsModal.value = new bootstrap.Modal(modal.value, {
          backdrop: 'static',
          keyboard: false,
        })

        // Setup router navigation guard
        unregisterGuard = router.beforeEach((to, from, next) => {
          if (!props.when) {
            next()
            return
          }

          nextNavigation = next
          bsModal.value?.show()
        })
      }
    })

    // Clean up
    onBeforeUnmount(() => {
      if (modal.value) {
        modal.value.removeEventListener('hidden.bs.modal', () => {
          if (navigationCallback) {
            navigationCallback()
            navigationCallback = null
          }
        })
      }

      if (unregisterGuard) {
        unregisterGuard()
      }

      if (bsModal.value) {
        bsModal.value.dispose()
      }

      if (props.when && props.onBeforeUnload) {
        window.removeEventListener('beforeunload', handleBeforeUnload)
      }
    })

    return {
      modal,
      handleLeave,
      handleStay,
    }
  },
}
</script>

<style scoped>
.modal-title {
  font-size: 1.1rem;
}

.modal-body {
  font-size: 0.95rem;
}
</style>
