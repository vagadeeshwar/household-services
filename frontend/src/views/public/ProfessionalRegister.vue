<template>
  <div class="container py-5">
    <FormNavigationGuard
      :when="!submitSuccessful && Object.keys(form).some((key) => form[key] !== initialForm[key])"
    />

    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow-sm">
          <div class="card-header bg-success text-white text-center py-3">
            <h4 class="mb-0">Professional Registration</h4>
            <p class="text-light mb-0 small">Join our network of service providers</p>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
              <div class="row g-3">
                <!-- Account Information -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2">Account Information</h5>
                </div>

                <!-- Username -->
                <div class="col-12">
                  <label for="username" class="form-label">Username</label>
                  <input
                    autocomplete="username"
                    type="text"
                    id="username"
                    v-model="form.username"
                    :class="['form-control', { 'is-invalid': v$.form.username.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.username.$touch()"
                    @blur="v$.form.username.$touch()"
                  />
                  <div class="invalid-feedback" v-if="v$.form.username.$error">
                    {{ v$.form.username.$errors[0]?.$message }}
                  </div>
                  <div class="form-text">
                    Must be at least 4 characters and can contain letters, numbers, and underscores.
                  </div>
                </div>

                <!-- Email -->
                <div class="col-12">
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    id="email"
                    v-model="form.email"
                    :class="['form-control', { 'is-invalid': v$.form.email.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.email.$touch()"
                  />
                  <div class="invalid-feedback" v-if="v$.form.email.$error">
                    {{ v$.form.email.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Personal Information -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2 mt-2">Personal Information</h5>
                </div>

                <!-- Full Name -->
                <div class="col-12">
                  <label for="fullName" class="form-label">Full Name</label>
                  <input
                    type="text"
                    id="fullName"
                    v-model="form.fullName"
                    :class="['form-control', { 'is-invalid': v$.form.fullName.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.fullName.$touch()"
                    @blur="v$.form.fullName.$touch()"
                  />
                  <div class="invalid-feedback" v-if="v$.form.fullName.$error">
                    {{ v$.form.fullName.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Phone -->
                <div class="col-md-6">
                  <label for="phone" class="form-label">Phone Number</label>
                  <div class="input-group">
                    <span class="input-group-text">+91</span>
                    <input
                      type="tel"
                      id="phone"
                      v-model="form.phone"
                      :class="['form-control', { 'is-invalid': v$.form.phone.$error }]"
                      :disabled="isLoading"
                      @input="v$.form.phone.$touch()"
                      @blur="v$.form.phone.$touch()"
                      maxlength="10"
                    />
                  </div>
                  <div class="invalid-feedback" v-if="v$.form.phone.$error">
                    {{ v$.form.phone.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- PIN Code -->
                <div class="col-md-6">
                  <label for="pinCode" class="form-label">PIN Code</label>
                  <input
                    type="text"
                    id="pinCode"
                    v-model="form.pinCode"
                    :class="['form-control', { 'is-invalid': v$.form.pinCode.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.pinCode.$touch()"
                    @blur="v$.form.pinCode.$touch()"
                    maxlength="6"
                  />
                  <div class="invalid-feedback" v-if="v$.form.pinCode.$error">
                    {{ v$.form.pinCode.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Address -->
                <div class="col-12">
                  <label for="address" class="form-label">Address</label>
                  <textarea
                    id="address"
                    v-model="form.address"
                    :class="['form-control', { 'is-invalid': v$.form.address.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.address.$touch()"
                    @blur="v$.form.address.$touch()"
                    rows="3"
                  ></textarea>
                  <div class="invalid-feedback" v-if="v$.form.address.$error">
                    {{ v$.form.address.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Professional Details -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2 mt-2">Professional Details</h5>
                </div>

                <!-- Service Type -->
                <div class="col-md-6">
                  <label for="serviceType" class="form-label">Service Type</label>
                  <select
                    id="serviceType"
                    v-model="form.serviceTypeId"
                    :class="['form-select', { 'is-invalid': v$.form.serviceTypeId.$error }]"
                    :disabled="isLoading"
                    @change="v$.form.serviceTypeId.$touch()"
                  >
                    <option value="">Select a service</option>
                    <option v-for="service in services" :key="service.id" :value="service.id">
                      {{ service.name }}
                    </option>
                  </select>
                  <div class="invalid-feedback" v-if="v$.form.serviceTypeId.$error">
                    {{ v$.form.serviceTypeId.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Experience Years -->
                <div class="col-md-6">
                  <label for="experience" class="form-label">Years of Experience</label>
                  <input
                    type="number"
                    id="experience"
                    v-model="form.experienceYears"
                    :class="['form-control', { 'is-invalid': v$.form.experienceYears.$error }]"
                    :disabled="isLoading"
                    min="0"
                    max="50"
                    @input="v$.form.experienceYears.$touch()"
                    @blur="v$.form.experienceYears.$touch()"
                  />
                  <div class="invalid-feedback" v-if="v$.form.experienceYears.$error">
                    {{ v$.form.experienceYears.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Description -->
                <div class="col-12">
                  <label for="description" class="form-label">Professional Description</label>
                  <textarea
                    id="description"
                    v-model="form.description"
                    :class="['form-control', { 'is-invalid': v$.form.description.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.description.$touch()"
                    @blur="v$.form.description.$touch()"
                    rows="4"
                    placeholder="Describe your experience, skills, and expertise..."
                  ></textarea>
                  <div class="invalid-feedback" v-if="v$.form.description.$error">
                    {{ v$.form.description.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Verification Document -->
                <div class="col-12">
                  <label for="verificationDoc" class="form-label">
                    Verification Documents
                    <small class="text-muted">(PDF, JPG, PNG - Max 5MB)</small>
                  </label>
                  <input
                    type="file"
                    id="verificationDoc"
                    ref="fileInput"
                    :class="['form-control', { 'is-invalid': v$.form.verificationDocument.$error }]"
                    :disabled="isLoading"
                    @change="handleFileChange"
                    accept=".pdf,.jpg,.jpeg,.png"
                  />
                  <div class="invalid-feedback" v-if="v$.form.verificationDocument.$error">
                    {{ v$.form.verificationDocument.$errors[0]?.$message }}
                  </div>
                  <small class="form-text text-muted">
                    Please upload identification and relevant certification documents.
                  </small>
                </div>

                <!-- Password Section -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2 mt-2">Security</h5>
                </div>

                <!-- Password -->
                <div class="col-md-6">
                  <label for="password" class="form-label">Password</label>
                  <div class="input-group">
                    <input
                      autocomplete="new-password"
                      :type="showPassword ? 'text' : 'password'"
                      id="password"
                      v-model="form.password"
                      :class="['form-control', { 'is-invalid': v$.form.password.$error }]"
                      :disabled="isLoading"
                      @input="v$.form.password.$touch()"
                      @blur="v$.form.password.$touch()"
                    />
                    <button class="btn btn-outline-secondary" type="button" @click="togglePassword">
                      <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                  </div>
                  <div class="invalid-feedback" v-if="v$.form.password.$error">
                    {{ v$.form.password.$errors[0]?.$message }}
                  </div>
                </div>
                <!-- Confirm Password -->
                <div class="col-md-6">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <input
                    autocomplete="new-password"
                    type="password"
                    id="confirmPassword"
                    v-model="form.confirmPassword"
                    :class="['form-control', { 'is-invalid': v$.form.confirmPassword.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.confirmPassword.$touch()"
                    @blur="v$.form.confirmPassword.$touch()"
                  />
                  <div class="invalid-feedback" v-if="v$.form.confirmPassword.$error">
                    {{ v$.form.confirmPassword.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Terms -->
                <div class="col-12">
                  <div class="form-check">
                    <input
                      type="checkbox"
                      class="form-check-input"
                      id="terms"
                      v-model="form.termsAccepted"
                      :class="{ 'is-invalid': v$.form.termsAccepted.$error }"
                      @change="v$.form.termsAccepted.$touch()"
                    />
                    <label class="form-check-label" for="terms">
                      I agree to the
                      <router-link to="/terms" target="_blank">Terms of Service</router-link>
                      and
                      <router-link to="/privacy" target="_blank">Privacy Policy</router-link>
                    </label>
                    <div class="invalid-feedback" v-if="v$.form.termsAccepted.$error">
                      {{ v$.form.termsAccepted.$errors[0]?.$message }}
                    </div>
                  </div>
                </div>

                <!-- Submit Button -->
                <div class="col-12">
                  <button
                    type="submit"
                    class="btn btn-success w-100"
                    :disabled="isLoading || v$.$invalid"
                  >
                    <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ isLoading ? 'Creating Account...' : 'Create Professional Account' }}
                  </button>
                </div>

                <!-- Login Link -->
                <div class="col-12 text-center">
                  <p class="mb-0">
                    Already have an account?
                    <router-link to="/login">Sign in</router-link>
                  </p>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useVuelidate } from '@vuelidate/core'
import { between, email, helpers, minLength, numeric, required } from '@vuelidate/validators'
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

const initialForm = {
  username: '',
  email: '',
  fullName: '',
  phone: '',
  pinCode: '',
  address: '',
  serviceTypeId: '',
  experienceYears: '',
  description: '',
  verificationDocument: null,
  password: '',
  confirmPassword: '',
  termsAccepted: false,
}

export default {
  name: 'ProfessionalRegisterForm',
  components: {},

  setup() {
    const store = useStore()
    const router = useRouter()
    const fileInput = ref(null)
    const submitSuccessful = ref(false)

    const form = reactive({ ...initialForm })
    const services = ref([])
    const isLoading = ref(false)
    const showPassword = ref(false)

    // Validation rules
    const rules = {
      form: {
        username: {
          required: helpers.withMessage('Username is required', required),
          minLength: helpers.withMessage('Username must be at least 4 characters', minLength(4)),
          alphaNum: helpers.withMessage(
            'Username can only contain letters, numbers, and underscores',
            helpers.regex(/^[a-zA-Z0-9_]+$/),
          ),
        },
        email: {
          required: helpers.withMessage('Email is required', required),
          email: helpers.withMessage('Please enter a valid email address', email),
        },
        fullName: {
          required: helpers.withMessage('Full name is required', required),
          minLength: helpers.withMessage('Full name must be at least 4 characters', minLength(4)),
          validName: helpers.withMessage(
            'Please enter a valid name',
            helpers.regex(/^[a-zA-Z\s.-]+$/),
          ),
        },
        phone: {
          required: helpers.withMessage('Phone number is required', required),
          validPhone: helpers.withMessage(
            'Please enter a valid 10-digit phone number',
            helpers.regex(/^[1-9]\d{9}$/),
          ),
        },
        pinCode: {
          required: helpers.withMessage('PIN code is required', required),
          validPin: helpers.withMessage(
            'Please enter a valid 6-digit PIN code',
            helpers.regex(/^[1-9]\d{5}$/),
          ),
        },
        address: {
          required: helpers.withMessage('Address is required', required),
          minLength: helpers.withMessage('Address is too short', minLength(10)),
        },
        serviceTypeId: {
          required: helpers.withMessage('Please select a service type', required),
        },
        experienceYears: {
          required: helpers.withMessage('Years of experience is required', required),
          numeric: helpers.withMessage('Please enter a valid number', numeric),
          between: helpers.withMessage('Experience must be between 0 and 50 years', between(0, 50)),
        },
        description: {
          required: helpers.withMessage('Professional description is required', required),
          minLength: helpers.withMessage(
            'Description must be at least 10 characters',
            minLength(10),
          ),
          maxLength: helpers.withMessage(
            'Description cannot exceed 1000 characters',
            (value) => value.length <= 1000,
          ),
        },
        verificationDocument: {
          required: helpers.withMessage('Please upload verification documents', required),
          validFileType: helpers.withMessage(
            'Please upload PDF, JPG, or PNG files only',
            (value) => {
              if (!value) return true
              const validTypes = ['application/pdf', 'image/jpeg', 'image/png']
              return validTypes.includes(value.type)
            },
          ),
          validFileSize: helpers.withMessage('File size must be less than 5MB', (value) => {
            if (!value) return true
            return value.size <= 5 * 1024 * 1024 // 5MB
          }),
        },
        password: {
          required: helpers.withMessage('Password is required', required),
          minLength: helpers.withMessage('Password must be at least 8 characters', minLength(8)),
          strongPassword: helpers.withMessage(
            'Password must include uppercase, lowercase, number, and special character',
            helpers.regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/),
          ),
        },
        confirmPassword: {
          required: helpers.withMessage('Please confirm your password', required),
          sameAsPassword: helpers.withMessage(
            'Passwords must match',
            (value) => value === form.password,
          ),
        },
        termsAccepted: {
          required: helpers.withMessage(
            'You must accept the terms and conditions',
            (value) => value === true,
          ),
        },
      },
    }

    const v$ = useVuelidate(rules, { form })

    const handleFileChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        console.log('File selected:', file) // Debug log

        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
          window.showToast({
            type: 'error',
            title: 'Please select a file smaller than 5MB',
          })
          event.target.value = '' // Reset file input
          form.verificationDocument = null
          return
        }

        // Validate file type
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png']
        if (!allowedTypes.includes(file.type)) {
          window.showToast({
            type: 'error',
            title: 'Please select a PDF, JPG, or PNG file',
          })
          event.target.value = '' // Reset file input
          form.verificationDocument = null
          return
        }

        form.verificationDocument = file
        v$.value.form.verificationDocument.$touch()
      }
    }

    // Form submission
    const handleSubmit = async () => {
      const isValid = await v$.value.$validate()
      if (!isValid) return

      isLoading.value = true

      try {
        const data = new FormData()
        data.append('username', form.username)
        data.append('email', form.email)
        data.append('password', form.password)
        data.append('full_name', form.fullName)
        data.append('phone', form.phone)
        data.append('address', form.address)
        data.append('pin_code', form.pinCode)
        data.append('experience_years', form.experienceYears)
        data.append('description', form.description)
        data.append('service_type_id', form.serviceTypeId)

        // Append the file correctly
        if (form.verificationDocument) {
          data.append('verification_document', form.verificationDocument)
        }

        await store.dispatch('auth/registerProfessional', { data: data })
        submitSuccessful.value = true

        window.showToast({
          type: 'success',
          title: 'Your account has been created. Please wait for verification.',
        })

        router.push({
          path: '/login',
          query: {
            registered: 'true',
            type: 'professional',
            email: form.email,
          },
        })
      } catch (error) {
        window.showToast({
          type: 'error',
          title: error.response?.data?.detail || 'Registration failed. Please try again.',
        })
      } finally {
        isLoading.value = false
      }
    }

    // UI helpers
    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    // Fetch services on mount
    const fetchActiveServices = async () => {
      try {
        const response = await store.dispatch('services/fetchActiveServices')
        services.value = response.data || []
      } catch (error) {
        console.error('Error loading services:', error)
        // Only show toast if it's not the initial page load
        if (!initialLoad.value) {
          window.showToast({
            type: 'error',
            title: 'Failed to load service types. Please refresh and try again.',
          })
        }
      }
    }

    // Track if this is the initial load
    const initialLoad = ref(true)
    onMounted(() => {
      fetchActiveServices().then(() => {
        initialLoad.value = false
      })
    })

    return {
      form,
      v$,
      services,
      isLoading,
      showPassword,
      fileInput,
      handleSubmit,
      handleFileChange,
      togglePassword,
      initialForm,
      submitSuccessful,
    }
  },
}
</script>

<style scoped>
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

.btn-outline-secondary:focus {
  box-shadow: none;
}

.invalid-feedback {
  display: block;
}

.form-text {
  font-size: 0.875rem;
  color: #6c757d;
}

h5 {
  color: var(--bs-success);
  font-size: 1.1rem;
  margin-top: 0.5rem;
}

/* Form responsiveness */
@media (max-width: 576px) {
  .container {
    padding: 1rem;
  }

  .card {
    border-radius: 0;
  }

  .card-header {
    border-radius: 0 !important;
  }
}

/* Animation for validation feedback */
@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }

  25% {
    transform: translateX(-5px);
  }

  75% {
    transform: translateX(5px);
  }
}

.is-invalid {
  animation: shake 0.3s ease-in-out;
}
</style>
