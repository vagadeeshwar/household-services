<template>
    <div class="dashboard">
        <!-- Stats Overview -->
        <div class="row g-4 mb-4">
            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary bg-opacity-10 p-3 rounded">
                                <i class="bi bi-calendar-check fs-4 text-primary"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Active Requests</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.service_requests?.active || 0 }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-success bg-opacity-10 p-3 rounded">
                                <i class="bi bi-check-circle fs-4 text-success"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Completed Services</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.service_requests?.completed || 0 }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-warning bg-opacity-10 p-3 rounded">
                                <i class="bi bi-clock fs-4 text-warning"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Pending Requests</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.service_requests?.pending || 0 }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-info bg-opacity-10 p-3 rounded">
                                <i class="bi bi-star fs-4 text-info"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Reviews Given</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.reviews_given || 0 }}</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Requests and Actions -->
        <div class="row g-4">
            <!-- Active Requests -->
            <div class="col-lg-8">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent border-0">
                        <div class="d-flex align-items-center justify-content-between">
                            <h5 class="mb-0">Recent Service Requests</h5>
                            <router-link to="/customer/requests" class="btn btn-sm btn-primary">
                                View All
                            </router-link>
                        </div>
                    </div>
                    <div class="card-body">
                        <div v-if="loading" class="text-center py-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>

                        <div v-else-if="recentRequests.length === 0" class="text-center py-4">
                            <i class="bi bi-inbox fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No service requests yet</p>
                        </div>

                        <div v-else class="table-responsive">
                            <table class="table table-hover align-middle">
                                <thead class="table-light">
                                    <tr>
                                        <th>Service</th>
                                        <th>Status</th>
                                        <th>Date</th>
                                        <th>Professional</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="request in recentRequests" :key="request.id">
                                        <td>{{ request.service.name }}</td>
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
                                        <td>{{ formatDate(request.preferred_time) }}</td>
                                        <td>
                                            <span v-if="request.professional">
                                                {{ request.professional.user.full_name }}
                                            </span>
                                            <span v-else class="text-muted">Not assigned</span>
                                        </td>
                                        <td>
                                            <button v-if="request.status === 'completed' && !request.review"
                                                class="btn btn-sm btn-outline-primary me-2"
                                                @click="openReviewModal(request)">
                                                Add Review
                                            </button>
                                            <button v-if="request.status === 'created'"
                                                class="btn btn-sm btn-outline-danger"
                                                @click="cancelRequest(request.id)">
                                                Cancel
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="col-lg-4">
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-transparent border-0">
                        <h5 class="mb-0">Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-3">
                            <router-link to="/customer/book-service" class="btn btn-primary">
                                <i class="bi bi-plus-circle me-2"></i>
                                Book New Service
                            </router-link>
                            <router-link to="/customer/services" class="btn btn-outline-primary">
                                <i class="bi bi-grid me-2"></i>
                                Browse Services
                            </router-link>
                            <router-link to="/customer/profile" class="btn btn-outline-secondary">
                                <i class="bi bi-person me-2"></i>
                                Update Profile
                            </router-link>
                        </div>
                    </div>
                </div>

                <!-- Recent Reviews -->
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent border-0">
                        <h5 class="mb-0">Your Recent Reviews</h5>
                    </div>
                    <div class="card-body">
                        <div v-if="loading" class="text-center py-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>

                        <div v-else-if="recentReviews.length === 0" class="text-center py-4">
                            <i class="bi bi-star fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No reviews yet</p>
                        </div>

                        <div v-else class="reviews-list">
                            <div v-for="review in recentReviews" :key="review.id" class="review-item mb-3">
                                <div class="d-flex align-items-center mb-2">
                                    <div class="rating text-warning me-2">
                                        <i v-for="n in 5" :key="n"
                                            :class="['bi', n <= review.rating ? 'bi-star-fill' : 'bi-star']">
                                        </i>
                                    </div>
                                    <small class="text-muted">
                                        {{ formatDate(review.created_at) }}
                                    </small>
                                </div>
                                <p class="mb-1">{{ review.comment }}</p>
                                <small class="text-muted">
                                    For: {{ review.service_request.service.name }}
                                </small>
                            </div>
                        </div>
                    </div>
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
                    <div class="modal-body">
                        <form @submit.prevent="submitReview">
                            <div class="mb-3">
                                <label class="form-label">Rating</label>
                                <div class="rating-input">
                                    <div class="btn-group">
                                        <button v-for="n in 5" :key="n" type="button" class="btn btn-outline-warning"
                                            :class="{ active: reviewForm.rating >= n }" @click="reviewForm.rating = n">
                                            <i class="bi bi-star-fill"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Comment</label>
                                <textarea v-model="reviewForm.comment" class="form-control" rows="3"
                                    placeholder="Share your experience..."></textarea>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary" :disabled="!reviewForm.rating">
                                    Submit Review
                                </button>
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
import { Modal } from 'bootstrap'
import moment from 'moment'
import axios from 'axios'

