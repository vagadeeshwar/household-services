<template>
  <div class="container py-5">
    <FormNavigationGuard :when="Object.keys(form).some((key) => form[key] !== initialForm[key])" />
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white text-center py-3">
            <h4 class="mb-0">Create Customer Account</h4>
            <p class="text-light mb-0 small">Join our community to access household services</p>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit" novalidate>
              <div class="row g-3">
                <!-- Account Information -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2">Account Information</h5>
                </div>

                <!-- Username -->
                <div class="col-12">
                  <label for="username" class="form-label">Username</label>
                  <input
                    type="text"
                    id="username"
                    v-model="form.username"
                    :class="['form-control', { 'is-invalid': v$.form.username.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.username.$touch()"
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
                    rows="3"
                  ></textarea>
                  <div class="invalid-feedback" v-if="v$.form.address.$error">
                    {{ v$.form.address.$errors[0]?.$message }}
                  </div>
                </div>

                <!-- Password Information -->
                <div class="col-12">
                  <h5 class="border-bottom pb-2 mt-2">Security</h5>
                </div>

                <!-- Password -->
                <div class="col-md-6">
                  <label for="password" class="form-label">Password</label>
                  <div class="input-group">
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      id="password"
                      v-model="form.password"
                      :class="['form-control', { 'is-invalid': v$.form.password.$error }]"
                      :disabled="isLoading"
                      @input="v$.form.password.$touch()"
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
                    type="password"
                    id="confirmPassword"
                    v-model="form.confirmPassword"
                    :class="['form-control', { 'is-invalid': v$.form.confirmPassword.$error }]"
                    :disabled="isLoading"
                    @input="v$.form.confirmPassword.$touch()"
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
                    class="btn btn-primary w-100"
                    :disabled="isLoading || v$.$invalid"
                  >
                    <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ isLoading ? 'Creating Account...' : 'Create Account' }}
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
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useVuelidate } from '@vuelidate/core'
import { required, email, minLength, helpers, maxLength } from '@vuelidate/validators'

const initialForm = {
  username: '',
  email: '',
  fullName: '',
  phone: '',
  pinCode: '',
  address: '',
  password: '',
  confirmPassword: '',
  termsAccepted: false,
}

export default {
  name: 'CustomerRegisterForm',
  components: {},

  setup() {
    const store = useStore()
    const router = useRouter()
    const form = reactive({ ...initialForm })

    const isLoading = ref(false)
    const showPassword = ref(false)

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
          maxLength: helpers.withMessage('Full name is too long', maxLength(50)),
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

    const handleSubmit = async () => {
      const isValid = await v$.value.$validate()
      if (!isValid) return

      isLoading.value = true
      try {
        // eslint-disable-next-line no-unused-vars
        const { confirmPassword, termsAccepted, ...formData } = form
        await store.dispatch('auth/registerCustomer', formData)

        window.showToast({
          type: 'success',
          title: 'Registration Successful',
          message: 'Your account has been created successfully!',
        })

        router.push({ path: '/login', query: { registered: 'true', email: form.email } })
      } catch (error) {
        window.showToast({
          type: 'error',
          title: 'Registration Failed',
          message: error.response?.data?.message || 'Registration failed. Please try again.',
        })
      } finally {
        isLoading.value = false
      }
    }

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    return {
      form,
      v$,
      isLoading,
      showPassword,
      handleSubmit,
      togglePassword,
      initialForm,
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
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.25rem rgba(var(--bs-primary-rgb), 0.15);
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
