# src/views/profile/ProfilePage.vue
<template>
    <div class="container py-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <!-- Profile Header -->
                <div class="card mb-4 shadow-sm">
                    <div class="card-body text-center">
                        <div class="avatar-circle mb-3">
                            <i class="bi bi-person-circle display-1 text-primary"></i>
                        </div>
                        <h4 class="mb-1">{{ profileData.full_name }}</h4>
                        <p class="text-muted mb-3">{{ profileData.role }}</p>
                        <div v-if="isProfessional" class="d-flex justify-content-center align-items-center gap-2">
                            <span :class="['badge', profileData.is_verified ? 'bg-success' : 'bg-warning']">
                                {{ profileData.is_verified ? 'Verified' : 'Pending Verification' }}
                            </span>
                            <div class="text-warning" v-if="profileData.average_rating">
                                <i class="bi bi-star-fill"></i>
                                {{ profileData.average_rating.toFixed(1) }}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Navigation Tabs -->
                <ul class="nav nav-tabs mb-4">
                    <li class="nav-item">
                        <a class="nav-link" :class="{ active: activeTab === 'profile' }" href="#"
                            @click.prevent="activeTab = 'profile'">Profile Details</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" :class="{ active: activeTab === 'security' }" href="#"
                            @click.prevent="activeTab = 'security'">Security</a>
                    </li>
                    <li class="nav-item" v-if="isProfessional">
                        <a class="nav-link" :class="{ active: activeTab === 'documents' }" href="#"
                            @click.prevent="activeTab = 'documents'">Documents</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" :class="{ active: activeTab === 'danger' }" href="#"
                            @click.prevent="activeTab = 'danger'">Danger Zone</a>
                    </li>
                </ul>

                <!-- Form Navigation Guard -->
                <FormNavigationGuard :is-dirty="formIsDirty" @proceed="handleNavigationConfirm" />

                <!-- Profile Details Form -->
                <div v-show="activeTab === 'profile'" class="card shadow-sm">
                    <div class="card-body">
                        <form @submit.prevent="handleProfileUpdate">
                            <div class="row g-3">
                                <!-- Basic Information -->
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2">Basic Information</h5>
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">Username</label>
                                    <input type="text" class="form-control" v-model="form.username" disabled>
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" v-model="form.email"
                                        :disabled="!isOwnProfile" required>
                                </div>

                                <div class="col-12">
                                    <label class="form-label">Full Name</label>
                                    <input type="text" class="form-control" v-model="form.full_name"
                                        :disabled="!isOwnProfile" required>
                                </div>

                                <!-- Contact Information -->
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2 mt-2">Contact Details</h5>
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">Phone Number</label>
                                    <input type="tel" class="form-control" v-model="form.phone"
                                        :disabled="!isOwnProfile" required>
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">PIN Code</label>
                                    <input type="text" class="form-control" v-model="form.pin_code"
                                        :disabled="!isOwnProfile" required>
                                </div>

                                <div class="col-12">
                                    <label class="form-label">Address</label>
                                    <textarea class="form-control" v-model="form.address" :disabled="!isOwnProfile"
                                        rows="3" required></textarea>
                                </div>

                                <!-- Professional Details -->
                                <template v-if="isProfessional">
                                    <div class="col-12">
                                        <h5 class="border-bottom pb-2 mt-2">Professional Details</h5>
                                    </div>

                                    <div class="col-md-6">
                                        <label class="form-label">Service Type</label>
                                        <select class="form-select" v-model="form.service_type_id"
                                            :disabled="!isOwnProfile || hasActiveRequests">
                                            <option v-for="service in services" :key="service.id" :value="service.id">
                                                {{ service.name }}
                                            </option>
                                        </select>
                                    </div>

                                    <div class="col-md-6">
                                        <label class="form-label">Years of Experience</label>
                                        <input type="number" class="form-control" v-model="form.experience_years"
                                            :disabled="!isOwnProfile">
                                    </div>

                                    <div class="col-12">
                                        <label class="form-label">Professional Description</label>
                                        <textarea class="form-control" v-model="form.description"
                                            :disabled="!isOwnProfile" rows="4"></textarea>
                                    </div>
                                </template>

                                <!-- Submit Button -->
                                <div class="col-12" v-if="isOwnProfile">
                                    <div class="d-grid gap-2">
                                        <button type="submit" class="btn btn-primary"
                                            :disabled="updating || !formIsDirty">
                                            <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
                                            {{ updating ? 'Updating...' : 'Update Profile' }}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- Security Tab -->
                <div v-show="activeTab === 'security'" class="card shadow-sm">
                    <div class="card-body">
                        <form @submit.prevent="handlePasswordChange">
                            <div class="mb-3">
                                <label class="form-label">Current Password</label>
                                <input type="password" class="form-control" v-model="passwordForm.old_password"
                                    required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">New Password</label>
                                <input type="password" class="form-control" v-model="passwordForm.new_password"
                                    required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Confirm New Password</label>
                                <input type="password" class="form-control" v-model="passwordForm.confirm_password"
                                    required>
                            </div>
                            <button type="submit" class="btn btn-primary" :disabled="changingPassword">
                                <span v-if="changingPassword" class="spinner-border spinner-border-sm me-2"></span>
                                {{ changingPassword ? 'Changing Password...' : 'Change Password' }}
                            </button>
                        </form>
                    </div>
                </div>

                <!-- Documents Tab -->
                <div v-show="activeTab === 'documents'" class="card shadow-sm">
                    <div class="card-body">
                        # src/views/profile/ProfilePage.vue (continued)
                        <form @submit.prevent="handleDocumentUpdate" enctype="multipart/form-data">
                            <div class="mb-4">
                                <h6>Current Document Status</h6>
                                <div v-if="profileData.verification_documents" class="bg-light p-3 rounded">
                                    <div class="d-flex align-items-center">
                                        <i class="bi bi-file-earmark-text fs-4 text-primary me-2"></i>
                                        <div>
                                            <p class="mb-0">Verification Document</p>
                                            <small class="text-muted">Uploaded on {{
                                                formatDate(profileData.document_upload_date)
                                            }}</small>
                                        </div>
                                        <a href="#" class="btn btn-sm btn-outline-primary ms-auto"
                                            @click.prevent="viewDocument">
                                            View Document
                                        </a>
                                    </div>
                                </div>
                                <div v-else class="alert alert-warning">
                                    <i class="bi bi-exclamation-triangle me-2"></i>
                                    No verification documents uploaded yet.
                                </div>
                            </div>

                            <div v-if="isOwnProfile" class="mb-4">
                                <h6>Update Document</h6>
                                <div class="alert alert-info mb-3">
                                    <i class="bi bi-info-circle me-2"></i>
                                    Uploading new documents will require re-verification of your account.
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">New Verification Document</label>
                                    <input type="file" class="form-control" @change="handleFileChange"
                                        accept=".pdf,.jpg,.jpeg,.png" required>
                                    <div class="form-text">Accepted formats: PDF, JPG, PNG (max 5MB)</div>
                                </div>
                                <button type="submit" class="btn btn-primary"
                                    :disabled="uploadingDocument || !selectedFile">
                                    <span v-if="uploadingDocument" class="spinner-border spinner-border-sm me-2"></span>
                                    {{ uploadingDocument ? 'Uploading...' : 'Upload Document' }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- Danger Zone Tab -->
                <div v-show="activeTab === 'danger'" class="card shadow-sm border-danger">
                    <div class="card-header bg-danger text-white">
                        <h5 class="mb-0">Danger Zone</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-warning">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            Actions in this section are irreversible. Please proceed with caution.
                        </div>

                        <div class="mb-4">
                            <h6>Delete Account</h6>
                            <p class="text-muted">Once you delete your account, there is no going back. Please be
                                certain.</p>
                            <button class="btn btn-danger" @click="showDeleteConfirm">
                                Delete Account
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Confirm Profile Update Modal -->
    <ConfirmDialog id="updateConfirmDialog" title="Confirm Profile Update"
        message="Are you sure you want to update your profile information?" type="primary" confirmText="Update"
        @confirm="confirmProfileUpdate" />

    <!-- Confirm Delete Account Modal -->
    <ConfirmDialog id="deleteConfirmDialog" title="Delete Account"
        message="This action cannot be undone. Please enter your password to confirm." type="danger"
        confirmText="Delete Forever" @confirm="confirmDeleteAccount">
        <template #body>
            <p class="mb-3">This action cannot be undone. Please enter your password to confirm.</p>
            <input type="password" class="form-control" v-model="deleteForm.password" placeholder="Enter your password">
        </template>
    </ConfirmDialog>

    <!-- View Document Modal -->
    <div class="modal fade" id="documentModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Verification Document</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <iframe :src="documentUrl" width="100%" height="600px" frameborder="0"></iframe>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import moment from 'moment'
import axios from 'axios'
import _ from 'lodash'

import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import FormNavigationGuard from '@/components/shared/FormNavigationGuard.vue'
import { useProfileManagement } from '@/composables/useProfileManagement'
import { useProfessionalProfile } from '@/composables/useProfessionalProfile'

export default {
    name: 'ProfilePage',
    components: {
        ConfirmDialog,
        FormNavigationGuard
    },

    setup() {
        const store = useStore()
        const route = useRoute()
        const router = useRouter()

        // State
        const activeTab = ref('profile')
        const profileData = ref({})
        const services = ref([])
        const loading = ref(true)
        const updating = ref(false)
        const changingPassword = ref(false)
        const uploadingDocument = ref(false)
        const selectedFile = ref(null)
        const documentUrl = ref('')

        // Form states
        const form = ref({})
        const originalForm = ref({})
        const passwordForm = ref({
            old_password: '',
            new_password: '',
            confirm_password: ''
        })
        const deleteForm = ref({
            password: ''
        })

        const {
            form,
            v$,
            formIsDirty,
            passwordForm,
            isOwnProfile,
            fetchProfile,
            updateProfile,
            changePassword,
            deleteAccount
        } = useProfileManagement()

        // Add professional features if user is professional
        const {
            verificationDoc,
            docError,
            hasActiveRequests,
            handleDocChange,
            updateDocument
        } = useProfessionalProfile()

        // Computed properties
        const isOwnProfile = computed(() => {
            return route.params.id ?
                store.getters['auth/userId'] === parseInt(route.params.id) :
                true
        })

        const isProfessional = computed(() => profileData.value.role === 'professional')

        const formIsDirty = computed(() => {
            return !_.isEqual(form.value, originalForm.value)
        })

        const hasActiveRequests = computed(() => {
            // Logic to check if professional has active requests
            return false // Implement the actual check
        })

        // Methods
        const fetchProfile = async () => {
            try {
                loading.value = true
                const response = await axios.get(route.params.id ?
                    `/api/users/${route.params.id}` : '/api/profile')
                profileData.value = response.data.data

                // Initialize form with profile data
                form.value = _.cloneDeep(profileData.value)
                originalForm.value = _.cloneDeep(profileData.value)

                if (isProfessional.value) {
                    fetchServices()
                }
            } catch (error) {
                window.showToast({
                    type: 'danger',
                    title: 'Error',
                    message: 'Failed to load profile data'
                })
            } finally {
                loading.value = false
            }
        }

        const fetchServices = async () => {
            try {
                const response = await axios.get('/api/services')
                services.value = response.data.data
            } catch (error) {
                console.error('Error fetching services:', error)
            }
        }

        const handleProfileUpdate = async () => {
            const modal = new Modal(document.getElementById('updateConfirmDialog'))
            modal.show()
        }

        const confirmProfileUpdate = async () => {
            try {
                updating.value = true
                await axios.put('/api/profile', form.value)

                originalForm.value = _.cloneDeep(form.value)
                window.showToast({
                    type: 'success',
                    title: 'Success',
                    message: 'Profile updated successfully'
                })
            } catch (error) {
                window.showToast({
                    type: 'danger',
                    title: 'Error',
                    message: error.response?.data?.message || 'Failed to update profile'
                })
            } finally {
                updating.value = false
            }
        }

        const handlePasswordChange = async () => {
            if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
                window.showToast({
                    type: 'danger',
                    title: 'Error',
                    message: 'Passwords do not match'
                })
                return
            }

            try {
                changingPassword.value = true
                await axios.post('/api/change-password', {
                    old_password: passwordForm.value.old_password,
                    new_password: passwordForm.value.new_password
                })

                passwordForm.value = {
                    old_password: '',
                    new_password: '',
                    confirm_password: ''
                }

                window.showToast({
                    type: 'success',
                    title: 'Success',
                    message: 'Password changed successfully'
                })
            } catch (error) {
                window.showToast({
                    type: 'danger',
                    title: 'Error',
                    message: error.response?.data?.message || 'Failed to change password'
                })
            } finally {
                changingPassword.value = false
            }
        }

        const handleFileChange = (event) => {
            const file = event.target.files[0]
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    window.showToast({
                        type: 'danger',
                        title: 'Error',
                        message: 'File size should not exceed 5MB'
                    })
                    event.target.value = ''
                    return
                }
                selectedFile.value = file
            }
        }

        const handleDocumentUpdate = async () => {
            if (!selectedFile.value) return

            const formData = new FormData()
            formData.append('verification_document', selectedFile.value)

            try {
                uploadingDocument.value = true
                await axios.put('/api/professionals/document', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                })

                window.showToast({
                    type: 'success',
                    title: 'Success',
                    message: 'Document uploaded successfully'
                })

                // Refresh profile data
                await fetchProfile()
            } catch (error) {
                window.showToast({
                    type: 'danger',
                    title: 'Error',
                    message: error.response?.data?.message || 'Failed to upload document'
                })
            } finally {
                uploadingDocument.value = false
                selectedFile.value = null
            }
        }

        const showDeleteConfirm = () => {
            const modal = new Modal(document.getElementById('deleteConfirmDialog'))
            modal.show()
        }

        const confirmDeleteAccount = async () => {
            try {
                await axios.delete('/api/delete-account', {
                    data: { password: deleteForm.value.password }
                })

                await store.dispatch('auth/logout')
                router.push('/login')
            } catch (error) {
                window.showToast({
                    type: 'danger',
                    title: 'Error',
                    message: error.response?.data?.message || 'Failed to delete account'
                })
            }
        }

        const viewDocument = () => {
            if (profileData.value.verification_documents) {
                documentUrl.value = `/api/static/uploads/verification_docs/${profileData.value.verification_documents}`
                const modal = new Modal(document.getElementById('documentModal'))
                modal.show()
            }
        }

        const formatDate = (date) => moment(date).format('MMMM D, YYYY')

        // Handle navigation
        const handleNavigationConfirm = () => {
            form.value = _.cloneDeep(originalForm.value)
        }

        // Lifecycle hooks
        onMounted(() => {
            fetchProfile()
        })

        return {
            activeTab,
            profileData,
            services,
            form,
            passwordForm,
            deleteForm,
            loading,
            updating,
            changingPassword,
            uploadingDocument,
            selectedFile,
            documentUrl,
            isOwnProfile,
            isProfessional,
            formIsDirty,
            hasActiveRequests,
            handleProfileUpdate,
            confirmProfileUpdate,
            handlePasswordChange,
            handleFileChange,
            handleDocumentUpdate,
            showDeleteConfirm,
            confirmDeleteAccount,
            viewDocument,
            handleNavigationConfirm,
            formatDate
        }
    }
}
</script>

<style scoped>
.avatar-circle {
    width: 100px;
    height: 100px;
    margin: 0 auto;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
}

.nav-tabs .nav-link {
    color: #6c757d;
}

.nav-tabs .nav-link.active {
    color: #0d6efd;
    font-weight: 500;
}

.form-label {
    font-weight: 500;
}

.card {
    transition: all 0.2s ease;
}

.card:hover {
    box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .15) !important;
}
</style>