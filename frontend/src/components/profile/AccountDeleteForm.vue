<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Account Deletion</h5>
      <button class="btn btn-sm btn-outline-danger" @click="toggleFormVisibility" v-if="!showForm">
        <i class="bi bi-trash me-1"></i>Delete Account
      </button>
    </div>
    <div class="card-body p-4">
      <div v-if="!showForm" class="text-center py-4">
        <p class="text-muted">Delete your account permanently. This action cannot be undone.</p>
      </div>

      <div v-else>
        <div class="alert alert-danger">
          <h5 class="alert-heading">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>Warning!
          </h5>
          <p>
            You are about to permanently delete your account. This action cannot be undone and will
            result in the permanent loss of all your data.
          </p>
          <hr />
          <p class="mb-0">
            If you are experiencing issues with the platform, please consider contacting support
            before proceeding with account deletion.
          </p>
        </div>

        <form @submit.prevent="showConfirmationModal">
          <div class="mb-3">
            <label for="password" class="form-label">Enter your password to confirm</label>
            <div class="input-group">
              <input
                :type="showPassword ? 'text' : 'password'"
                class="form-control"
                id="password"
                v-model="formData.password"
                :class="{ 'is-invalid': validationErrors.password }"
                required
              />
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="showPassword = !showPassword"
              >
                <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
              </button>
              <div class="invalid-feedback">{{ validationErrors.password }}</div>
            </div>
          </div>

          <div class="d-flex justify-content-end gap-2 mt-4">
            <button type="button" class="btn btn-outline-secondary" @click="cancelForm">
              Cancel
            </button>
            <button type="submit" class="btn btn-danger">Proceed with Deletion</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div
      class="modal fade"
      id="deleteConfirmationModal"
      tabindex="-1"
      aria-labelledby="deleteConfirmationModalLabel"
      aria-hidden="true"
      ref="confirmModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title" id="deleteConfirmationModalLabel">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>Final Confirmation
            </h5>
            <button
              type="button"
              class="btn-close btn-close-white"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you absolutely sure you want to delete your account?</p>
            <p>
              This will immediately log you out and permanently delete all your data, including:
            </p>
            <ul>
              <li>Your profile information</li>
              <li>Your service requests and history</li>
              <li>Your reviews and ratings</li>
            </ul>
            <p class="text-danger fw-bold">This action CANNOT be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-danger"
              @click="deleteAccount"
              :disabled="isDeleting"
            >
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2"></span>
              Yes, Delete My Account
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import * as bootstrap from 'bootstrap'

export default {
  name: 'AccountDeleteForm',

  setup() {
    const store = useStore()
    const router = useRouter()

    const showForm = ref(false)
    const showPassword = ref(false)
    const isDeleting = ref(false)
    const confirmModal = ref(null)
    let bsConfirmModal = null

    // Form data
    const formData = reactive({
      password: '',
    })

    // Validation errors
    const validationErrors = reactive({
      password: '',
    })

    // Methods
    const toggleFormVisibility = () => {
      showForm.value = true
      resetForm()
    }

    const cancelForm = () => {
      showForm.value = false
      resetForm()
    }

    const resetForm = () => {
      formData.password = ''
      validationErrors.password = ''
    }

    const validateForm = () => {
      validationErrors.password = ''

      if (!formData.password) {
        validationErrors.password = 'Password is required'
        return false
      }

      return true
    }

    const showConfirmationModal = () => {
      if (!validateForm()) return

      if (bsConfirmModal) {
        bsConfirmModal.show()
      }
    }

    const deleteAccount = async () => {
      isDeleting.value = true
      try {
        // Call API to delete account
        await store.dispatch('auth/deleteAccount', {
          password: formData.password,
        })

        // Close modal
        if (bsConfirmModal) {
          bsConfirmModal.hide()
        }

        // Show success message
        window.showToast({
          type: 'success',
          title: 'Account Deleted',
          message: 'Your account has been successfully deleted',
        })

        // Log out and redirect to home
        await store.dispatch('auth/logout')
        router.push('/')
      } catch (error) {
        // Show error toast
        window.showToast({
          type: 'error',
          title: 'Deletion Failed',
          message: error.response?.data?.detail || 'Failed to delete account',
        })

        // Set validation error for password
        if (error.response?.status === 401) {
          validationErrors.password = 'Password is incorrect'
        }

        // Close modal if open
        if (bsConfirmModal) {
          bsConfirmModal.hide()
        }
      } finally {
        isDeleting.value = false
      }
    }

    // Initialize modal
    onMounted(() => {
      if (confirmModal.value) {
        bsConfirmModal = new bootstrap.Modal(confirmModal.value)
      }
    })

    return {
      showForm,
      showPassword,
      isDeleting,
      formData,
      validationErrors,
      confirmModal,
      toggleFormVisibility,
      cancelForm,
      showConfirmationModal,
      deleteAccount,
    }
  },
}
</script>
