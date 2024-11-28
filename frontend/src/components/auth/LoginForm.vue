// frontend/src/components/auth/LoginForm.vue
<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow">
          <div class="card-header bg-primary text-white text-center py-3">
            <h4 class="mb-0">Welcome Back!</h4>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleSubmit" novalidate>
              <!-- Alert for errors -->
              <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                {{ error }}
                <button type="button" class="btn-close" @click="error = ''"></button>
              </div>

              <!-- Username Field -->
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" id="username" v-model="form.username"
                  :class="['form-control', { 'is-invalid': v$.form.username.$error }]" :disabled="isLoading"
                  @input="v$.form.username.$touch()" />
                <div class="invalid-feedback">
                  {{ v$.form.username.$errors[0]?.$message }}
                </div>
              </div>

              <!-- Password Field -->
              <div class="mb-4">
                <label for="password" class="form-label">Password</label>
                <div class="input-group">
                  <input :type="showPassword ? 'text' : 'password'" id="password" v-model="form.password"
                    :class="['form-control', { 'is-invalid': v$.form.password.$error }]" :disabled="isLoading"
                    @input="v$.form.password.$touch()" />
                  <button class="btn btn-outline-secondary" type="button" @click="togglePassword">
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                  <div class="invalid-feedback">
                    {{ v$.form.password.$errors[0]?.$message }}
                  </div>
                </div>
              </div>

              <!-- Submit Button -->
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="isLoading">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-1"></span>
                  {{ isLoading ? 'Signing in...' : 'Sign In' }}
                </button>
              </div>

              <!-- Registration Links -->
              <div class="mt-4 text-center">
                <p class="mb-2">Don't have an account? Register as:</p>
                <div class="d-flex justify-content-center gap-2">
                  <router-link to="/register/customer" class="btn btn-outline-primary btn-sm">
                    Customer
                  </router-link>
                  <router-link to="/register/professional" class="btn btn-outline-success btn-sm">
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
import { required, minLength } from '@vuelidate/validators'

export default {
  name: 'LoginForm',

  setup() {
    const store = useStore()
    const router = useRouter()
    const isLoading = ref(false)
    const error = ref('')
    const showPassword = ref(false)

    const form = reactive({
      username: '',
      password: ''
    })

    const rules = {
      form: {
        username: { required, minLength: minLength(4) },
        password: { required, minLength: minLength(8) }
      }
    }

    const v$ = useVuelidate(rules, { form })

    const handleSubmit = async () => {
      error.value = ''

      // Validate form
      const isValid = await v$.value.$validate()
      if (!isValid) return

      isLoading.value = true

      try {
        await store.dispatch('auth/login', form)

        // Redirect based on user role
        const role = store.getters['auth/userRole']
        switch (role) {
          case 'admin':
            router.push('/admin/dashboard')
            break
          case 'professional':
            router.push('/professional/dashboard')
            break
          case 'customer':
            router.push('/customer/dashboard')
            break
          default:
            router.push('/dashboard')
        }
      } catch (err) {
        error.value = err.detail || 'An error occurred during login'
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
      error,
      showPassword,
      handleSubmit,
      togglePassword
    }
  }
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
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15);
}

.btn-outline-secondary:focus {
  box-shadow: none;
}
</style>