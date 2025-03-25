<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">My Service Requests</h1>
        <p class="text-muted">Track and manage your service requests</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <!-- Status Filter -->
          <div class="col-md-3">
            <label for="statusFilter" class="form-label">Status</label>
            <select
              id="statusFilter"
              class="form-select"
              v-model="filters.status"
              @change="applyFilters"
            >
              <option value="">All Requests</option>
              <option value="created">Pending</option>
              <option value="assigned">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          <!-- Date Range Filters -->
          <div class="col-md-3">
            <label for="startDate" class="form-label">From Date</label>
            <input
              type="date"
              id="startDate"
              class="form-control"
              v-model="filters.start_date"
              @change="validateDateRange"
            />
          </div>

          <div class="col-md-3">
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
          <div class="col-md-3">
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
          <p class="mt-2 text-muted">Loading your service requests...</p>
        </div>

        <div v-else-if="requests.length === 0" class="text-center p-5">
          <i class="bi bi-clipboard-x text-muted" style="font-size: 3rem"></i>
          <p class="mt-3 mb-0">No service requests found.</p>
          <button class="btn btn-link mt-2" @click="resetFilters">Reset filters</button>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover table-striped mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Service</th>
                <th scope="col">Professional</th>
                <th scope="col">Scheduled Date</th>
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
                  <div v-if="request.professional">
                    <div class="fw-medium">{{ request.professional.full_name }}</div>
                    <div
                      class="d-flex align-items-center"
                      v-if="request.professional.average_rating"
                    >
                      <i class="bi bi-star-fill text-warning me-1"></i>
                      <small>{{ request.professional.average_rating }}</small>
                    </div>
                  </div>
                  <span v-else class="badge bg-secondary">Not Assigned</span>
                </td>
                <td>
                  <div>{{ formatDate(request.preferred_time) }}</div>
                  <small class="text-muted">{{ formatTime(request.preferred_time) }}</small>
                </td>
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

                    <!-- Cancel Request (only for "created" status) -->
                    <button
                      v-if="request.status === 'created'"
                      class="btn btn-sm btn-outline-danger"
                      @click="confirmCancelRequest(request)"
                      title="Cancel request"
                    >
                      <i class="bi bi-x-circle"></i>
                    </button>

                    <!-- Complete Request (only for "assigned" status) -->
                    <button
                      v-if="request.status === 'assigned'"
                      class="btn btn-sm btn-outline-success"
                      @click="confirmCompleteRequest(request)"
                      title="Mark as completed"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>

                    <!-- Review Button (only for "completed" status and no review) -->
                    <button
                      v-if="request.status === 'completed' && !request.has_review"
                      class="btn btn-sm btn-outline-warning"
                      @click="openReviewModal(request)"
                      title="Submit review"
                    >
                      <i class="bi bi-star"></i>
                    </button>

                    <!-- View Review Button (if review exists) -->
                    <button
                      v-if="request.has_review"
                      class="btn btn-sm btn-outline-info"
                      @click="viewRequestDetails(request)"
                      title="View review"
                    >
                      <i class="bi bi-star-half"></i>
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
              <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
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
                          <h6 class="mb-0 fw-bold">Professional Assigned</h6>
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
                      <label class="form-label text-muted small">Scheduled Date & Time</label>
                      <div class="fw-medium">
                        {{ formatDateTime(selectedRequest.preferred_time) }}
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

              <!-- Professional Information -->
              <div class="col-md-12" v-if="selectedRequest.professional">
                <div class="card border">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Professional Information</h6>
                  </div>
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                      <div class="avatar me-3 bg-light rounded-circle">
                        <i class="bi bi-person-badge"></i>
                      </div>
                      <div>
                        <div class="fw-bold">{{ selectedRequest.professional.full_name }}</div>
                        <div
                          class="d-flex align-items-center"
                          v-if="selectedRequest.professional.average_rating"
                        >
                          <i class="bi bi-star-fill text-warning me-1"></i>
                          <small>{{ selectedRequest.professional.average_rating }}</small>
                        </div>
                      </div>
                    </div>

                    <div class="mb-2 row">
                      <div class="col-md-4 text-muted">Phone:</div>
                      <div class="col-md-8">{{ selectedRequest.professional.phone }}</div>
                    </div>

                    <div class="mb-2 row" v-if="selectedRequest.professional.experience_years">
                      <div class="col-md-4 text-muted">Experience:</div>
                      <div class="col-md-8">
                        {{ selectedRequest.professional.experience_years }} years
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Review Information (if exists) -->
              <div class="col-md-12" v-if="selectedRequest.has_review && selectedRequest.review">
                <div class="card border">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Your Review</h6>
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
              class="btn btn-danger"
              @click="confirmCancelRequest(selectedRequest)"
            >
              <i class="bi bi-x-circle me-1"></i> Cancel Request
            </button>

            <button
              v-if="selectedRequest.status === 'assigned'"
              type="button"
              class="btn btn-success"
              @click="confirmCompleteRequest(selectedRequest)"
            >
              <i class="bi bi-check-circle me-1"></i> Mark as Completed
            </button>

            <button
              v-if="selectedRequest.status === 'completed' && !selectedRequest.has_review"
              type="button"
              class="btn btn-warning"
              @click="openReviewModal(selectedRequest)"
            >
              <i class="bi bi-star me-1"></i> Submit Review
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Modal -->
    <div
      class="modal fade"
      id="reviewModal"
      tabindex="-1"
      aria-labelledby="reviewModalLabel"
      aria-hidden="true"
      ref="reviewModal"
    >
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title" id="reviewModalLabel">
              <i class="bi bi-star me-2"></i>Review Service
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <p>
                You're reviewing service provided by
                <strong>{{ selectedRequest.professional?.full_name }}</strong>
              </p>
            </div>

            <div class="mb-4">
              <label class="form-label">Rating</label>
              <div class="rating-container">
                <span v-for="i in 5" :key="i" class="rating-star" @click="review.rating = i">
                  <i
                    class="bi"
                    :class="i <= review.rating ? 'bi-star-fill text-warning' : 'bi-star'"
                  ></i>
                </span>
              </div>
            </div>

            <div class="mb-3">
              <label for="reviewComment" class="form-label">Comments</label>
              <textarea
                id="reviewComment"
                class="form-control"
                v-model="review.comment"
                rows="4"
                placeholder="Share your experience with this service..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-primary"
              @click="submitReview"
              :disabled="!review.rating || !review.comment || isSubmittingReview"
            >
              <i
                class="bi"
                :class="isSubmittingReview ? 'bi-hourglass-split' : 'bi-check-circle'"
              ></i>
              {{ isSubmittingReview ? 'Submitting...' : 'Submit Review' }}
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
              <i class="bi bi-check-circle-fill text-success me-2"></i>Complete Service Request
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
              Once a request is marked as completed, you'll be able to submit a review for the
              service.
            </div>

            <div class="mb-3">
              <label for="completionRemarks" class="form-label">Remarks (Optional)</label>
              <textarea
                id="completionRemarks"
                class="form-control"
                v-model="completionRemarks"
                rows="3"
                placeholder="Add any comments about the service completion..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-success"
              @click="completeRequest"
              :disabled="isProcessing"
            >
              <i class="bi" :class="isProcessing ? 'bi-hourglass-split' : 'bi-check-circle'"></i>
              {{ isProcessing ? 'Processing...' : 'Confirm Completion' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel Request Confirmation Modal -->
    <div
      class="modal fade"
      id="cancelRequestModal"
      tabindex="-1"
      aria-labelledby="cancelRequestModalLabel"
      aria-hidden="true"
      ref="cancelModal"
    >
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title" id="cancelRequestModalLabel">
              <i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>Cancel Service Request
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to cancel this service request?</p>

            <div class="alert alert-warning">
              <i class="bi bi-exclamation-circle-fill me-2"></i>
              This action cannot be undone. You'll need to create a new request if you need this
              service in the future.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              No, Keep Request
            </button>
            <button
              type="button"
              class="btn btn-danger"
              @click="cancelRequest"
              :disabled="isProcessing"
            >
              <i class="bi" :class="isProcessing ? 'bi-hourglass-split' : 'bi-x-circle'"></i>
              {{ isProcessing ? 'Processing...' : 'Yes, Cancel Request' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import * as bootstrap from 'bootstrap'
import { requestStatusBadges, statusLabels } from '@/assets/requestStatuses'
import { formatDate, formatDateTime, formatTime } from '@/utils/date'
import { useLoading } from '@/composables/useLoading'
import { useRoute } from 'vue-router'

export default defineComponent({
  name: 'CustomerRequests',

  setup() {
    const store = useStore()
    const { isLoading, withLoading } = useLoading()

    // References to modals
    const detailModal = ref(null)
    const reviewModal = ref(null)
    const completeModal = ref(null)
    const cancelModal = ref(null)

    let bsDetailModal = null
    let bsReviewModal = null
    let bsCompleteModal = null
    let bsCancelModal = null

    const route = useRoute()

    // State
    const requests = computed(() => store.getters['requests/allRequests'])
    const pagination = computed(() => store.getters['requests/pagination'])
    const selectedRequest = ref(null)
    const isProcessing = ref(false)
    const isSubmittingReview = ref(false)

    // Form data
    const review = ref({
      rating: 0,
      comment: '',
    })

    const completionRemarks = ref('')

    // Filters
    const filters = ref({
      status: '',
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

    // Methods
    const fetchRequests = async (forceRefresh = false) => {
      // Start with empty params object
      const params = {}

      // Only add non-empty filters
      Object.entries(filters.value).forEach(([key, value]) => {
        // Include parameters that have values (not empty strings, null, or undefined)
        if (value !== '' && value !== null && value !== undefined) {
          params[key] = value
        }
      })

      try {
        await withLoading(
          store.dispatch('requests/fetchCustomerRequests', { params, forceRefresh }),
          'Loading your service requests...',
        )
      } catch (error) {
        console.error('Error fetching requests:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load requests',
        })
      }
    }

    const getStatusBadgeClass = (status) => requestStatusBadges[status]
    const getStatusLabel = (status) => statusLabels[status]

    const viewRequestDetails = (request) => {
      selectedRequest.value = request
      bsDetailModal.show()
    }

    const openReviewModal = (request) => {
      selectedRequest.value = request
      // Reset review form
      review.value = {
        rating: 0,
        comment: '',
      }
      bsReviewModal.show()
    }

    const submitReview = async () => {
      if (!review.value.rating) {
        window.showToast({
          type: 'warning',
          title: 'Please select a rating',
        })
        return
      }

      try {
        isSubmittingReview.value = true

        await store.dispatch('requests/submitReview', {
          id: selectedRequest.value.id,
          data: {
            rating: review.value.rating,
            comment: review.value.comment.trim() || null,
          },
        })

        // Close the modal
        bsReviewModal.hide()

        // Success message
        window.showToast({
          type: 'success',
          title: 'Review submitted successfully',
        })

        // Refresh requests
        await fetchRequests(true)
      } catch (error) {
        console.error('Error submitting review:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to submit review',
        })
      } finally {
        isSubmittingReview.value = false
      }
    }

    const confirmCompleteRequest = (request) => {
      selectedRequest.value = request
      completionRemarks.value = ''
      bsCompleteModal.show()
    }

    const completeRequest = async () => {
      try {
        isProcessing.value = true

        await store.dispatch('requests/completeRequest', {
          id: selectedRequest.value.id,
          data: {
            remarks: completionRemarks.value.trim() || 'Service completed successfully',
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
          title: 'Request marked as completed',
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

    const confirmCancelRequest = (request) => {
      selectedRequest.value = request
      bsCancelModal.show()
    }

    const cancelRequest = async () => {
      try {
        isProcessing.value = true

        await store.dispatch('requests/cancelRequest', {
          id: selectedRequest.value.id,
        })

        // Close modals
        bsCancelModal.hide()
        if (bsDetailModal && bsDetailModal._isShown) {
          bsDetailModal.hide()
        }

        // Success message
        window.showToast({
          type: 'success',
          title: 'Request cancelled successfully',
        })

        // Refresh requests
        await fetchRequests(true)
      } catch (error) {
        console.error('Error cancelling request:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to cancel request',
        })
      } finally {
        isProcessing.value = false
      }
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
      fetchRequests()
    }

    const resetFilters = () => {
      filters.value = {
        status: '',
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

    const checkQueryParams = () => {
      // Only proceed if we have a professional ID in query params AND professionals are loaded
      if (route.query.status) {
        filters.value.status = route.query.status
      }

      fetchRequests(true)
    }

    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      if (detailModal.value) {
        bsDetailModal = new bootstrap.Modal(detailModal.value)
      }

      if (reviewModal.value) {
        bsReviewModal = new bootstrap.Modal(reviewModal.value)
      }

      if (completeModal.value) {
        bsCompleteModal = new bootstrap.Modal(completeModal.value)
      }

      if (cancelModal.value) {
        bsCancelModal = new bootstrap.Modal(cancelModal.value)
      }

      // Fetch initial data
      await fetchRequests()

      checkQueryParams()
    })

    return {
      // State
      requests,
      pagination,
      paginationRange,
      selectedRequest,
      review,
      completionRemarks,
      filters,
      isLoading,
      isProcessing,
      isSubmittingReview,

      // Refs
      detailModal,
      reviewModal,
      completeModal,
      cancelModal,

      // Methods
      fetchRequests,
      viewRequestDetails,
      openReviewModal,
      submitReview,
      confirmCompleteRequest,
      completeRequest,
      confirmCancelRequest,
      cancelRequest,
      validateDateRange,
      applyFilters,
      resetFilters,
      changePage,
      getStatusBadgeClass,
      getStatusLabel,
      formatDate,
      formatDateTime,
      formatTime,
      checkQueryParams,
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

/* Star rating styles */
.rating-container {
  display: flex;
  gap: 0.5rem;
}

.rating-star {
  cursor: pointer;
  font-size: 1.5rem;
  transition: transform 0.1s;
}

.rating-star:hover {
  transform: scale(1.2);
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

  .rating-container {
    gap: 0.25rem;
  }

  .rating-star {
    font-size: 1.25rem;
  }
}
</style>
