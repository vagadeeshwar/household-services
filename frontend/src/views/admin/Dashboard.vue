<!-- src/views/admin/DashboardOverview.vue -->
<template>
    <div class="dashboard-overview">
        <!-- Stats Cards Row -->
        <div class="row g-4 mb-4">
            <!-- Professionals Card -->
            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary bg-opacity-10 p-3 rounded">
                                <i class="bi bi-people fs-4 text-primary"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Service Professionals</h6>
                                <small class="text-muted">
                                    {{ stats.verified_professionals }} verified
                                </small>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.total_professionals }}</h3>
                    </div>
                </div>
            </div>

            <!-- Customers Card -->
            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-success bg-opacity-10 p-3 rounded">
                                <i class="bi bi-person-check fs-4 text-success"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Active Customers</h6>
                                <small class="text-muted">
                                    Past 30 days
                                </small>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.total_customers }}</h3>
                    </div>
                </div>
            </div>

            <!-- Service Requests Card -->
            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-info bg-opacity-10 p-3 rounded">
                                <i class="bi bi-clipboard-check fs-4 text-info"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Service Requests</h6>
                                <small class="text-muted">
                                    {{ stats.pending_requests }} pending
                                </small>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ stats.total_requests }}</h3>
                    </div>
                </div>
            </div>

            <!-- Actions Required Card -->
            <div class="col-md-6 col-lg-3">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-warning bg-opacity-10 p-3 rounded">
                                <i class="bi bi-exclamation-circle fs-4 text-warning"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Actions Required</h6>
                                <small class="text-muted">Needs attention</small>
                            </div>
                        </div>
                        <h3 class="mb-0">{{ pendingActions }}</h3>
                    </div>
                </div>
            </div>
        </div>
        <!-- Alert for errors -->
        <div v-if="error" class="alert alert-danger alert-dismissible fade show mb-4" role="alert">
            {{ error }}
            <button type="button" class="btn-close" @click="error = null"></button>
        </div>

        <!-- Main Content Row -->
        <div class="row g-4">
            <!-- Left Column -->
            <div class="col-lg-8">
                <!-- Pending Verifications -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-transparent">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">
                                Pending Verifications
                                <span class="badge bg-warning ms-2">
                                    {{ stats.pending_verifications }}
                                </span>
                            </h5>
                            <router-link to="/admin/verifications" class="btn btn-sm btn-primary">
                                View All
                            </router-link>
                        </div>
                    </div>
                    <div class="card-body p-0">
                        <div v-if="loading" class="text-center py-4">
                            <div class="spinner-border text-primary">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <div v-else-if="!pendingVerifications.length" class="text-center py-4">
                            <i class="bi bi-check-circle fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No pending verifications</p>
                        </div>
                        <div v-else class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="bg-light">
                                    <tr>
                                        <th>Professional</th>
                                        <th>Service Type</th>
                                        <th>Experience</th>
                                        <th>Date Applied</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="prof in pendingVerifications" :key="prof?.id">
                                        <td>
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <div class="fw-medium">
                                                        {{ prof?.user?.full_name || 'Unknown' }}
                                                    </div>
                                                    <small class="text-muted">
                                                        {{ prof?.user?.email || 'No email' }}
                                                    </small>
                                                </div>
                                            </div>
                                        </td>
                                        <td>{{ prof?.service_type?.name || 'Unknown Service' }}</td>
                                        <td>{{ prof?.experience_years || 0 }} years</td>
                                        <td>{{ formatDate(prof?.created_at) }}</td>
                                        <td>
                                            <button class="btn btn-sm btn-primary" @click="viewDocuments(prof)"
                                                :disabled="!prof?.verification_documents">
                                                Review
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
                    <div class="card-header bg-transparent">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Recent Service Requests</h5>
                            <router-link to="/admin/requests" class="btn btn-sm btn-primary">
                                View All
                            </router-link>
                        </div>
                    </div>
                    <div class="card-body p-0">
                        <div v-if="loading" class="text-center py-4">
                            <div class="spinner-border text-primary">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <div v-else-if="!recentRequests.length" class="text-center py-4">
                            <i class="bi bi-inbox fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No recent service requests</p>
                        </div>
                        <div v-else class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="bg-light">
                                    <tr>
                                        <th>Customer</th>
                                        <th>Service</th>
                                        <th>Professional</th>
                                        <th>Status</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="request in recentRequests" :key="request?.id">
                                        <td>{{ request?.customer?.user?.full_name || 'Unknown' }}</td>
                                        <td>{{ request?.service?.name || 'Unknown Service' }}</td>
                                        <td>
                                            <span v-if="request?.professional?.user?.full_name">
                                                {{ request.professional.user.full_name }}
                                            </span>
                                            <span v-else class="text-muted">Not assigned</span>
                                        </td>
                                        <td>
                                            <span :class="[
                                                'badge',
                                                {
                                                    'bg-warning': request?.status === 'created',
                                                    'bg-primary': request?.status === 'assigned',
                                                    'bg-success': request?.status === 'completed'
                                                }
                                            ]">
                                                {{ request?.status || 'Unknown' }}
                                            </span>
                                        </td>
                                        <td>{{ formatDate(request?.created_at) }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column -->
            <div class="col-lg-4">
                <!-- Quick Actions -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-transparent">
                        <h5 class="mb-0">Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary" @click="openNewServiceModal">
                                <i class="bi bi-plus-circle me-2"></i>
                                Add New Service
                            </button>
                            <router-link to="/admin/export" class="btn btn-outline-primary">
                                <i class="bi bi-download me-2"></i>
                                Export Reports
                            </router-link>
                            <router-link to="/admin/settings" class="btn btn-outline-secondary">
                                <i class="bi bi-gear me-2"></i>
                                Platform Settings
                            </router-link>
                        </div>
                    </div>
                </div>

                <!-- Reported Reviews -->
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">
                                Reported Reviews
                                <span class="badge bg-danger ms-2">
                                    {{ stats.reported_reviews }}
                                </span>
                            </h5>
                            <router-link to="/admin/reviews" class="btn btn-sm btn-primary">
                                View All
                            </router-link>
                        </div>
                    </div>
                    <div class="card-body">
                        <div v-if="loading" class="text-center py-4">
                            <div class="spinner-border text-primary">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <div v-else-if="!reportedReviews.length" class="text-center py-4">
                            <i class="bi bi-check-circle fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No reported reviews</p>
                        </div>
                        <div v-else>
                            <div v-for="review in reportedReviews" :key="review?.id"
                                class="review-card p-3 mb-3 bg-light rounded">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <div class="rating text-warning">
                                        <i v-for="n in 5" :key="n"
                                            :class="['bi', n <= (review?.rating || 0) ? 'bi-star-fill' : 'bi-star']">
                                        </i>
                                    </div>
                                    <span class="badge bg-danger">Reported</span>
                                </div>
                                <p class="mb-2">{{ review?.comment || 'No comment provided' }}</p>
                                <div class="report-reason mb-2">
                                    <small class="text-danger">
                                        <i class="bi bi-exclamation-triangle me-1"></i>
                                        {{ review?.report_reason || 'No reason provided' }}
                                    </small>
                                </div>
                                <div class="d-flex justify-content-between align-items-center mt-2">
                                    <small class="text-muted">
                                        {{ formatDate(review?.created_at) }}
                                    </small>
                                    <div>
                                        <button class="btn btn-sm btn-outline-danger me-2"
                                            @click="handleRemoveReview(review?.id)" :disabled="!review?.id">
                                            Remove
                                        </button>
                                        <button class="btn btn-sm btn-outline-secondary"
                                            @click="handleDismissReview(review?.id)" :disabled="!review?.id">
                                            Dismiss
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Document Review Modal -->
        <div class="modal fade" id="documentModal" tabindex="-1" ref="documentModal">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Review Verification Documents</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Professional Details -->
                        <div v-if="selectedProfessional" class="mb-4">
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
                                    </tbody>
                                </table>
                            </div>
                            <!-- Document Preview -->
                            <h6>Verification Documents</h6>
                            <div class="document-preview bg-light p-3 rounded">
                                <iframe v-if="documentUrl" :src="documentUrl" class="w-100" style="height: 500px;">
                                </iframe>
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

        <!-- New Service Modal -->
        <div class="modal fade" id="newServiceModal" tabindex="-1" ref="newServiceModal">
            <!-- Modal content here -->
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { Modal } from 'bootstrap';
import moment from 'moment';
import axios from 'axios';

export default {
    name: 'DashboardOverview',

    setup() {
        // Initialize with proper data structures
        const loading = ref(true);
        const error = ref(null);
        const stats = ref({
            total_professionals: 0,
            verified_professionals: 0,
            total_customers: 0,
            active_customers: 0,
            pending_verifications: 0,
            reported_reviews: 0,
            service_requests: {
                total: 0,
                pending: 0,
                completed: 0
            }
        });

        const pendingVerifications = ref([]);
        const recentRequests = ref([]);
        const reportedReviews = ref([]);
        const selectedProfessional = ref(null);
        const verifying = ref(null);
        const documentUrl = ref('');
        const documentModal = ref(null);
        const newServiceModal = ref(null);

        const fetchDashboardData = async () => {
            try {
                loading.value = true;
                error.value = null;

                const [statsRes, verificationsRes, requestsRes, reviewsRes] = await Promise.all([
                    axios.get('/api/dashboard-stats'),
                    axios.get('/api/detailed-stats?stat_type=pending_verifications'),
                    axios.get('/api/detailed-stats?stat_type=recent_requests'),
                    axios.get('/api/detailed-stats?stat_type=reported_reviews')
                ]);

                // Validate responses before assignment
                if (statsRes.data?.data) {
                    stats.value = statsRes.data.data;
                }

                if (verificationsRes.data?.data) {
                    pendingVerifications.value = verificationsRes.data.data;
                }

                if (requestsRes.data?.data) {
                    recentRequests.value = requestsRes.data.data;
                }

                if (reviewsRes.data?.data) {
                    reportedReviews.value = reviewsRes.data.data;
                }

            } catch (err) {
                console.error('Error fetching dashboard data:', err);
                error.value = err.response?.data?.message || 'Error loading dashboard data';
            } finally {
                loading.value = false;
            }
        };

        const formatDate = (date) => {
            if (!date) return 'N/A';
            return moment(date).format('MMM D, YYYY');
        };

        const viewDocuments = (professional) => {
            if (!professional) return;
            selectedProfessional.value = professional;

            if (professional.verification_documents) {
                documentUrl.value = `/api/static/uploads/verification_docs/${professional.verification_documents}`;
                const modal = new Modal(document.getElementById('documentModal'));
                modal?.show();
            }
        };

        const verifyProfessional = async (professionalId) => {
            try {
                verifying.value = professionalId;
                await axios.post(`/api/professionals/${professionalId}/verify`);
                await fetchDashboardData();
                documentModal.value.hide();
            } catch (error) {
                console.error('Error verifying professional:', error);
            } finally {
                verifying.value = null;
            }
        };

        const openNewServiceModal = () => {
            if (!newServiceModal.value) {
                newServiceModal.value = new Modal(document.getElementById('newServiceModal'));
            }
            newServiceModal.value.show();
        };

        const handleDismissReview = async (reviewId) => {
            try {
                await axios.post(`/api/reviews/${reviewId}/dismiss`);
                await fetchDashboardData();
            } catch (error) {
                console.error('Error dismissing review:', error);
            }
        };

        const handleRemoveReview = async (reviewId) => {
            if (!confirm('Are you sure you want to remove this review?')) return;

            try {
                await axios.delete(`/api/reviews/${reviewId}`);
                await fetchDashboardData();
            } catch (error) {
                console.error('Error removing review:', error);
            }
        };

        const pendingActions = computed(() => {
            return (stats.value.pending_verifications || 0) + (stats.value.reported_reviews || 0);
        });

        // Lifecycle hooks
        onMounted(() => {
            fetchDashboardData().catch(err => {
                console.error('Error during component mount:', err);
                error.value = 'Failed to initialize dashboard';
            });
        });

        return {
            loading,
            stats,
            error,
            pendingVerifications,
            recentRequests,
            reportedReviews,
            selectedProfessional,
            verifying,
            documentUrl,
            documentModal,
            newServiceModal,
            pendingActions,
            viewDocuments,
            verifyProfessional,
            openNewServiceModal,
            handleDismissReview,
            handleRemoveReview,
            formatDate
        };
    }
};
</script>
<style scoped>
.dashboard-overview {
    padding: 1.5rem;
}

.card {
    transition: box-shadow 0.3s ease-in-out, transform 0.2s ease;
}

.card:hover {
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

.review-card {
    transition: background-color 0.2s ease;
}

.review-card:hover {
    background-color: #f0f0f0 !important;
}

.rating i {
    font-size: 0.875rem;
    margin-right: 1px;
}

.table th {
    font-weight: 600;
}

.document-preview {
    border: 1px solid #dee2e6;
    border-radius: 0.25rem;
}

.table-hover>tbody>tr:hover {
    background-color: rgba(0, 0, 0, 0.02);
}

/* Custom scrollbar for reviews section */
.card-body {
    scrollbar-width: thin;
    scrollbar-color: #888 #f1f1f1;
}

.card-body::-webkit-scrollbar {
    width: 6px;
}

.card-body::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

.card-body::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
}

.card-body::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* Loading spinner colors */
.spinner-border {
    --bs-spinner-width: 1.5rem;
    --bs-spinner-height: 1.5rem;
    --bs-spinner-border-width: 0.15em;
}

.bg-light {
    background-color: #f8f9fa !important;
}
</style>