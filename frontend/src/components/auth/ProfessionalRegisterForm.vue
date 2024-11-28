// frontend/src/components/auth/ProfessionalRegisterForm.vue
<template>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="card shadow">
                    <div class="card-header bg-success text-white text-center py-3">
                        <h4 class="mb-0">Professional Registration</h4>
                    </div>
                    <div class="card-body p-4">
                        <!-- Alert for errors -->
                        <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                            {{ error }}
                            <button type="button" class="btn-close" @click="error = ''"></button>
                        </div>

                        <!-- Registration Form -->
                        <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
                            <div class="row g-3">
                                <!-- Basic Information Section -->
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2">Basic Information</h5>
                                </div>

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

                                <!-- Contact Section -->
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2 mt-2">Contact Details</h5>
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

                                <!-- Professional Details Section -->
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2 mt-2">Professional Details</h5>
                                </div>

                                <!-- Service Type -->
                                <div class="col-md-6">
                                    <label for="serviceType" class="form-label">Service Type</label>
                                    <select id="serviceType" v-model="form.service_type_id"
                                        :class="['form-select', { 'is-invalid': v$.form.service_type_id.$error }]"
                                        :disabled="isLoading" @change="v$.form.service_type_id.$touch()">
                                        <option value="">Select a service</option>
                                        <option v-for="service in services" :key="service.id" :value="service.id">
                                            {{ service.name }}
                                        </option>
                                    </select>
                                    <div class="invalid-feedback">
                                        {{ v$.form.service_type_id.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- Experience Years -->
                                <div class="col-md-6">
                                    <label for="experience" class="form-label">Years of Experience</label>
                                    <input type="number" id="experience" v-model="form.experience_years"
                                        :class="['form-control', { 'is-invalid': v$.form.experience_years.$error }]"
                                        :disabled="isLoading" min="0" max="50"
                                        @input="v$.form.experience_years.$touch()" />
                                    <div class="invalid-feedback">
                                        {{ v$.form.experience_years.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- Description -->
                                <div class="col-12">
                                    <label for="description" class="form-label">Professional Description</label>
                                    <textarea id="description" v-model="form.description"
                                        :class="['form-control', { 'is-invalid': v$.form.description.$error }]"
                                        :disabled="isLoading" @input="v$.form.description.$touch()" rows="4"
                                        placeholder="Describe your experience, skills, and expertise..."></textarea>
                                    <div class="invalid-feedback">
                                        {{ v$.form.description.$errors[0]?.$message }}
                                    </div>
                                </div>

                                <!-- Verification Document -->
                                <div class="col-12">
                                    <label for="verificationDoc" class="form-label">
                                        Verification Documents
                                        <small class="text-muted">(PDF, JPG, PNG - Max 5MB)</small>
                                    </label>
                                    <input type="file" id="verificationDoc"
                                        :class="['form-control', { 'is-invalid': v$.form.verification_document.$error }]"
                                        :disabled="isLoading" @change="handleFileChange"
                                        accept=".pdf,.jpg,.jpeg,.png" />
                                    <div class="invalid-feedback">
                                        {{ v$.form.verification_document.$errors[0]?.$message }}
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
                                        <button type="submit" class="btn btn-success" :disabled="isLoading">
                                            <span v-if="isLoading" class="spinner-border spinner-border-sm me-1"></span>
                                            {{ isLoading ? 'Creating Account...' : 'Create Professional Account' }}
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
    </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useVuelidate } from '@vuelidate/core'
import { required, email, minLength, sameAs, helpers, numeric, between } from '@vuelidate/validators'
import axios from 'axios'

export default {
    name: 'ProfessionalRegisterForm',

    setup() {
        const store = useStore()
        const router = useRouter()
        const isLoading = ref(false)
        const error = ref('')
        const showPassword = ref(false)
        const services = ref([])

        const form = reactive({
            username: '',
            email: '',
            full_name: '',
            phone: '',
            pin_code: '',
            address: '',
            service_type_id: '',
            experience_years: '',
            description: '',
            verification_document: null,
            password: '',
            confirm_password: ''
        })

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
                service_type_id: {
                    required: helpers.withMessage('Please select a service type', required),
                },
                experience_years: {
                    required,
                    numeric,
                    between: between(0, 50),
                },
                description: {
                    required,
                    minLength: helpers.withMessage(
                        'Description must be at least 10 characters long',
                        minLength(10)
                    ),
                    maxLength: helpers.withMessage(
                        'Description cannot exceed 1000 characters',
                        value => value.length <= 1000
                    ),
                },
                verification_document: {
                    required: helpers.withMessage('Please upload verification documents', required),
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
                    sameAsPassword: sameAs('password'),
                }
            }
        }

        const v$ = useVuelidate(rules, { form })

        // Fetch available services when component mounts
        onMounted(async () => {
            try {
                const response = await axios.get('/api/services')
                services.value = response.data.data
            } catch (err) {
                error.value = 'Failed to load available services'
            }
        })

        const handleFileChange = (event) => {
            const file = event.target.files[0]
            if (file) {
                // Validate file type
                const validTypes = ['image/jpeg', 'image/png', 'application/pdf']
                if (!validTypes.includes(file.type)) {
                    error.value = 'Invalid file type. Please upload PDF, JPG, or PNG files only.'
                    event.target.value = ''
                    return
                }

                // Validate file size (5MB max)
                if (file.size > 5 * 1024 * 1024) {
                    error.value = 'File size too large. Maximum size is 5MB.'
                    event.target.value = ''
                    return
                }

                form.verification_document = file
            }
        }

        const handleSubmit = async () => {
            error.value = ''

            // Validate form
            const isValid = await v$.value.$validate()
            if (!isValid) return

            isLoading.value = true

            try {
                // Create FormData for multipart/form-data submission
                const formData = new FormData()

                // Append all form fields except confirm_password
                Object.keys(form).forEach(key => {
                    if (key !== 'confirm_password') {
                        formData.append(key, form[key])
                    }
                })

                await axios.post('/api/register/professional', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                })

                // Show success message and redirect to login
                router.push({
                    path: '/login',
                    query: {
                        registered: 'true',
                        type: 'professional'
                    }
                })
            } catch (err) {
                error.value = err.response?.data?.detail || 'An error occurred during registration'
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
            services,
            handleSubmit,
            handleFileChange,
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
    border-color: #198754;
    box-shadow: 0 0 0 0.25rem rgba(25, 135, 84, 0.15);
}

.btn-outline-secondary:focus {
    box-shadow: none;
}

h5 {
    color: #198754;
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

.form-text {
    font-size: 0.875rem;
}
</style>