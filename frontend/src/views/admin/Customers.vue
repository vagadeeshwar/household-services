<template>
  <div class="container py-4">
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">Manage Customers</h1>
        <p class="text-muted">View and manage customer accounts</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label for="searchTerm" class="form-label">Search</label>
            <div class="input-group">
              <input
                type="text"
                id="searchTerm"
                class="form-control"
                placeholder="Search by name or email"
                v-model="searchTerm"
                @input="handleSearchInput"
              />
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="clearSearch"
                title="Clear search"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
          </div>
          <div class="col-md-4">
            <label for="statusFilter" class="form-label">Status</label>
            <select
              id="statusFilter"
              class="form-select"
              v-model="filters.active"
              @change="applyFilters"
            >
              <option value="">All Statuses</option>
              <option :value="true">Active</option>
              <option :value="false">Blocked</option>
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

    <!-- Customers Table -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="isLoading" class="text-center p-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading customers...</p>
        </div>
        <div v-else-if="filteredCustomers.length === 0" class="text-center p-5">
          <i class="bi bi-people text-muted" style="font-size: 3rem"></i>
          <p class="mt-3 mb-0">No customers found matching the criteria.</p>
          <button class="btn btn-link mt-2" @click="resetFilters">Reset filters</button>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover table-striped mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th scope="col">Email</th>
                <th scope="col">Phone</th>
                <th scope="col">PIN Code</th>
                <th scope="col">Status</th>
                <th scope="col">Joined</th>
                <th scope="col" class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="customer in filteredCustomers"
                :key="customer.customer_id"
                class="align-middle"
              >
                <td>{{ customer.customer_id }}</td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar me-2 bg-light rounded-circle">
                      <i class="bi bi-person"></i>
                    </div>
                    <div>
                      <div class="fw-bold">{{ customer.full_name }}</div>
                      <small class="text-muted">{{ customer.username }}</small>
                    </div>
                  </div>
                </td>
                <td>{{ customer.email }}</td>
                <td>{{ customer.phone }}</td>
                <td>{{ customer.pin_code }}</td>
                <td>
                  <span :class="['badge', customer.is_active ? 'bg-success' : 'bg-danger']">
                    {{ customer.is_active ? 'Active' : 'Blocked' }}
                  </span>
                </td>
                <td>{{ formatDate(customer.created_at) }}</td>
                <td class="text-end">
                  <div class="btn-group">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="viewCustomerDetails(customer)"
                      title="View details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button
                      class="btn btn-sm"
                      :class="customer.is_active ? 'btn-outline-danger' : 'btn-outline-success'"
                      @click="toggleBlockStatus(customer)"
                      :title="customer.is_active ? 'Block account' : 'Unblock account'"
                    >
                      <i
                        class="bi"
                        :class="customer.is_active ? 'bi-slash-circle' : 'bi-unlock'"
                      ></i>
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
            >Showing {{ filteredCustomers.length }} of {{ pagination.total || 0 }} customers</span
          >
        </div>
        <nav aria-label="Customers pagination" v-if="pagination.pages > 1">
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

    <!-- Customer Detail Modal -->
    <div
      class="modal fade"
      id="customerDetailModal"
      tabindex="-1"
      aria-labelledby="customerDetailModalLabel"
      aria-hidden="true"
      ref="detailModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedCustomer">
          <div class="modal-header">
            <h5 class="modal-title" id="customerDetailModalLabel">Customer Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-4 mb-3">
                <div class="text-center">
                  <div
                    class="avatar mx-auto mb-3 bg-light rounded-circle d-flex align-items-center justify-content-center"
                    style="width: 100px; height: 100px"
                  >
                    <i class="bi bi-person-circle" style="font-size: 3rem"></i>
                  </div>
                  <h5 class="mb-1">{{ selectedCustomer.full_name }}</h5>
                  <div class="d-flex justify-content-center align-items-center">
                    <span
                      :class="['badge', selectedCustomer.is_active ? 'bg-success' : 'bg-danger']"
                    >
                      {{ selectedCustomer.is_active ? 'Active' : 'Blocked' }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="col-md-8">
                <h6 class="mb-3">Account Information</h6>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Email</label>
                      <div>{{ selectedCustomer.email }}</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Phone</label>
                      <div>{{ selectedCustomer.phone }}</div>
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label text-muted small">Address</label>
                  <div>{{ selectedCustomer.address }}</div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">PIN Code</label>
                      <div>{{ selectedCustomer.pin_code }}</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Username</label>
                      <div>{{ selectedCustomer.username }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <hr />
            <div class="row">
              <div class="col-12">
                <h6 class="mb-3">Additional Information</h6>
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Member Since</label>
                      <div>{{ formatDate(selectedCustomer.created_at) }}</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Last Login</label>
                      <div>{{ formatDateTime(selectedCustomer.last_login) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <hr />

            <!-- Recent Service Requests -->
            <div class="row">
              <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h6 class="mb-0">Recent Service Requests</h6>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="viewAllCustomerRequests"
                    v-if="customerRequests.length > 0"
                  >
                    <i class="bi bi-eye me-1"></i> View All
                  </button>
                </div>
                <div v-if="isLoadingRequests" class="text-center py-4">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                  <p class="text-muted mt-2 mb-0">Loading service requests...</p>
                </div>
                <div v-else-if="customerRequests.length === 0" class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>
                  This customer has no service requests yet.
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-sm table-hover border">
                    <thead class="table-light">
                      <tr>
                        <th>ID</th>
                        <th>Service</th>
                        <th>Date</th>
                        <th>Professional</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="request in customerRequests"
                        :key="request.id"
                        class="align-middle"
                      >
                        <td>#{{ request.id }}</td>
                        <td>
                          <div class="d-flex align-items-center">
                            <div>
                              <div class="fw-medium">{{ request.service_name }}</div>
                              <small class="text-muted">₹{{ request.service_price }}</small>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div>{{ formatDate(request.date_of_request) }}</div>
                          <small class="text-muted">{{ formatTime(request.preferred_time) }}</small>
                        </td>
                        <td>
                          <div v-if="request.professional">
                            {{ request.professional.full_name }}
                            <div
                              class="text-muted small"
                              v-if="request.professional.average_rating"
                            >
                              <i class="bi bi-star-fill text-warning"></i>
                              {{ request.professional.average_rating }}
                            </div>
                          </div>
                          <span v-else class="badge bg-secondary">Not Assigned</span>
                        </td>
                        <td>
                          <span class="badge" :class="getStatusBadgeClass(request.status)">
                            {{ getStatusLabel(request.status) }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
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

    <!-- Block/Unblock Confirmation Modal -->
    <div
      class="modal fade"
      id="confirmActionModal"
      tabindex="-1"
      aria-labelledby="confirmActionModalLabel"
      aria-hidden="true"
      ref="confirmModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="confirmActionModalLabel">
              {{ confirmAction.title }}
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>{{ confirmAction.message }}</p>
            <div v-if="confirmAction.type === 'block'">
              <label for="blockReason" class="form-label">Reason for blocking</label>
              <textarea
                id="blockReason"
                class="form-control"
                rows="3"
                v-model="blockReason"
                placeholder="Please provide a reason for blocking this customer"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              :class="['btn', confirmAction.buttonClass]"
              @click="executeConfirmedAction"
              :disabled="actionInProgress"
            >
              <span
                v-if="actionInProgress"
                class="spinner-border spinner-border-sm me-1"
                role="status"
                aria-hidden="true"
              ></span>
              {{ confirmAction.buttonText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import * as bootstrap from 'bootstrap'
import { formatDate, formatDateTime, formatTime } from '@/utils/date'
import { useLoading } from '@/composables/useLoading'
import { requestStatusBadges, statusLabels } from '@/assets/requestStatuses'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'AdminCustomers',
  setup() {
    const store = useStore()
    const { isLoading, withLoading } = useLoading()

    // References to modals
    const detailModal = ref(null)
    const confirmModal = ref(null)
    let bsDetailModal = null
    let bsConfirmModal = null

    const router = useRouter()

    // State
    const customers = computed(() => store.getters['customers/allCustomers'])
    const pagination = computed(() => store.getters['customers/pagination'])

    const customerRequests = computed(() => store.getters['requests/allRequests'])
    const isLoadingRequests = computed(() => store.getters['requests/isLoading'])

    const selectedCustomer = ref(null)
    const searchTerm = ref('')
    const blockReason = ref('')
    const actionInProgress = ref(false)

    // Filters
    const filters = reactive({
      active: '',
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

    const fetchCustomerRequests = async (customerId) => {
      try {
        await store.dispatch('requests/fetchCustomerRequestsById', {
          id: customerId,
          params: {
            page: 1,
            per_page: 5, // Limit to 5 recent requests
            summary: false,
          },
          forceRefresh: false,
        })
      } catch (error) {
        console.error('Error fetching customer requests:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load customer requests',
        })
      }
    }

    const getStatusBadgeClass = (status) => requestStatusBadges[status]

    const getStatusLabel = (status) => statusLabels[status]

    const viewAllCustomerRequests = () => {
      if (selectedCustomer.value) {
        router.push({
          name: 'AdminRequests',
          query: {
            customer_id: selectedCustomer.value.customer_id,
            customer_name: selectedCustomer.value.full_name,
          },
        })
        // Close the modal
        bsDetailModal.hide()
      }
    }

    const viewCustomerDetails = (customer) => {
      selectedCustomer.value = customer
      bsDetailModal.show()
      // Only fetch the customer's requests
      fetchCustomerRequests(customer.customer_id).catch((error) => {
        console.error('Error fetching customer requests:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load customer requests',
        })
      })
    }

    const filteredCustomers = computed(() => {
      if (!searchTerm.value.trim()) {
        return customers.value
      }
      const term = searchTerm.value.toLowerCase().trim()
      return customers.value.filter((customer) => {
        const fullName = customer.full_name?.toLowerCase() || ''
        const email = customer.email?.toLowerCase() || ''
        const username = customer.username?.toLowerCase() || ''
        const phone = customer.phone?.toLowerCase() || ''
        return (
          fullName.includes(term) ||
          email.includes(term) ||
          username.includes(term) ||
          phone.includes(term)
        )
      })
    })

    // Action confirmation
    const confirmAction = ref({
      title: '',
      message: '',
      buttonText: '',
      buttonClass: '',
      type: '',
      callback: null,
    })

    // Methods
    const fetchCustomers = async (forceRefresh = false) => {
      // Start with empty params object
      const params = {}
      // Only add non-empty filters
      Object.entries(filters).forEach(([key, value]) => {
        // Include parameters that have values (not empty strings, null, or undefined)
        if (value !== '' && value !== null && value !== undefined) {
          params[key] = value
        }
      })

      await withLoading(
        store.dispatch('customers/fetchCustomers', { params, forceRefresh }),
        'Loading customers...',
      )
    }

    const toggleBlockStatus = (customer) => {
      if (customer.is_active) {
        confirmAction.value = {
          title: 'Block Customer',
          message: `Are you sure you want to block ${customer.full_name}? This will prevent them from accessing the platform.`,
          buttonText: 'Block',
          buttonClass: 'btn-danger',
          type: 'block',
          callback: () => blockCustomer(customer),
        }
      } else {
        confirmAction.value = {
          title: 'Unblock Customer',
          message: `Are you sure you want to unblock ${customer.full_name}? This will restore their access to the platform.`,
          buttonText: 'Unblock',
          buttonClass: 'btn-success',
          type: 'unblock',
          callback: () => unblockCustomer(customer),
        }
      }
      blockReason.value = ''
      bsConfirmModal.show()
    }

    const blockCustomer = async (customer) => {
      if (confirmAction.value.type === 'block' && !blockReason.value.trim()) {
        window.showToast({
          type: 'warning',
          title: 'Please provide a reason for blocking this customer',
        })
        return
      }

      actionInProgress.value = true
      try {
        await store.dispatch('customers/blockCustomer', {
          id: customer.customer_id,
          data: { reason: blockReason.value.trim() },
        })

        window.showToast({
          type: 'success',
          title: `${customer.full_name} has been blocked`,
        })

        // Refresh data
        await fetchCustomers(true)
        bsConfirmModal.hide()
      } catch (error) {
        console.error('Error blocking customer:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to block customer',
        })
      } finally {
        actionInProgress.value = false
      }
    }

    const unblockCustomer = async (customer) => {
      actionInProgress.value = true
      try {
        await store.dispatch('customers/unblockCustomer', { id: customer.customer_id })

        window.showToast({
          type: 'info',
          title: 'Customer has been unblocked successfully',
        })

        fetchCustomers(true)

        bsConfirmModal.hide()
      } catch (error) {
        console.error('Error unblocking customer:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to unblock customer',
        })
      } finally {
        actionInProgress.value = false
      }
    }

    const executeConfirmedAction = () => {
      if (confirmAction.value.callback) {
        confirmAction.value.callback()
      }
    }

    const handleSearchInput = () => {
      // Client-side filtering handled by computed property
      // Reset to first page when searching
      filters.page = 1
    }

    const clearSearch = () => {
      searchTerm.value = ''
      filters.page = 1
    }

    const applyFilters = () => {
      filters.page = 1
      fetchCustomers()
    }

    const resetFilters = () => {
      searchTerm.value = ''
      filters.active = ''
      filters.page = 1
      fetchCustomers(true)
    }

    const changePage = (page) => {
      if (page < 1 || page > pagination.value.pages) return
      filters.page = page
      fetchCustomers()
    }

    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      if (detailModal.value) {
        bsDetailModal = new bootstrap.Modal(detailModal.value)
      }
      if (confirmModal.value) {
        bsConfirmModal = new bootstrap.Modal(confirmModal.value)
      }

      // Fetch initial data
      await fetchCustomers()
    })

    return {
      // State
      customers,
      filteredCustomers,
      pagination,
      paginationRange,
      selectedCustomer,
      searchTerm,
      filters,
      confirmAction,
      blockReason,
      actionInProgress,
      isLoading,

      // Refs
      detailModal,
      confirmModal,

      // Methods
      fetchCustomers,
      viewCustomerDetails,
      toggleBlockStatus,
      executeConfirmedAction,
      handleSearchInput,
      clearSearch,
      applyFilters,
      resetFilters,
      changePage,
      formatDate,
      formatDateTime,
      customerRequests,
      isLoadingRequests,
      fetchCustomerRequests,
      getStatusBadgeClass,
      getStatusLabel,
      viewAllCustomerRequests,
      formatTime,
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