export default {
    name: 'CustomerDashboard',

    setup() {
        const loading = ref(true)
        const stats = ref({})
        const recentRequests = ref([])
        const recentReviews = ref([])
        const reviewModal = ref(null)
        const selectedRequest = ref(null)

        const reviewForm = reactive({
            rating: 0,
            comment: ''
        })

        // Fetch dashboard data
        const fetchDashboardData = async () => {
            try {
                loading.value = true
                const [statsRes, requestsRes, reviewsRes] = await Promise.all([
                    axios.get('/api/dashboard-stats'),
                    axios.get('/api/customer/requests?per_page=5'),
                    axios.get('/api/requests/reviews?per_page=3')
                ])

                stats.value = statsRes.data.data
                recentRequests.value = requestsRes.data.data
                recentReviews.value = reviewsRes.data.data
            } catch (error) {
                console.error('Error fetching dashboard data:', error)
            } finally {
                loading.value = false
            }
        }

        const openReviewModal = (request) => {
            selectedRequest.value = request
            reviewForm.rating = 0
            reviewForm.comment = ''
            const modal = new Modal(reviewModal.value)
            modal.show()
        }

        const submitReview = async () => {
            if (!selectedRequest.value || !reviewForm.rating) return

            try {
                await axios.post(`/api/requests/${selectedRequest.value.id}/review`, reviewForm)
                const modal = Modal.getInstance(reviewModal.value)
                modal.hide()
                await fetchDashboardData()
            } catch (error) {
                console.error('Error submitting review:', error)
            }
        }

        const cancelRequest = async (requestId) => {
            if (!confirm('Are you sure you want to cancel this request?')) return

            try {
                await axios.post(`/api/requests/${requestId}/cancel`)
                await fetchDashboardData()
            } catch (error) {
                console.error('Error canceling request:', error)
            }
        }

        const formatDate = (date) => {
            return moment(date).format('MMM D, YYYY h:mm A')
        }

        onMounted(() => {
            fetchDashboardData()
        })

        return {
            loading,
            stats,
            recentRequests,
            recentReviews,
            reviewModal,
            reviewForm,
            openReviewModal,
            submitReview,
            cancelRequest,
            formatDate
        }
    }
}
</script>

<style scoped>
.dashboard {
    padding: 1.5rem;
}

.card {
    transition: transform 0.2s;
}

.card:hover {
    transform: translateY(-2px);
}

.rating-input .btn-group {
    width: 100%;
}

.rating-input .btn {
    flex: 1;
}

.rating-input .btn:not(:last-child) {
    margin-right: 5px;
}

.rating-input .btn.active {
    background-color: #ffc107;
    border-color: #ffc107;
    color: white;
}

.reviews-list {
    max-height: 300px;
    overflow-y: auto;
}

.review-item {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #f8f9fa;
}

.review-item:not(:last-child) {
    margin-bottom: 1rem;
}
</style>