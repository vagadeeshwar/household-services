<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Browse Services</h1>
        <p class="text-muted">Find the perfect service for your home needs</p>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <!-- Search -->
          <div class="col-md-4">
            <label class="form-label">Search Services</label>
            <div class="input-group">
              <input
                type="text"
                class="form-control"
                placeholder="Search services by name..."
                v-model="filters.search"
                @input="debouncedSearch"
              />
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="clearSearch"
                :disabled="!filters.search"
              >
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>

          <!-- Sort Options -->
          <div class="col-md-4">
            <label class="form-label">Sort By</label>
            <select class="form-select" v-model="filters.sortBy" @change="applyFilters">
              <option value="name">Name</option>
              <option value="base_price">Price: Low to High</option>
              <option value="-base_price">Price: High to Low</option>
              <option value="estimated_time">Duration</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label d-block">&nbsp;</label>
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading services...</p>
    </div>

    <!-- Error Alert -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button @click="fetchServices(true)" class="btn btn-sm btn-outline-danger ms-2">Retry</button>
    </div>

    <!-- No Services Found -->
    <div v-else-if="filteredServices.length === 0" class="text-center py-5">
      <div class="display-6 text-muted mb-3"><i class="bi bi-search"></i></div>
      <h4>No Services Found</h4>
      <p class="text-muted">Try adjusting your search criteria</p>
      <button @click="resetFilters" class="btn btn-outline-primary">
        <i class="bi bi-arrow-counterclockwise me-2"></i>Reset Filters
      </button>
    </div>

    <!-- Services Grid -->
    <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="service in filteredServices" :key="service.id" class="col">
        <div class="card h-100 shadow-sm hover-card">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="service-icon me-3">
                <i class="bi bi-tools"></i>
              </div>
              <h5 class="card-title mb-0">{{ service.name }}</h5>
            </div>
            <p class="card-text text-truncate mb-3">{{ service.description }}</p>
            <div class="d-flex justify-content-between mb-3">
              <div>
                <span class="fs-4 fw-semibold text-primary">₹{{ service.base_price }}</span>
              </div>
              <div>
                <span class="badge bg-light text-dark">
                  <i class="bi bi-clock me-1"></i>{{ formatDuration(service.estimated_time) }}
                </span>
              </div>
            </div>
            <div class="d-grid gap-2">
              <button class="btn btn-outline-primary" @click="showDetailsModal(service)">
                <i class="bi bi-info-circle me-2"></i>View Details
              </button>
              <button class="btn btn-primary" @click="showBookingModal(service)">
                <i class="bi bi-calendar-plus me-2"></i>Book Service
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1" class="mt-4">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button @click="changePage(currentPage - 1)" class="page-link">
            <i class="bi bi-chevron-left"></i>
          </button>
        </li>
        <li
          v-for="pageNum in displayedPages"
          :key="pageNum"
          class="page-item"
          :class="{ active: currentPage === pageNum }"
        >
          <button @click="changePage(pageNum)" class="page-link">{{ pageNum }}</button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <button @click="changePage(currentPage + 1)" class="page-link">
            <i class="bi bi-chevron-right"></i>
          </button>
        </li>
      </ul>
    </nav>

    <!-- Service Details Modal -->
    <div class="modal fade" id="detailsModal" tabindex="-1" ref="detailsModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-info-circle me-2"></i>Service Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body" v-if="selectedService">
            <div class="card border-0">
              <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="card-title mb-0">{{ selectedService.name }}</h5>
                </div>
              </div>
              <div class="card-body">
                <div class="row mb-4">
                  <div class="col-md-6">
                    <div class="d-flex align-items-center mb-3">
                      <div class="icon-box bg-primary-subtle me-3">
                        <i class="bi bi-currency-rupee text-primary"></i>
                      </div>
                      <div>
                        <h6 class="mb-0 text-muted">Base Price</h6>
                        <div class="h4 mb-0">₹{{ selectedService.base_price.toFixed(2) }}</div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-center mb-3">
                      <div class="icon-box bg-success-subtle me-3">
                        <i class="bi bi-clock text-success"></i>
                      </div>
                      <div>
                        <h6 class="mb-0 text-muted">Estimated Time</h6>
                        <div class="h4 mb-0">
                          {{ formatDuration(selectedService.estimated_time) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <h6 class="text-muted mb-2">Description</h6>
                <p class="bg-light p-3 rounded">{{ selectedService.description }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button
              type="button"
              class="btn btn-primary"
              @click="showBookingModal(selectedService)"
            >
              <i class="bi bi-calendar-plus me-2"></i>Book Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div class="modal fade" id="bookingModal" tabindex="-1" ref="bookingModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-calendar-plus me-2"></i>Book Service</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createServiceRequest" id="bookingForm">
              <div v-if="selectedService" class="mb-4">
                <div class="card bg-light border-0">
                  <div class="card-body py-2">
                    <div class="d-flex align-items-center">
                      <div class="flex-shrink-0">
                        <i class="bi bi-tools fs-4 text-primary"></i>
                      </div>
                      <div class="flex-grow-1 ms-3">
                        <h6 class="mb-0">{{ selectedService.name }}</h6>
                        <div class="small text-muted d-flex align-items-center mt-1">
                          <span class="me-3">
                            <i class="bi bi-currency-rupee me-1"></i
                            >{{ selectedService.base_price }}
                          </span>
                          <span>
                            <i class="bi bi-clock me-1"></i
                            >{{ formatDuration(selectedService.estimated_time) }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="serviceDate" class="form-label"
                  >Preferred Date & Time<span class="text-danger">*</span></label
                >
                <input
                  type="datetime-local"
                  id="serviceDate"
                  class="form-control"
                  v-model="bookingForm.preferred_time"
                  :class="{ 'is-invalid': bookingErrors.preferred_time }"
                  required
                  :min="minDateTime"
                  :max="maxDateTime"
                />
                <div class="invalid-feedback">
                  {{ bookingErrors.preferred_time }}
                </div>
                <div class="form-text">
                  Select a date and time within the next 7 days (9 AM to 6 PM)
                </div>
              </div>

              <div class="mb-3">
                <label for="serviceDescription" class="form-label"
                  >Description<span class="text-danger">*</span></label
                >
                <textarea
                  id="serviceDescription"
                  class="form-control"
                  rows="3"
                  placeholder="Please describe your specific requirements"
                  v-model="bookingForm.description"
                  :class="{ 'is-invalid': bookingErrors.description }"
                  required
                ></textarea>
                <div class="invalid-feedback">
                  {{ bookingErrors.description }}
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="submit"
              form="bookingForm"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isSubmitting ? 'Booking...' : 'Book Service' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as bootstrap from 'bootstrap'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { formatDateTime, formatDuration } from '@/utils/date'

export default {
  name: 'CustomerServices',

  setup() {
    const store = useStore()
    const router = useRouter()

    // Modal refs for Bootstrap
    const detailsModal = ref(null)
    const bookingModal = ref(null)
    let bsDetailsModal = null
    let bsBookingModal = null

    // State
    const services = computed(() => store.getters['services/allServices'] || [])
    const isLoading = computed(() => store.getters['services/isLoading'])
    const error = computed(() => store.getters['services/error'])
    const pagination = computed(() => store.getters['services/pagination'])
    const currentPage = ref(1)
    const perPage = ref(10)
    const selectedService = ref(null)
    const isSubmitting = ref(false)

    // Filters state
    const filters = reactive({
      search: '',
      sortBy: 'name',
    })

    // Booking form
    const bookingForm = reactive({
      service_id: null,
      preferred_time: '',
      description: '',
    })

    const bookingErrors = reactive({
      preferred_time: '',
      description: '',
    })

    // Datetime constraints
    const minDateTime = computed(() => {
      const now = new Date()
      // Set to next working hour (9AM - 6PM)
      const hour = now.getHours()
      if (hour < 9) {
        now.setHours(9, 0, 0, 0)
      } else if (hour >= 18) {
        // If it's after 6PM, set to 9AM the next day
        now.setDate(now.getDate() + 1)
        now.setHours(9, 0, 0, 0)
      } else {
        // Round to next hour
        now.setHours(hour + 1, 0, 0, 0)
      }
      return now.toISOString().slice(0, 16)
    })

    const maxDateTime = computed(() => {
      const max = new Date()
      max.setDate(max.getDate() + 7)
      max.setHours(18, 0, 0, 0)
      return max.toISOString().slice(0, 16)
    })

    // Search debounce timer
    let searchTimer = null

    // Computed properties
    const totalServices = computed(() => pagination.value?.total || 0)
    const totalPages = computed(() => pagination.value?.pages || 1)

    const filteredServices = computed(() => {
      if (!services.value) return []

      let result = [...services.value]

      // Filter by search term
      if (filters.search) {
        const query = filters.search.toLowerCase()
        result = result.filter(
          (service) =>
            service.name.toLowerCase().includes(query) ||
            service.description.toLowerCase().includes(query),
        )
      }

      // Sort services
      result = [...result].sort((a, b) => {
        const sortField = filters.sortBy.startsWith('-')
          ? filters.sortBy.substring(1)
          : filters.sortBy

        const sortOrder = filters.sortBy.startsWith('-') ? -1 : 1

        let valA = a[sortField]
        let valB = b[sortField]

        // Handle string comparisons
        if (typeof valA === 'string') {
          valA = valA.toLowerCase()
          valB = valB.toLowerCase()
        }

        return sortOrder * (valA > valB ? 1 : -1)
      })

      return result
    })

    const displayedPages = computed(() => {
      const pages = []
      const maxVisiblePages = 5
      const totalPg = totalPages.value || 1

      let startPage = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
      let endPage = Math.min(totalPg, startPage + maxVisiblePages - 1)

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1)
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      return pages
    })

    // Methods
    const fetchServices = async (forceRefresh = false) => {
      try {
        await store.dispatch('services/fetchActiveServices', {
          params: {
            page: currentPage.value,
            per_page: perPage.value,
          },
          forceRefresh,
        })
      } catch (err) {
        console.error('Error fetching services:', err)
      }
    }

    const showDetailsModal = (service) => {
      selectedService.value = service
      bsDetailsModal.show()
    }

    const showBookingModal = (service) => {
      // If coming from details modal, close it first
      if (bsDetailsModal && bsDetailsModal._isShown) {
        bsDetailsModal.hide()
      }

      selectedService.value = service
      resetBookingForm()
      bookingForm.service_id = service.id

      // Set default date to tomorrow at 10 AM
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      tomorrow.setHours(10, 0, 0, 0)
      bookingForm.preferred_time = tomorrow.toISOString().slice(0, 16)

      bsBookingModal.show()
    }

    const resetBookingForm = () => {
      bookingForm.service_id = null
      bookingForm.preferred_time = ''
      bookingForm.description = ''

      // Clear validation errors
      Object.keys(bookingErrors).forEach((key) => {
        bookingErrors[key] = ''
      })
    }

    const validateBookingForm = () => {
      let isValid = true

      // Reset validation errors
      Object.keys(bookingErrors).forEach((key) => {
        bookingErrors[key] = ''
      })

      // Preferred time validation
      if (!bookingForm.preferred_time) {
        bookingErrors.preferred_time = 'Please select a preferred date and time'
        isValid = false
      } else {
        const selectedTime = new Date(bookingForm.preferred_time)
        const now = new Date()
        const maxDate = new Date()
        maxDate.setDate(now.getDate() + 7)

        if (selectedTime < now) {
          bookingErrors.preferred_time = 'Please select a future date and time'
          isValid = false
        } else if (selectedTime > maxDate) {
          bookingErrors.preferred_time = 'Please select a date within the next 7 days'
          isValid = false
        }

        // Check if within business hours (9 AM to 6 PM)
        const hours = selectedTime.getHours()
        if (hours < 9 || hours >= 18) {
          bookingErrors.preferred_time = 'Please select a time between 9 AM and 6 PM'
          isValid = false
        }
      }

      // Description validation
      if (!bookingForm.description.trim()) {
        bookingErrors.description = 'Please provide a description'
        isValid = false
      } else if (bookingForm.description.length < 10) {
        bookingErrors.description = 'Description is too short (minimum 10 characters)'
        isValid = false
      } else if (bookingForm.description.length > 1000) {
        bookingErrors.description = 'Description is too long (maximum 1000 characters)'
        isValid = false
      }

      return isValid
    }

    const createServiceRequest = async () => {
      if (!validateBookingForm()) return

      isSubmitting.value = true

      try {
        await store.dispatch('requests/createRequest', {
          data: {
            service_id: bookingForm.service_id,
            preferred_time: bookingForm.preferred_time,
            description: bookingForm.description,
          },
        })

        window.showToast({
          type: 'success',
          title: 'Service Request Created',
          message: 'Your service request has been created successfully',
        })

        bsBookingModal.hide()

        // Navigate to the requests page to see the new request
        router.push('/customer/requests?status=created')
      } catch (err) {
        // Handle specific errors
        if (err.response?.data?.detail) {
          window.showToast({
            type: 'error',
            title: 'Booking Error',
            message: err.response.data.detail,
          })
        } else {
          window.showToast({
            type: 'error',
            title: 'Booking Error',
            message: 'An error occurred while creating your service request',
          })
        }
      } finally {
        isSubmitting.value = false
      }
    }

    const changePage = (page) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      fetchServices()
    }

    const debouncedSearch = () => {
      clearTimeout(searchTimer)
      searchTimer = setTimeout(() => {
        applyFilters()
      }, 300)
    }

    const clearSearch = () => {
      filters.search = ''
      applyFilters()
    }

    const resetFilters = () => {
      filters.search = ''
      filters.sortBy = 'name'
      applyFilters(true)
    }

    const applyFilters = (forceRefresh = false) => {
      currentPage.value = 1
      fetchServices(forceRefresh)
    }

    // Watch for filter changes
    watch(
      () => filters.sortBy,
      () => {
        applyFilters()
      },
    )

    // Lifecycle hooks
    onMounted(() => {
      // Initialize Bootstrap modals
      if (detailsModal.value) {
        bsDetailsModal = new bootstrap.Modal(detailsModal.value)
      }

      if (bookingModal.value) {
        bsBookingModal = new bootstrap.Modal(bookingModal.value)
      }

      // Initial data fetch
      fetchServices()
    })

    return {
      // Refs and state
      services,
      isLoading,
      error,
      detailsModal,
      bookingModal,
      currentPage,
      totalPages,
      selectedService,
      isSubmitting,
      filters,
      bookingForm,
      bookingErrors,
      minDateTime,
      maxDateTime,

      // Computed
      filteredServices,
      totalServices,
      displayedPages,

      // Methods
      fetchServices,
      formatDateTime,
      formatDuration,
      showDetailsModal,
      showBookingModal,
      createServiceRequest,
      changePage,
      debouncedSearch,
      clearSearch,
      resetFilters,
      applyFilters,
    }
  },
}
</script>

<style scoped>
.service-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--bs-primary);
}

.hover-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-box i {
  font-size: 1.5rem;
}

/* Custom form validation styles */
.form-control.is-invalid,
.form-select.is-invalid,
.form-check-input.is-invalid {
  border-color: #dc3545;
  box-shadow: 0 0 0 0.25rem rgba(220, 53, 69, 0.25);
}

/* For mobile devices */
@media (max-width: 768px) {
  .card-text {
    max-height: 3.6em;
    overflow: hidden;
  }

  .icon-box {
    width: 40px;
    height: 40px;
  }

  .icon-box i {
    font-size: 1.25rem;
  }
}
</style>
