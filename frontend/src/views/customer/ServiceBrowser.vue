<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-2">My Service Requests</h1>
        <p class="text-muted">Track and manage your service requests</p>
      </div>
      <div>
        <router-link to="/customer/services" class="btn btn-primary">
          <i class="bi bi-plus-circle me-2"></i>Book New Service
        </router-link>
      </div>
    </div>

    <!-- Request Filters -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-md-6">
            <ul class="nav nav-pills">
              <li class="nav-item">
                <a
                  class="nav-link"
                  :class="{ active: activeStatus === 'all' }"
                  @click.prevent="filterByStatus('all')"
                  href="#"
                >
                  All Requests
                </a>
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  :class="{ active: activeStatus === 'created' }"
                  @click.prevent="filterByStatus('created')"
                  href="#"
                >
                  <i class="bi bi-hourglass-split me-1"></i>Pending
                  <span
                    v-if="requestCountByStatus.created"
                    class="badge bg-light text-primary ms-1"
                  >
                    {{ requestCountByStatus.created }}
                  </span>
                </a>
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  :class="{ active: activeStatus === 'assigned' }"
                  @click.prevent="filterByStatus('assigned')"
                  href="#"
                >
                  <i class="bi bi-arrow-repeat me-1"></i>In Progress
                  <span
                    v-if="requestCountByStatus.assigned"
                    class="badge bg-light text-primary ms-1"
                  >
                    {{ requestCountByStatus.assigned }}
                  </span>
                </a>
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  :class="{ active: activeStatus === 'completed' }"
                  @click.prevent="filterByStatus('completed')"
                  href="#"
                >
                  <i class="bi bi-check2-circle me-1"></i>Completed
                </a>
              </li>
            </ul>
          </div>
          <div class="col-md-6 mt-3 mt-md-0">
            <div class="d-flex">
              <div class="input-group">
                <input
                  type="text"
                  class="form-control"
                  placeholder="Search requests..."
                  v-model="searchQuery"
                  @input="handleSearch"
                />
                <button class="btn btn-outline-secondary" type="button" @click="clearSearch">
                  <i class="bi bi-x"></i>
                </button>
              </div>
              <button class="btn btn-outline-primary ms-2" @click="refreshRequests">
                <i class="bi bi-arrow-clockwise"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading your service requests...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button @click="fetchRequests" class="btn btn-sm btn-outline-danger ms-2">Retry</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredRequests.length === 0" class="text-center py-5">
      <div class="py-4">
        <i class="bi bi-clipboard-x fs-1 text-muted mb-3 d-block"></i>
        <h5>No service requests found</h5>
        <p class="text-muted mb-4">
          {{
            activeStatus === 'all'
              ? 'You have not made any service requests yet.'
              : activeStatus === 'created'
                ? 'You have no pending service requests.'
                : activeStatus === 'assigned'
                  ? 'You have no ongoing service requests.'
                  : 'You have no completed service requests.'
          }}
        </p>
        <router-link to="/customer/services" class="btn btn-primary"> Book a Service </router-link>
      </div>
    </div>

    <!-- Service Requests List -->
    <div v-else class="card shadow-sm">
      <div class="list-group list-group-flush">
        <div v-for="request in paginatedRequests" :key="request.id" class="list-group-item">
          <div class="row align-items-center">
            <!-- Request Info Column -->
            <div class="col-md-4">
              <span class="badge" :class="getStatusBadgeClass(request.status)">
                {{ formatStatus(request.status) }}
              </span>
              <h5 class="mt-2 mb-1">{{ request.service.name }}</h5>
              <div class="d-flex align-items-center small text-muted">
                <i class="bi bi-calendar-event me-1"></i>
                <span>{{ formatDate(request.preferred_time) }}</span>
              </div>
            </div>

            <!-- Details Column -->
            <div class="col-md-4">
              <div class="d-flex flex-column">
                <div class="mb-2" v-if="request.professional">
                  <div class="d-flex align-items-center">
                    <div class="avatar-circle me-2 bg-light text-primary">
                      <i class="bi bi-person-badge"></i>
                    </div>
                    <div>
                      <div class="small text-muted">Professional</div>
                      <div class="fw-medium">{{ request.professional.user.full_name }}</div>
                    </div>
                  </div>
                </div>
                <div v-else class="mb-2 text-muted small fst-italic">
                  <i class="bi bi-hourglass me-1"></i>
                  Awaiting professional assignment
                </div>
                <div>
                  <div class="small text-muted">Service Details</div>
                  <div class="text-truncate-2">
                    {{ request.description || 'No description provided' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Price & Actions Column -->
            <div class="col-md-4">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <div class="small text-muted">Service Price</div>
                  <div class="fw-bold">₹{{ request.service.base_price }}</div>
                  <div class="small text-muted">
                    Duration: {{ formatDuration(request.service.estimated_time) }}
                  </div>
                </div>
                <div class="d-flex">
                  <button
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="viewRequestDetails(request)"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button
                    v-if="request.status === 'created'"
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmCancelRequest(request)"
                    :disabled="processingRequestId === request.id"
                  >
                    <i v-if="processingRequestId !== request.id" class="bi bi-x-circle"></i>
                    <span v-else class="spinner-border spinner-border-sm"></span>
                  </button>
                  <button
                    v-if="request.status === 'completed' && !request.review"
                    class="btn btn-sm btn-outline-warning"
                    @click="showReviewModal(request)"
                  >
                    <i class="bi bi-star"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="card-footer bg-white p-3">
        <div class="row align-items-center">
          <div class="col-md-6 text-muted">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ totalRequests }} requests
          </div>
          <div class="col-md-6">
            <ul class="pagination pagination-sm mb-0 justify-content-md-end">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)"
                  >Previous</a
                >
              </li>
              <li
                v-for="pageNum in displayedPages"
                :key="pageNum"
                class="page-item"
                :class="{ active: currentPage === pageNum }"
              >
                <a class="page-link" href="#" @click.prevent="changePage(pageNum)">{{ pageNum }}</a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Next</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Request Detail Modal -->
    <div class="modal fade" id="requestDetailModal" tabindex="-1" ref="requestDetailModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title">Request Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <!-- Service Details -->
              <div class="col-md-7">
                <div class="card h-100">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Service Information</h6>
                    <span class="badge" :class="getStatusBadgeClass(selectedRequest.status)">
                      {{ formatStatus(selectedRequest.status) }}
                    </span>
                  </div>
                  <div class="card-body">
                    <h5>{{ selectedRequest.service.name }}</h5>
                    <p class="text-muted">{{ selectedRequest.service.description }}</p>

                    <div class="row g-3 mt-2">
                      <div class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-clock text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Scheduled Time</div>
                            <div>{{ formatDateLong(selectedRequest.preferred_time) }}</div>
                          </div>
                        </div>
                      </div>
                      <div class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-hourglass-split text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Duration</div>
                            <div>{{ formatDuration(selectedRequest.service.estimated_time) }}</div>
                          </div>
                        </div>
                      </div>
                      <div class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-currency-rupee text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Price</div>
                            <div>₹{{ selectedRequest.service.base_price }}</div>
                          </div>
                        </div>
                      </div>
                      <div v-if="selectedRequest.status !== 'created'" class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-calendar-date text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Date of Assignment</div>
                            <div>{{ formatDateOnly(selectedRequest.date_of_assignment) }}</div>
                          </div>
                        </div>
                      </div>
                      <div v-if="selectedRequest.status === 'completed'" class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-calendar-check text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Date of Completion</div>
                            <div>{{ formatDateOnly(selectedRequest.date_of_completion) }}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="mt-4">
                      <h6>Request Description</h6>
                      <p>{{ selectedRequest.description || 'No additional details provided.' }}</p>
                    </div>

                    <div v-if="selectedRequest.remarks" class="mt-4">
                      <h6>Service Remarks</h6>
                      <p>{{ selectedRequest.remarks }}</p>
                    </div>

                    <!-- Review Section -->
                    <div v-if="selectedRequest.review" class="mt-4 border-top pt-3">
                      <h6>Your Review</h6>
                      <div class="d-flex mb-2">
                        <div v-for="i in 5" :key="i" class="me-1">
                          <i
                            class="bi"
                            :class="
                              i <= selectedRequest.review.rating
                                ? 'bi-star-fill text-warning'
                                : 'bi-star'
                            "
                          ></i>
                        </div>
                        <span class="ms-2">{{ selectedRequest.review.rating }}/5</span>
                      </div>
                      <p v-if="selectedRequest.review.comment">
                        {{ selectedRequest.review.comment }}
                      </p>
                      <p v-else class="text-muted fst-italic">No comment provided</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Professional Details -->
              <div class="col-md-5">
                <div class="card h-100">
                  <div class="card-header">
                    <h6 class="mb-0">Professional Information</h6>
                  </div>
                  <div class="card-body">
                    <div v-if="selectedRequest.professional">
                      <div class="d-flex align-items-center mb-4">
                        <div class="avatar-circle bg-light text-primary me-3">
                          <i class="bi bi-person-badge-fill"></i>
                        </div>
                        <div>
                          <h6 class="mb-0">{{ selectedRequest.professional.user.full_name }}</h6>
                          <p class="text-muted mb-0 small">Service Professional</p>
                        </div>
                      </div>

                      <div class="mb-3">
                        <div class="small text-muted mb-1">Contact Details</div>
                        <div class="d-flex align-items-center mb-2">
                          <i class="bi bi-envelope me-2 text-muted"></i>
                          <span>{{ selectedRequest.professional.user.email }}</span>
                        </div>
                        <div class="d-flex align-items-center">
                          <i class="bi bi-telephone me-2 text-muted"></i>
                          <span>{{ formatPhone(selectedRequest.professional.user.phone) }}</span>
                        </div>
                      </div>

                      <div class="mb-3">
                        <div class="small text-muted mb-1">Professional Experience</div>
                        <div>{{ selectedRequest.professional.experience_years }} years</div>
                      </div>

                      <div class="mb-3">
                        <div class="small text-muted mb-1">Average Rating</div>
                        <div class="d-flex align-items-center">
                          <i class="bi bi-star-fill text-warning me-1"></i>
                          <span
                            >{{ selectedRequest.professional.average_rating.toFixed(1) }}/5.0</span
                          >
                        </div>
                      </div>
                    </div>
                    <div v-else class="text-center py-4">
                      <i class="bi bi-person-badge text-muted fs-1 mb-3 d-block"></i>
                      <p class="text-muted">No professional assigned yet</p>
                      <p class="small text-muted">
                        A professional will be assigned to your request soon.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button
              v-if="selectedRequest.status === 'created'"
              type="button"
              class="btn btn-danger"
              @click="confirmCancelRequestFromModal"
              :disabled="isProcessing"
            >
              <span v-if="isProcessing" class="spinner-border spinner-border-sm me-1"></span>
              Cancel Request
            </button>
            <button
              v-if="selectedRequest.status === 'completed' && !selectedRequest.review"
              type="button"
              class="btn btn-warning"
              @click="showReviewModalFromDetail"
            >
              <i class="bi bi-star me-1"></i>Add Review
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel Confirmation Modal -->
    <div class="modal fade" id="cancelRequestModal" tabindex="-1" ref="cancelRequestModal">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title">Cancel Service Request</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-warning mb-3">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              Are you sure you want to cancel this service request? This action cannot be undone.
            </div>
            <div class="mb-3">
              <h6>Service Details:</h6>
              <ul class="list-unstyled">
                <li><strong>Service:</strong> {{ selectedRequest.service.name }}</li>
                <li>
                  <strong>Scheduled Time:</strong>
                  {{ formatDateLong(selectedRequest.preferred_time) }}
                </li>
                <li><strong>Price:</strong> ₹{{ selectedRequest.service.base_price }}</li>
              </ul>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Keep Request
            </button>
            <button
              type="button"
              class="btn btn-danger"
              @click="cancelRequest"
              :disabled="isProcessing"
            >
              <span v-if="isProcessing" class="spinner-border spinner-border-sm me-1"></span>
              Cancel Request
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Modal -->
    <div class="modal fade" id="reviewModal" tabindex="-1" ref="reviewModal">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title">Rate Your Experience</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitReview">
              <div class="mb-3">
                <label class="form-label">Service</label>
                <input
                  type="text"
                  class="form-control"
                  disabled
                  :value="selectedRequest.service.name"
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Professional</label>
                <input
                  type="text"
                  class="form-control"
                  disabled
                  :value="selectedRequest.professional?.user.full_name || 'Not assigned'"
                />
              </div>
              <div class="mb-4">
                <label class="form-label">Rating <span class="text-danger">*</span></label>
                <div class="rating-stars">
                  <div class="d-flex">
                    <span
                      v-for="star in 5"
                      :key="star"
                      class="fs-2 cursor-pointer star-icon"
                      @click="reviewForm.rating = star"
                      @mouseover="hoverRating = star"
                      @mouseleave="hoverRating = 0"
                    >
                      <i
                        :class="[
                          'bi',
                          (hoverRating || reviewForm.rating) >= star
                            ? 'bi-star-fill text-warning'
                            : 'bi-star text-muted',
                        ]"
                      ></i>
                    </span>
                  </div>
                  <div v-if="ratingError" class="text-danger small mt-2">{{ ratingError }}</div>
                  <div class="mt-1 small text-muted">
                    {{ getRatingLabel() }}
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label for="reviewComment" class="form-label">Comment (Optional)</label>
                <textarea
                  id="reviewComment"
                  class="form-control"
                  v-model="reviewForm.comment"
                  rows="4"
                  placeholder="Share your experience with this service..."
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-primary"
              @click="submitReview"
              :disabled="isProcessing"
            >
              <span v-if="isProcessing" class="spinner-border spinner-border-sm me-1"></span>
              Submit Review
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import moment from 'moment'
import * as bootstrap from 'bootstrap'

