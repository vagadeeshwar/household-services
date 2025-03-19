<template>
  <div class="container py-4">
    <div class="row g-4">
      <!-- Welcome Section -->
      <div class="col-12">
        <div class="card shadow-sm border-0 bg-success bg-gradient text-white">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h2 class="mb-1">Welcome back, {{ userName }}!</h2>
                <p class="mb-0 opacity-75">
                  <i class="bi bi-check-circle-fill me-1"></i> Your account is active
                </p>
              </div>
              <div class="d-none d-md-block">
                <div class="text-end">
                  <p class="mb-0">{{ currentDate }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <template v-if="isLoading">
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading dashboard data...</p>
        </div>
      </template>

      <!-- Error State -->
      <template v-else-if="error">
        <div class="col-12">
          <div class="alert alert-danger d-flex align-items-center" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <div>{{ error }}</div>
          </div>
          <div class="text-center mt-3">
            <button @click="fetchDashboardData" class="btn btn-primary">Try Again</button>
          </div>
        </div>
      </template>

      <!-- Dashboard Content -->
      <template v-else>
        <!-- Stats Cards -->
        <div class="col-12">
          <div class="row g-3">
            <!-- Total Requests Card -->
            <div class="col-md-3 col-sm-6">
              <div class="card shadow-sm h-100">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="card-title mb-0 text-muted">All Requests</h6>
                    <i class="bi bi-list-check text-primary fs-4"></i>
                  </div>
                  <h2 class="mb-0">{{ requestsData.total || '0' }}</h2>
                  <div class="text-muted small mt-2">Total service requests</div>
                </div>
              </div>
            </div>

            <!-- Pending Requests Card -->
            <div class="col-md-3 col-sm-6">
              <div class="card shadow-sm h-100">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="card-title mb-0 text-muted">Pending</h6>
                    <i class="bi bi-hourglass-split text-warning fs-4"></i>
                  </div>
                  <h2 class="mb-0">{{ requestsData.pending || '0' }}</h2>
                  <div class="text-muted small mt-2">Awaiting assignment</div>
                </div>
              </div>
            </div>

            <!-- Active Requests Card -->
            <div class="col-md-3 col-sm-6">
              <div class="card shadow-sm h-100">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="card-title mb-0 text-muted">Active</h6>
                    <i class="bi bi-arrow-repeat text-info fs-4"></i>
                  </div>
                  <h2 class="mb-0">{{ requestsData.active || '0' }}</h2>
                  <div class="text-muted small mt-2">In progress</div>
                </div>
              </div>
            </div>

            <!-- Completed Requests Card -->
            <div class="col-md-3 col-sm-6">
              <div class="card shadow-sm h-100">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="card-title mb-0 text-muted">Completed</h6>
                    <i class="bi bi-check-circle text-success fs-4"></i>
                  </div>
                  <h2 class="mb-0">{{ requestsData.completed || '0' }}</h2>
                  <div class="text-muted small mt-2">Successfully completed</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Current Service Requests -->
        <div class="col-md-8">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-white py-3">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0">My Service Requests</h5>
                <div class="btn-group" role="group">
                  <button
                    v-for="status in ['All', 'Pending', 'Active', 'Completed']"
                    :key="status"
                    type="button"
                    class="btn btn-sm"
                    :class="
                      currentFilter === status.toLowerCase() ? 'btn-primary' : 'btn-outline-primary'
                    "
                    @click="filterRequests(status.toLowerCase())"
                  >
                    {{ status }}
                  </button>
                </div>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="list-group list-group-flush">
                <div v-if="filteredRequests.length === 0" class="text-center py-4 text-muted">
                  <i class="bi bi-calendar-x fs-3 mb-2"></i>
                  <p class="mb-0">No service requests found</p>
                  <router-link to="/customer/services" class="btn btn-sm btn-primary mt-2">
                    Book a Service
                  </router-link>
                </div>
                <div v-for="request in filteredRequests" :key="request.id" class="list-group-item">
                  <div class="d-flex justify-content-between align-items-center flex-wrap">
                    <div>
                      <div class="d-flex align-items-center mb-2">
                        <span
                          :class="[
                            'badge me-2',
                            request.status === 'created'
                              ? 'bg-warning'
                              : request.status === 'assigned'
                                ? 'bg-info'
                                : 'bg-success',
                          ]"
                        >
                          {{ formatStatus(request.status) }}
                        </span>
                        <h6 class="mb-0">{{ request.service.name }}</h6>
                      </div>
                      <p class="mb-1 text-muted small">
                        <i class="bi bi-clock me-1"></i>
                        {{ formatDate(request.preferred_time) }}
                      </p>
                      <p class="mb-1 small" v-if="request.professional">
                        <i class="bi bi-person-badge me-1"></i>
                        Professional: {{ request.professional.user.full_name }}
                      </p>
                      <p class="mb-0 small text-truncate">
                        <i class="bi bi-chat-left-text me-1"></i>
                        {{ request.description }}
                      </p>
                    </div>
                    <div class="mt-2 mt-md-0">
                      <router-link
                        :to="`/customer/requests/${request.id}`"
                        class="btn btn-sm btn-outline-primary"
                      >
                        Details
                      </router-link>
                      <button
                        v-if="request.status === 'completed' && !hasReview(request)"
                        class="btn btn-sm btn-outline-warning ms-1"
                        @click="showReviewModal(request)"
                      >
                        Add Review
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-footer bg-white p-3 text-center">
              <router-link to="/customer/requests" class="btn btn-outline-primary">
                View All Requests
              </router-link>
            </div>
          </div>
        </div>

        <!-- Popular Services -->
        <div class="col-md-4">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-white py-3">
              <h5 class="card-title mb-0">Popular Services</h5>
            </div>
            <div class="card-body p-0">
              <div class="list-group list-group-flush">
                <div v-if="popularServices.length === 0" class="text-center py-4 text-muted">
                  <i class="bi bi-tools fs-3 mb-2"></i>
                  <p class="mb-0">Loading services...</p>
                </div>
                <div v-for="service in popularServices" :key="service.id" class="list-group-item">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 class="mb-1">{{ service.name }}</h6>
                      <p class="mb-0 text-muted small">
                        <i class="bi bi-clock me-1"></i>
                        {{ formatDuration(service.estimated_time) }}
                        <span class="mx-1">•</span>
                        <i class="bi bi-currency-rupee me-1"></i>
                        {{ service.base_price }}
                      </p>
                    </div>
                    <button class="btn btn-sm btn-primary" @click="bookService(service)">
                      Book
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-footer bg-white p-3 text-center">
              <router-link to="/customer/services" class="btn btn-outline-primary">
                Browse All Services
              </router-link>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-header bg-white py-3">
              <h5 class="card-title mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-3 col-sm-6">
                  <router-link
                    to="/customer/services"
                    class="card h-100 bg-light text-center text-decoration-none"
                  >
                    <div class="card-body py-4">
                      <i class="bi bi-tools text-primary fs-3 mb-3"></i>
                      <h6 class="card-title mb-0">Book Service</h6>
                      <p class="small text-muted mb-0">Find the right service for your needs</p>
                    </div>
                  </router-link>
                </div>
                <div class="col-md-3 col-sm-6">
                  <router-link
                    to="/customer/requests?status=created"
                    class="card h-100 bg-light text-center text-decoration-none"
                  >
                    <div class="card-body py-4">
                      <i class="bi bi-hourglass-split text-warning fs-3 mb-3"></i>
                      <h6 class="card-title mb-0">Pending Requests</h6>
                      <p class="small text-muted mb-0">Track unassigned requests</p>
                    </div>
                  </router-link>
                </div>
                <div class="col-md-3 col-sm-6">
                  <router-link
                    to="/customer/professionals"
                    class="card h-100 bg-light text-center text-decoration-none"
                  >
                    <div class="card-body py-4">
                      <i class="bi bi-person-badge text-info fs-3 mb-3"></i>
                      <h6 class="card-title mb-0">Find Professionals</h6>
                      <p class="small text-muted mb-0">Browse top rated service providers</p>
                    </div>
                  </router-link>
                </div>
                <div class="col-md-3 col-sm-6">
                  <router-link
                    to="/customer/profile"
                    class="card h-100 bg-light text-center text-decoration-none"
                  >
                    <div class="card-body py-4">
                      <i class="bi bi-person-circle text-success fs-3 mb-3"></i>
                      <h6 class="card-title mb-0">My Profile</h6>
                      <p class="small text-muted mb-0">Update your information</p>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Add Review Modal -->
    <div class="modal fade" id="reviewModal" tabindex="-1" ref="reviewModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Leave a Review</h5>
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
                  :value="selectedRequest?.service?.name || ''"
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Rating</label>
                <div class="star-rating">
                  <div class="d-flex">
                    <span
                      v-for="star in 5"
                      :key="star"
                      class="fs-3 cursor-pointer star-icon"
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
                  <p class="small text-muted mt-1">
                    {{ ratingLabel }}
                  </p>
                </div>
              </div>
              <div class="mb-3">
                <label for="comment" class="form-label">Comment (Optional)</label>
                <textarea
                  id="comment"
                  class="form-control"
                  v-model="reviewForm.comment"
                  rows="4"
                  placeholder="Share your experience with this service..."
                ></textarea>
              </div>
              <div class="d-grid gap-2">
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="!reviewForm.rating || isSubmittingReview"
                >
                  <span
                    v-if="isSubmittingReview"
                    class="spinner-border spinner-border-sm me-2"
                  ></span>
                  {{ isSubmittingReview ? 'Submitting...' : 'Submit Review' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Book Service Modal -->
    <div class="modal fade" id="bookServiceModal" tabindex="-1" ref="bookServiceModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Book Service</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitBooking">
              <div class="mb-3">
                <label class="form-label">Service</label>
                <input
                  type="text"
                  class="form-control"
                  disabled
                  :value="selectedService?.name || ''"
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Price</label>
                <div class="input-group">
                  <span class="input-group-text">₹</span>
                  <input
                    type="text"
                    class="form-control"
                    disabled
                    :value="selectedService?.base_price || ''"
                  />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Duration</label>
                <input
                  type="text"
                  class="form-control"
                  disabled
                  :value="selectedService ? formatDuration(selectedService.estimated_time) : ''"
                />
              </div>
              <div class="mb-3">
                <label for="preferredTime" class="form-label">Preferred Date & Time</label>
                <input
                  type="datetime-local"
                  id="preferredTime"
                  class="form-control"
                  v-model="bookingForm.preferredTime"
                  :min="minDateTime"
                  :max="maxDateTime"
                  :class="{ 'is-invalid': bookingErrors.preferredTime }"
                />
                <div class="invalid-feedback" v-if="bookingErrors.preferredTime">
                  {{ bookingErrors.preferredTime }}
                </div>
                <small class="form-text text-muted">
                  Services are available between 9:00 AM and 5:00 PM
                </small>
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea
                  id="description"
                  class="form-control"
                  v-model="bookingForm.description"
                  rows="3"
                  placeholder="Please describe your requirements..."
                  :class="{ 'is-invalid': bookingErrors.description }"
                ></textarea>
                <div class="invalid-feedback" v-if="bookingErrors.description">
                  {{ bookingErrors.description }}
                </div>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="isSubmittingBooking">
                  <span
                    v-if="isSubmittingBooking"
                    class="spinner-border spinner-border-sm me-2"
                  ></span>
                  {{ isSubmittingBooking ? 'Booking...' : 'Book Now' }}
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
import * as bootstrap from 'bootstrap'
import moment from 'moment'
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
  name: 'CustomerDashboard',
  setup() {
    const store = useStore()
    // eslint-disable-next-line no-unused-vars
    const router = useRouter()

    // Modal refs
    const reviewModal = ref(null)
    const bookServiceModal = ref(null)
    let bsReviewModal = null
    let bsBookServiceModal = null

    // State
    const isLoading = ref(true)
    const error = ref(null)
    const dashboardData = ref(null)
    const serviceRequests = ref([])
    const popularServices = ref([])
    const currentFilter = ref('all')
    const refreshInterval = ref(null)
    const selectedRequest = ref(null)
    const selectedService = ref(null)
    const hoverRating = ref(0)

    const isSubmittingReview = ref(false)
    const isSubmittingBooking = ref(false)

    // Form state
    const reviewForm = reactive({
      rating: 0,
      comment: '',
    })

    const bookingForm = reactive({
      preferredTime: '',
      description: '',
    })

    const bookingErrors = reactive({
      preferredTime: '',
      description: '',
    })

    // Computed properties
    const userName = computed(() => store.getters['auth/userName'] || 'Customer')
    const currentDate = computed(() => moment().format('dddd, MMMM D, YYYY'))

    const requestsData = computed(() => {
      if (!dashboardData.value) return { total: 0, pending: 0, active: 0, completed: 0 }
      return dashboardData.value.service_requests
    })

    const filteredRequests = computed(() => {
      if (!serviceRequests.value) return []

      if (currentFilter.value === 'all') {
        return serviceRequests.value
      }

      const statusMap = {
        pending: 'created',
        active: 'assigned',
        completed: 'completed',
      }

      return serviceRequests.value.filter(
        (request) => request.status === statusMap[currentFilter.value],
      )
    })

    const ratingLabel = computed(() => {
      const rating = hoverRating.value || reviewForm.rating
      const labels = [
        '',
        'Poor - Not satisfied',
        'Fair - Below expectations',
        'Good - Met expectations',
        'Very Good - Above expectations',
        'Excellent - Highly satisfied',
      ]
      return labels[rating] || ''
    })

    const minDateTime = computed(() => {
      // Allow booking from tomorrow
      const tomorrow = moment().add(1, 'day').set({ hour: 9, minute: 0 })
      return tomorrow.format('YYYY-MM-DDTHH:mm')
    })

    const maxDateTime = computed(() => {
      // Allow booking up to 7 days ahead, until 5 PM
      const maxDay = moment().add(7, 'days').set({ hour: 17, minute: 0 })
      return maxDay.format('YYYY-MM-DDTHH:mm')
    })

    // Methods
    const fetchDashboardData = async () => {
      isLoading.value = true
      error.value = null

      try {
        // Fetch dashboard overview data
        const response = await store.dispatch('stats/fetchDashboardStats')
        dashboardData.value = response

        // Fetch recent service requests
        const requestsResponse = await store.dispatch('requests/fetchCustomerRequests', {
          page: 1,
          perPage: 5,
        })
        serviceRequests.value = requestsResponse.data

        // Fetch popular services
        const servicesResponse = await store.dispatch('services/fetchActiveServices', {
          page: 1,
          perPage: 5,
          isActive: true,
        })
        popularServices.value = servicesResponse.data
      } catch (err) {
        error.value = 'Failed to load dashboard data. Please try again.'
        console.error('Dashboard error:', err)
      } finally {
        isLoading.value = false
      }
    }

    const formatDate = (dateString) => {
      const date = moment(dateString)
      // If today, show time only
      if (date.isSame(moment(), 'day')) {
        return `Today at ${date.format('h:mm A')}`
      }
      // If tomorrow, show "Tomorrow"
      if (date.isSame(moment().add(1, 'day'), 'day')) {
        return `Tomorrow at ${date.format('h:mm A')}`
      }
      // Otherwise show date and time
      return date.format('MMM D [at] h:mm A')
    }

    const formatDuration = (minutes) => {
      if (minutes < 60) {
        return `${minutes}m`
      }
      const hrs = Math.floor(minutes / 60)
      const mins = minutes % 60
      return mins > 0 ? `${hrs}h ${mins}m` : `${hrs}h`
    }

    const formatStatus = (status) => {
      const statusMap = {
        created: 'Pending',
        assigned: 'In Progress',
        completed: 'Completed',
      }
      return statusMap[status] || status
    }

    const filterRequests = (filter) => {
      currentFilter.value = filter
    }

    const hasReview = (request) => {
      return request.review !== null && request.review !== undefined
    }

    const showReviewModal = (request) => {
      selectedRequest.value = request
      reviewForm.rating = 0
      reviewForm.comment = ''
      bsReviewModal.show()
    }

    const submitReview = async () => {
      if (!selectedRequest.value || !reviewForm.rating) return

      isSubmittingReview.value = true

      try {
        await store.dispatch('requests/submitReview', {
          id: selectedRequest.value.id,
          data: {
            rating: reviewForm.rating,
            comment: reviewForm.comment,
          },
        })

        window.showToast({
          type: 'success',
          title: 'Thank you for your feedback!',
        })

        bsReviewModal.hide()
        fetchDashboardData() // Refresh data

        // eslint-disable-next-line no-unused-vars
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Failed to submit review. Please try again.',
        })
      } finally {
        isSubmittingReview.value = false
      }
    }

    const bookService = (service) => {
      selectedService.value = service

      // Initialize form with defaults
      const defaultTime = moment().add(1, 'day').set({ hour: 10, minute: 0 })
      bookingForm.preferredTime = defaultTime.format('YYYY-MM-DDTHH:mm')
      bookingForm.description = ''

      // Reset errors
      bookingErrors.preferredTime = ''
      bookingErrors.description = ''

      bsBookServiceModal.show()
    }

    const validateBookingForm = () => {
      let isValid = true

      // Reset errors
      bookingErrors.preferredTime = ''
      bookingErrors.description = ''

      // Validate preferred time
      if (!bookingForm.preferredTime) {
        bookingErrors.preferredTime = 'Please select a preferred time'
        isValid = false
      } else {
        const selectedTime = moment(bookingForm.preferredTime)
        const now = moment()

        // Must be in the future
        if (selectedTime <= now) {
          bookingErrors.preferredTime = 'Please select a future date and time'
          isValid = false
        }

        // Must be between 9 AM and 5 PM
        const hour = selectedTime.hour()
        if (hour < 9 || hour >= 17) {
          bookingErrors.preferredTime = 'Services are only available between 9:00 AM and 5:00 PM'
          isValid = false
        }

        // Check if service can be completed by 6 PM
        if (selectedService.value) {
          const endTime = moment(selectedTime).add(selectedService.value.estimated_time, 'minutes')
          const cutoffTime = moment(selectedTime).set({ hour: 18, minute: 0 })

          if (endTime > cutoffTime) {
            bookingErrors.preferredTime =
              'Service cannot be completed by 6:00 PM with this start time'
            isValid = false
          }
        }
      }

      // Validate description
      if (!bookingForm.description.trim()) {
        bookingErrors.description = 'Please provide a description of your request'
        isValid = false
      } else if (bookingForm.description.length < 10) {
        bookingErrors.description = 'Description must be at least 10 characters'
        isValid = false
      }

      return isValid
    }

    const submitBooking = async () => {
      if (!selectedService.value) return

      if (!validateBookingForm()) return

      isSubmittingBooking.value = true

      try {
        await store.dispatch('requests/createRequest', {
          serviceId: selectedService.value.id,
          preferredTime: bookingForm.preferredTime,
          description: bookingForm.description,
        })

        window.showToast({
          type: 'success',
          title: 'Your service request has been created successfully!',
        })

        bsBookServiceModal.hide()
        fetchDashboardData() // Refresh data
      } catch (err) {
        let errorMessage = 'Failed to book service. Please try again.'
        if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail
        }

        window.showToast({
          type: 'error',
          title: errorMessage,
        })
      } finally {
        isSubmittingBooking.value = false
      }
    }

    // Setup automatic refresh every 5 minutes
    const setupRefreshInterval = () => {
      refreshInterval.value = setInterval(() => {
        fetchDashboardData()
      }, 300000) // 5 minutes
    }

    // Lifecycle hooks
    onMounted(() => {
      // Initialize Bootstrap modals
      if (reviewModal.value) {
        bsReviewModal = new bootstrap.Modal(reviewModal.value)
      }

      if (bookServiceModal.value) {
        bsBookServiceModal = new bootstrap.Modal(bookServiceModal.value)
      }

      fetchDashboardData()
      setupRefreshInterval()
    })

    onBeforeUnmount(() => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
    })

    return {
      isLoading,
      error,
      dashboardData,
      serviceRequests,
      popularServices,
      userName,
      currentDate,
      requestsData,
      currentFilter,
      filteredRequests,
      selectedRequest,
      selectedService,
      reviewForm,
      hoverRating,
      ratingLabel,
      isSubmittingReview,
      bookingForm,
      bookingErrors,
      isSubmittingBooking,
      minDateTime,
      maxDateTime,
      reviewModal,
      bookServiceModal,
      fetchDashboardData,
      formatDate,
      formatDuration,
      formatStatus,
      filterRequests,
      hasReview,
      showReviewModal,
      submitReview,
      bookService,
      submitBooking,
    }
  },
}
</script>

<style scoped>
.card {
  transition:
    transform 0.2s ease-in-out,
    box-shadow 0.2s ease-in-out;
  border-radius: 0.5rem;
  overflow: hidden;
}

a.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.list-group-item {
  padding: 1rem;
  border-left: none;
  border-right: none;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}

.badge {
  font-weight: normal;
  padding: 0.35em 0.65em;
}

.bg-gradient {
  background-image: linear-gradient(135deg, #198754, #157347);
}

.star-icon {
  cursor: pointer;
  transition: transform 0.1s ease-in-out;
}

.star-icon:hover {
  transform: scale(1.1);
}

@media (max-width: 767.98px) {
  .btn-group {
    width: 100%;
    margin-top: 0.5rem;
  }
}
</style>
