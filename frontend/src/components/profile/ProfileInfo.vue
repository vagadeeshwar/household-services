<template>
  <div v-if="isLoading" class="text-center py-5">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading profile data...</span>
    </div>
  </div>
  <div v-else class="card shadow-sm mb-4">
    <!-- Header -->
    <div class="card-header" :class="{ 'bg-primary text-white': !editMode, 'bg-white': editMode }">
      <div v-if="!editMode" class="d-flex align-items-center p-3">
        <!-- Profile header in view mode -->
        <div class="rounded-circle bg-white text-primary p-3">
          <i class="bi bi-person-circle fs-2"></i>
        </div>
        <div class="ms-3">
          <h4 class="mb-1">{{ userData?.full_name }}</h4>
          <p class="mb-0 opacity-75">{{ formatRoleTitle(userData?.role) }}</p>
        </div>
      </div>
      <div v-else class="d-flex justify-content-between align-items-center py-3">
        <!-- Profile header in edit mode -->
        <h5 class="mb-0">Update Profile</h5>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body p-4">
      <!-- Success Alert -->
      <div
        v-if="showSuccessMessage"
        class="alert alert-success alert-dismissible fade show mb-4"
        role="alert"
      >
        <i class="bi bi-check-circle-fill me-2"></i>
        Your profile has been updated successfully!
        <button
          type="button"
          class="btn-close"
          @click="showSuccessMessage = false"
          aria-label="Close"
        ></button>
      </div>

      <!-- View Mode -->
      <div v-if="!editMode" class="row g-4">
        <!-- Personal Information -->
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="border-bottom pb-2">Personal Information</h5>
            <div v-if="userData?.role !== 'admin'">
              <button class="btn btn-sm btn-outline-primary" @click="toggleEditMode">
                <i class="bi bi-pencil me-1"></i>Edit
              </button>
            </div>
          </div>
          <div class="row g-3 mt-2">
            <div class="col-md-6">
              <label class="form-label text-muted">Username</label>
              <p class="fw-medium">{{ userData?.username }}</p>
            </div>
            <div class="col-md-6">
              <label class="form-label text-muted">Email</label>
              <p class="fw-medium">{{ userData?.email }}</p>
            </div>
            <div class="col-md-6">
              <label class="form-label text-muted">Full Name</label>
              <p class="fw-medium">{{ userData?.full_name }}</p>
            </div>
            <div class="col-md-6">
              <label class="form-label text-muted">Phone</label>
              <p class="fw-medium">+91 {{ userData?.phone }}</p>
            </div>
            <div class="col-12">
              <label class="form-label text-muted">Address</label>
              <p class="fw-medium">{{ userData?.address }}</p>
            </div>
            <div class="col-md-6">
              <label class="form-label text-muted">PIN Code</label>
              <p class="fw-medium">{{ userData?.pin_code }}</p>
            </div>

            <!-- Professional-specific fields -->
            <template v-if="isUserProfessional">
              <div class="col-md-6">
                <label class="form-label text-muted">Experience</label>
                <p class="fw-medium">{{ userData?.experience_years }} years</p>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted">Service Type</label>
                <p class="fw-medium">{{ serviceName }}</p>
              </div>
              <div class="col-12">
                <label class="form-label text-muted">Description</label>
                <p class="fw-medium">{{ userData?.description }}</p>
              </div>
              <div class="col-md-6" v-if="userData?.average_rating">
                <label class="form-label text-muted">Average Rating</label>
                <p class="fw-medium">
                  <span class="text-warning">
                    <i
                      v-for="i in 5"
                      :key="i"
                      class="bi"
                      :class="
                        i <= Math.round(userData?.average_rating) ? 'bi-star-fill' : 'bi-star'
                      "
                    ></i>
                  </span>
                  {{ userData?.average_rating?.toFixed(1) }}
                </p>
              </div>
            </template>
          </div>
        </div>

        <!-- Account Information -->
        <div class="col-12">
          <h5 class="border-bottom pb-2">Account Information</h5>
          <div class="row g-3 mt-2">
            <div class="col-md-6">
              <label class="form-label text-muted">Account Status</label>
              <p>
                <span class="badge" :class="userData?.is_active ? 'bg-success' : 'bg-danger'">
                  {{ userData?.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span
                  v-if="isUserProfessional"
                  class="badge ms-2"
                  :class="userData?.is_verified ? 'bg-success' : 'bg-warning'"
                >
                  {{ userData?.is_verified ? 'Verified' : 'Pending Verification' }}
                </span>
              </p>
            </div>
            <div class="col-md-6">
              <label class="form-label text-muted">Last Login</label>
              <p class="fw-medium">{{ formattedLastLogin }}</p>
            </div>
            <div class="col-md-6">
              <label class="form-label text-muted">Account Created</label>
              <p class="fw-medium">{{ formattedCreatedAt }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Mode -->
      <form @submit.prevent="handleSubmit" v-if="editMode">
        <div class="row g-3">
          <div class="col-md-6">
            <label for="email" class="form-label">Email</label>
            <input
              type="email"
              class="form-control"
              id="email"
              v-model="v$.email.$model"
              :class="{ 'is-invalid': v$.email.$error }"
            />
            <div v-if="v$.email.$error" class="invalid-feedback">
              <span v-if="v$.email.required.$invalid">Email is required</span>
              <span v-else-if="v$.email.email.$invalid">Please enter a valid email address</span>
            </div>
          </div>

          <div class="col-md-6">
            <label for="fullName" class="form-label">Full Name</label>
            <input
              type="text"
              class="form-control"
              id="fullName"
              v-model="v$.full_name.$model"
              :class="{ 'is-invalid': v$.full_name.$error }"
            />
            <div v-if="v$.full_name.$error" class="invalid-feedback">
              <span v-if="v$.full_name.required.$invalid">Full name is required</span>
              <span v-else-if="v$.full_name.minLength.$invalid"
                >Full name must be at least 4 characters</span
              >
            </div>
          </div>

          <div class="col-md-6">
            <label for="phone" class="form-label">Phone</label>
            <input
              type="text"
              class="form-control"
              id="phone"
              v-model="v$.phone.$model"
              :class="{ 'is-invalid': v$.phone.$error }"
            />
            <div v-if="v$.phone.$error" class="invalid-feedback">
              <span v-if="v$.phone.required.$invalid">Phone number is required</span>
              <span v-else-if="v$.phone.phoneFormat.$invalid"
                >Phone number must be 10 digits and not start with 0</span
              >
            </div>
          </div>

          <div class="col-md-6">
            <label for="pinCode" class="form-label">PIN Code</label>
            <input
              type="text"
              class="form-control"
              id="pinCode"
              v-model="v$.pin_code.$model"
              :class="{ 'is-invalid': v$.pin_code.$error }"
            />
            <div v-if="v$.pin_code.$error" class="invalid-feedback">
              <span v-if="v$.pin_code.required.$invalid">PIN code is required</span>
              <span v-else-if="v$.pin_code.pinCodeFormat.$invalid"
                >PIN code must be 6 digits and not start with 0</span
              >
            </div>
          </div>

          <div class="col-12">
            <label for="address" class="form-label">Address</label>
            <textarea
              class="form-control"
              id="address"
              rows="3"
              v-model="v$.address.$model"
              :class="{ 'is-invalid': v$.address.$error }"
            ></textarea>
            <div v-if="v$.address.$error" class="invalid-feedback">
              <span v-if="v$.address.required.$invalid">Address is required</span>
              <span v-else-if="v$.address.minLength.$invalid"
                >Address must be at least 5 characters</span
              >
            </div>
          </div>

          <!-- Professional-specific fields -->
          <div class="col-12" v-if="isUserProfessional && userData?.description !== undefined">
            <label for="description" class="form-label">Professional Description</label>
            <textarea
              class="form-control"
              id="description"
              rows="4"
              v-model="v$.description.$model"
              :class="{ 'is-invalid': v$.description.$error }"
            ></textarea>
            <div v-if="v$.description.$error" class="invalid-feedback">
              <span v-if="v$.description.required.$invalid"
                >Professional description is required</span
              >
              <span v-else-if="v$.description.minLength.$invalid"
                >Description must be at least 10 characters</span
              >
            </div>
            <div class="form-text">Describe your expertise and services you provide.</div>
          </div>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-4">
          <button type="button" class="btn btn-outline-secondary" @click="cancelEdit">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting || v$.$invalid">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            Save Changes
          </button>
        </div>
      </form>
    </div>

    <!-- Form Navigation Guard -->
    <FormNavigationGuard
      :when="hasUnsavedChanges"
      message="You have unsaved changes. Are you sure you want to leave?"
    />
  </div>
</template>

<script>
import { ref, computed, reactive, watch, onBeforeUnmount, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useVuelidate } from '@vuelidate/core'
import { required, email, minLength, helpers, maxLength } from '@vuelidate/validators'
import { formatDateTime } from '@/utils/date'

export default {
  name: 'UnifiedProfileComponent',

  emits: ['profile-updated'],

  setup({ emit }) {
    const store = useStore()
    const editMode = ref(false)
    const isSubmitting = ref(false)
    const hasUnsavedChanges = ref(false)
    const showSuccessMessage = ref(false)

    // Get user data and loading state from Vuex store
    const userData = computed(() => store.getters['auth/currentUser'])
    const isLoading = computed(() => store.getters['auth/isLoading'])

    // Computed properties for user role and formatted dates
    const isUserProfessional = computed(() => userData.value?.role === 'professional')

    const formattedLastLogin = computed(() => formatDateTime(userData.value?.last_login))
    const formattedCreatedAt = computed(() => formatDateTime(userData.value?.created_at))

    // Get actual service name instead of just ID for professionals
    const serviceName = computed(() => {
      if (!isUserProfessional.value || !userData.value?.service_type_id) return ''

      // Check if services are already loaded
      const services = store.getters['services/allServices'] || []
      if (services.length === 0) {
        // If services aren't loaded yet, fetch them
        fetchServices()
        return `Loading service information...`
      }

      // Find matching service
      const service = services.find((s) => s.id === userData.value.service_type_id)
      return service ? service.name : `Service #${userData.value.service_type_id}`
    })

    const fetchServices = async () => {
      try {
        // Only fetch if we don't already have services
        if ((store.getters['services/allServices'] || []).length === 0) {
          // Dispatch action to fetch all services
          await store.dispatch('services/fetchActiveServices', {
            params: { per_page: 100 }, // Fetch more services to ensure we get all
            forceRefresh: true, // Force refresh to ensure we have latest data
          })
        }
      } catch (error) {
        console.error('Error fetching services:', error)
        window.showToast({
          type: 'warning',
          title: 'Could not load service information',
          message: 'Service details may be incomplete',
        })
      }
    }

    // Form data
    const formData = reactive({
      email: '',
      full_name: '',
      phone: '',
      address: '',
      pin_code: '',
      description: '',
    })

    // Original form data for change detection
    const originalFormData = reactive({
      email: '',
      full_name: '',
      phone: '',
      address: '',
      pin_code: '',
      description: '',
    })

    // Custom validators
    const phoneFormat = helpers.regex(/^[1-9]\d{9}$/)
    const pinCodeFormat = helpers.regex(/^[1-9][0-9]{5}$/)

    // Vuelidate rules
    const rules = computed(() => {
      const baseRules = {
        email: { required, email },
        full_name: { required, minLength: minLength(4), maxLength: maxLength(100) },
        phone: { required, phoneFormat },
        pin_code: { required, pinCodeFormat },
        address: { required, minLength: minLength(5), maxLength: maxLength(200) },
      }

      // Add professional-specific rules if needed
      if (isUserProfessional.value && userData.value?.description !== undefined) {
        baseRules.description = { required, minLength: minLength(10), maxLength: maxLength(1000) }
      }

      return baseRules
    })

    // Initialize Vuelidate
    const v$ = useVuelidate(rules, formData)

    // Watch for changes to detect unsaved edits
    watch(
      formData,
      () => {
        if (editMode.value) {
          hasUnsavedChanges.value = !objectsEqual(formData, originalFormData)
        }
      },
      { deep: true },
    )

    // Helper to compare objects
    const objectsEqual = (obj1, obj2) => {
      return JSON.stringify(obj1) === JSON.stringify(obj2)
    }

    // Utility functions
    const formatRoleTitle = (role) => {
      if (!role) return ''
      return role.charAt(0).toUpperCase() + role.slice(1)
    }

    // Methods
    const toggleEditMode = () => {
      resetForm()
      editMode.value = true
    }

    const cancelEdit = () => {
      if (hasUnsavedChanges.value) {
        if (!confirm('You have unsaved changes. Are you sure you want to cancel?')) {
          return
        }
      }
      editMode.value = false
      hasUnsavedChanges.value = false
      resetForm()
    }

    const resetForm = () => {
      if (!userData.value) return

      // Reset form data from user data
      formData.email = userData.value?.email || ''
      formData.full_name = userData.value?.full_name || ''
      formData.phone = userData.value?.phone || ''
      formData.address = userData.value?.address || ''
      formData.pin_code = userData.value?.pin_code || ''

      // Professional fields
      if (isUserProfessional.value) {
        formData.description = userData.value?.description || ''
      }

      // Store original form data for change detection
      Object.assign(originalFormData, { ...formData })

      // Reset validation
      v$.value.$reset()
    }
    const handleSubmit = async () => {
      // Validate the form using Vuelidate
      const isFormValid = await v$.value.$validate()
      if (!isFormValid) return
      isSubmitting.value = true
      try {
        // Prepare update data
        const updateData = {
          email: formData.email,
          full_name: formData.full_name,
          phone: formData.phone,
          address: formData.address,
          pin_code: formData.pin_code,
        }
        // Add description for professionals
        if (isUserProfessional.value && formData.description !== undefined) {
          updateData.description = formData.description
        }
        // Update profile via Vuex
        await store.dispatch('auth/updateProfile', { data: updateData })

        // Show success message
        showSuccessMessage.value = true

        // Also show toast notification
        window.showToast({
          type: 'success',
          title: 'Profile Updated',
        })

        // Exit edit mode
        editMode.value = false
        hasUnsavedChanges.value = false

        // Emit event to parent component
        if (typeof emit === 'function') {
          emit('profile-updated')
        }

        // Store timeout ID so it can be cleared if needed
        const timeoutId = setTimeout(() => {
          if (showSuccessMessage.value) {
            // Check if component is still mounted/value exists
            showSuccessMessage.value = false
          }
        }, 5000)

        // Clean up timeout on component unmount
        onBeforeUnmount(() => {
          clearTimeout(timeoutId)
        })
      } catch (error) {
        // Show error toast
        window.showToast({
          type: 'error',
          title: error.response?.data?.detail || 'Failed to update profile',
        })
        // Handle API validation errors
        if (error.response?.data?.errors) {
          const serverErrors = error.response.data.errors
          // Map server errors to form fields
          Object.keys(serverErrors).forEach((key) => {
            if (v$.value[key]) {
              v$.value[key].$setErrors([serverErrors[key]])
            }
          })
        }
      } finally {
        isSubmitting.value = false
      }
    }

    // Initialize form data when userData changes
    watch(
      userData,
      () => {
        if (userData.value) {
          resetForm()
        }
      },
      { immediate: true },
    )

    onMounted(() => {
      if (isUserProfessional.value) {
        fetchServices()
      }
    })

    return {
      // State
      userData,
      isLoading,
      editMode,
      isSubmitting,
      hasUnsavedChanges,
      showSuccessMessage,
      isUserProfessional,
      formattedLastLogin,
      formattedCreatedAt,
      serviceName,

      // Form validation
      formData,
      v$,

      // Methods
      formatRoleTitle,
      toggleEditMode,
      cancelEdit,
      handleSubmit,
    }
  },
}
</script>

<style scoped>
.alert {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.invalid-feedback {
  display: block;
}

.form-control.is-invalid:focus {
  box-shadow: 0 0 0 0.25rem rgba(220, 53, 69, 0.25);
}

.badge {
  font-weight: 500;
}
</style>
