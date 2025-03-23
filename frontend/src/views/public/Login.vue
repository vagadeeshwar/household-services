<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white text-center py-3">
            <h4 class="mb-0">Welcome Back!</h4>
            <p class="text-light mb-0 small">Sign in to your account</p>
          </div>

          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit" novalidate>
              <!-- Username Field -->
              <div class="mb-3">
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
              </div>

              <!-- Password Field -->
              <div class="mb-4">
                <label for="password" class="form-label">Password</label>
                <div class="input-group">
                  <input
                    autocomplete="current-password"
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

              <!-- Submit Button -->
              <div class="d-grid gap-2 mb-4">
                <button type="submit" class="btn btn-primary" :disabled="isLoading || v$.$invalid">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isLoading ? 'Signing in...' : 'Sign In' }}
                </button>
              </div>

              <!-- Registration Links -->
              <div class="text-center">
                <p class="mb-2">Don't have an account? Register as:</p>
                <div class="d-flex justify-content-center gap-2">
                  <router-link to="/register/customer" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-person me-1"></i>
                    Customer
                  </router-link>
                  <router-link to="/register/professional" class="btn btn-outline-success btn-sm">
                    <i class="bi bi-tools me-1"></i>
                    Professional
                  </router-link>
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
import { required, helpers } from '@vuelidate/validators'

export default {
  name: 'LoginForm',

  setup() {
    const store = useStore()
    const router = useRouter()

    const form = reactive({
      username: '',
      password: '',
    })

    const isLoading = ref(false)
    const showPassword = ref(false)

    // Validation rules
    const rules = {
      form: {
        username: {
          required: helpers.withMessage('Username is required', required),
        },
        password: {
          required: helpers.withMessage('Password is required', required),
        },
      },
    }

    const v$ = useVuelidate(rules, { form })

    const handleSubmit = async () => {
      try {
        const isValid = await v$.value.$validate()
        if (!isValid) return

        isLoading.value = true

        await store.dispatch('auth/login', {
          data: {
            username: form.username.trim(),
            password: form.password,
          },
        })

        const user = store.getters['auth/currentUser']

        window.showToast({
          type: 'success',
          title: `Welcome back, ${user.full_name}!`,
        })

        // Navigate based on user role
        const roleRoutes = {
          admin: '/admin/dashboard',
          professional: '/professional/dashboard',
          customer: '/customer/dashboard',
        }

        const defaultRoute = roleRoutes[user.role]
        if (!defaultRoute) {
          throw new Error('Invalid user role')
        }

        await router.replace(defaultRoute)
      } catch (error) {
        handleLoginError(error)
      } finally {
        isLoading.value = false
      }
    }

    const handleLoginError = (error) => {
      let errorTitle = 'Login failed. Please check your credentials.'

      // Handle errors based on error_type from the API response
      if (error.response?.data) {
        const { error_type, detail } = error.response.data

        // Use the backend error message if available
        if (detail) {
          errorTitle = detail
        }

        // Enhanced error handling based on error_type
        if (error_type) {
          switch (error_type) {
            case 'InvalidCredentials':
              errorTitle = 'Username or password is incorrect. Please try again.'
              break
            case 'InactiveAccount':
              errorTitle =
                'Your account has been deactivated. Please contact support for assistance.'
              break
            case 'UnverifiedProfessional':
              errorTitle =
                'Your professional account is pending verification. Please wait for admin approval or contact support.'
              break
            case 'DatabaseError':
              errorTitle = 'A system error occurred. Please try again later or contact support.'
              break
            default:
              // Keep the error message from the detail if no specific handling
              break
          }
        }
      } else if (error.message === 'Invalid user role') {
        errorTitle = 'Account Error'
        errorTitle = 'Invalid account type. Please contact support.'
      } else if (error.message) {
        // If it's a JavaScript error with message
        errorTitle = error.message
      }

      window.showToast({
        type: 'error',
        title: errorTitle,
      })
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

.form-control:focus {
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.25rem rgba(var(--bs-primary-rgb), 0.15);
}

.btn-outline-secondary:focus {
  box-shadow: none;
}

.invalid-feedback {
  display: block;
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