export default {
  name: 'CustomerServiceRequests',
  setup() {
    const store = useStore()
    const route = useRoute()
    // eslint-disable-next-line no-unused-vars
    const router = useRouter()

    // Refs for modals
    const requestDetailModal = ref(null)
    const cancelRequestModal = ref(null)
    const reviewModal = ref(null)
    let bsRequestDetailModal = null
    let bsCancelRequestModal = null
    let bsReviewModal = null

    // State
    const requests = ref([])
    const isLoading = ref(true)
    const error = ref(null)
    const activeStatus = ref('all')
    const searchQuery = ref('')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const selectedRequest = ref(null)
    const processingRequestId = ref(null)
    const hoverRating = ref(0)
    const reviewForm = ref({
      rating: 0,
      comment: '',
    })
    const ratingError = ref('')

    // Computed properties
    const isProcessing = computed(() => processingRequestId.value !== null)

    const filteredRequests = computed(() => {
      // First, filter by status if needed
      let result = [...requests.value]

      if (activeStatus.value !== 'all') {
        result = result.filter((request) => request.status === activeStatus.value)
      }

      // Then filter by search term if present
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(
          (request) =>
            request.service.name.toLowerCase().includes(query) ||
            request.description?.toLowerCase().includes(query) ||
            request.professional?.user?.full_name?.toLowerCase().includes(query) ||
            false,
        )
      }

      return result
    })

    const totalRequests = computed(() => filteredRequests.value.length)
    const totalPages = computed(() => Math.ceil(totalRequests.value / itemsPerPage.value))

    const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value)
    const endIndex = computed(() =>
      Math.min(startIndex.value + itemsPerPage.value, totalRequests.value),
    )

    const paginatedRequests = computed(() => {
      return filteredRequests.value.slice(startIndex.value, endIndex.value)
    })

    const displayedPages = computed(() => {
      const totalPagesToShow = 5
      const pages = []
      let startPage = Math.max(1, currentPage.value - Math.floor(totalPagesToShow / 2))
      let endPage = Math.min(totalPages.value, startPage + totalPagesToShow - 1)

      // Adjust if we're near the end
      if (endPage - startPage + 1 < totalPagesToShow) {
        startPage = Math.max(1, endPage - totalPagesToShow + 1)
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      return pages
    })

    const requestCountByStatus = computed(() => {
      const count = {
        created: 0,
        assigned: 0,
        completed: 0,
      }

      requests.value.forEach((request) => {
        if (count[request.status] !== undefined) {
          count[request.status]++
        }
      })

      return count
    })

    // Methods
    const fetchRequests = async () => {
      isLoading.value = true
      error.value = null

      try {
        const response = await store.dispatch('requests/fetchCustomerRequests', {
          status: activeStatus.value === 'all' ? null : activeStatus.value,
        })

        requests.value = response.data || []
        currentPage.value = 1 // Reset to first page after filter change
      } catch (err) {
        console.error('Error fetching requests:', err)
        error.value = 'Failed to load service requests. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    const refreshRequests = () => {
      fetchRequests()
    }

    const filterByStatus = (status) => {
      activeStatus.value = status
      currentPage.value = 1
      fetchRequests()
    }

    const handleSearch = () => {
      currentPage.value = 1
      // Only refresh if search is cleared, otherwise just filter in-memory
      if (searchQuery.value === '') {
        refreshRequests()
      }
    }

    const clearSearch = () => {
      searchQuery.value = ''
      handleSearch()
    }

    const changePage = (page) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
    }

    const viewRequestDetails = (request) => {
      selectedRequest.value = request
      bsRequestDetailModal.show()
    }

    const confirmCancelRequest = (request) => {
      selectedRequest.value = request
      bsCancelRequestModal.show()
    }

    const confirmCancelRequestFromModal = () => {
      if (!selectedRequest.value) return
      bsRequestDetailModal.hide()
      setTimeout(() => {
        bsCancelRequestModal.show()
      }, 500)
    }

    const cancelRequest = async () => {
      if (!selectedRequest.value || isProcessing.value) return

      processingRequestId.value = selectedRequest.value.id
      try {
        await store.dispatch('requests/cancelRequest', selectedRequest.value.id)

        window.showToast({
          type: 'success',
          title: 'Service request cancelled successfully!',
        })

        bsCancelRequestModal.hide()

        // Remove the cancelled request from the list
        requests.value = requests.value.filter((r) => r.id !== selectedRequest.value.id)
      } catch (error) {
        window.showToast({
          type: 'error',
          title: error.response?.data?.detail || 'Failed to cancel request. Please try again.',
        })
      } finally {
        processingRequestId.value = null
      }
    }

    const showReviewModal = (request) => {
      selectedRequest.value = request
      resetReviewForm()
      bsReviewModal.show()
    }

    const showReviewModalFromDetail = () => {
      if (!selectedRequest.value) return
      bsRequestDetailModal.hide()
      setTimeout(() => {
        resetReviewForm()
        bsReviewModal.show()
      }, 500)
    }

    const resetReviewForm = () => {
      reviewForm.value = {
        rating: 0,
        comment: '',
      }
      ratingError.value = ''
      hoverRating.value = 0
    }

    const submitReview = async () => {
      if (!selectedRequest.value || isProcessing.value) return

      // Validate rating
      if (!reviewForm.value.rating) {
        ratingError.value = 'Please select a rating.'
        return
      }

      processingRequestId.value = selectedRequest.value.id
      try {
        await store.dispatch('requests/submitReview', {
          id: selectedRequest.value.id,
          data: reviewForm.value,
        })

        window.showToast({
          type: 'success',
          title: 'Thank you for your feedback!',
        })

        bsReviewModal.hide()
        fetchRequests() // Refresh the list
      } catch (error) {
        window.showToast({
          type: 'error',
          title: error.response?.data?.detail || 'Failed to submit review. Please try again.',
        })
      } finally {
        processingRequestId.value = null
      }
    }

    const getRatingLabel = () => {
      const rating = hoverRating.value || reviewForm.value.rating
      const labels = [
        '',
        'Poor - Not satisfied',
        'Fair - Below expectations',
        'Good - Met expectations',
        'Very Good - Above expectations',
        'Excellent - Highly satisfied',
      ]
      return labels[rating] || ''
    }

    // Formatting helpers
    const formatDate = (dateString) => {
      const date = moment(dateString)

      // If today, show "Today at [time]"
      if (date.isSame(moment(), 'day')) {
        return `Today at ${date.format('h:mm A')}`
      }

      // If tomorrow, show "Tomorrow at [time]"
      if (date.isSame(moment().add(1, 'day'), 'day')) {
        return `Tomorrow at ${date.format('h:mm A')}`
      }

      // If within the next 7 days, show day name and time
      if (date.diff(moment(), 'days') < 7) {
        return `${date.format('dddd')} at ${date.format('h:mm A')}`
      }

      // Otherwise show date and time
      return `${date.format('MMM D')} at ${date.format('h:mm A')}`
    }

    const formatDateLong = (dateString) => {
      return moment(dateString).format('dddd, MMMM D, YYYY h:mm A')
    }

    const formatDateOnly = (dateString) => {
      if (!dateString) return 'N/A'
      return moment(dateString).format('MMM D, YYYY')
    }

    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60

      if (hours === 0) {
        return `${mins} minutes`
      } else if (mins === 0) {
        return `${hours} hour${hours > 1 ? 's' : ''}`
      } else {
        return `${hours} hour${hours > 1 ? 's' : ''} ${mins} min`
      }
    }

    const formatPhone = (phone) => {
      return `+91 ${phone}`
    }

    const formatStatus = (status) => {
      const statusMap = {
        created: 'Pending',
        assigned: 'In Progress',
        completed: 'Completed',
      }
      return statusMap[status] || status
    }

    const getStatusBadgeClass = (status) => {
      const classMap = {
        created: 'bg-warning',
        assigned: 'bg-info',
        completed: 'bg-success',
      }
      return classMap[status] || 'bg-secondary'
    }

    // Initialize from route query params
    watch(
      () => route.query.status,
      (newStatus) => {
        if (newStatus && ['all', 'created', 'assigned', 'completed'].includes(newStatus)) {
          activeStatus.value = newStatus
        }
      },
      { immediate: true },
    )

    // Lifecycle hooks
    onMounted(() => {
      if (requestDetailModal.value) {
        bsRequestDetailModal = new bootstrap.Modal(requestDetailModal.value)
      }

      if (cancelRequestModal.value) {
        bsCancelRequestModal = new bootstrap.Modal(cancelRequestModal.value)
      }

      if (reviewModal.value) {
        bsReviewModal = new bootstrap.Modal(reviewModal.value)
      }

      // Check if we have a status in the query params
      const queryStatus = route.query.status
      if (queryStatus && ['all', 'created', 'assigned', 'completed'].includes(queryStatus)) {
        activeStatus.value = queryStatus
      }

      fetchRequests()
    })

    return {
      requests,
      isLoading,
      error,
      activeStatus,
      searchQuery,
      currentPage,
      itemsPerPage,
      totalRequests,
      totalPages,
      startIndex,
      endIndex,
      selectedRequest,
      processingRequestId,
      requestDetailModal,
      cancelRequestModal,
      reviewModal,
      filteredRequests,
      paginatedRequests,
      displayedPages,
      requestCountByStatus,
      reviewForm,
      hoverRating,
      ratingError,
      isProcessing,

      // Methods
      fetchRequests,
      refreshRequests,
      filterByStatus,
      handleSearch,
      clearSearch,
      changePage,
      viewRequestDetails,
      confirmCancelRequest,
      confirmCancelRequestFromModal,
      cancelRequest,
      showReviewModal,
      showReviewModalFromDetail,
      submitReview,
      getRatingLabel,

      // Formatting helpers
      formatDate,
      formatDateLong,
      formatDateOnly,
      formatDuration,
      formatPhone,
      formatStatus,
      getStatusBadgeClass,
    }
  },
}
</script>

<style scoped>
.nav-pills .nav-link {
  cursor: pointer;
  padding: 0.5rem 1rem;
}

.nav-pills .nav-link.active {
  background-color: var(--bs-primary);
}

.list-group-item {
  padding: 1.25rem;
  transition: background-color 0.2s;
}

.list-group-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.card {
  border: none;
  border-radius: 0.5rem;
  overflow: hidden;
}

.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cursor-pointer {
  cursor: pointer;
}

.rating-stars .star-icon {
  cursor: pointer;
  transition: transform 0.2s;
}

.rating-stars .star-icon:hover {
  transform: scale(1.1);
}

/* Responsive styles */
@media (max-width: 767.98px) {
  .card-footer .pagination {
    justify-content: center !important;
    margin-top: 1rem;
  }

  .card-footer .text-muted {
    text-align: center;
  }

  .nav-pills {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 0.5rem;
  }

  .nav-pills .nav-link {
    white-space: nowrap;
    padding: 0.5rem 0.75rem;
  }
}
</style>
