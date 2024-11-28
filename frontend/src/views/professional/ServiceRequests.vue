<!-- src/views/professional/ServiceRequests.vue -->
<template>
    <div class="container py-4">
        <!-- Success Alert -->
        <div v-if="showSuccessAlert" class="alert alert-success alert-dismissible fade show mb-4" role="alert">
            {{ successMessage }}
            <button type="button" class="btn-close" @click="showSuccessAlert = false"></button>
        </div>

        <!-- Stats Overview -->
        <div class="row g-4 mb-4">
            <div class="col-sm-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary bg-opacity-10 p-3 rounded">
                                <i class="bi bi-briefcase fs-4 text-primary"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Active Jobs</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.service_requests?.active || 0 }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-sm-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-success bg-opacity-10 p-3 rounded">
                                <i class="bi bi-check-circle fs-4 text-success"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Completed</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.service_requests?.completed || 0 }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-sm-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-info bg-opacity-10 p-3 rounded">
                                <i class="bi bi-star fs-4 text-info"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Rating</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">
                            {{ stats.reviews?.average_rating?.toFixed(1) || '0.0' }}
                            <small class="text-muted fs-6">/5</small>
                        </h3>
                    </div>
                </div>
            </div>

            <div class="col-sm-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-warning bg-opacity-10 p-3 rounded">
                                <i class="bi bi-bell fs-4 text-warning"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Available</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ availableRequests.length }}</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tabs -->
        <ul class="nav nav-tabs mb-4">
            <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'available' }" href="#"
                    @click.prevent="activeTab = 'available'">
                    Available Requests
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'active' }" href="#"
                    @click.prevent="activeTab = 'active'">
                    Active Jobs
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'completed' }" href="#"
                    @click.prevent="activeTab = 'completed'">
                    Completed
                </a>
            </li>
        </ul>

        <!-- Content Area -->
        <div class="card border-0 shadow-sm">
            <!-- Available Requests Tab -->
            <div v-show="activeTab === 'available'" class="card-body p-0">
                <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="availableRequests.length === 0" class="text-center py-5">
                    <i class="bi bi-inbox fs-1 text-muted"></i>
                    <p class="mt-2 mb-0">No available service requests</p>
                </div>

                <div v-else class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Customer</th>
                                <th>Location</th>
                                <th>Schedule</th>
                                <th>Description</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="request in availableRequests" :key="request.id">
                                <td>
                                    {{ request.customer.user.full_name }}
                                    <small class="text-muted d-block">
                                        {{ request.customer.user.phone }}
                                    </small>
                                </td>
                                <td>{{ request.customer.user.pin_code }}</td>
                                <td>
                                    <div>{{ formatDate(request.preferred_time) }}</div>
                                    <small class="text-muted">
                                        {{ formatTime(request.preferred_time) }}
                                    </small>
                                </td>
                                <td>
                                    <span class="text-truncate d-inline-block" style="max-width: 200px;">
                                        {{ request.description }}
                                    </span>
                                </td>
                                <td>
                                    <div class="d-flex gap-2">
                                        <button class="btn btn-sm btn-success" @click="handleAccept(request)"
                                            :disabled="accepting === request.id">
                                            <span v-if="accepting === request.id"
                                                class="spinner-border spinner-border-sm me-1">
                                            </span>
                                            Accept
                                        </button>
                                        <button class="btn btn-sm btn-outline-secondary"
                                            @click="openDetailsModal(request)">
                                            View
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Active Jobs Tab -->
            <div v-show="activeTab === 'active'" class="card-body p-0">
                <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="activeJobs.length === 0" class="text-center py-5">
                    <i class="bi bi-briefcase fs-1 text-muted"></i>
                    <p class="mt-2 mb-0">No active jobs</p>
                </div>

                <div v-else class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Customer</th>
                                <th>Service</th>
                                <th>Schedule</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="job in activeJobs" :key="job.id">
                                <td>
                                    {{ job.customer.user.full_name }}
                                    <small class="text-muted d-block">
                                        {{ job.customer.user.phone }}
                                    </small>
                                </td>
                                <td>{{ job.service.name }}</td>
                                <td>
                                    <div>{{ formatDate(job.preferred_time) }}</div>
                                    <small class="text-muted">
                                        {{ formatTime(job.preferred_time) }}
                                    </small>
                                </td>
                                <td>
                                    <span class="badge bg-primary">{{ job.status }}</span>
                                </td>
                                <td>
                                    <div class="d-flex gap-2">
                                        <button class="btn btn-sm btn-success" @click="openCompleteModal(job)">
                                            Complete
                                        </button>
                                        <button class="btn btn-sm btn-outline-secondary" @click="openDetailsModal(job)">
                                            View
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Completed Jobs Tab -->
            <div v-show="activeTab === 'completed'" class="card-body p-0">
                <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="completedJobs.length === 0" class="text-center py-5">
                    <i class="bi bi-check-circle fs-1 text-muted"></i>
                    <p class="mt-2 mb-0">No completed jobs</p>
                </div>

                <div v-else class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Customer</th>
                                <th>Service</th>
                                <th>Completed On</th>
                                <th>Review</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="job in completedJobs" :key="job.id">
                                <td>
                                    {{ job.customer.user.full_name }}
                                    <small class="text-muted d-block">
                                        {{ job.customer.user.phone }}
                                    </small>
                                </td>
                                <td>{{ job.service.name }}</td>
                                <td>
                                    {{ formatDate(job.date_of_completion) }}
                                </td>
                                <td>
                                    <div v-if="job.review" class="text-warning">
                                        <i v-for="n in 5" :key="n"
                                            :class="['bi', n <= job.review.rating ? 'bi-star-fill' : 'bi-star']">
                                        </i>
                                    </div>
                                    <span v-else class="text-muted">No review yet</span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-secondary" @click="openDetailsModal(job)">
                                        View
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Complete Job Modal -->
        <div class="modal fade" id="completeModal" tabindex="-1" ref="completeModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Complete Service</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form @submit.prevent="handleComplete">
                        <div class="modal-body">
                            <div v-if="error" class="alert alert-danger">{{ error }}</div>

                            <div class="mb-3">
                                <label class="form-label">Service Remarks</label>
                                <textarea class="form-control" v-model="completionForm.remarks" rows="3"
                                    placeholder="Describe the completed work..." required>
                                </textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-success" :disabled="completing">
                                <span v-if="completing" class="spinner-border spinner-border-sm me-2"></span>
                                {{ completing ? 'Completing...' : 'Mark as Complete' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Details Modal -->
        <div class="modal fade" id="detailsModal" tabindex="-1" ref="detailsModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Request Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" v-if="selectedRequest">
                        <div class="mb-4">
                            <h6>Service Information</h6>
                            <table class="table table-sm">
                                <tr>
                                    <th style="width: 150px">Service Type</th>
                                    <td>{{ selectedRequest.service.name }}</td>
                                </tr>
                                <tr>
                                    <th>Base Price</th>
                                    <td>₹{{ selectedRequest.service.base_price }}</td>
                                </tr>
                                <tr>
                                    <th>Status</th>
                                    <td>
                                        <span :class="[
                                            'badge',
                                            {
                                                'bg-warning': selectedRequest.status === 'created',
                                                'bg-primary': selectedRequest.status === 'assigned',
                                                'bg-success': selectedRequest.status === 'completed'
                                            }
                                        ]">
                                            {{ selectedRequest.status }}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </div>

                        <div class="mb-4">
                            <h6>Customer Information</h6>
                            <table class="table table-sm">
                                <tr>
                                    <th style="width: 150px">Name</th>
                                    <td>{{ selectedRequest.customer.user.full_name }}</td>
                                </tr>
                                <tr>
                                    <th>Phone</th>
                                    <td>{{ selectedRequest.customer.user.phone }}</td>
                                </tr>
                                <tr>
                                    <th>PIN Code</th>
                                    <td>{{ selectedRequest.customer.user.pin_code }}</td>
                                </tr>
                            </table>
                        </div>

                        <div class="mb-4">
                            <h6>Schedule</h6>
                            <table class="table table-sm">
                                <tr>
                                    <th style="width: 150px">Date</th>
                                    <td>{{ formatDate(selectedRequest.preferred_time) }}</td>
                                </tr>
                                <tr>
                                    <th>Time</th>
                                    <td>{{ formatTime(selectedRequest.preferred_time) }}</td>
                                </tr>
                                <tr>
                                    <th>Duration</th>
                                    <td>{{ selectedRequest.service.estimated_time }} minutes</td>
                                </tr>
                            </table>
                        </div>

                        <div class="mb-4">
                            <h6>Description</h6>
                            <p class="mb-0">{{ selectedRequest.description }}</p>
                        </div>

                        <div v-if="selectedRequest.status === 'completed'" class="mb-4">
                            <h6>Completion Details</h6>
                            <table class="table table-sm">
                                <tr>
                                    <th style="width: 150px">Completed On</th>
                                    <td>{{ formatDate(selectedRequest.date_of_completion) }}</td>
                                </tr>
                                <tr>
                                    <th>Remarks</th>
                                    <td>{{ selectedRequest.remarks || 'No remarks' }}</td>
                                </tr>
                            </table>
                        </div>

                        <div v-if="selectedRequest.review" class="mb-4">
                            <h6>Customer Review</h6>
                            <div class="bg-light p-3 rounded">
                                <div class="text-warning mb-2">
                                    <i v-for="n in 5" :key="n"
                                        :class="['bi', n <= selectedRequest.review.rating ? 'bi-star-fill' : 'bi-star']">
                                    </i>
                                </div>
                                <p class="mb-1">{{ selectedRequest.review.comment }}</p>
                                <small class="text-muted">
                                    Posted on {{ formatDate(selectedRequest.review.created_at) }}
                                </small>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import moment from 'moment'
import axios from 'axios'

export default {
    name: 'ServiceRequests',

    setup() {
        // State
        const loading = ref(true)
        const activeTab = ref('available')
        const requests = ref([])
        const stats = ref({})
        const error = ref('')
        const accepting = ref(null)
        const completing = ref(false)
        const selectedRequest = ref(null)
        const completeModal = ref(null)
        const detailsModal = ref(null)
        const showSuccessAlert = ref(false)
        const successMessage = ref('')

        const completionForm = ref({
            remarks: ''
        })

        // Computed properties for different request types
        const availableRequests = computed(() =>
            requests.value.filter(r => r.status === 'created')
        )

        const activeJobs = computed(() =>
            requests.value.filter(r => r.status === 'assigned')
        )

        const completedJobs = computed(() =>
            requests.value.filter(r => r.status === 'completed')
        )

        // Fetch requests from backend
        const fetchRequests = async () => {
            try {
                loading.value = true
                const [requestsResponse, statsResponse] = await Promise.all([
                    axios.get('/api/professional/requests?type=all'),
                    axios.get('/api/dashboard-stats')
                ])

                requests.value = requestsResponse.data.data
                stats.value = statsResponse.data.data
            } catch (err) {
                console.error('Error fetching requests:', err)
                error.value = 'Failed to load service requests'
            } finally {
                loading.value = false
            }
        }

        // Accept a service request
        const handleAccept = async (request) => {
            try {
                accepting.value = request.id
                await axios.post(`/api/requests/${request.id}/accept`)
                await fetchRequests()
                showSuccessAlert.value = true
                successMessage.value = 'Service request accepted successfully'
            } catch (err) {
                error.value = err.response?.data?.detail || 'Failed to accept request'
            } finally {
                accepting.value = null
            }
        }

        // Open complete modal
        const openCompleteModal = (request) => {
            selectedRequest.value = request
            completionForm.value = { remarks: '' }
            error.value = ''

            if (!completeModal.value) {
                completeModal.value = new Modal(document.getElementById('completeModal'))
            }
            completeModal.value.show()
        }

        // Open details modal
        const openDetailsModal = (request) => {
            selectedRequest.value = request

            if (!detailsModal.value) {
                detailsModal.value = new Modal(document.getElementById('detailsModal'))
            }
            detailsModal.value.show()
        }

        // Complete a service
        const handleComplete = async () => {
            if (!selectedRequest.value || !completionForm.value.remarks.trim()) return

            try {
                completing.value = true
                await axios.post(`/api/requests/${selectedRequest.value.id}/complete`, completionForm.value)
                await fetchRequests()
                completeModal.value.hide()
                showSuccessAlert.value = true
                successMessage.value = 'Service marked as completed successfully'
            } catch (err) {
                error.value = err.response?.data?.detail || 'Failed to complete service'
            } finally {
                completing.value = false
            }
        }

        // Utility functions
        const formatDate = (date) => moment(date).format('MMM D, YYYY')
        const formatTime = (date) => moment(date).format('h:mm A')

        onMounted(() => {
            fetchRequests()
        })

        return {
            loading,
            activeTab,
            stats,
            error,
            accepting,
            completing,
            selectedRequest,
            completionForm,
            showSuccessAlert,
            successMessage,
            availableRequests,
            activeJobs,
            completedJobs,
            handleAccept,
            openCompleteModal,
            openDetailsModal,
            handleComplete,
            formatDate,
            formatTime
        }
    }
}
</script>

<style scoped>
.card {
    transition: box-shadow 0.3s ease-in-out;
}

.nav-tabs .nav-link {
    color: #6c757d;
}

.nav-tabs .nav-link.active {
    color: #0d6efd;
    font-weight: 500;
}

.table> :not(:first-child) {
    border-top: none;
}
</style>