<template>
  <div class="container py-5">
    <Loading v-if="!user" />
    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <!-- Profile Card -->
        <div class="card shadow-sm">
          <div class="card-header bg-success text-white p-4">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-white text-success p-3">
                <i class="bi bi-person-badge fs-2"></i>
              </div>
              <div class="ms-3">
                <h4 class="mb-1">{{ user.full_name }}</h4>
                <p class="mb-0 opacity-75">Professional Service Provider</p>
              </div>
            </div>
          </div>

          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit" v-if="isEditing" novalidate>
              <div class="row g-4">
                <!-- Personal Information -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2">Personal Information</h5>
                  <div class="row g-3 mt-2">
                    <!-- Username (Read-only) -->
                    <div class="col-md-6">
                      <label class="form-label">Username</label>
                      <input type="text" class="form-control" :value="user.username" readonly disabled />
                    </div>

                    <!-- Email -->
                    <div class="col-md-6">
                      <label for="email" class="form-label">Email</label>
                      <input type="email" id="email" v-model="form.email"
                        :class="['form-control', { 'is-invalid': v$.form.email.$error }]"
                        @input="v$.form.email.$touch()" />
                      <div class="invalid-feedback" v-if="v$.form.email.$error">
                        {{ v$.form.email.$errors[0]?.$message }}
                      </div>
                    </div>

                    <!-- Full Name -->
                    <div class="col-md-6">
                      <label for="fullName" class="form-label">Full Name</label>
                      <input type="text" id="fullName" v-model="form.fullName"
                        :class="['form-control', { 'is-invalid': v$.form.fullName.$error }]"
                        @input="v$.form.fullName.$touch()" />
                      <div class="invalid-feedback" v-if="v$.form.fullName.$error">
                        {{ v$.form.fullName.$errors[0]?.$message }}
                      </div>
                    </div>

                    <!-- Phone -->
                    <div class="col-md-6">
                      <label for="phone" class="form-label">Phone</label>
                      <div class="input-group">
                        <span class="input-group-text">+91</span>
                        <input type="tel" id="phone" v-model="form.phone"
                          :class="['form-control', { 'is-invalid': v$.form.phone.$error }]"
                          @input="v$.form.phone.$touch()" maxlength="10" />
                      </div>
                      <div class="invalid-feedback" v-if="v$.form.phone.$error">
                        {{ v$.form.phone.$errors[0]?.$message }}
                      </div>
                    </div>

                    <!-- Address -->
                    <div class="col-12">
                      <label for="address" class="form-label">Address</label>
                      <textarea id="address" v-model="form.address"
                        :class="['form-control', { 'is-invalid': v$.form.address.$error }]"
                        @input="v$.form.address.$touch()" rows="3"></textarea>
                      <div class="invalid-feedback" v-if="v$.form.address.$error">
                        {{ v$.form.address.$errors[0]?.$message }}
                      </div>
                    </div>

                    <!-- PIN Code -->
                    <div class="col-md-6">
                      <label for="pinCode" class="form-label">PIN Code</label>
                      <input type="text" id="pinCode" v-model="form.pinCode"
                        :class="['form-control', { 'is-invalid': v$.form.pinCode.$error }]"
                        @input="v$.form.pinCode.$touch()" maxlength="6" />
                      <div class="invalid-feedback" v-if="v$.form.pinCode.$error">
                        {{ v$.form.pinCode.$errors[0]?.$message }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Professional Information -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2">Professional Information</h5>
                  <div class="row g-3 mt-2">
                    <!-- Description -->
                    <div class="col-12">
                      <label for="description" class="form-label">Professional Description</label>
                      <textarea id="description" v-model="form.description"
                        :class="['form-control', { 'is-invalid': v$.form.description.$error }]"
                        @input="v$.form.description.$touch()" rows="4"></textarea>
                      <div class="invalid-feedback" v-if="v$.form.description.$error">
                        {{ v$.form.description.$errors[0]?.$message }}
                      </div>
                    </div>

                    <!-- Service Type and Experience Years -->
                    <div class="col-md-6">
                      <label class="form-label">Service Type</label>
                      <p class="form-control-plaintext">{{ user.service_type || 'N/A' }}</p>
                      <small class="text-muted">To change service type, visit the Service section</small>
                    </div>

                    <div class="col-md-6">
                      <label class="form-label">Years of Experience</label>
                      <p class="form-control-plaintext">{{ user.experience_years || 0 }} years</p>
                    </div>
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="col-12">
                  <div class="d-flex gap-2 justify-content-end">
                    <button type="button" class="btn btn-light" @click="cancelEdit">
                      Cancel
                    </button>
                    <button type="submit" class="btn btn-success" :disabled="isLoading">
                      <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                      {{ isLoading ? 'Saving Changes...' : 'Save Changes' }}
                    </button>
                  </div>
                </div>
              </div>
            </form>

            <!-- View Mode -->
            <div v-else>
              <div class="row g-4">
                <!-- Personal Information -->
                <div class="col-12">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="border-bottom pb-2">Personal Information</h5>
                    <button class="btn btn-outline-success btn-sm" @click="startEdit">
                      <i class="bi bi-pencil me-2"></i>Edit Profile
                    </button>
                  </div>
                  <div class="row g-3">
                    <div class="col-md-6">
                      <label class="form-label text-muted">Username</label>
                      <p class="fw-medium">{{ user.username }}</p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">Email</label>
                      <p class="fw-medium">{{ user.email }}</p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">Full Name</label>
                      <p class="fw-medium">{{ user.full_name }}</p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">Phone</label>
                      <p class="fw-medium">+91 {{ user.phone }}</p>
                    </div>
                    <div class="col-12">
                      <label class="form-label text-muted">Address</label>
                      <p class="fw-medium">{{ user.address }}</p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">PIN Code</label>
                      <p class="fw-medium">{{ user.pin_code }}</p>
                    </div>
                  </div>
                </div>

                <!-- Professional Information -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2">Professional Information</h5>
                  <div class="row g-3">
                    <div class="col-12">
                      <label class="form-label text-muted">Professional Description</label>
                      <p class="fw-medium">{{ user.description }}</p>
                    </div>

                    <div class="col-md-6">
                      <label class="form-label text-muted">Service Type</label>
                      <p class="fw-medium">{{ user.service_type || 'N/A' }}</p>
                    </div>

                    <div class="col-md-6">
                      <label class="form-label text-muted">Years of Experience</label>
                      <p class="fw-medium">{{ user.experience_years }} years</p>
                    </div>

                    <div class="col-md-6">
                      <label class="form-label text-muted">Average Rating</label>
                      <p class="fw-medium">
                        <i class="bi bi-star-fill text-warning me-1"></i>
                        {{ user.average_rating.toFixed(1) || '0.0' }}/5.0
                      </p>
                    </div>

                    <div class="col-md-6">
                      <label class="form-label text-muted">Verification Status</label>
                      <p>
                        <span :class="['badge', user.is_verified ? 'bg-success' : 'bg-warning']">
                          {{ user.is_verified ? 'Verified' : 'Pending Verification' }}
                        </span>
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Account Information -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2">Account Information</h5>
                  <div class="row g-3">
                    <div class="col-md-6">
                      <label class="form-label text-muted">Account Status</label>
                      <p>
                        <span class="badge bg-success">Active</span>
                      </p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">Last Login</label>
                      <p class="fw-medium">{{ formatDate(user.last_login) }}</p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">Account Created</label>
                      <p class="fw-medium">{{ formatDate(user.created_at) }}</p>
                    </div>
                  </div>
                </div>

                <!-- Security Actions -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2">Security</h5>
                  <div class="row g-3">
                    <div class="col-md-6">
                      <button class="btn btn-outline-success" @click="showPasswordModal">
                        <i class="bi bi-key me-2"></i>Change Password
                      </button>
                    </div>
                    <div class="col-md-6">
                      <button class="btn btn-outline-danger" @click="showDeleteModal">
                        <i class="bi bi-trash me-2"></i>Delete Account
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Password Change Modal -->
    <div class="modal fade" ref="passwordModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Change Password</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="handlePasswordChange">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Current Password</label>
                <input type="password" v-model="passwordForm.oldPassword"
                  :class="['form-control', { 'is-invalid': passwordError }]" required />
                <div class="invalid-feedback" v-if="passwordError">
                  {{ passwordError }}
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">New Password</label>
                <input type="password" v-model="passwordForm.newPassword"
                  :class="['form-control', { 'is-invalid': newPasswordError }]" required />
                <div class="invalid-feedback" v-if="newPasswordError">
                  {{ newPasswordError }}
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Confirm New Password</label>
                <input type="password" v-model="passwordForm.confirmPassword"
                  :class="['form-control', { 'is-invalid': confirmPasswordError }]" required />
                <div class="invalid-feedback" v-if="confirmPasswordError">
                  {{ confirmPasswordError }}
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-success" :disabled="passwordLoading">
                <span v-if="passwordLoading" class="spinner-border spinner-border-sm me-2"></span>
                {{ passwordLoading ? 'Changing...' : 'Change Password' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Account Modal -->
    <div class="modal fade" ref="deleteModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-danger">Delete Account</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="handleDeleteAccount">
            <div class="modal-body">
              <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>
                This action cannot be undone. All your data, including service history and reviews,
                will be permanently deleted.
              </div>
              <div class="mb-3">
                <label class="form-label">Enter your password to confirm</label>
                <input type="password" v-model="deleteForm.password"
                  :class="['form-control', { 'is-invalid': deleteError }]" required />
                <div class="invalid-feedback" v-if="deleteError">
                  {{ deleteError }}
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-danger" :disabled="deleteLoading">
                <span v-if="deleteLoading" class="spinner-border spinner-border-sm me-2"></span>
                {{ deleteLoading ? 'Deleting...' : 'Delete Account' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useVuelidate } from '@vuelidate/core'

import { required, email, minLength, maxLength, helpers } from '@vuelidate/validators'

import moment from 'moment'
import * as bootstrap from 'bootstrap'


export default {
  name: 'ProfessionalProfile',

  setup() {
    const store = useStore()
    const router = useRouter()
    const user = computed(() => store.getters['auth/currentUser'])

    // Modals
    const passwordModal = ref(null)
    const deleteModal = ref(null)
    let bsPasswordModal = null
    let bsDeleteModal = null

    // Form States
    const isEditing = ref(false)
    const isLoading = ref(true)
    const passwordLoading = ref(false)
    const deleteLoading = ref(false)

    // Error States
    const passwordError = ref('')
    const newPasswordError = ref('')
    const confirmPasswordError = ref('')
    const deleteError = ref('')

    // Edit Profile Form
    const form = reactive({
      email: '',
      fullName: '',
      phone: '',
      address: '',
      pinCode: '',
      description: ''
    })

    // Password Change Form
    const passwordForm = reactive({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    // Delete Account Form
    const deleteForm = reactive({
      password: ''
    })
    const phoneValidator = helpers.regex(/^[1-9]\d{9}$/)
    const pincodeValidator = helpers.regex(/^[1-9]\d{5}$/)
    const nameValidator = helpers.regex(/^[a-zA-Z\s.-]+$/)
    const usernameValidator = helpers.regex(/^[a-zA-Z0-9_]+$/)

    // Custom validators
    const createCustomValidator = (message, validator) => helpers.withMessage(message, validator)

    // Validation rules
    const rules = {
      form: {
        username: {
          required: createCustomValidator('Username is required', required),
          minLength: createCustomValidator('Username must be at least 4 characters', minLength(4)),
          alphaNum: createCustomValidator(
            'Username can only contain letters, numbers, and underscores',
            usernameValidator
          )
        },
        email: {
          required: createCustomValidator('Email is required', required),
          email: createCustomValidator('Please enter a valid email address', email)
        },
        fullName: {
          required: createCustomValidator('Full name is required', required),
          minLength: createCustomValidator('Full name must be at least 4 characters', minLength(4)),
          validName: createCustomValidator('Please enter a valid name', nameValidator)
        },
        phone: {
          required: createCustomValidator('Phone number is required', required),
          validPhone: createCustomValidator(
            'Please enter a valid 10-digit phone number',
            phoneValidator
          )
        },
        pinCode: {
          required: createCustomValidator('PIN code is required', required),
          validPin: createCustomValidator(
            'Please enter a valid 6-digit PIN code',
            pincodeValidator
          )
        },
        address: {
          required: createCustomValidator('Address is required', required),
          minLength: createCustomValidator('Address is too short', minLength(10)),
          maxLength: createCustomValidator('Address is too long', maxLength(200))
        },
        description: {
          required: createCustomValidator('Professional description is required', required),
          minLength: createCustomValidator('Description must be at least 10 characters', minLength(10)),
          maxLength: createCustomValidator('Description cannot exceed 1000 characters', maxLength(1000))
        },
        serviceTypeId: {
          required: createCustomValidator('Please select a service type', required)
        },
        experienceYears: {
          required: createCustomValidator('Years of experience is required', required),
          validExperience: createCustomValidator(
            'Experience must be between 0 and 50 years',
            value => !isNaN(value) && value >= 0 && value <= 50
          )
        },
        password: {
          required: createCustomValidator('Password is required', required),
          minLength: createCustomValidator('Password must be at least 8 characters', minLength(8)),
          strongPassword: createCustomValidator(
            'Password must include uppercase, lowercase, number, and special character',
            helpers.regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/)
          )
        },
        confirmPassword: {
          required: createCustomValidator('Please confirm your password', required),
          sameAsPassword: createCustomValidator(
            'Passwords must match',
            (value, formData) => value === formData.password
          )
        },
        verificationDocument: {
          required: createCustomValidator('Please upload verification documents', required),
          validFile: createCustomValidator(
            'Please upload a valid file (PDF, JPG, or PNG under 5MB)',
            value => {
              if (!value) return true
              const validTypes = ['application/pdf', 'image/jpeg', 'image/png']
              return validTypes.includes(value.type) && value.size <= 5 * 1024 * 1024
            }
          )
        },
        termsAccepted: {
          required: createCustomValidator('You must accept the terms and conditions', value => value === true)
        }
      }
    }

    const v$ = useVuelidate(rules, { form })

    // Setup modals
    onMounted(() => {
      if (passwordModal.value) {
        bsPasswordModal = new bootstrap.Modal(passwordModal.value)
      }
      if (deleteModal.value) {
        bsDeleteModal = new bootstrap.Modal(deleteModal.value)
      }
    })

    // Helpers
    const formatDate = (date) => {
      return date ? moment(date).format('MMM DD, YYYY hh:mm A') : 'N/A'
    }

    const resetForms = () => {
      Object.assign(passwordForm, {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      })
      passwordError.value = ''
      newPasswordError.value = ''
      confirmPasswordError.value = ''
    }

    // Actions
    const startEdit = () => {
      form.email = user.value.email
      form.fullName = user.value.full_name
      form.phone = user.value.phone
      form.address = user.value.address
      form.pinCode = user.value.pin_code
      form.description = user.value.description || ''
      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
      v$.value.$reset()
    }

    const handleSubmit = async () => {
      const isValid = await v$.value.$validate()
      if (!isValid) return

      isLoading.value = true
      try {
        await store.dispatch('auth/updateProfile', {
          email: form.email,
          fullName: form.fullName,
          phone: form.phone,
          address: form.address,
          pinCode: form.pinCode,
          description: form.description
        })

        window.showToast({
          type: 'success',
          title: 'Profile Updated',
          message: 'Your profile has been updated successfully.'
        })

        isEditing.value = false
      } catch (error) {
        window.showToast({
          type: 'error',
          title: 'Update Failed',
          message: error.response?.data?.message || 'Failed to update profile.'
        })
      } finally {
        isLoading.value = false
      }
    }

    const showPasswordModal = () => {
      resetForms()
      bsPasswordModal.show()
    }


    const handlePasswordChange = async () => {
      try {
        // Validate passwords match
        if (passwordForm.newPassword !== passwordForm.confirmPassword) {
          confirmPasswordError.value = 'Passwords do not match'
          return
        }

        passwordLoading.value = true
        await store.dispatch('auth/changePassword', {
          oldPassword: passwordForm.oldPassword,
          newPassword: passwordForm.newPassword
        })

        bsPasswordModal.hide()
        window.showToast({
          type: 'success',
          title: 'Success',
          message: 'Password changed successfully'
        })
        resetForms()
        router.push('/login')

      } catch (error) {
        passwordError.value = error.response?.data?.message || 'Failed to change password'
      } finally {
        passwordLoading.value = false
      }
    }

    const showDeleteModal = () => {
      resetForms()
      bsDeleteModal.show()
    }

    const handleDeleteAccount = async () => {
      deleteLoading.value = true
      try {
        await store.dispatch('auth/deleteAccount', {
          password: deleteForm.password
        })


        window.showToast({
          type: 'success',
          title: 'Account Deleted',
          message: 'Your account has been deleted successfully.'
        })

        router.push('/login')
      } catch (error) {
        deleteError.value = error.response?.data?.message || 'Failed to delete account.'
      } finally {
        deleteLoading.value = false
      }
    }

    return {
      user,
      form,
      v$,
      isEditing,
      isLoading,
      passwordModal,
      deleteModal,
      passwordForm,
      deleteForm,
      passwordError,
      newPasswordError,
      confirmPasswordError,
      deleteError,
      passwordLoading,
      deleteLoading,
      formatDate,
      startEdit,
      cancelEdit,
      handleSubmit,
      showPasswordModal,
      handlePasswordChange,
      showDeleteModal,
      handleDeleteAccount
    }
  }
}
</script>

<style scoped>
.form-label {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.card {
  border: none;
  border-radius: 10px;
}

.card-header {
  border-radius: 10px 10px 0 0 !important;
}

.form-control:focus,
.form-check-input:focus {
  border-color: var(--bs-success);
  box-shadow: 0 0 0 0.25rem rgba(var(--bs-success-rgb), 0.15);
}

.form-control-plaintext {
  font-weight: 500;
  margin-bottom: 0;
}

.invalid-feedback {
  display: block;
}

@media (max-width: 768px) {
  .card-body {
    padding: 1.5rem !important;
  }
}
</style>
