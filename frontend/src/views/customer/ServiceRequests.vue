<!-- src/views/customer/ServiceRequests.vue -->
<template>
    <div class="container py-4">
        <!-- Success Alert -->
        <div v-if="showSuccessAlert" class="alert alert-success alert-dismissible fade show mb-4" role="alert">
            {{ successMessage }}
            <button type="button" class="btn-close" @click="showSuccessAlert = false"></button>
        </div>

        <!-- Stats Cards -->
        <div class="row g-4 mb-4">
            <div class="col-sm-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary bg-opacity-10 p-3 rounded">
                                <i class="bi bi-clock fs-4 text-primary"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Pending</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.pending || 0 }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-sm-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-info bg-opacity-10 p-3 rounded">
                                <i class="bi bi-person-workspace fs-4 text-info"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Assigned</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.assigned || 0 }}</h3>
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
                        <h3 class="mb-0">{{ stats.completed || 0 }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-sm-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-warning bg-opacity-10 p-3 rounded">
                                <i class="bi bi-star fs-4 text-warning"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Reviews</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.reviews || 0 }}</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Requests Table -->
        <div class="card border-0 shadow-sm">
            <div class="card-header bg-white py-3">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">My Service Requests</h5>
                    <div class="d-flex gap-2">
                        <!-- Filter Dropdown -->
                        <div class="dropdown">
                            <button class="btn btn-outline-secondary dropdown-toggle" type="button"
                                data-bs-toggle="dropdown">
                                {{ selectedFilter === 'all' ? 'All Requests' :
                                    selectedFilter === 'created' ? 'Pending' :
                                        selectedFilter === 'assigned' ? 'Assigned' : 'Completed' }}
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" @click="selectedFilter = 'all'">All Requests</a>
                                </li>
                                <li><a class="dropdown-item" href="#" @click="selectedFilter = 'created'">Pending</a>
                                </li>
                                <li><a class="dropdown-item" href="#" @click="selectedFilter = 'assigned'">Assigned</a>
                                </li>
                                <li><a class="dropdown-item" href="#"
                                        @click="selectedFilter = 'completed'">Completed</a></li>
                            </ul>
                        </div>

                        <!-- Book New Service Button -->
                        <router-link to="/services" class="btn btn-primary">
                            <i class="bi bi-plus-lg me-1"></i>
                            Book New Service
                        </router-link>
                    </div>
                </div>
            </div>

            <div class="card-body p-0">
                <!-- Loading State -->
                <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-else-if="filteredRequests.length === 0" class="text-center py-5">
                    <i class="bi bi-inbox fs-1 text-muted"></i>
                    <p class="mt-2 mb-0">No service requests found</p>
                    <router-link to="/services" class="btn btn-primary mt-3">
                        Book Your First Service
                    </router-link>
                </div>

                <!-- Requests Table -->
                <div v-else class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Service</th>
                                <th>Professional</th>
                                <th>Schedule</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="request in filteredRequests" :key="request.id">
                                <td>
                                    <div class="fw-medium">{{ request.service.name }}</div>
                                    <small class="text-muted d-block">
                                        {{ truncate(request.description, 50) }}
                                    </small>
                                </td>
                                <td>
                                    <div v-if="request.professional">
                                        {{ request.professional.user.full_name }}
                                        <div class="text-success small" v-if="request.professional.average_rating">
                                            <i class="bi bi-star-fill me-1"></i>
                                            {{ request.professional.average_rating.toFixed(1) }}
                                        </div>
                                    </div>
                                    <span v-else class="text-muted">Not assigned</span>
                                </td>
                                <td>
                                    <div>{{ formatDate(request.preferred_time) }}</div>
                                    <small class="text-muted">
                                        {{ formatTime(request.preferred_time) }}
                                    </small>
                                </td>
                                <td>
                                    <span :class="[
                                        'badge',
                                        {
                                            'bg-warning': request.status === 'created',
                                            'bg-primary': request.status === 'assigned',
                                            'bg-success': request.status === 'completed'
                                        }
                                    ]">
                                        {{ request.status }}
                                    </span>
                                </td>
                                <td>
                                    <div class="d-flex gap-2">
                                        <!-- Cancel button for pending requests -->
                                        <button v-if="request.status === 'created'"
                                            class="btn btn-sm btn-outline-danger" @click="handleCancel(request)"
                                            :disabled="cancelling === request.id">
                                            <span v-if="cancelling === request.id"
                                                class="spinner-border spinner-border-sm">
                                            </span>
                                            <span v-else>Cancel</span>
                                        </button>

                                        <!-- Review button for completed requests without review -->
                                        <button v-if="request.status === 'completed' && !request.review"
                                            class="btn btn-sm btn-outline-primary" @click="openReviewModal(request)">
                                            Add Review
                                        </button>

                                        <!-- View button for all requests -->
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
        </div>

        <!-- Review Modal -->
        <div class="modal fade" id="reviewModal" tabindex="-1" ref="reviewModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Review</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form @submit.prevent="submitReview">
                        <div class="modal-body">
                            <div v-if="error" class="alert alert-danger">{{ error }}</div>

                            <div class="mb-3">
                                <label class="form-label d-block">Rating</label>
                                <div class="btn-group" role="group">
                                    <button v-for="n in 5" :key="n" type="button" class="btn"
                                        :class="reviewForm.rating >= n ? 'btn-warning' : 'btn-outline-warning'"
                                        @click="reviewForm.rating = n">
                                        <i class="bi bi-star-fill"></i>
                                    </button>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Comment</label>
                                <textarea class="form-control" v-model="reviewForm.comment" rows="3"
                                    placeholder="Share your experience..." required>
                                </textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-primary"
                                :disabled="!reviewForm.rating || submittingReview">
                                <span v-if="submittingReview" class="spinner-border spinner-border-sm me-2"></span>
                                {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
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

                        <div v-if="selectedRequest.professional" class="mb-4">
                            <h6>Professional</h6>
                            <table class="table table-sm">
                                <tr>
                                    <th style="width: 150px">Name</th>
                                    <td>{{ selectedRequest.professional.user.full_name }}</td>
                                </tr>
                                <tr>
                                    <th>Experience</th>
                                    <td>{{ selectedRequest.professional.experience_years }} years</td>
                                </tr>
                                <tr>
                                    <th>Rating</th>
                                    <td>
                                        <div class="text-warning">
                                            <i v-for="n in 5" :key="n"
                                                :class="['bi', n <= Math.round(selectedRequest.professional.average_rating || 0) ? 'bi-star-fill' : 'bi-star']">
                                            </i>
                                            <span class="text-dark ms-1">
                                                {{ selectedRequest.professional.average_rating?.toFixed(1) || "Not rated" }} 
                                            </span>
                                        </div>
                                    </td>
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
                            <h6>Your Review</h6>
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
import { useRoute } from 'vue-router'
import moment from 'moment'
import axios from 'axios'

export default {
    name: 'ServiceRequests',

    setup() {
        const route = useRoute()
        const loading = ref(true)
        const requests = ref([])
        const stats = ref({})
        const selectedFilter = ref('all')
        const error = ref('')
        const cancelling = ref(null)
        const selectedRequest = ref(null)
        const reviewModal = ref(null)
        const detailsModal = ref(null)
        const submittingReview = ref(false)
        const showSuccessAlert = ref(false)
        const successMessage = ref('')

        // Review form state
        const reviewForm = ref({
            rating: 0,
            comment: ''
        })

        // Show success message from query params
        onMounted(() => {
            if (route.query.success === 'true') {
                showSuccessAlert.value = true
                successMessage.value = route.query.message || 'Operation completed successfully!'
            }
            fetchRequests()
        })

        // Filter requests based on selected status
        const filteredRequests = computed(() => {
            if (selectedFilter.value === 'all') return requests.value
            return requests.value.filter(request => request.status === selectedFilter.value)
        })

        // Fetch requests from backend
        const fetchRequests = async () => {
            try {
                loading.value = true
                const [requestsResponse, statsResponse] = await Promise.all([
                    axios.get('/api/customer/requests'),
                    axios.get('/api/dashboard-stats')
                ])

                requests.value = requestsResponse.data.data
                stats.value = statsResponse.data.data.service_requests || {}
            } catch (err) {
                console.error('Error fetching requests:', err)
                error.value = 'Failed to load service requests'
            } finally {
                loading.value = false
            }
        }

        // Cancel a service request
        const handleCancel = async (request) => {
            if (!confirm('Are you sure you want to cancel this service request?')) return

            try {
                cancelling.value = request.id
                await axios.post(`/api/requests/${request.id}/cancel`)
                await fetchRequests()
                showSuccessAlert.value = true
                successMessage.value = 'Service request cancelled successfully'
            } catch (err) {
                error.value = err.response?.data?.detail || 'Failed to cancel request'
            } finally {
                cancelling.value = null
            }
        }

        // Open review modal
        const openReviewModal = (request) => {
            selectedRequest.value = request
            reviewForm.value = { rating: 0, comment: '' }
            error.value = ''

            if (!reviewModal.value) {
                reviewModal.value = new Modal(document.getElementById('reviewModal'))
            }
            reviewModal.value.show()
        }

        // Open details modal
        const openDetailsModal = (request) => {
            selectedRequest.value = request

            if (!detailsModal.value) {
                detailsModal.value = new Modal(document.getElementById('detailsModal'))
            }
            detailsModal.value.show()
        }

        // Submit review
        const submitReview = async () => {
            if (!selectedRequest.value || !reviewForm.value.rating) return

            try {
                submittingReview.value = true
                await axios.post(`/api/requests/${selectedRequest.value.id}/review`, reviewForm.value)
                await fetchRequests()
                reviewModal.value.hide()
                showSuccessAlert.value = true
                successMessage.value = 'Review submitted successfully'
            } catch (err) {
                error.value = err.response?.data?.detail || 'Failed to submit review'
            } finally {
                submittingReview.value = false
            }
        }

        // Utility functions
        const formatDate = (date) => moment(date).format('MMM D, YYYY')
        const formatTime = (date) => moment(date).format('h:mm A')
        const truncate = (str, length) => {
            if (!str) return ''
            return str.length > length ? str.substring(0, length) + '...' : str
        }

        return {
            loading,
            requests,
            stats,
            selectedFilter,
            error,
            cancelling,
            selectedRequest,
            reviewForm,
            submittingReview,
            showSuccessAlert,
            successMessage,
            filteredRequests,
            handleCancel,
            openReviewModal,
            openDetailsModal,
            submitReview,
            formatDate,
            formatTime,
            truncate
        }
    }
}
</script>

<style scoped>
.card {
    transition: box-shadow 0.3s ease-in-out;
}

.btn-group .btn {
    min-width: 40px;
}

.table> :not(:first-child) {
    border-top: none;
}
</style>