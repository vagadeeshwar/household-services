# src/views/professional/ServiceRequestManagement.vue
<template>
    <div class="container-fluid py-4">
        <!-- Status Tabs -->
        <ul class="nav nav-tabs mb-4">
            <li class="nav-item" v-for="tab in tabs" :key="tab.value">
                <button class="nav-link" :class="{ active: activeTab === tab.value }" @click="activeTab = tab.value">
                    {{ tab.label }}
                    <span v-if="requestCounts[tab.value]" class="badge bg-primary ms-2">
                        {{ requestCounts[tab.value] }}
                    </span>
                </button>
            </li>
        </ul>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <!-- Error Alert -->
        <div v-else-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
            {{ error }}
            <button type="button" class="btn-close" @click="error = null"></button>
        </div>

        <!-- Empty State -->
        <div v-else-if="!filteredRequests.length" class="text-center py-5">
            <i class="bi bi-inbox fs-1 text-muted"></i>
            <p class="mt-2 mb-0">No {{ activeTab }} requests found</p>
        </div>

        <!-- Request Cards -->
        <div v-else class="row g-4">
            <div v-for="request in filteredRequests" :key="request.id" class="col-12">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <!-- Customer Info -->
                            <div class="col-md-3">
                                <div class="d-flex align-items-center">
                                    <div class="bg-light rounded-circle p-3 me-3">
                                        <i class="bi bi-person fs-4"></i>
                                    </div>
                                    <div>
                                        <h6 class="mb-1">{{ request.customer.full_name }}</h6>
                                        <p class="text-muted mb-0">
                                            <i class="bi bi-telephone me-1"></i>
                                            {{ request.customer.phone }}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <!-- Service Details -->
                            <div class="col-md-3">
                                <h6 class="text-muted mb-1">Service Type</h6>
                                <p class="mb-0">{{ request.service.name }}</p>
                            </div>

                            <!-- Schedule -->
                            <div class="col-md-3">
                                <h6 class="text-muted mb-1">Schedule</h6>
                                <p class="mb-0">
                                    <i class="bi bi-calendar me-1"></i>
                                    {{ formatDate(request.preferred_time) }}
                                </p>
                                <p class="mb-0">
                                    <i class="bi bi-clock me-1"></i>
                                    {{ formatTime(request.preferred_time) }}
                                </p>
                            </div>

                            <!-- Actions -->
                            <div class="col-md-3 text-md-end mt-3 mt-md-0">
                                <button v-if="activeTab === 'pending'" class="btn btn-success me-2"
                                    @click="handleAccept(request.id)" :disabled="processing === request.id">
                                    <span v-if="processing === request.id"
                                        class="spinner-border spinner-border-sm me-2"></span>
                                    Accept
                                </button>
                                <button v-if="activeTab === 'pending'" class="btn btn-danger"
                                    @click="handleReject(request.id)" :disabled="processing === request.id">
                                    Reject
                                </button>
                                <button v-if="activeTab === 'active'" class="btn btn-primary"
                                    @click="openCompleteModal(request)" :disabled="processing === request.id">
                                    Complete
                                </button>
                                <button v-if="activeTab === 'completed'" class="btn btn-outline-primary"
                                    @click="viewDetails(request)">
                                    View Details
                                </button>
                            </div>
                        </div>

                        <!-- Additional Details (Description) -->
                        <div class="mt-3">
                            <h6 class="text-muted mb-2">Description</h6>
                            <p class="mb-0">{{ request.description }}</p>
                        </div>

                        <!-- Review Info (for completed requests) -->
                        <div v-if="request.review" class="mt-3 border-top pt-3">
                            <div class="d-flex align-items-center">
                                <div class="rating text-warning me-2">
                                    <i v-for="n in 5" :key="n" class="bi"
                                        :class="n <= request.review.rating ? 'bi-star-fill' : 'bi-star'">
                                    </i>
                                </div>
                                <p class="mb-0">{{ request.review.comment }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Complete Service Modal -->
        <div class="modal fade" id="completeModal" tabindex="-1" ref="completeModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Complete Service Request</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="handleComplete">
                            <div class="mb-3">
                                <label class="form-label">Completion Remarks</label>
                                <textarea v-model="completionRemarks" class="form-control" rows="3"
                                    placeholder="Describe the work completed..." required>
                </textarea>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary me-2"
                                    data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" class="btn btn-primary" :disabled="processing">
                                    <span v-if="processing" class="spinner-border spinner-border-sm me-2"></span>
                                    Complete Service
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
import { ref, computed, onMounted } from 'vue';
import { Modal } from 'bootstrap';
import moment from 'moment';

export default {
    name: 'ServiceRequestManagement',

    setup() {
        const activeTab = ref('pending');
        const loading = ref(true);
        const error = ref(null);
        const processing = ref(null);
        const completeModal = ref(null);
        const completionRemarks = ref('');
        const selectedRequest = ref(null);

        const tabs = [
            { label: 'Pending Requests', value: 'pending' },
            { label: 'Active Requests', value: 'active' },
            { label: 'Completed', value: 'completed' }
        ];

        const requests = ref({
            pending: [],
            active: [],
            completed: []
        });

        const requestCounts = computed(() => ({
            pending: requests.value.pending.length,
            active: requests.value.active.length,
            completed: requests.value.completed.length
        }));

        const filteredRequests = computed(() => {
            return requests.value[activeTab.value] || [];
        });

        // Fetch requests from API
        const fetchRequests = async () => {
            try {
                loading.value = true;
                error.value = null;

                // Replace with actual API call
                await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay

                requests.value = {
                    pending: [
                        {
                            id: 1,
                            customer: {
                                full_name: 'John Doe',
                                phone: '9876543210'
                            },
                            service: {
                                name: 'AC Repair'
                            },
                            preferred_time: new Date('2024-03-30T10:00:00'),
                            description: 'AC not cooling properly'
                        }
                    ],
                    active: [
                        {
                            id: 2,
                            customer: {
                                full_name: 'Jane Smith',
                                phone: '9876543211'
                            },
                            service: {
                                name: 'AC Installation'
                            },
                            preferred_time: new Date('2024-03-29T14:00:00'),
                            description: 'New AC installation'
                        }
                    ],
                    completed: [
                        {
                            id: 3,
                            customer: {
                                full_name: 'Mike Johnson',
                                phone: '9876543212'
                            },
                            service: {
                                name: 'AC Maintenance'
                            },
                            preferred_time: new Date('2024-03-28T11:00:00'),
                            description: 'Regular maintenance',
                            review: {
                                rating: 5,
                                comment: 'Excellent service!'
                            }
                        }
                    ]
                };
            } catch (err) {
                error.value = 'Failed to load service requests';
                console.error('Error fetching requests:', err);
            } finally {
                loading.value = false;
            }
        };

        const handleAccept = async (requestId) => {
            try {
                processing.value = requestId;
                // Replace with actual API call
                await new Promise(resolve => setTimeout(resolve, 1000));

                // Move request from pending to active
                const request = requests.value.pending.find(r => r.id === requestId);
                requests.value.pending = requests.value.pending.filter(r => r.id !== requestId);
                requests.value.active.push(request);

                window.showToast({
                    type: 'success',
                    title: 'Success',
                    message: 'Request accepted successfully'
                });
            } catch (err) {
                error.value = 'Failed to accept request';
                console.error('Error accepting request:', err);
            } finally {
                processing.value = null;
            }
        };

        const handleReject = async (requestId) => {
            try {
                processing.value = requestId;
                // Replace with actual API call
                await new Promise(resolve => setTimeout(resolve, 1000));

                requests.value.pending = requests.value.pending.filter(r => r.id !== requestId);

                window.showToast({
                    type: 'success',
                    title: 'Success',
                    message: 'Request rejected successfully'
                });
            } catch (err) {
                error.value = 'Failed to reject request';
                console.error('Error rejecting request:', err);
            } finally {
                processing.value = null;
            }
        };

        const openCompleteModal = (request) => {
            selectedRequest.value = request;
            completionRemarks.value = '';
            const modal = new Modal(completeModal.value);
            modal.show();
        };

        const handleComplete = async () => {
            if (!selectedRequest.value || !completionRemarks.value.trim()) return;

            try {
                processing.value = selectedRequest.value.id;
                // Replace with actual API call
                await new Promise(resolve => setTimeout(resolve, 1000));

                const request = requests.value.active.find(r => r.id === selectedRequest.value.id);
                requests.value.active = requests.value.active.filter(r => r.id !== selectedRequest.value.id);
                requests.value.completed.push({
                    ...request,
                    remarks: completionRemarks.value
                });

                const modal = Modal.getInstance(completeModal.value);
                modal.hide();

                window.showToast({
                    type: 'success',
                    title: 'Success',
                    message: 'Service completed successfully'
                });
            } catch (err) {
                error.value = 'Failed to complete service';
                console.error('Error completing service:', err);
            } finally {
                processing.value = null;
                selectedRequest.value = null;
            }
        };

        const viewDetails = (request) => {
            // Implement view details functionality
            console.log('View details:', request);
        };

        const formatDate = (date) => {
            return moment(date).format('MMM D, YYYY');
        };

        const formatTime = (date) => {
            return moment(date).format('h:mm A');
        };

        onMounted(() => {
            fetchRequests();
        });

        return {
            activeTab,
            tabs,
            loading,
            error,
            processing,
            requests,
            completeModal,
            completionRemarks,
            requestCounts,
            filteredRequests,
            handleAccept,
            handleReject,
            openCompleteModal,
            handleComplete,
            viewDetails,
            formatDate,
            formatTime
        };
    }
};
</script>

<style scoped>
.nav-tabs .nav-link {
    color: #6c757d;
    cursor: pointer;
}

.nav-tabs .nav-link.active {
    color: #0d6efd;
    font-weight: 500;
}

.card {
    transition: transform 0.2s;
}

.card:hover {
    transform: translateY(-2px);
}

.rating i {
    font-size: 0.875rem;
    margin-right: 2px;
}
</style>