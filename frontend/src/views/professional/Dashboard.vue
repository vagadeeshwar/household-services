// frontend/src/views/professional/Dashboard.vue
<template>
    <div class="dashboard">
        <!-- Profile Status Alert -->
        <div v-if="!stats.profile_status?.is_verified" class="alert alert-warning alert-dismissible fade show mb-4"
            role="alert">
            <div class="d-flex align-items-center">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <div>
                    <strong>Account Pending Verification</strong>
                    <p class="mb-0">Your account is currently under review. You'll be notified once verified.</p>
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>

        <!-- Stats Overview -->
        <div class="row g-4 mb-4">
            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
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

            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-success bg-opacity-10 p-3 rounded">
                                <i class="bi bi-check-circle fs-4 text-success"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Completed Jobs</h6>
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
                            <div class="bg-info bg-opacity-10 p-3 rounded">
                                <i class="bi bi-star fs-4 text-info"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Average Rating</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">
                            {{ stats.reviews?.average_rating?.toFixed(1) || '0.0' }}
                            <small class="text-muted fs-6">/5</small>
                        </h3>
                    </div>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-warning bg-opacity-10 p-3 rounded">
                                <i class="bi bi-bell fs-4 text-warning"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Available Requests</h6>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ availableRequests.length }}</h3>
                    </div>
                </div>
            </div>
        </div>

        <div class="row g-4">
            <!-- Available Service Requests -->
            <div class="col-lg-8">
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-transparent border-0">
                        <div class="d-flex align-items-center justify-content-between">
                            <h5 class="mb-0">Available Service Requests</h5>
                            <router-link to="/professional/requests" class="btn btn-sm btn-primary">
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

                        <div v-else-if="availableRequests.length === 0" class="text-center py-4">
                            <i class="bi bi-calendar-x fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No available service requests</p>
                        </div>

                        <div v-else class="table-responsive">
                            <table class="table table-hover align-middle">
                                <thead class="table-light">
                                    <tr>
                                        <th>Customer</th>
                                        <th>Location</th>
                                        <th>Preferred Time</th>
                                        <th>Description</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="request in availableRequests" :key="request.id">
                                        <td>{{ request.customer.user.full_name }}</td>
                                        <td>{{ request.customer.user.pin_code }}</td>
                                        <td>{{ formatDate(request.preferred_time) }}</td>
                                        <td>
                                            <span class="text-truncate d-inline-block" style="max-width: 200px;">
                                                {{ request.description }}
                                            </span>
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-success" @click="acceptRequest(request.id)"
                                                :disabled="accepting === request.id">
                                                <span v-if="accepting === request.id"
                                                    class="spinner-border spinner-border-sm me-1">
                                                </span>
                                                Accept
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Active Jobs -->
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent border-0">
                        <div class="d-flex align-items-center justify-content-between">
                            <h5 class="mb-0">Active Jobs</h5>
                            <router-link to="/professional/jobs" class="btn btn-sm btn-primary">
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

                        <div v-else-if="activeJobs.length === 0" class="text-center py-4">
                            <i class="bi bi-briefcase fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No active jobs</p>
                        </div>

                        <div v-else class="table-responsive">
                            <table class="table table-hover align-middle">
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
                                        <td>{{ job.customer.user.full_name }}</td>
                                        <td>{{ job.service.name }}</td>
                                        <td>{{ formatDate(job.preferred_time) }}</td>
                                        <td>
                                            <span class="badge bg-primary">{{ job.status }}</span>
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-success me-2" @click="openCompleteModal(job)">
                                                Complete
                                            </button>
                                            <button class="btn btn-sm btn-outline-primary" @click="viewDetails(job)">
                                                Details
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Side Section -->
            <div class="col-lg-4">
                <!-- Professional Profile Card -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-body">
                        <div class="text-center mb-4">
                            <div class="avatar mb-3">
                                <i class="bi bi-person-circle display-1 text-primary"></i>
                            </div>
                            <h5 class="mb-1">{{ user.full_name }}</h5>
                            <p class="text-muted mb-2">{{ user.service_type }}</p>
                            <div class="rating text-warning">
                                <i v-for="n in 5" :key="n"
                                    :class="['bi', n <= Math.round(stats.reviews?.average_rating || 0) ? 'bi-star-fill' : 'bi-star']">
                                </i>
                                <span class="ms-2 text-muted">
                                    ({{ stats.reviews?.total || 0 }} reviews)
                                </span>
                            </div>
                        </div>

                        <div class="border-top pt-3">
                            <div class="row text-center">
                                <div class="col">
                                    <h6 class="mb-1">{{ stats.service_requests?.total || 0 }}</h6>
                                    <small class="text-muted">Total Jobs</small>
                                </div>
                                <div class="col border-start">
                                    <h6 class="mb-1">{{ stats.service_requests?.completed || 0 }}</h6>
                                    <small class="text-muted">Completed</small>
                                </div>
                                <div class="col border-start">
                                    <h6 class="mb-1">{{ user.experience_years }}</h6>
                                    <small class="text-muted">Years Exp.</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Reviews -->
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent border-0">
                        <h5 class="mb-0">Recent Reviews</h5>
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
                            <div v-for="review in recentReviews" :key="review.id"
                                class="review-item mb-3 p-3 bg-light rounded">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <div class="rating text-warning">
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
                                    By: {{ review.service_request.customer.user.full_name }}
                                </small>
                            </div>
                        </div>
                    </div>
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
                    <div class="modal-body">
                        <form @submit.prevent="completeJob">
                            <div class="mb-3">
                                <label class="form-label">Completion Remarks</label>
                                <textarea v-model="completionForm.remarks" class="form-control" rows="3"
                                    placeholder="Describe the completed work..." required></textarea>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-success" :disabled="completing">
                                    <span v-if="completing" class="spinner-border spinner-border-sm me-1"></span>
                                    Mark as Complete
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { Modal } from 'bootstrap'
import moment from 'moment'
import axios from 'axios'

