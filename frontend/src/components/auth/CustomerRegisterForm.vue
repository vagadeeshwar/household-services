// frontend/src/components/auth/CustomerRegisterForm.vue
<template>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <!-- Main form content remains the same until the end -->
            <div class="col-md-8 col-lg-6">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white text-center py-3">
                        <h4 class="mb-0">Customer Registration</h4>
                    </div>
                    <div class="card-body p-4">
                        <!-- Alert for errors -->
                        <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                            {{ error }}
                            <button type="button" class="btn-close" @click="error = ''"></button>
                        </div>

                        <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
                            <div class="row g-3">
                                <!-- Username -->
                                <div class="col-12">
                                    <label for="username" class="form-label">Username</label>
                                    <input type="text" id="username" v-model="form.username"
                                        :class="['form-control', { 'is-invalid': v$.form.username.$error }]"
                                        :disabled="isLoading" @input="v$.form.username.$touch()" />
                                    <div class="invalid-feedback">
                                        {{ v$.form.username.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- Email -->
                                <div class="col-12">
                                    <label for="email" class="form-label">Email</label>
                                    <input type="email" id="email" v-model="form.email"
                                        :class="['form-control', { 'is-invalid': v$.form.email.$error }]"
                                        :disabled="isLoading" @input="v$.form.email.$touch()" />
                                    <div class="invalid-feedback">
                                        {{ v$.form.email.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- Full Name -->
                                <div class="col-12">
                                    <label for="fullName" class="form-label">Full Name</label>
                                    <input type="text" id="fullName" v-model="form.full_name"
                                        :class="['form-control', { 'is-invalid': v$.form.full_name.$error }]"
                                        :disabled="isLoading" @input="v$.form.full_name.$touch()" />
                                    <div class="invalid-feedback">
                                        {{ v$.form.full_name.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- Phone -->
                                <div class="col-md-6">
                                    <label for="phone" class="form-label">Phone Number</label>
                                    <input type="tel" id="phone" v-model="form.phone"
                                        :class="['form-control', { 'is-invalid': v$.form.phone.$error }]"
                                        :disabled="isLoading" @input="v$.form.phone.$touch()" />
                                    <div class="invalid-feedback">
                                        {{ v$.form.phone.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- PIN Code -->
                                <div class="col-md-6">
                                    <label for="pinCode" class="form-label">PIN Code</label>
                                    <input type="text" id="pinCode" v-model="form.pin_code"
                                        :class="['form-control', { 'is-invalid': v$.form.pin_code.$error }]"
                                        :disabled="isLoading" @input="v$.form.pin_code.$touch()" />
                                    <div class="invalid-feedback">
                                        {{ v$.form.pin_code.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- Address -->
                                <div class="col-12">
                                    <label for="address" class="form-label">Address</label>
                                    <textarea id="address" v-model="form.address"
                                        :class="['form-control', { 'is-invalid': v$.form.address.$error }]"
                                        :disabled="isLoading" @input="v$.form.address.$touch()" rows="3"></textarea>
                                    <div class="invalid-feedback">
                                        {{ v$.form.address.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- Password -->
                                <div class="col-md-6">
                                    <label for="password" class="form-label">Password</label>
                                    <div class="input-group">
                                        <input :type="showPassword ? 'text' : 'password'" id="password"
                                            v-model="form.password"
                                            :class="['form-control', { 'is-invalid': v$.form.password.$error }]"
                                            :disabled="isLoading" @input="v$.form.password.$touch()" />
                                        <button class="btn btn-outline-secondary" type="button" @click="togglePassword">
                                            <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                                        </button>
                                        <div class="invalid-feedback">
                                            {{ v$.form.password.$errors[0]?.$message }}
                                        </div>
                                    </div>
                                </div>

                                <!-- Confirm Password -->
                                <div class="col-md-6">
                                    <label for="confirmPassword" class="form-label">Confirm Password</label>
                                    <input type="password" id="confirmPassword" v-model="form.confirm_password"
                                        :class="['form-control', { 'is-invalid': v$.form.confirm_password.$error }]"
                                        :disabled="isLoading" @input="v$.form.confirm_password.$touch()" />
                                    <div class="invalid-feedback">
                                        {{ v$.form.confirm_password.$errors[0]?.$message }}
                                    </div>
                                </div>
                                <!-- Submit Button -->
                                <div class="col-12">
                                    <div class="d-grid gap-2">
                                        <button type="submit" class="btn btn-primary" :disabled="isLoading">
                                            <span v-if="isLoading" class="spinner-border spinner-border-sm me-1"></span>
                                            {{ isLoading ? 'Creating Account...' : 'Create Account' }}
                                        </button>
                                    </div>
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
        <FormNavigationGuard v-if="shouldShowNavigationGuard" :is-dirty="isFormDirty"
            @proceed="handleNavigationConfirm" />
    </div>
    <ConfirmDialog id="navigationConfirmDialog" title="Unsaved Changes"
        message="You have unsaved changes. Are you sure you want to leave?" type="warning" confirm-text="Leave"
        cancel-text="Stay" @confirm="handleNavigationConfirm" />
</template>
<script>
import { ref, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useVuelidate } from '@vuelidate/core'
import { required, email, minLength, helpers } from '@vuelidate/validators'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import { useFormNavigation } from '@/mixins/formNavigation'

export default {
    name: 'CustomerRegisterForm',
    components: {
        ConfirmDialog
    },
    setup() {
        const store = useStore()
        const router = useRouter()
        const isLoading = ref(false)
        const error = ref('')
        const showPassword = ref(false)
        const isRegistered = ref(false)

        const initialForm = {
            username: '',
            email: '',
            full_name: '',
            phone: '',
            pin_code: '',
            address: '',
            password: '',
            confirm_password: ''
        }

        const form = reactive({ ...initialForm })

        const isFormDirty = computed(() => {
            return Object.keys(form).some(key => form[key] !== initialForm[key])
        })

        const shouldShowNavigationGuard = computed(() => {
            return isFormDirty.value && !isRegistered.value
        })

        const resetForm = () => {
            Object.keys(form).forEach(key => {
                form[key] = initialForm[key]
            })
        }

        // Use the form navigation mixin
        const handleNavigationConfirm = () => {
            resetForm()
            hideModal()
            // Let the router continue with navigation
            router.push(router.currentRoute.value.query.redirect || '/login')
        }

        const hideModal = () => {
            if (!modalInstance.value) {
                modalInstance.value = Modal.getInstance(document.getElementById('navigationConfirmDialog'))
            }
            if (modalInstance.value) {
                modalInstance.value.hide()
                // Clean up backdrop
                const backdrop = document.querySelector('.modal-backdrop')
                if (backdrop) {
                    backdrop.remove()
                }
                document.body.classList.remove('modal-open')
                document.body.style.removeProperty('padding-right')
            }
        }

        const rules = {
            form: {
                username: {
                    required,
                    minLength: minLength(4),
                    alphaNum: helpers.regex(/^[a-zA-Z0-9_.-]+$/),
                },
                email: {
                    required,
                    email,
                },
                full_name: {
                    required,
                    minLength: minLength(4),
                    validName: helpers.regex(/^[a-zA-Z\s.-]+$/),
                },
                phone: {
                    required,
                    validPhone: helpers.regex(/^[1-9]\d{9}$/),

                },
                pin_code: {
                    required,
                    validPin: helpers.regex(/^[1-9][0-9]{5}$/),
                },
                address: {
                    required,
                    minLength: minLength(5),
                    maxLength: helpers.withMessage(
                        'Address cannot exceed 200 characters',
                        value => value.length <= 200
                    ),
                },
                password: {
                    required,
                    minLength: minLength(8),
                    hasUppercase: helpers.regex(/[A-Z]/),
                    hasLowercase: helpers.regex(/[a-z]/),
                    hasNumber: helpers.regex(/\d/),
                    hasSpecial: helpers.regex(/[!@#$%^&*(),.?":{}|<>]/),
                },
                confirm_password: {
                    required,
                    sameAsPassword: helpers.withMessage(
                        'Passwords must match',
                        value => value === form.password
                    )
                }
            }
        }

        const v$ = useVuelidate(rules, { form })

        const handleSubmit = async () => {
            error.value = ''

            const isValid = await v$.value.$validate()
            if (!isValid) return

            isLoading.value = true

            try {
                const { confirm_password, ...formData } = form
                await store.dispatch('auth/register', {
                    role: 'customer',
                    data: formData
                })

                // Set registration success flag
                isRegistered.value = true

                window.showToast({
                    type: 'success',
                    title: 'Registration Successful',
                    message: 'Your account has been created successfully. Please login to continue.'
                })

                router.push({
                    path: '/login',
                    query: { registered: 'true' }
                })
            } catch (err) {
                error.value = err.detail || 'An error occurred during registration'
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
            isFormDirty,
            isRegistered,
            shouldShowNavigationGuard,
            handleSubmit,
            handleNavigationConfirm,
            togglePassword
        }
    }
}
</script>