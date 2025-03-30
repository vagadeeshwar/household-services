<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">Service Requests</h1>
        <p class="text-muted">View, accept and manage service requests assigned to you</p>
      </div>
    </div>

    <!-- Request Type Tabs -->
    <div class="card mb-4">
      <div class="card-body">
        <ul class="nav nav-pills mb-3">
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: filters.type === 'available' }"
              href="#"
              @click.prevent="changeRequestType('available')"
            >
              <i class="bi bi-inbox me-1"></i> Available
              <span class="badge bg-primary ms-1" v-if="requestCounts.available">
                {{ requestCounts.available }}
              </span>
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: filters.type === 'ongoing' }"
              href="#"
              @click.prevent="changeRequestType('ongoing')"
            >
              <i class="bi bi-hourglass-split me-1"></i> Ongoing
              <span class="badge bg-primary ms-1" v-if="requestCounts.ongoing">
                {{ requestCounts.ongoing }}
              </span>
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: filters.type === 'completed' }"
              href="#"
              @click.prevent="changeRequestType('completed')"
            >
              <i class="bi bi-check2-all me-1"></i> Completed
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: filters.type === 'all' }"
              href="#"
              @click.prevent="changeRequestType('all')"
            >
              <i class="bi bi-list me-1"></i> All Requests
            </a>
          </li>
        </ul>

        <!-- Additional Filters -->
        <div class="row g-3 mt-2">
          <!-- Date Range Filters -->
          <div class="col-md-4">
            <label for="startDate" class="form-label">From Date</label>
            <input
              type="date"
              id="startDate"
              class="form-control"
              v-model="filters.start_date"
              @change="validateDateRange"
            />
          </div>
          <div class="col-md-4">
            <label for="endDate" class="form-label">To Date</label>
            <input
              type="date"
              id="endDate"
              class="form-control"
              v-model="filters.end_date"
              @change="applyFilters"
              :min="filters.start_date"
            />
          </div>

          <!-- Reset Button -->
          <div class="col-md-4">
            <label class="form-label d-block">&nbsp;</label>
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset Filters
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Requests Display -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="isLoading" class="text-center p-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading service requests...</p>
        </div>

        <div v-else-if="requests.length === 0" class="text-center p-5">
          <div v-if="filters.type === 'available'">
            <i class="bi bi-inbox text-muted" style="font-size: 3rem"></i>
            <p class="mt-3 mb-0">No service requests available to accept at the moment.</p>
            <p class="text-muted">Check back later or try changing your filters.</p>
          </div>
          <div v-else-if="filters.type === 'ongoing'">
            <i class="bi bi-hourglass text-muted" style="font-size: 3rem"></i>
            <p class="mt-3 mb-0">You have no ongoing service requests.</p>
            <p class="text-muted">Check available requests to start working on new assignments.</p>
          </div>
          <div v-else>
            <i class="bi bi-clipboard-x text-muted" style="font-size: 3rem"></i>
            <p class="mt-3 mb-0">No service requests found.</p>
            <button class="btn btn-link mt-2" @click="resetFilters">Reset filters</button>
          </div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover table-striped mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Service</th>
                <th scope="col">Customer</th>
                <th scope="col">Request Date</th>
                <th scope="col">Status</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in requests" :key="request.id" class="align-middle">
                <td>{{ request.id }}</td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="service-icon me-2">
                      <i class="bi bi-tools"></i>
                    </div>
                    <div>
                      <div class="fw-bold">{{ request.service_name }}</div>
                      <small class="text-muted">₹{{ request.service_price }}</small>
                    </div>
                  </div>
                </td>
                <td>
                  <div v-if="request.customer">
                    <div class="fw-medium">{{ request.customer.full_name }}</div>
                    <small class="text-muted">{{ request.customer.phone }}</small>
                  </div>
                  <span v-else class="text-muted">Unknown Customer</span>
                </td>
                <td>{{ formatDate(request.date_of_request) }}</td>

                <td>
                  <span class="badge" :class="getStatusBadgeClass(request.status)">
                    {{ getStatusLabel(request.status) }}
                  </span>
                </td>
                <td>
                  <div class="btn-group">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="viewRequestDetails(request)"
                      title="View details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>

                    <!-- Accept Request (only for "created" status) -->
                    <button
                      v-if="request.status === 'created' && filters.type === 'available'"
                      class="btn btn-sm btn-outline-success"
                      @click="confirmAcceptRequest(request)"
                      title="Accept request"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>

                    <!-- Complete Request (only for "assigned" status) -->
                    <button
                      v-if="
                        request.status === 'assigned' &&
                        filters.type !== 'available' &&
                        filters.type !== 'completed'
                      "
                      class="btn btn-sm btn-outline-success"
                      @click="confirmCompleteRequest(request)"
                      title="Mark as completed"
                    >
                      <i class="bi bi-check2-all"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Pagination -->
      <div class="card-footer bg-white d-flex justify-content-between align-items-center">
        <div>
          <span class="text-muted"
            >Showing {{ requests.length }} of {{ pagination.total || 0 }} requests</span
          >
        </div>
        <nav aria-label="Requests pagination" v-if="pagination.pages > 1">
          <ul class="pagination pagination-sm mb-0">
            <li class="page-item" :class="{ disabled: !pagination.has_prev }">
              <a
                class="page-link"
                href="#"
                @click.prevent="changePage(pagination.current_page - 1)"
                aria-label="Previous"
              >
                <span aria-hidden="true">&laquo;</span>
              </a>
            </li>
            <li
              v-for="page in paginationRange"
              :key="page"
              class="page-item"
              :class="{ active: page === pagination.current_page }"
            >
              <a class="page-link" href="#" @click.prevent="changePage(page)">
                {{ page }}
              </a>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.has_next }">
              <a
                class="page-link"
                href="#"
                @click.prevent="changePage(pagination.current_page + 1)"
                aria-label="Next"
              >
                <span aria-hidden="true">&raquo;</span>
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Request Details Modal -->
    <div
      class="modal fade"
      id="requestDetailModal"
      tabindex="-1"
      aria-labelledby="requestDetailModalLabel"
      aria-hidden="true"
      ref="detailModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title" id="requestDetailModalLabel">
              Request #{{ selectedRequest.id }} Details
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <!-- Request Overview -->
            <div class="d-flex justify-content-between align-items-start mb-4">
              <div>
                <h6 class="fs-5 mb-2">{{ selectedRequest.service_name }}</h6>
                <span class="badge" :class="getStatusBadgeClass(selectedRequest.status)">
                  {{ getStatusLabel(selectedRequest.status) }}
                </span>
              </div>
              <div class="text-end">
                <div class="fw-bold">₹{{ selectedRequest.service_price }}</div>
                <div class="text-muted">Request #{{ selectedRequest.id }}</div>
              </div>
            </div>

            <div class="row g-4">
              <!-- Request Timeline -->
              <div class="col-md-6">
                <div class="card h-100 border">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Request Timeline</h6>
                  </div>
                  <div class="card-body">
                    <ul class="timeline">
                      <li class="timeline-item mb-3">
                        <div class="timeline-marker bg-primary"></div>
                        <div class="timeline-content">
                          <h6 class="mb-0 fw-bold">Request Created</h6>
                          <div class="text-muted">
                            {{ formatDateTime(selectedRequest.date_of_request) }}
                          </div>
                        </div>
                      </li>
                      <li class="timeline-item mb-3" v-if="selectedRequest.date_of_assignment">
                        <div class="timeline-marker bg-primary"></div>
                        <div class="timeline-content">
                          <h6 class="mb-0 fw-bold">You Accepted Request</h6>
                          <div class="text-muted">
                            {{ formatDateTime(selectedRequest.date_of_assignment) }}
                          </div>
                        </div>
                      </li>
                      <li class="timeline-item" v-if="selectedRequest.date_of_completion">
                        <div class="timeline-marker bg-success"></div>
                        <div class="timeline-content">
                          <h6 class="mb-0 fw-bold">Service Completed</h6>
                          <div class="text-muted">
                            {{ formatDateTime(selectedRequest.date_of_completion) }}
                          </div>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- Request Details -->
              <div class="col-md-6">
                <div class="card h-100 border">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Request Details</h6>
                  </div>
                  <div class="card-body">
                    <div class="mb-3">
                      <label class="form-label text-muted small">Preferred Time</label>
                      <div class="fw-medium">
                        {{ formatLocalDateTime(selectedRequest.preferred_time) }}
                      </div>
                    </div>
                    <div class="mb-3" v-if="selectedRequest.description">
                      <label class="form-label text-muted small">Description</label>
                      <div>{{ selectedRequest.description }}</div>
                    </div>
                    <div v-if="selectedRequest.remarks">
                      <label class="form-label text-muted small">Completion Remarks</label>
                      <div>{{ selectedRequest.remarks }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Customer Information -->
              <div class="col-md-12">
                <div class="card border">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Customer Information</h6>
                  </div>
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                      <div class="avatar me-3 bg-light rounded-circle">
                        <i class="bi bi-person"></i>
                      </div>
                      <div>
                        <div class="fw-bold">{{ getCustomerName(selectedRequest) }}</div>
                      </div>
                    </div>
                    <div class="mb-2 row" v-if="selectedRequest.customer">
                      <div class="col-md-4 text-muted">Phone:</div>
                      <div class="col-md-8">{{ selectedRequest.customer.phone }}</div>
                    </div>
                    <div
                      class="mb-2 row"
                      v-if="selectedRequest.customer && selectedRequest.customer.address"
                    >
                      <div class="col-md-4 text-muted">Address:</div>
                      <div class="col-md-8">{{ selectedRequest.customer.address }}</div>
                    </div>
                    <div
                      class="row"
                      v-if="selectedRequest.customer && selectedRequest.customer.pin_code"
                    >
                      <div class="col-md-4 text-muted">PIN Code:</div>
                      <div class="col-md-8">{{ selectedRequest.customer.pin_code }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Review Information (if exists) -->
              <div class="col-md-12" v-if="selectedRequest.has_review && selectedRequest.review">
                <div class="card border">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Customer Review</h6>
                  </div>
                  <div class="card-body">
                    <div class="mb-2">
                      <span v-for="i in 5" :key="i" class="me-1">
                        <i
                          class="bi"
                          :class="
                            i <= selectedRequest.review.rating
                              ? 'bi-star-fill text-warning'
                              : 'bi-star text-muted'
                          "
                        ></i>
                      </span>
                      <span class="ms-2 fw-bold">{{ selectedRequest.review.rating }} / 5</span>
                    </div>
                    <div>{{ selectedRequest.review.comment || 'No comment provided' }}</div>
                    <div class="text-muted mt-2 small">
                      Submitted on {{ formatDateTime(selectedRequest.review.created_at) }}
                    </div>

                    <!-- Report Review Option -->
                    <div class="mt-3" v-if="!selectedRequest.review.is_reported">
                      <button
                        class="btn btn-sm btn-outline-danger"
                        @click="openReportReviewModal(selectedRequest.review)"
                      >
                        <i class="bi bi-flag me-1"></i> Report Review
                      </button>
                    </div>
                    <div class="alert alert-warning mt-3" v-else>
                      <i class="bi bi-exclamation-triangle-fill me-2"></i>
                      <strong>You have reported this review</strong>
                      <div v-if="selectedRequest.review.report_reason">
                        Reason: {{ selectedRequest.review.report_reason }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <!-- Action buttons based on status -->
            <button
              v-if="selectedRequest.status === 'created'"
              type="button"
              class="btn btn-success"
              @click="confirmAcceptRequest(selectedRequest)"
            >
              <i class="bi bi-check-circle me-1"></i> Accept Request
            </button>
            <button
              v-if="selectedRequest.status === 'assigned'"
              type="button"
              class="btn btn-success"
              @click="confirmCompleteRequest(selectedRequest)"
            >
              <i class="bi bi-check2-all me-1"></i> Mark as Completed
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Accept Request Confirmation Modal -->
    <div
      class="modal fade"
      id="acceptRequestModal"
      tabindex="-1"
      aria-labelledby="acceptRequestModalLabel"
      aria-hidden="true"
      ref="acceptModal"
    >
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title" id="acceptRequestModalLabel">
              <i class="bi bi-check-circle-fill text-success me-2"></i>Accept Service Request
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to accept this service request?</p>

            <div class="alert alert-info">
              <i class="bi bi-info-circle-fill me-2"></i>
              By accepting this request, you commit to providing service with your full effort.
              Please check your availability before confirming.
            </div>

            <div class="card mb-3">
              <div class="card-body">
                <div class="mb-2"><strong>Service:</strong> {{ selectedRequest.service_name }}</div>
                <div class="mb-2">
                  <strong>Customer:</strong> {{ getCustomerName(selectedRequest) }}
                </div>
                <div class="mb-2">
                  <strong>Preferred Time:</strong>
                  {{ formatLocalDateTime(selectedRequest.preferred_time) }}
                </div>
                <div v-if="selectedRequest.description">
                  <strong>Description:</strong> {{ selectedRequest.description }}
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-success"
              @click="acceptRequest"
              :disabled="isProcessing"
            >
              <i class="bi" :class="isProcessing ? 'bi-hourglass-split' : 'bi-check-circle'"></i>
              {{ isProcessing ? 'Processing...' : 'Confirm Acceptance' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Request Modal -->
    <div
      class="modal fade"
      id="completeRequestModal"
      tabindex="-1"
      aria-labelledby="completeRequestModalLabel"
      aria-hidden="true"
      ref="completeModal"
    >
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title" id="completeRequestModalLabel">
              <i class="bi bi-check2-all text-success me-2"></i>Complete Service Request
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to mark this service request as completed?</p>

            <div class="alert alert-info">
              <i class="bi bi-info-circle-fill me-2"></i>
              Please provide completion remarks detailing the work performed. The customer will be
              notified once the request is marked as completed.
            </div>

            <div class="mb-3">
              <label for="completionRemarks" class="form-label"
                >Completion Remarks <span class="text-danger">*</span></label
              >
              <textarea
                id="completionRemarks"
                class="form-control"
                v-model="completionRemarks"
                rows="3"
                placeholder="Describe the work completed, parts replaced, or any other relevant information..."
                required
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-success"
              @click="completeRequest"
              :disabled="isProcessing || !completionRemarks.trim()"
            >
              <i class="bi" :class="isProcessing ? 'bi-hourglass-split' : 'bi-check2-all'"></i>
              {{ isProcessing ? 'Processing...' : 'Confirm Completion' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- Report Review Modal -->
    <div
      class="modal fade"
      id="reportReviewModal"
      tabindex="-1"
      aria-labelledby="reportReviewModalLabel"
      aria-hidden="true"
      ref="reportModal"
    >
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedReview">
          <div class="modal-header">
            <h5 class="modal-title" id="reportReviewModalLabel">
              <i class="bi bi-flag-fill text-danger me-2"></i>Report Review
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>Please enter a reason for reporting this review:</p>

            <div class="mb-3">
              <label for="reportReason" class="form-label"
                >Reason <span class="text-danger">*</span></label
              >
              <textarea
                id="reportReason"
                class="form-control"
                v-model="reportReason"
                rows="3"
                placeholder="Please provide details about why you're reporting this review (minimum 10 characters)..."
                required
              ></textarea>
              <div class="form-text text-danger" v-if="reportReason && reportReason.length < 10">
                Please provide at least 10 characters
              </div>
            </div>

            <div class="alert alert-warning">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              Reported reviews will be evaluated by our admin team. False reports may affect your
              account status.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-danger"
              @click="submitReviewReport"
              :disabled="isProcessing || !isValidReport"
            >
              <i class="bi" :class="isProcessing ? 'bi-hourglass-split' : 'bi-flag'"></i>
              {{ isProcessing ? 'Processing...' : 'Submit Report' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import * as bootstrap from 'bootstrap'
import { requestStatusBadges, statusLabels } from '@/assets/requestStatuses'
import { formatDate, formatDateTime, formatTime } from '@/utils/date'
import { useLoading } from '@/composables/useLoading'

export default defineComponent({
  name: 'ProfessionalRequests',

  setup() {
    const store = useStore()
    const { isLoading, withLoading } = useLoading()

    // References to modals
    const detailModal = ref(null)
    const acceptModal = ref(null)
    const completeModal = ref(null)
    const reportModal = ref(null)
    let bsDetailModal = null
    let bsAcceptModal = null
    let bsCompleteModal = null
    let bsReportModal = null

    // State
    const requests = computed(() => store.getters['requests/allRequests'])
    const pagination = computed(() => store.getters['requests/pagination'])
    const selectedRequest = ref(null)
    const selectedReview = ref(null)
    const isProcessing = ref(false)
    const completionRemarks = ref('')
    const reportReason = ref('')
    const reportDetails = ref('')
    const requestCounts = ref({
      available: 0,
      ongoing: 0,
      completed: 0,
    })

    // Filters
    const filters = ref({
      type: 'available',
      start_date: '',
      end_date: '',
      page: 1,
      per_page: 10,
    })

    // Computed
    const paginationRange = computed(() => {
      const current = pagination.value.current_page
      const total = pagination.value.pages
      const range = []

      // Show 5 pages at most
      const maxPages = 5
      const start = Math.max(1, current - Math.floor(maxPages / 2))
      const end = Math.min(total, start + maxPages - 1)

      for (let i = start; i <= end; i++) {
        range.push(i)
      }

      return range
    })

    const isValidReport = computed(() => {
      // Check if report reason has at least 10 characters
      return reportReason.value && reportReason.value.trim().length >= 10
    })

    // Methods
    const fetchRequests = async (forceRefresh = false) => {
      // Start with empty params object
      const params = { ...filters.value }

      // Only add non-empty filters
      Object.keys(params).forEach((key) => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key]
        }
      })

      try {
        const response = await withLoading(
          store.dispatch('requests/fetchProfessionalRequests', {
            params,
            forceRefresh,
          }),
          'Loading service requests...',
        )

        // Update request counts if summary data is available
        if (response && response.data && response.data.total_requests) {
          updateRequestCounts(response.data)
        }
      } catch (error) {
        console.error('Error fetching requests:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load requests',
        })
      }
    }

    const formatLocalDateTime = (dateString) => {
      if (!dateString) return 'N/A'

      const date = new Date(dateString)

      // Format options for a nice readable date and time
      const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      }

      return new Intl.DateTimeFormat('en-US', options).format(date)
    }

    const updateRequestCounts = (data) => {
      // Update the counts if the data contains the necessary information
      if (data.active_requests !== undefined) {
        requestCounts.value.ongoing = data.active_requests
      }

      if (data.available_requests !== undefined) {
        requestCounts.value.available = data.available_requests
      } else if (data.pending_requests !== undefined) {
        requestCounts.value.available = data.pending_requests
      }

      if (data.completed_requests !== undefined) {
        requestCounts.value.completed = data.completed_requests
      }
    }

    const getStatusBadgeClass = (status) => requestStatusBadges[status]
    const getStatusLabel = (status) => statusLabels[status]

    const viewRequestDetails = (request) => {
      selectedRequest.value = request
      bsDetailModal.show()
    }

    const getCustomerName = (request) => {
      if (request.customer && request.customer.full_name) {
        return request.customer.full_name
      }

      if (request.customer_name) {
        return request.customer_name
      }

      return 'Unknown Customer'
    }

    const confirmAcceptRequest = (request) => {
      selectedRequest.value = request
      bsAcceptModal.show()
    }

    const acceptRequest = async () => {
      try {
        isProcessing.value = true

        await store.dispatch('requests/acceptRequest', {
          id: selectedRequest.value.id,
        })

        // Close modals
        bsAcceptModal.hide()
        if (bsDetailModal && bsDetailModal._isShown) {
          bsDetailModal.hide()
        }

        // Success message
        window.showToast({
          type: 'success',
          title: 'The customer has been notified that you have accepted their request.',
        })

        // Refresh requests
        await fetchRequests(true)
      } catch (error) {
        console.error('Error accepting request:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to accept request',
        })
      } finally {
        isProcessing.value = false
      }
    }

    const confirmCompleteRequest = (request) => {
      selectedRequest.value = request
      completionRemarks.value = ''
      bsCompleteModal.show()
    }

    const completeRequest = async () => {
      if (!completionRemarks.value.trim()) {
        window.showToast({
          type: 'warning',
          title: 'Please provide details about the work you completed.',
        })
        return
      }

      try {
        isProcessing.value = true

        await store.dispatch('requests/completeRequest', {
          id: selectedRequest.value.id,
          data: {
            remarks: completionRemarks.value.trim(),
          },
        })

        // Close modals
        bsCompleteModal.hide()
        if (bsDetailModal && bsDetailModal._isShown) {
          bsDetailModal.hide()
        }

        // Success message
        window.showToast({
          type: 'success',
          title: 'The customer has been notified that you have completed their request.',
        })

        // Refresh requests
        await fetchRequests(true)
      } catch (error) {
        console.error('Error completing request:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to complete request',
        })
      } finally {
        isProcessing.value = false
      }
    }

    const openReportReviewModal = (review) => {
      selectedReview.value = review
      reportReason.value = '' // Reset the report reason
      bsReportModal.show()
    }
    const submitReviewReport = async () => {
      if (!isValidReport.value) {
        window.showToast({
          type: 'warning',
          title: 'Please provide a reason with at least 10 characters.',
        })
        return
      }

      try {
        isProcessing.value = true

        await store.dispatch('requests/reportReview', {
          id: selectedReview.value.id,
          data: {
            report_reason: reportReason.value.trim(),
          },
        })

        // Close modal
        bsReportModal.hide()
        bsDetailModal.hide()

        // Success message
        window.showToast({
          type: 'success',
          title: 'Our team will review your report and take appropriate action.',
        })

        await fetchRequests(true)

        isProcessing.value = false
      } catch (error) {
        console.error('Error reporting review:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to report review',
        })
        isProcessing.value = false
      }
    }

    const changeRequestType = (type) => {
      filters.value.type = type
      filters.value.page = 1
      fetchRequests(true)
    }

    const validateDateRange = () => {
      if (filters.value.start_date && filters.value.end_date) {
        const startDate = new Date(filters.value.start_date)
        const endDate = new Date(filters.value.end_date)
        if (startDate > endDate) {
          // If start date is after end date, update end date to match start date
          filters.value.end_date = filters.value.start_date
        }
      }
      applyFilters()
    }

    const applyFilters = () => {
      filters.value.page = 1
      fetchRequests(true)
    }

    const resetFilters = () => {
      const currentType = filters.value.type
      filters.value = {
        type: currentType, // Keep the current tab selection
        start_date: '',
        end_date: '',
        page: 1,
        per_page: 10,
      }
      fetchRequests(true)
    }

    const changePage = (page) => {
      if (page < 1 || page > pagination.value.pages) return
      filters.value.page = page
      fetchRequests()
    }

    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      if (detailModal.value) {
        bsDetailModal = new bootstrap.Modal(detailModal.value)
      }
      if (acceptModal.value) {
        bsAcceptModal = new bootstrap.Modal(acceptModal.value)
      }
      if (completeModal.value) {
        bsCompleteModal = new bootstrap.Modal(completeModal.value)
      }
      if (reportModal.value) {
        bsReportModal = new bootstrap.Modal(reportModal.value)
      }

      // Fetch initial data
      await fetchRequests()
    })

    // Watch for date filter changes
    watch(
      () => filters.value.start_date,
      (newVal) => {
        if (
          newVal &&
          filters.value.end_date &&
          new Date(newVal) > new Date(filters.value.end_date)
        ) {
          filters.value.end_date = newVal
        }
      },
    )

    return {
      // State
      requests,
      pagination,
      paginationRange,
      selectedRequest,
      selectedReview,
      completionRemarks,
      reportReason,
      reportDetails,
      filters,
      isLoading,
      isProcessing,
      isValidReport,
      requestCounts,

      // Refs
      detailModal,
      acceptModal,
      completeModal,
      reportModal,

      // Methods
      fetchRequests,
      viewRequestDetails,
      getCustomerName,
      confirmAcceptRequest,
      acceptRequest,
      confirmCompleteRequest,
      completeRequest,
      openReportReviewModal,
      submitReviewReport,
      changeRequestType,
      validateDateRange,
      applyFilters,
      resetFilters,
      changePage,
      getStatusBadgeClass,
      getStatusLabel,
      formatDate,
      formatDateTime,
      formatTime,
      formatLocalDateTime,
    }
  },
})
</script>

<style scoped>
.avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.table th,
.table td {
  vertical-align: middle;
}

.form-label {
  font-weight: 500;
}

.service-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  color: var(--bs-primary);
  border-radius: 4px;
}

/* Timeline styling */
.timeline {
  position: relative;
  padding-left: 1.5rem;
  list-style: none;
}

.timeline-marker {
  position: absolute;
  left: 0;
  height: 12px;
  width: 12px;
  border-radius: 50%;
  margin-top: 6px;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 5px;
  height: calc(100% - 12px);
  width: 2px;
  background-color: #e9ecef;
  margin-top: 18px;
}

/* Nav Pills Styling */
.nav-pills .nav-link {
  color: #495057;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  margin-right: 0.5rem;
}

.nav-pills .nav-link:hover {
  background-color: #e9ecef;
}

.nav-pills .nav-link.active {
  color: white;
  background-color: var(--bs-primary);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .btn-group {
    display: flex;
    flex-direction: column;
  }

  .btn-group .btn {
    border-radius: 0.25rem !important;
    margin-bottom: 0.25rem;
  }

  .nav-pills {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 0.5rem;
  }

  .nav-pills .nav-link {
    white-space: nowrap;
    font-size: 0.875rem;
  }
}
</style>
