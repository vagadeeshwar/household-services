<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Change Password</h5>
      <button class="btn btn-sm btn-outline-primary" @click="toggleFormVisibility" v-if="!showForm">
        <i class="bi bi-key me-1"></i>Change Password
      </button>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="handleSubmit" v-if="showForm">
        <div class="mb-3">
          <label for="currentPassword" class="form-label">Current Password</label>
          <div class="input-group">
            <input
              :type="showCurrentPassword ? 'text' : 'password'"
              class="form-control"
              id="currentPassword"
              v-model="formData.currentPassword"
              :class="{ 'is-invalid': validationErrors.currentPassword }"
              required
            />
            <button
              class="btn btn-outline-secondary"
              type="button"
              @click="showCurrentPassword = !showCurrentPassword"
            >
              <i class="bi" :class="showCurrentPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
            </button>
            <div class="invalid-feedback">{{ validationErrors.currentPassword }}</div>
          </div>
        </div>

        <div class="mb-3">
          <label for="newPassword" class="form-label">New Password</label>
          <div class="input-group">
            <input
              :type="showNewPassword ? 'text' : 'password'"
              class="form-control"
              id="newPassword"
              v-model="formData.newPassword"
              :class="{ 'is-invalid': validationErrors.newPassword }"
              required
            />
            <button
              class="btn btn-outline-secondary"
              type="button"
              @click="showNewPassword = !showNewPassword"
            >
              <i class="bi" :class="showNewPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
            </button>
            <div class="invalid-feedback">{{ validationErrors.newPassword }}</div>
          </div>
          <div class="form-text">
            Password must be at least 8 characters long and include uppercase, lowercase, number,
            and special character.
          </div>
        </div>

        <div class="mb-3">
          <label for="confirmPassword" class="form-label">Confirm New Password</label>
          <div class="input-group">
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              class="form-control"
              id="confirmPassword"
              v-model="formData.confirmPassword"
              :class="{ 'is-invalid': validationErrors.confirmPassword }"
              required
            />
            <button
              class="btn btn-outline-secondary"
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <i class="bi" :class="showConfirmPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
            </button>
            <div class="invalid-feedback">{{ validationErrors.confirmPassword }}</div>
          </div>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-4">
          <button type="button" class="btn btn-outline-secondary" @click="cancelForm">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            Change Password
          </button>
        </div>
      </form>

      <div v-else class="text-center py-4">
        <p class="text-muted">You can change your password for security reasons.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'PasswordChangeForm',

  setup() {
    const store = useStore()
    const router = useRouter()

    const showForm = ref(false)
    const isSubmitting = ref(false)

    // Password visibility toggles
    const showCurrentPassword = ref(false)
    const showNewPassword = ref(false)
    const showConfirmPassword = ref(false)

    // Form data
    const formData = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    })

    // Validation errors
    const validationErrors = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
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
      // Clear form data
      formData.currentPassword = ''
      formData.newPassword = ''
      formData.confirmPassword = ''

      // Clear validation errors
      validationErrors.currentPassword = ''
      validationErrors.newPassword = ''
      validationErrors.confirmPassword = ''
    }

    const validateForm = () => {
      let isValid = true

      // Reset validation errors
      validationErrors.currentPassword = ''
      validationErrors.newPassword = ''
      validationErrors.confirmPassword = ''

      // Validate current password
      if (!formData.currentPassword) {
        validationErrors.currentPassword = 'Current password is required'
        isValid = false
      }

      // Validate new password
      if (!formData.newPassword) {
        validationErrors.newPassword = 'New password is required'
        isValid = false
      } else if (formData.newPassword.length < 8) {
        validationErrors.newPassword = 'Password must be at least 8 characters'
        isValid = false
      } else if (!/[A-Z]/.test(formData.newPassword)) {
        validationErrors.newPassword = 'Password must contain an uppercase letter'
        isValid = false
      } else if (!/[a-z]/.test(formData.newPassword)) {
        validationErrors.newPassword = 'Password must contain a lowercase letter'
        isValid = false
      } else if (!/\d/.test(formData.newPassword)) {
        validationErrors.newPassword = 'Password must contain a number'
        isValid = false
      } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(formData.newPassword)) {
        validationErrors.newPassword = 'Password must contain a special character'
        isValid = false
      }

      // Validate confirm password
      if (!formData.confirmPassword) {
        validationErrors.confirmPassword = 'Please confirm your new password'
        isValid = false
      } else if (formData.newPassword !== formData.confirmPassword) {
        validationErrors.confirmPassword = 'Passwords do not match'
        isValid = false
      }

      return isValid
    }

    const handleSubmit = async () => {
      if (!validateForm()) return

      isSubmitting.value = true
      try {
        // Call API to change password
        await store.dispatch('auth/changePassword', {
          params: {
            old_password: formData.currentPassword,
            new_password: formData.newPassword,
          },
        })

        // Show success message
        window.showToast({
          type: 'success',
          title: 'Password Changed',
          message: 'Your password has been changed successfully. Please login again.',
        })

        // Log out and redirect to login
        await store.dispatch('auth/logout')
        router.push('/login')
      } catch (error) {
        // Show error toast
        window.showToast({
          type: 'error',
          title: 'Change Failed',
          message: error.response?.data?.detail || 'Failed to change password',
        })

        // Set validation error for current password
        if (error.response?.status === 401) {
          validationErrors.currentPassword = 'Current password is incorrect'
        }
      } finally {
        isSubmitting.value = false
      }
    }

    return {
      showForm,
      isSubmitting,
      formData,
      validationErrors,
      showCurrentPassword,
      showNewPassword,
      showConfirmPassword,
      toggleFormVisibility,
      cancelForm,
      handleSubmit,
    }
  },
}
</script>
