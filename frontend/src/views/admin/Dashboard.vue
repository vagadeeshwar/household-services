// frontend/src/views/admin/Dashboard.vue
<template>
    <div class="dashboard">
        <!-- Platform Overview Stats -->
        <div class="row g-4 mb-4">
            <!-- Total Professionals -->
            <div class="col-md-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary bg-opacity-10 p-3 rounded">
                                <i class="bi bi-person-badge fs-4 text-primary"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Total Professionals</h6>
                                <small class="text-muted">
                                    {{ stats.verified_professionals }} verified
                                </small>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.total_professionals || 0 }}</h3>
                    </div>
                </div>
            </div>

            <!-- Total Customers -->
            <div class="col-md-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-success bg-opacity-10 p-3 rounded">
                                <i class="bi bi-people fs-4 text-success"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Total Customers</h6>
                                <small class="text-muted">
                                    {{ stats.active_customers }} active
                                </small>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.total_customers || 0 }}</h3>
                    </div>
                </div>
            </div>

            <!-- Service Requests -->
            <div class="col-md-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-info bg-opacity-10 p-3 rounded">
                                <i class="bi bi-calendar2-check fs-4 text-info"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Service Requests</h6>
                                <small class="text-muted">
                                    {{ stats.service_requests?.pending }} pending
                                </small>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.service_requests?.total || 0 }}</h3>
                    </div>
                </div>
            </div>

            <!-- Pending Actions -->
            <div class="col-md-6 col-lg-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-warning bg-opacity-10 p-3 rounded">
                                <i class="bi bi-exclamation-circle fs-4 text-warning"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Pending Actions</h6>
                                <small class="text-muted">Requires attention</small>
                            </div>
                        </div>
                        <h3 class="mb-0">
                            {{ stats.pending_verifications + stats.reported_reviews || 0 }}
                        </h3>
                    </div>
                </div>
            </div>
        </div>

        <div class="row g-4">
            <!-- Main Content Area -->
            <div class="col-lg-8">
                <!-- Pending Verifications -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-transparent border-0">
                        <div class="d-flex align-items-center justify-content-between">
                            <h5 class="mb-0">
                                Pending Verifications
                                <span class="badge bg-warning ms-2">
                                    {{ stats.pending_verifications }}
                                </span>
                            </h5>
                            <router-link to="/admin/professionals?verified=false" class="btn btn-sm btn-primary">
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

                        <div v-else-if="pendingVerifications.length === 0" class="text-center py-4">
                            <i class="bi bi-patch-check fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No pending verifications</p>
                        </div>

                        <div v-else class="table-responsive">
                            <table class="table table-hover align-middle">
                                <thead class="table-light">
                                    <tr>
                                        <th>Professional</th>
                                        <th>Service Type</th>
                                        <th>Experience</th>
                                        <th>Registered</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="prof in pendingVerifications" :key="prof.id">
                                        <td>
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <div class="fw-bold">{{ prof.user.full_name }}</div>
                                                    <small class="text-muted">{{ prof.user.email }}</small>
                                                </div>
                                            </div>
                                        </td>
                                        <td>{{ prof.service_type.name }}</td>
                                        <td>{{ prof.experience_years }} years</td>
                                        <td>{{ formatDate(prof.created_at) }}</td>
                                        <td>
                                            <button class="btn btn-sm btn-success me-2"
                                                @click="verifyProfessional(prof.id)" :disabled="verifying === prof.id">
                                                <span v-if="verifying === prof.id"
                                                    class="spinner-border spinner-border-sm me-1">
                                                </span>
                                                Verify
                                            </button>
                                            <button class="btn btn-sm btn-outline-primary" @click="viewDocuments(prof)">
                                                Documents
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Recent Service Requests -->
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent border-0">
                        <div class="d-flex align-items-center justify-content-between">
                            <h5 class="mb-0">Recent Service Requests</h5>
                            <router-link to="/admin/requests" class="btn btn-sm btn-primary">
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
                            <i class="bi bi-calendar-x fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No service requests</p>
                        </div>

                        <div v-else class="table-responsive">
                            <table class="table table-hover align-middle">
                                <thead class="table-light">
                                    <tr>
                                        <th>Customer</th>
                                        <th>Service</th>
                                        <th>Professional</th>
                                        <th>Status</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="request in recentRequests" :key="request.id">
                                        <td>{{ request.customer.user.full_name }}</td>
                                        <td>{{ request.service.name }}</td>
                                        <td>
                                            <span v-if="request.professional">
                                                {{ request.professional.user.full_name }}
                                            </span>
                                            <span v-else class="text-muted">Not assigned</span>
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
                                        <td>{{ formatDate(request.preferred_time) }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sidebar Content -->
            <div class="col-lg-4">
                <!-- Reported Reviews -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-transparent border-0">
                        <div class="d-flex align-items-center justify-content-between">
                            <h5 class="mb-0">
                                Reported Reviews
                                <span class="badge bg-danger ms-2">
                                    {{ stats.reported_reviews }}
                                </span>
                            </h5>
                            <router-link to="/admin/reviews?reported=true" class="btn btn-sm btn-primary">
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

                        <div v-else-if="reportedReviews.length === 0" class="text-center py-4">
                            <i class="bi bi-shield-check fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No reported reviews</p>
                        </div>

                        <div v-else>
                            <div v-for="review in reportedReviews" :key="review.id"
                                class="review-card p-3 mb-3 bg-light rounded">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <div>
                                        <div class="rating text-warning">
                                            <i v-for="n in 5" :key="n"
                                                :class="['bi', n <= review.rating ? 'bi-star-fill' : 'bi-star']">
                                            </i>
                                        </div>
                                        <small class="text-muted d-block">
                                            {{ formatDate(review.created_at) }}
                                        </small>
                                    </div>
                                    <span class="badge bg-danger">Reported</span>
                                </div>
                                <p class="mb-2">{{ review.comment }}</p>
                                <div class="report-reason mb-2">
                                    <small class="text-danger">
                                        <i class="bi bi-exclamation-triangle me-1"></i>
                                        {{ review.report_reason }}
                                    </small>
                                </div>
                                <div class="review-meta text-muted small">
                                    <div>Service: {{ review.service_request.service.name }}</div>
                                    <div>Professional: {{ review.service_request.professional.user.full_name }}</div>
                                    <div>Customer: {{ review.service_request.customer.user.full_name }}</div>
                                </div>
                                <div class="mt-3 d-flex gap-2">
                                    <button class="btn btn-sm btn-danger" @click="removeReview(review.id)"
                                        :disabled="removingReview === review.id">
                                        Remove Review
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" @click="dismissReport(review.id)"
                                        :disabled="dismissingReport === review.id">
                                        Dismiss Report
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats -->
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent border-0">
                        <h5 class="mb-0">Platform Statistics</h5>
                    </div>
                    <div class="card-body">
                        <canvas ref="statsChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Document Preview Modal -->
        <div class="modal fade" id="documentModal" tabindex="-1" ref="documentModal">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Verification Documents</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div v-if="selectedProfessional" class="p-3">
                            <div class="mb-4">
                                <h6>Professional Details</h6>
                                <div class="table-responsive">
                                    <table class="table table-borderless">
                                        <tbody>
                                            <tr>
                                                <th style="width: 150px">Name:</th>
                                                <td>{{ selectedProfessional.user.full_name }}</td>
                                            </tr>
                                            <tr>
                                                <th>Service Type:</th>
                                                <td>{{ selectedProfessional.service_type.name }}</td>
                                            </tr>
                                            <tr>
                                                <th>Experience:</th>
                                                <td>{{ selectedProfessional.experience_years }} years</td>
                                            </tr>
                                            <tr>
                                                <th>Description:</th>
                                                <td>{{ selectedProfessional.description }}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div>
                                <h6>Verification Document</h6>
                                <div class="document-preview bg-light p-3 rounded">
                                    <iframe v-if="documentUrl" :src="documentUrl" class="w-100"
                                        style="height: 500px;"></iframe>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            Close
                        </button>
                        <button type="button" class="btn btn-success"
                            @click="verifyProfessional(selectedProfessional?.id)"
                            :disabled="verifying === selectedProfessional?.id">
                            <span v-if="verifying === selectedProfessional?.id"
                                class="spinner-border spinner-border-sm me-1">
                            </span>
                            Verify Professional
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import Chart from 'chart.js/auto'
import moment from 'moment'
import axios from 'axios'

export default {
    name: 'AdminDashboard',

    setup() {
        const loading = ref(true)
        const stats = ref({})
        const pendingVerifications = ref([])
        const recentRequests = ref([])
        const reportedReviews = ref([])
        const verifying = ref(null)
        const removingReview = ref(null)
        const dismissingReport = ref(null)
        const documentModal = ref(null)
        const selectedProfessional = ref(null)
        const documentUrl = ref('')
        const statsChart = ref(null)
        let chart = null

        const fetchDashboardData = async () => {
            try {
                loading.value = true
                const [
                    statsRes,
                    verificationsRes,
                    requestsRes,
                    reviewsRes
                ] = await Promise.all([
                    axios.get('/api/dashboard-stats'),
                    axios.get('/api/detailed-stats?stat_type=pending_verifications'),
                    axios.get('/api/detailed-stats?stat_type=recent_requests'),
                    axios.get('/api/detailed-stats?stat_type=reported_reviews')
                ])

                stats.value = statsRes.data.data
                pendingVerifications.value = verificationsRes.data.data
                recentRequests.value = requestsRes.data.data
                reportedReviews.value = reviewsRes.data.data

                initializeChart()
            } catch (error) {
                console.error('Error fetching dashboard data:', error)
            } finally {
                loading.value = false
            }
        }

        const initializeChart = () => {
            if (chart) {
                chart.destroy()
            }

            const ctx = statsChart.value.getContext('2d')
            chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Professionals', 'Customers', 'Active Requests', 'Completed'],
                    datasets: [{
                        label: 'Platform Statistics',
                        data: [
                            stats.value.total_professionals || 0,
                            stats.value.total_customers || 0,
                            stats.value.service_requests?.active || 0,
                            stats.value.service_requests?.completed || 0
                        ],
                        backgroundColor: [
                            'rgba(13, 110, 253, 0.5)',  // primary
                            'rgba(25, 135, 84, 0.5)',   // success
                            'rgba(13, 202, 240, 0.5)',  // info
                            'rgba(25, 135, 84, 0.5)'    // success
                        ],
                        borderColor: [
                            'rgb(13, 110, 253)',
                            'rgb(25, 135, 84)',
                            'rgb(13, 202, 240)',
                            'rgb(25, 135, 84)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            })
        }

        const verifyProfessional = async (professionalId) => {
            try {
                verifying.value = professionalId
                await axios.post(`/api/professionals/${professionalId}/verify`)
                await fetchDashboardData()

                if (documentModal.value) {
                    const modal = Modal.getInstance(documentModal.value)
                    modal?.hide()
                }
            } catch (error) {
                console.error('Error verifying professional:', error)
            } finally {
                verifying.value = null
            }
        }

        const viewDocuments = async (professional) => {
            selectedProfessional.value = professional
            documentUrl.value = `/api/static/uploads/verification_docs/${professional.verification_documents}`
            const modal = new Modal(documentModal.value)
            modal.show()
        }

        const removeReview = async (reviewId) => {
            if (!confirm('Are you sure you want to remove this review?')) return

            try {
                removingReview.value = reviewId
                await axios.delete(`/api/reviews/${reviewId}`)
                await fetchDashboardData()
            } catch (error) {
                console.error('Error removing review:', error)
            } finally {
                removingReview.value = null
            }
        }

        const dismissReport = async (reviewId) => {
            try {
                dismissingReport.value = reviewId
                await axios.post(`/api/reviews/${reviewId}/dismiss-report`)
                await fetchDashboardData()
            } catch (error) {
                console.error('Error dismissing report:', error)
            } finally {
                dismissingReport.value = null
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
            pendingVerifications,
            recentRequests,
            reportedReviews,
            verifying,
            removingReview,
            dismissingReport,
            documentModal,
            selectedProfessional,
            documentUrl,
            statsChart,
            verifyProfessional,
            viewDocuments,
            removeReview,
            dismissReport,
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

.review-card {
    transition: all 0.2s;
}

.review-card:hover {
    background-color: #f8f9fa !important;
}

.report-reason {
    padding: 0.5rem;
    background-color: #fff;
    border-radius: 0.25rem;
}

.table th {
    font-weight: 600;
}

.document-preview {
    border: 1px solid #dee2e6;
}
</style>