export default {
    name: 'ProfessionalDashboard',

    setup() {
        const store = useStore()
        const loading = ref(true)
        const stats = ref({})
        const availableRequests = ref([])
        const activeJobs = ref([])
        const recentReviews = ref([])
        const accepting = ref(null)
        const completing = ref(false)
        const completeModal = ref(null)
        const selectedJob = ref(null)

        const user = computed(() => store.getters['auth/getUser'])

        const completionForm = reactive({
            remarks: ''
        })

        // Fetch dashboard data
        const fetchDashboardData = async () => {
            try {
                loading.value = true
                const [statsRes, requestsRes, jobsRes, reviewsRes] = await Promise.all([
                    axios.get('/api/professional/requests?type=active'),
                    axios.get('/api/professional/reviews?per_page=3')
                ])

                stats.value = statsRes.data.data
                availableRequests.value = requestsRes.data.data
                activeJobs.value = jobsRes.data.data
                recentReviews.value = reviewsRes.data.data
            } catch (error) {
                console.error('Error fetching dashboard data:', error)
            } finally {
                loading.value = false
            }
        }

        const acceptRequest = async (requestId) => {
            try {
                accepting.value = requestId
                await axios.post(`/api/requests/${requestId}/accept`)
                await fetchDashboardData()
            } catch (error) {
                console.error('Error accepting request:', error)
            } finally {
                accepting.value = null
            }
        }

        const openCompleteModal = (job) => {
            selectedJob.value = job
            completionForm.remarks = ''
            const modal = new Modal(completeModal.value)
            modal.show()
        }

        const completeJob = async () => {
            if (!selectedJob.value || !completionForm.remarks.trim()) return

            try {
                completing.value = true
                await axios.post(`/api/requests/${selectedJob.value.id}/complete`, completionForm)
                const modal = Modal.getInstance(completeModal.value)
                modal.hide()
                await fetchDashboardData()
            } catch (error) {
                console.error('Error completing job:', error)
            } finally {
                completing.value = false
            }
        }

        const viewDetails = (job) => {
            // Implement job details view navigation
            router.push(`/professional/jobs/${job.id}`)
        }

        const formatDate = (date) => {
            return moment(date).format('MMM D, YYYY h:mm A')
        }

        onMounted(() => {
            fetchDashboardData()
        })

        return {
            user,
            loading,
            stats,
            availableRequests,
            activeJobs,
            recentReviews,
            accepting,
            completing,
            completeModal,
            completionForm,
            acceptRequest,
            openCompleteModal,
            completeJob,
            viewDetails,
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

.avatar {
    width: 100px;
    height: 100px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.rating i {
    cursor: default;
    margin-right: 2px;
}

.reviews-list {
    max-height: 400px;
    overflow-y: auto;
}

.review-item:hover {
    background-color: #f0f0f0 !important;
}

/* Custom scrollbar for reviews list */
.reviews-list::-webkit-scrollbar {
    width: 6px;
}

.reviews-list::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

.reviews-list::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
}

.reviews-list::-webkit-scrollbar-thumb:hover {
    background: #555;
}
</style>