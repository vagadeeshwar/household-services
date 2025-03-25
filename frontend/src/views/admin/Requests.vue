<template>
  <div class="container py-4">
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">Service Requests</h1>
        <p class="text-muted">Manage and monitor all service requests across the platform</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <!-- User Selector (Customer/Professional) -->
          <div class="col-md-4">
            <label for="userSelector" class="form-label">Select User</label>
            <select
              id="userSelector"
              class="form-select"
              v-model="selectedUser"
              @change="handleUserChange"
            >
              <optgroup label="Customers">
                <option
                  v-for="customer in customers"
                  :key="`customer-${customer.customer_id}`"
                  :value="{ type: 'customer', id: customer.customer_id, name: customer.full_name }"
                >
                  {{ customer.full_name }} (Customer)
                </option>
              </optgroup>
              <optgroup label="Professionals">
                <option
                  v-for="professional in professionals"
                  :key="`professional-${professional.professional_id}`"
                  :value="{
                    type: 'professional',
                    id: professional.professional_id,
                    name: professional.full_name,
                  }"
                >
                  {{ professional.full_name }} (Professional)
                </option>
              </optgroup>
            </select>
          </div>

          <!-- Status Filter -->
          <div class="col-md-2">
            <label for="statusFilter" class="form-label">Status</label>
            <select
              id="statusFilter"
              class="form-select"
              v-model="filters.status"
              @change="applyFilters"
            >
              <option value="">All Statuses</option>
              <option value="created">Pending</option>
              <option value="assigned">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          <!-- Service Type Filter -->
          <div class="col-md-2">
            <label for="serviceType" class="form-label">Service Type</label>
            <select
              id="serviceType"
              class="form-select"
              v-model="selectedServiceId"
              @change="handleServiceChange"
            >
              <option value="">All Services</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>

          <!-- Date Range Filter -->
          <div class="col-md-2">
            <label for="startDate" class="form-label">Start Date</label>
            <input
              type="date"
              id="startDate"
              class="form-control"
              v-model="filters.start_date"
              @change="validateDateRange"
            />
          </div>
          <div class="col-md-2">
            <label for="endDate" class="form-label">End Date</label>
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
          <div class="col-md-12 text-end">
            <button class="btn btn-outline-secondary" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset Filters
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Requests Table -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="isLoading" class="text-center p-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading service requests...</p>
        </div>
        <div v-else-if="filteredRequests.length === 0" class="text-center p-5">
          <i class="bi bi-clipboard-x text-muted" style="font-size: 3rem"></i>
          <p class="mt-3 mb-0">No service requests found for this user with the applied filters.</p>
          <button class="btn btn-link mt-2" @click="resetFilters">Reset filters</button>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover table-striped mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Service</th>
                <th scope="col">
                  {{ selectedUser?.type === 'customer' ? 'Professional' : 'Customer' }}
                </th>
                <th scope="col">Request Date</th>
                <th scope="col">Status</th>
                <th scope="col" class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in filteredRequests" :key="request.id" class="align-middle">
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
                  <!-- Show professional if customer view, or customer if professional view -->
                  <div v-if="selectedUser?.type === 'customer' && request.professional">
                    <div class="fw-medium">{{ request.professional.full_name }}</div>
                    <div
                      class="d-flex align-items-center"
                      v-if="request.professional.average_rating"
                    >
                      <i class="bi bi-star-fill text-warning me-1"></i>
                      <small>{{ request.professional.average_rating }}</small>
                    </div>
                  </div>
                  <span
                    v-else-if="selectedUser?.type === 'customer' && !request.professional"
                    class="badge bg-secondary"
                    >Not Assigned</span
                  >
                  <div v-else-if="selectedUser?.type === 'professional' && request.customer">
                    <div class="fw-medium">{{ request.customer.full_name }}</div>
                  </div>
                  <span v-else class="text-muted">Unknown</span>
                </td>
                <td>{{ formatDate(request.date_of_request) }}</td>

                <td>
                  <span class="badge" :class="getStatusBadgeClass(request.status)">
                    {{ getStatusLabel(request.status) }}
                  </span>
                </td>
                <td class="text-end">
                  <div class="btn-group">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="viewRequestDetails(request)"
                      title="View details"
                    >
                      <i class="bi bi-eye"></i>
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
            >Showing {{ filteredRequests.length }} of {{ pagination.total || 0 }} requests</span
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

    <!-- Request Detail Modal -->
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
                      <label class="form-label text-muted small">Preferred Time</label>
                      <div class="fw-medium">
                        {{ formatTime(selectedRequest.preferred_time) }}
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
              <div class="col-md-6">
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
                        <small class="text-muted" v-if="selectedRequest.customer_id"
                          >ID: {{ selectedRequest.customer_id }}</small
                        >
                      </div>
                    </div>
                    <div class="mb-2" v-if="customerDetails">
                      <div class="mb-2 row">
                        <div class="col-md-4 text-muted">Email:</div>
                        <div class="col-md-8">{{ customerDetails.email }}</div>
                      </div>
                      <div class="mb-2 row">
                        <div class="col-md-4 text-muted">Phone:</div>
                        <div class="col-md-8">{{ customerDetails.phone }}</div>
                      </div>
                      <div class="mb-2 row">
                        <div class="col-md-4 text-muted">Address:</div>
                        <div class="col-md-8">{{ customerDetails.address }}</div>
                      </div>
                      <div class="row">
                        <div class="col-md-4 text-muted">PIN Code:</div>
                        <div class="col-md-8">{{ customerDetails.pin_code }}</div>
                      </div>
                    </div>
                    <div v-else class="text-center py-3">
                      <small class="text-muted">Loading customer details...</small>
                    </div>
                  </div>
                </div>
              </div>
              <!-- Professional Information -->
              <div class="col-md-6">
                <div class="card border">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Professional Information</h6>
                  </div>
                  <div class="card-body">
                    <div v-if="professionalDetails">
                      <div class="d-flex align-items-center mb-3">
                        <div class="avatar me-3 bg-light rounded-circle">
                          <i class="bi bi-person-badge"></i>
                        </div>
                        <div>
                          <div class="fw-bold">{{ professionalDetails.full_name }}</div>
                          <div
                            class="d-flex align-items-center"
                            v-if="professionalDetails.average_rating"
                          >
                            <i class="bi bi-star-fill text-warning me-1"></i>
                            <small>{{ professionalDetails.average_rating }}</small>
                          </div>
                        </div>
                      </div>
                      <div class="mb-2">
                        <div class="mb-2 row">
                          <div class="col-md-4 text-muted">Email:</div>
                          <div class="col-md-8">{{ professionalDetails.email }}</div>
                        </div>
                        <div class="mb-2 row">
                          <div class="col-md-4 text-muted">Phone:</div>
                          <div class="col-md-8">{{ professionalDetails.phone }}</div>
                        </div>
                        <div class="mb-2 row" v-if="professionalDetails.experience_years">
                          <div class="col-md-4 text-muted">Experience:</div>
                          <div class="col-md-8">
                            {{ professionalDetails.experience_years }} years
                          </div>
                        </div>
                        <div class="mb-2 row" v-if="professionalDetails.service_type_id">
                          <div class="col-md-4 text-muted">Service:</div>
                          <div class="col-md-8">
                            {{ getServiceName(professionalDetails.service_type_id) }}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div
                      v-else-if="
                        selectedRequest.status === 'assigned' ||
                        selectedRequest.status === 'completed'
                      "
                      class="text-center py-3"
                    >
                      <div
                        class="spinner-border spinner-border-sm text-primary me-2"
                        role="status"
                      ></div>
                      <small class="text-muted">Loading professional details...</small>
                    </div>
                    <div v-else class="text-center py-4">
                      <i class="bi bi-person-x text-muted mb-2" style="font-size: 2rem"></i>
                      <p class="mb-0">No professional assigned yet</p>
                      <small class="text-muted">(Request is pending assignment)</small>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Review Information -->
              <div class="col-md-12" v-if="selectedRequest.has_review && selectedRequest.review">
                <div class="card border">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Customer Review</h6>
                  </div>
                  <div class="card-body">
                    <div class="d-flex mb-2">
                      <div>
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
                    <div v-if="selectedRequest.review.is_reported" class="alert alert-warning mt-3">
                      <i class="bi bi-exclamation-triangle-fill me-2"></i>
                      <strong>This review has been reported</strong>
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

