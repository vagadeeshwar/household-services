<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="h3 mb-2">Service Requests</h1>
        <p class="text-muted">Manage your service requests and appointments</p>
      </div>
    </div>

    <!-- Request Type Navigation -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <ul class="nav nav-pills">
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeTab === 'available' }"
              @click.prevent="setActiveTab('available')"
              href="#"
            >
              <i class="bi bi-list-stars me-2"></i>Available Requests
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeTab === 'ongoing' }"
              @click.prevent="setActiveTab('ongoing')"
              href="#"
            >
              <i class="bi bi-arrow-repeat me-2"></i>Ongoing Services
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeTab === 'completed' }"
              @click.prevent="setActiveTab('completed')"
              href="#"
            >
              <i class="bi bi-check2-circle me-2"></i>Completed Services
            </a>
          </li>
        </ul>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading service requests...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button @click="fetchRequests" class="btn btn-sm btn-outline-danger ms-2">Retry</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="requests.length === 0" class="text-center py-5">
      <div class="py-5">
        <i class="bi bi-calendar-x fs-1 text-muted mb-3 d-block"></i>
        <h5>No {{ activeTab }} requests found</h5>
        <p class="text-muted">
          {{
            activeTab === 'available'
              ? 'Check back later for new service requests.'
              : activeTab === 'ongoing'
                ? 'You have no ongoing services at this time.'
                : 'You have no completed services yet.'
          }}
        </p>
      </div>
    </div>

    <!-- Requests List -->
    <div v-else class="card shadow-sm">
      <div class="card-header bg-white py-3">
        <div class="row align-items-center">
          <div class="col">
            <h5 class="mb-0">{{ getActiveTabTitle() }}</h5>
          </div>
          <div class="col-auto">
            <div class="input-group">
              <input
                type="text"
                class="form-control form-control-sm"
                placeholder="Search..."
                v-model="searchQuery"
                @input="handleSearch"
              />
              <button class="btn btn-sm btn-outline-secondary" type="button" @click="clearSearch">
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="list-group list-group-flush">
        <div v-for="request in filteredRequests" :key="request.id" class="list-group-item p-0">
          <div class="p-3">
            <div class="row align-items-center">
              <!-- Request Details Column -->
              <div class="col-md-7">
                <div class="d-flex align-items-center">
                  <div class="mr-3">
                    <span class="badge" :class="getStatusBadgeClass(request.status)">
                      {{ formatStatus(request.status) }}
                    </span>
                  </div>
                  <div class="ms-2">
                    <h6 class="mb-1">{{ request.service.name }}</h6>
                    <p class="text-muted small mb-0">
                      <i class="bi bi-geo-alt me-1"></i
                      >{{ truncateText(request.customer.user.address, 50) }}
                    </p>
                  </div>
                </div>
                <div class="mt-2">
                  <div class="d-flex align-items-center small text-muted">
                    <div class="me-3">
                      <i class="bi bi-clock me-1"></i>{{ formatDate(request.preferred_time) }}
                    </div>
                    <div class="me-3">
                      <i class="bi bi-hourglass-split me-1"></i
                      >{{ formatDuration(request.service.estimated_time) }}
                    </div>
                    <div>
                      <i class="bi bi-currency-rupee me-1"></i>{{ request.service.base_price }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Customer Info Column -->
              <div class="col-md-3 py-2">
                <div class="d-flex align-items-center">
                  <div class="avatar-circle me-2 bg-light text-primary">
                    <i class="bi bi-person"></i>
                  </div>
                  <div>
                    <h6 class="mb-0 small">{{ request.customer.user.full_name }}</h6>
                    <p class="text-muted mb-0 small">
                      <i class="bi bi-telephone me-1"></i
                      >{{ formatPhone(request.customer.user.phone) }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Action Column -->
              <div class="col-md-2 text-md-end mt-2 mt-md-0">
                <button
                  class="btn btn-sm btn-outline-primary me-1"
                  @click="viewRequestDetails(request)"
                >
                  <i class="bi bi-eye"></i>
                </button>
                <button
                  v-if="activeTab === 'available'"
                  class="btn btn-sm btn-success"
                  @click="acceptRequest(request)"
                  :disabled="isRequestProcessing"
                >
                  <span
                    v-if="processingRequestId === request.id"
                    class="spinner-border spinner-border-sm me-1"
                  ></span>
                  Accept
                </button>
                <button
                  v-if="activeTab === 'ongoing'"
                  class="btn btn-sm btn-outline-success"
                  @click="completeRequest(request)"
                  :disabled="isRequestProcessing"
                >
                  <span
                    v-if="processingRequestId === request.id"
                    class="spinner-border spinner-border-sm me-1"
                  ></span>
                  Complete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="card-footer bg-white py-3">
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
            <h5 class="modal-title">Service Request Details</h5>
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
                            <div class="small text-muted">Schedule Time</div>
                            <div>{{ formatDate(selectedRequest.preferred_time) }}</div>
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
                      <div class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-calendar-date text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Request Date</div>
                            <div>{{ formatDateOnly(selectedRequest.date_of_request) }}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="mt-4">
                      <h6>Request Description</h6>
                      <p>{{ selectedRequest.description || 'No additional details provided.' }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Customer Details -->
              <div class="col-md-5">
                <div class="card h-100">
                  <div class="card-header">
                    <h6 class="mb-0">Customer Information</h6>
                  </div>
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-4">
                      <div class="avatar-circle bg-light text-primary me-3">
                        <i class="bi bi-person-fill"></i>
                      </div>
                      <div>
                        <h6 class="mb-0">{{ selectedRequest.customer.user.full_name }}</h6>
                        <p class="text-muted mb-0 small">Customer</p>
                      </div>
                    </div>

                    <div class="mb-3">
                      <div class="small text-muted mb-1">Contact Details</div>
                      <div class="d-flex align-items-center mb-2">
                        <i class="bi bi-envelope me-2 text-muted"></i>
                        <span>{{ selectedRequest.customer.user.email }}</span>
                      </div>
                      <div class="d-flex align-items-center">
                        <i class="bi bi-telephone me-2 text-muted"></i>
                        <span>{{ formatPhone(selectedRequest.customer.user.phone) }}</span>
                      </div>
                    </div>

                    <div>
                      <div class="small text-muted mb-1">Service Location</div>
                      <div class="d-flex align-items-center">
                        <i class="bi bi-geo-alt me-2 text-muted"></i>
                        <span>{{ selectedRequest.customer.user.address }}</span>
                      </div>
                      <div class="mt-2 d-flex align-items-center">
                        <i class="bi bi-pin-map me-2 text-muted"></i>
                        <span>PIN: {{ selectedRequest.customer.user.pin_code }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button
              v-if="activeTab === 'available'"
              type="button"
              class="btn btn-success"
              @click="acceptRequestFromModal"
              :disabled="isRequestProcessing"
            >
              <span v-if="isRequestProcessing" class="spinner-border spinner-border-sm me-1"></span>
              Accept Request
            </button>
            <button
              v-if="activeTab === 'ongoing'"
              type="button"
              class="btn btn-success"
              @click="showCompleteModal"
              :disabled="isRequestProcessing"
            >
              <span v-if="isRequestProcessing" class="spinner-border spinner-border-sm me-1"></span>
              Mark as Completed
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Request Modal -->
    <div class="modal fade" id="completeRequestModal" tabindex="-1" ref="completeRequestModal">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title">Complete Service Request</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitCompletion">
              <div class="mb-3">
                <label for="remarks" class="form-label"
                  >Service Remarks <span class="text-danger">*</span></label
                >
                <textarea
                  id="remarks"
                  class="form-control"
                  v-model="completionRemarks"
                  rows="4"
                  placeholder="Please provide details about the service completed..."
                  :class="{ 'is-invalid': remarksError }"
                  required
                ></textarea>
                <div class="invalid-feedback" v-if="remarksError">
                  {{ remarksError }}
                </div>
                <div class="form-text">
                  Include important details about the work performed, materials used, and any
                  follow-up recommendations.
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-success"
              @click="submitCompletion"
              :disabled="isRequestProcessing"
            >
              <span v-if="isRequestProcessing" class="spinner-border spinner-border-sm me-1"></span>
              Complete Service
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
  name: 'ProfessionalServiceRequests',
  setup() {
    const store = useStore()
    const route = useRoute()
    // eslint-disable-next-line no-unused-vars
    const router = useRouter()

    // Refs for modals
    const requestDetailModal = ref(null)
    const completeRequestModal = ref(null)
    let bsRequestDetailModal = null
    let bsCompleteRequestModal = null

    // State
    const activeTab = ref('available') // available, ongoing, completed
    const requests = ref([])
    const isLoading = ref(true)
    const error = ref(null)
    const currentPage = ref(1)
    const searchQuery = ref('')
    const selectedRequest = ref(null)
    const completionRemarks = ref('')
    const remarksError = ref('')
    const processingRequestId = ref(null)

    // Computed properties
    const isRequestProcessing = computed(() => processingRequestId.value !== null)

    const totalRequests = computed(() => store.getters['requests/pagination']?.total || 0)
    const totalPages = computed(() => store.getters['requests/pagination']?.pages || 1)
    const perPage = computed(() => store.getters['requests/pagination']?.per_page || 10)

    const startIndex = computed(() => (currentPage.value - 1) * perPage.value)
    const endIndex = computed(() => Math.min(startIndex.value + perPage.value, totalRequests.value))

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

    const filteredRequests = computed(() => {
      if (!searchQuery.value.trim()) return requests.value

      const query = searchQuery.value.toLowerCase()
      return requests.value.filter(
        (request) =>
          request.service.name.toLowerCase().includes(query) ||
          request.customer.user.full_name.toLowerCase().includes(query) ||
          request.customer.user.address.toLowerCase().includes(query) ||
          request.description?.toLowerCase().includes(query),
      )
    })

    // Methods
    const setActiveTab = (tab) => {
      activeTab.value = tab
      currentPage.value = 1
      searchQuery.value = ''
      fetchRequests()
    }

    const getActiveTabTitle = () => {
      switch (activeTab.value) {
        case 'available':
          return 'Available Service Requests'
        case 'ongoing':
          return 'Ongoing Services'
        case 'completed':
          return 'Completed Services'
        default:
          return 'Service Requests'
      }
    }

    const fetchRequests = async () => {
      isLoading.value = true
      error.value = null

      try {
        // Map activeTab to the API's type parameter
        const typeParam = {
          available: 'new',
          ongoing: 'ongoing',
          completed: 'completed',
        }[activeTab.value]

        const response = await store.dispatch('requests/fetchProfessionalRequests', {
          type: typeParam,
          page: currentPage.value,
          perPage: perPage.value,
        })

        requests.value = response.data || []
      } catch (err) {
        console.error('Error fetching requests:', err)
        error.value = 'Failed to load service requests. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    const changePage = (page) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      fetchRequests()
    }

    const handleSearch = () => {
      // If search is cleared, we might want to refresh the full list
      if (searchQuery.value === '') {
        fetchRequests()
      }
    }

    const clearSearch = () => {
      searchQuery.value = ''
      handleSearch()
    }

    const viewRequestDetails = (request) => {
      selectedRequest.value = request
      bsRequestDetailModal.show()
    }

    const acceptRequest = async (request) => {
      if (isRequestProcessing.value) return

      processingRequestId.value = request.id
      try {
        await store.dispatch('requests/acceptRequest', request.id)
        window.showToast({
          type: 'success',
          title: 'Success',
          message: 'Service request accepted successfully!',
        })
        fetchRequests() // Refresh the list
      } catch (error) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: error.response?.data?.message || 'Failed to accept request. Please try again.',
        })
      } finally {
        processingRequestId.value = null
      }
    }

    const acceptRequestFromModal = async () => {
      if (!selectedRequest.value || isRequestProcessing.value) return

      processingRequestId.value = selectedRequest.value.id
      try {
        await store.dispatch('requests/acceptRequest', selectedRequest.value.id)
        window.showToast({
          type: 'success',
          title: 'Success',
          message: 'Service request accepted successfully!',
        })
        bsRequestDetailModal.hide()
        fetchRequests() // Refresh the list
      } catch (error) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: error.response?.data?.message || 'Failed to accept request. Please try again.',
        })
      } finally {
        processingRequestId.value = null
      }
    }

    const completeRequest = (request) => {
      selectedRequest.value = request
      completionRemarks.value = ''
      remarksError.value = ''
      bsCompleteRequestModal.show()
    }

    const showCompleteModal = () => {
      if (!selectedRequest.value) return
      bsRequestDetailModal.hide()
      completionRemarks.value = ''
      remarksError.value = ''
      bsCompleteRequestModal.show()
    }

    const submitCompletion = async () => {
      if (!selectedRequest.value || isRequestProcessing.value) return

      // Validate remarks
      if (!completionRemarks.value.trim()) {
        remarksError.value = 'Please provide remarks about the completed service'
        return
      }

      processingRequestId.value = selectedRequest.value.id
      try {
        await store.dispatch('requests/completeRequest', {
          id: selectedRequest.value.id,
          remarks: completionRemarks.value.trim(),
        })

        window.showToast({
          type: 'success',
          title: 'Success',
          message: 'Service has been marked as completed!',
        })

        bsCompleteRequestModal.hide()
        fetchRequests() // Refresh the list
      } catch (error) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: error.response?.data?.message || 'Failed to complete service. Please try again.',
        })
      } finally {
        processingRequestId.value = null
      }
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

      // Otherwise, show full date and time
      return date.format('MMM D, YYYY h:mm A')
    }

    const formatDateOnly = (dateString) => {
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

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }

    // Initialize from route query params
    watch(
      () => route.query.type,
      (newType) => {
        if (newType && ['available', 'ongoing', 'completed'].includes(newType)) {
          activeTab.value = newType
        }
      },
      { immediate: true },
    )

    // Lifecycle hooks
    onMounted(() => {
      if (requestDetailModal.value) {
        bsRequestDetailModal = new bootstrap.Modal(requestDetailModal.value)
      }

      if (completeRequestModal.value) {
        bsCompleteRequestModal = new bootstrap.Modal(completeRequestModal.value)
      }

      // Check if we have a type in the query params
      const queryType = route.query.type
      if (queryType && ['available', 'ongoing', 'completed'].includes(queryType)) {
        activeTab.value = queryType
      }

      fetchRequests()
    })

    return {
      activeTab,
      requests,
      isLoading,
      error,
      currentPage,
      totalPages,
      perPage,
      totalRequests,
      startIndex,
      endIndex,
      displayedPages,
      searchQuery,
      selectedRequest,
      filteredRequests,
      requestDetailModal,
      completeRequestModal,
      completionRemarks,
      remarksError,
      processingRequestId,
      isRequestProcessing,

      // Methods
      setActiveTab,
      getActiveTabTitle,
      fetchRequests,
      changePage,
      handleSearch,
      clearSearch,
      viewRequestDetails,
      acceptRequest,
      acceptRequestFromModal,
      completeRequest,
      showCompleteModal,
      submitCompletion,
      formatDate,
      formatDateOnly,
      formatDuration,
      formatPhone,
      formatStatus,
      getStatusBadgeClass,
      truncateText,
    }
  },
}
</script>

<style scoped>
.nav-pills .nav-link {
  cursor: pointer;
  padding: 0.5rem 1rem;
}

.list-group-item {
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
  width: 40px;
  height: 40px;
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

/* Responsive styles */
@media (max-width: 767.98px) {
  .card-footer .pagination {
    justify-content: center !important;
    margin-top: 1rem;
  }

  .card-footer .text-muted {
    text-align: center;
  }
}
</style>