import { useRoute } from 'vue-router'

export default defineComponent({
  name: 'AdminRequests',

  setup() {
    const store = useStore()
    const { isLoading, withLoading } = useLoading()

    // References to modals
    const detailModal = ref(null)
    let bsDetailModal = null

    const route = useRoute()

    // State
    const requests = computed(() => store.getters['requests/allRequests'])
    const pagination = computed(() => store.getters['requests/pagination'])
    const customers = ref([])
    const professionals = ref([])
    const services = ref([])
    const selectedRequest = ref(null)
    const customerDetails = ref(null)
    const professionalDetails = ref(null)
    const selectedUser = ref(null)
    const selectedServiceId = ref('')

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

    const filteredRequests = computed(() => {
      // If no service type filter, return all requests
      if (!selectedServiceId.value) {
        return requests.value
      }

      // Filter requests by service type (frontend filtering)
      return requests.value.filter((request) => {
        return request.service_id == selectedServiceId.value
      })
    })

    // Methods
    const fetchCustomers = async () => {
      try {
        const response = await store.dispatch('customers/fetchCustomers', {
          params: { per_page: 100 },
          forceRefresh: true,
        })
        customers.value = response.data || []

        // Auto-select first customer if none selected
        if (customers.value.length > 0 && !selectedUser.value) {
          selectedUser.value = {
            type: 'customer',
            id: customers.value[0].customer_id,
            name: customers.value[0].full_name,
          }
          fetchRequests()
        }
      } catch (error) {
        console.error('Error fetching customers:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load customers',
        })
      }
    }

    const fetchProfessionals = async () => {
      try {
        const response = await store.dispatch('professionals/fetchProfessionals', {
          params: { per_page: 100 },
          forceRefresh: true,
        })
        professionals.value = response.data || []
      } catch (error) {
        console.error('Error fetching professionals:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load professionals',
        })
      }
    }

    const fetchServices = async () => {
      try {
        const response = await store.dispatch('services/fetchAllServices', {
          params: { per_page: 100 },
        })
        services.value = response.data || []
      } catch (error) {
        console.error('Error fetching services:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load services',
        })
      }
    }

    const fetchRequests = async (forceRefresh = false) => {
      if (!selectedUser.value) return

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
        if (selectedUser.value.type === 'customer') {
          await withLoading(
            store.dispatch('requests/fetchCustomerRequestsById', {
              id: selectedUser.value.id,
              params,
              forceRefresh,
            }),
            'Loading customer requests...',
          )
        } else {
          await withLoading(
            store.dispatch('requests/fetchProfessionalRequestsById', {
              id: selectedUser.value.id,
              params,
              forceRefresh,
            }),
            'Loading professional requests...',
          )
        }
      } catch (error) {
        console.error('Error fetching requests:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load requests',
        })
      }
    }
    const fetchCustomerDetails = async (customerId) => {
      try {
        customerDetails.value = null
        if (!customerId) return

        // The issue is here - we need to check the response structure
        const response = await store.dispatch('customers/fetchCustomerById', {
          id: customerId,
          forceRefresh: true, // Force fresh data
        })

        // Correctly handle the response based on actual API structure
        if (response && response.data) {
          customerDetails.value = response.data
        } else if (response) {
          // If data property doesn't exist, the full response might be the customer data
          customerDetails.value = response
        }

        console.log('Customer details loaded:', customerDetails.value)
      } catch (error) {
        console.error('Error fetching customer details:', error)
        window.showToast({
          type: 'danger',
          title: 'Failed to load customer details',
        })
      }
    }

    const fetchProfessionalDetails = async (professionalId) => {
      try {
        professionalDetails.value = null
        if (!professionalId) return
        console.log('Fetching professional details for ID:', professionalId)
        // Fix the parameter order to match the store action definition
        const response = await store.dispatch('professionals/fetchProfessionalById', {
          id: professionalId,
          params: {}, // Add the missing params object
          forceRefresh: false,
        })
        console.log('Professional details response:', response)
        // Updated handling of response data
        if (response && response.data) {
          professionalDetails.value = response.data
        } else {
          professionalDetails.value = response
        }
      } catch (error) {
        console.error('Error fetching professional details:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load professional details',
        })
      }
    }

    const getCustomerName = (request) => {
      // First check if we have customerDetails loaded
      if (customerDetails.value && customerDetails.value.full_name) {
        return customerDetails.value.full_name
      }
      // Then fall back to the request.customer property
      if (request.customer && request.customer.full_name) {
        return request.customer.full_name
      }
      // Finally try other properties that might contain the name
      if (request.customer_name) {
        return request.customer_name
      }
      return 'Unknown Customer'
    }

    const getStatusBadgeClass = (status) => requestStatusBadges[status]
    const getStatusLabel = (status) => statusLabels[status]

    const viewRequestDetails = (request) => {
      selectedRequest.value = request
      // Reset details
      customerDetails.value = null
      professionalDetails.value = null
      // Show modal first
      bsDetailModal.show()

      // Extract IDs directly from the request object when possible
      let customerId = null
      let professionalId = null

      // For requests viewed from professional perspective
      if (selectedUser.value?.type === 'professional') {
        // Get customer info from the request - check all possible locations
        customerId =
          request.customer_id ||
          (request.customer && request.customer.id) ||
          (request.customer && request.customer.customer_id)

        console.log('Extracted customer ID:', customerId)
        // The professional is the current user
        professionalId = selectedUser.value.id
      }
      // For requests viewed from customer perspective
      else if (selectedUser.value?.type === 'customer') {
        // The customer is the current user
        customerId = selectedUser.value.id
        // Only try to get professional if status is assigned or completed
        if (
          (request.status === 'assigned' || request.status === 'completed') &&
          request.professional
        ) {
          professionalId = request.professional.id || request.professional_id
        }
      }

      // Fetch the details if we have IDs
      if (customerId) {
        fetchCustomerDetails(customerId)
      }

      if (professionalId) {
        fetchProfessionalDetails(professionalId)
      }
    }

    const handleUserChange = () => {
      // Reset filters when user changes
      resetFilters()
    }

    const handleServiceChange = () => {
      // No backend request needed since filtering by service happens on the frontend
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
      filters.value = {
        status: '',
        start_date: '',
        end_date: '',
        page: 1,
        per_page: 10,
      }
      selectedServiceId.value = ''
      fetchRequests(true)
    }

    const changePage = (page) => {
      if (page < 1 || page > pagination.value.pages) return
      filters.value.page = page
      fetchRequests()
    }

    const getServiceName = (serviceId) => {
      if (!serviceId || !services.value) return 'Unknown service'
      const service = services.value.find((s) => s.id === serviceId)
      return service ? service.name : 'Unknown service'
    }

    const checkQueryParams = () => {
      // Only proceed if we have a professional ID in query params AND professionals are loaded
      if (route.query.professional_id && professionals.value && professionals.value.length > 0) {
        const profId = parseInt(route.query.professional_id)
        // Find the professional in the list
        const prof = professionals.value.find((p) => p.professional_id === profId)
        if (prof) {
          // Just set the selected user to this professional
          selectedUser.value = {
            type: 'professional',
            id: prof.professional_id,
            name: prof.full_name || route.query.professional_name,
          }
          // The existing handleUserChange will fetch requests for this professional
          fetchRequests(true)
        } else {
          console.log(`Professional with ID ${profId} not found in loaded professionals`)
        }
      } else if (route.query.customer_id && customers.value && customers.value.length > 0) {
        const fetchCustomerById = parseInt(route.query.customer_id)
        // Find the customer in the list
        const customer = customers.value.find((p) => p.customer_id === fetchCustomerById)
        if (customer) {
          // Just set the selected user to this customer
          selectedUser.value = {
            type: 'customer',
            id: customer.customer_id,
            name: customer.full_name || route.query.customer_name,
          }
          // The existing handleUserChange will fetch requests for this customer
          fetchRequests(true)
        } else {
          console.log(`Customer with ID ${fetchCustomerById} not found in loaded customers`)
        }
      }
    }

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

    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      if (detailModal.value) {
        bsDetailModal = new bootstrap.Modal(detailModal.value)
      }

      try {
        // Fetch initial data
        await Promise.all([fetchCustomers(), fetchProfessionals(), fetchServices()])
        // Only check query params after data is loaded successfully
        checkQueryParams()
      } catch (error) {
        console.error('Error loading initial data:', error)
        window.showToast({
          type: 'danger',
          title: 'Please try refreshing the page',
        })
      }
    })

    // Add a watch on professionals to handle late loading
    watch(
      () => professionals.value,
      (newVal) => {
        if (newVal && newVal.length > 0 && route.query.professional_id) {
          checkQueryParams()
        }
      },
    )
    watch(
      () => customers.value,
      (newVal) => {
        if (newVal && newVal.length > 0 && route.query.customer_id) {
          checkQueryParams()
        }
      },
    )

    return {
      // State
      requests,
      filteredRequests,
      customers,
      professionals,
      services,
      pagination,
      paginationRange,
      selectedRequest,
      customerDetails,
      professionalDetails,
      selectedUser,
      selectedServiceId,
      filters,
      isLoading,

      // Refs
      detailModal,

      // Methods
      fetchRequests,
      viewRequestDetails,
      getCustomerName,
      getStatusBadgeClass,
      getStatusLabel,
      handleUserChange,
      handleServiceChange,
      validateDateRange,
      applyFilters,
      resetFilters,
      changePage,
      formatDate,
      formatDateTime,
      formatTime,
      getServiceName,
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
}
</style>
