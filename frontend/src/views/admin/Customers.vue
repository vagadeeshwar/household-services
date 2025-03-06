<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">Customer Management</h1>
      <div class="btn-group">
        <button class="btn btn-outline-primary" :class="{ active: !showBlocked }"
          @click="showBlocked = false">
          Active Customers
        </button>
        <button class="btn btn-outline-danger" :class="{ active: showBlocked }"
          @click="showBlocked = true">
          Blocked Customers
          <span v-if="blockedCount > 0" class="badge bg-danger ms-1">{{ blockedCount }}</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">PIN Code</label>
            <input type="text" class="form-control" placeholder="Filter by PIN code"
              v-model="filters.pinCode" @input="debouncedFilter" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Signup Date</label>
            <select class="form-select" v-model="filters.dateRange" @change="onFiltersChange">
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Search</label>
            <div class="input-group">
              <input type="text" class="form-control" placeholder="Search by name or email..."
                v-model="filters.search" @input="debouncedSearch" />
              <button class="btn btn-outline-secondary" type="button" @click="clearSearch">
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <Loading :show="isLoading" message="Loading customers..." :overlay="true" />

    <!-- Customers Table -->
    <div v-if="!isLoading" class="card shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Location</th>
              <th scope="col">Requests</th>
              <th scope="col">Status</th>
              <th scope="col">Joined</th>
              <th scope="col" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="customers.length === 0">
              <td colspan="7" class="text-center py-4 text-muted">
                <i class="bi bi-search me-2"></i>No customers found
              </td>
            </tr>
            <tr v-for="customer in customers" :key="customer.id">
              <td>{{ customer.customer_id }}</td>
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar bg-success text-white me-2">
                    <i class="bi bi-person-fill"></i>
                  </div>
                  <div>
                    <div class="fw-medium">{{ customer.full_name }}</div>
                    <div class="small text-muted">{{ customer.email }}</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="d-flex align-items-center">
                  <i class="bi bi-geo-alt text-danger me-2"></i>
                  {{ customer.pin_code }}
                </div>
              </td>
              <td>
                <span class="badge bg-info">
                  {{ customer.request_count || 0 }}
                </span>
              </td>
              <td>
                <span :class="[
                  'badge',
                  customer.is_active ? 'bg-success' : 'bg-danger',
                ]">
                  {{ customer.is_active ? 'Active' : 'Blocked' }}
                </span>
              </td>
              <td>{{ formatDate(customer.created_at) }}</td>
              <td class="text-end">
                <div class="btn-group">
                  <button class="btn btn-sm btn-outline-primary" @click="viewCustomer(customer)">
                    <i class="bi bi-eye"></i>
                  </button>
                  <button v-if="customer.is_active" class="btn btn-sm btn-outline-danger"
                    @click="showBlockModal(customer)" :disabled="isActionLoading">
                    <i class="bi bi-slash-circle"></i>
                  </button>
                  <button v-else class="btn btn-sm btn-outline-success"
                    @click="unblockCustomer(customer)" :disabled="isActionLoading">
                    <i class="bi bi-check-circle"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div class="card-footer bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-6 text-muted">
            Showing {{ customers.length }} of {{ totalCustomers }} customers
          </div>
          <div class="col-md-6">
            <ul class="pagination mb-0 justify-content-md-end">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button @click="changePage(currentPage - 1)" class="page-link">Previous</button>
              </li>
              <li v-for="pageNum in displayedPages" :key="pageNum" class="page-item"
                :class="{ active: currentPage === pageNum }">
                <button @click="changePage(pageNum)" class="page-link">{{ pageNum }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button @click="changePage(currentPage + 1)" class="page-link">Next</button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="alert alert-danger mt-4">
      <i class="bi bi-exclamation-circle me-2"></i>
      {{ error }}
      <button @click="fetchCustomers" class="btn btn-sm btn-outline-danger ms-2">
        Retry
      </button>
    </div>

    <!-- Customer Details Modal -->
    <div class="modal fade" id="customerModal" tabindex="-1" ref="customerModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedCustomer">
          <div class="modal-header">
            <h5 class="modal-title">Customer Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"
              aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="card">
              <div class="card-header p-4">
                <div class="d-flex align-items-center">
                  <div class="avatar-lg bg-success text-white me-4">
                    <i class="bi bi-person-fill"></i>
                  </div>
                  <div>
                    <h4 class="mb-1">{{ selectedCustomer.full_name }}</h4>
                    <p class="mb-0 text-muted">
                      Customer
                      <span :class="[
                        'badge ms-2',
                        selectedCustomer.is_active ? 'bg-success' : 'bg-danger',
                      ]">
                        {{ selectedCustomer.is_active ? 'Active' : 'Blocked' }}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
              <div class="card-body p-4">
                <div class="row g-4">
                  <!-- Personal Information -->
                  <div class="col-12">
                    <h5 class="border-bottom pb-2">Personal Information</h5>
                    <div class="row g-3 mt-2">
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Email</div>
                        <div>{{ selectedCustomer.email }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Phone</div>
                        <div>+91 {{ selectedCustomer.phone }}</div>
                      </div>
                      <div class="col-12">
                        <div class="fw-medium mb-1">Address</div>
                        <div>{{ selectedCustomer.address }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">PIN Code</div>
                        <div>{{ selectedCustomer.pin_code }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- Account Information -->
                  <div class="col-12">
                    <h5 class="border-bottom pb-2">Account Information</h5>
                    <div class="row g-3 mt-2">
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Username</div>
                        <div>{{ selectedCustomer.username }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Account Status</div>
                        <div>
                          <span :class="[
                            'badge',
                            selectedCustomer.is_active ? 'bg-success' : 'bg-danger',
                          ]">
                            {{ selectedCustomer.is_active ? 'Active' : 'Blocked' }}
                          </span>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Account Created</div>
                        <div>{{ formatDate(selectedCustomer.created_at, true) }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Last Login</div>
                        <div>{{ selectedCustomer.last_login ?
                          formatDate(selectedCustomer.last_login, true) : 'Never' }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- Service Request Stats -->
                  <div v-if="customerStats.total_requests !== undefined" class="col-12">
                    <h5 class="border-bottom pb-2">Service Request Statistics</h5>
                    <div class="row g-3 mt-2">
                      <div class="col-md-3">
                        <div class="border rounded p-3 text-center h-100">
                          <div class="text-muted small mb-1">Total Requests</div>
                          <div class="h5 mb-0">{{ customerStats.total_requests }}</div>
                        </div>
                      </div>
                      <div class="col-md-3">
                        <div class="border rounded p-3 text-center h-100">
                          <div class="text-muted small mb-1">Pending</div>
                          <div class="h5 mb-0">{{ customerStats.pending_requests || 0 }}</div>
                        </div>
                      </div>
                      <div class="col-md-3">
                        <div class="border rounded p-3 text-center h-100">
                          <div class="text-muted small mb-1">Active</div>
                          <div class="h5 mb-0">{{ customerStats.active_requests || 0 }}</div>
                        </div>
                      </div>
                      <div class="col-md-3">
                        <div class="border rounded p-3 text-center h-100">
                          <div class="text-muted small mb-1">Completed</div>
                          <div class="h5 mb-0">{{ customerStats.completed_requests || 0 }}</div>
                        </div>
                      </div>
                    </div>
                    <div class="text-center mt-3">
                      <button class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-list-check me-1"></i>
                        View Customer Requests
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button v-if="selectedCustomer.is_active" type="button" class="btn btn-danger"
              @click="showBlockModal(selectedCustomer)" :disabled="isActionLoading">
              <i class="bi bi-slash-circle me-1"></i>
              Block Customer
            </button>
            <button v-else type="button" class="btn btn-success"
              @click="unblockCustomer(selectedCustomer)" :disabled="isActionLoading">
              <i class="bi bi-check-circle me-1"></i>
              Unblock Customer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Block Customer Modal -->
    <div class="modal fade" id="blockModal" tabindex="-1" ref="blockModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">
              <i class="bi bi-slash-circle me-2"></i>
              Block Customer
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"
              aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to block <strong>{{ selectedCustomer?.full_name }}</strong>?
            </p>
            <p class="text-muted">This will prevent them from creating new service requests.</p>
            <div class="mb-3">
              <label for="blockReason" class="form-label">Reason for blocking</label>
              <textarea class="form-control" id="blockReason" rows="3" v-model="blockReason"
                placeholder="Please provide a reason..."
                :class="{ 'is-invalid': blockReasonError }"></textarea>
              <div class="invalid-feedback">{{ blockReasonError }}</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="blockCustomer"
              :disabled="isActionLoading">
              <span v-if="isActionLoading" class="spinner-border spinner-border-sm me-2"></span>
              Block Customer
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import * as bootstrap from 'bootstrap';
import moment from 'moment';
import { useRoute, useRouter } from 'vue-router';
import { useLoading } from '@/composables/useLoading';

export default {
  name: 'AdminCustomers',
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    const { isLoading, showLoading, hideLoading, withLoading } = useLoading();

    // Modal refs
    const customerModal = ref(null);
    const blockModal = ref(null);
    let bsCustomerModal = null;
    let bsBlockModal = null;

    // State
    const customers = computed(() => store.getters['customers/allCustomers'] || []);
    const selectedCustomer = ref(null);
    const customerStats = ref({});
    const error = ref(null);
    const isActionLoading = ref(false);
    const blockReason = ref('');
    const blockReasonError = ref('');
    const searchTimeout = ref(null);
    const filterTimeout = ref(null);
    const showBlocked = ref(false);

    // Pagination
    const currentPage = ref(1);
    const perPage = ref(10);
    const totalCustomers = computed(() => store.getters['customers/pagination']?.total || 0);
    const totalPages = computed(() => store.getters['customers/pagination']?.pages || 1);

    // Filters
    const filters = ref({
      pinCode: '',
      dateRange: '',
      search: '',
    });

    // Computed
    const blockedCount = computed(() => {
      return customers.value.filter(c => !c.is_active).length;
    });

    const displayedPages = computed(() => {
      const pages = [];
      const maxVisiblePages = 5;
      let startPage = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2));
      let endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1);

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      return pages;
    });

    const fetchCustomers = async () => {
      return withLoading(async () => {
        try {
          error.value = null;

          // Prepare date range params if needed
          let dateParams = {};
          if (filters.value.dateRange) {
            const now = moment();
            let startDate;

            switch (filters.value.dateRange) {
              case 'today':
                startDate = now.startOf('day');
                break;
              case 'week':
                startDate = now.startOf('week');
                break;
              case 'month':
                startDate = now.startOf('month');
                break;
              case 'year':
                startDate = now.startOf('year');
                break;
            }

            if (startDate) {
              dateParams = {
                start_date: startDate.format('YYYY-MM-DD'),
                end_date: now.format('YYYY-MM-DD')
              };
            }
          }

          await store.dispatch('customers/fetchCustomers', {
            page: currentPage.value,
            perPage: perPage.value,
            active: showBlocked.value ? false : true,
            pinCode: filters.value.pinCode || undefined,
            search: filters.value.search || undefined,
            ...dateParams
          });
        } catch (err) {
          error.value = err.message || 'Failed to load customers';
          console.error(err);
        }
      }, 'Loading customers...');
    };

    // Watch for query params
    watch(() => route.query, (newQuery) => {
      if (newQuery.status === 'blocked') {
        showBlocked.value = true;
      }

      fetchCustomers();
    }, { immediate: true });

    // Watch for status filter
    watch(() => showBlocked.value, (newValue) => {
      currentPage.value = 1;
      fetchCustomers();

      // Update URL without reloading
      const query = newValue ? { status: 'blocked' } : {};
      router.replace({ query });
    });

    // Methods


    const formatDate = (dateString, includeTime = false) => {
      if (!dateString) return 'N/A';
      return includeTime
        ? moment(dateString).format('MMM D, YYYY h:mm A')
        : moment(dateString).format('MMM D, YYYY');
    };

    const viewCustomer = async (customer) => {
      try {
        showLoading('Loading customer details...');
        // Get detailed information about the customer
        const response = await store.dispatch('customers/fetchCustomerById', customer.customer_id);
        selectedCustomer.value = response.data;

        // Get customer statistics (service requests, etc.)
        try {
          const statsResponse = await store.dispatch('stats/fetchDetailedStats', {
            type: 'customer_stats',
            customerId: customer.customer_id
          });
          customerStats.value = statsResponse.data || {};
        } catch (statsErr) {
          console.error('Error fetching customer stats:', statsErr);
          customerStats.value = {};
        }

        bsCustomerModal.show();
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: 'Failed to load customer details'
        });
        console.error(err);
      } finally {
        hideLoading();
      }
    };

    const showBlockModal = (customer) => {
      selectedCustomer.value = customer;
      blockReason.value = '';
      blockReasonError.value = '';

      // Close details modal if open
      if (bsCustomerModal && bsCustomerModal._isShown) {
        bsCustomerModal.hide();
      }

      bsBlockModal.show();
    };

    const blockCustomer = async () => {
      if (isActionLoading.value) return;

      // Validate reason
      if (!blockReason.value.trim()) {
        blockReasonError.value = 'Please provide a reason for blocking';
        return;
      }

      try {
        isActionLoading.value = true;
        await store.dispatch('customers/blockCustomer', {
          id: selectedCustomer.value.customer_id,
          reason: blockReason.value
        });

        window.showToast({
          type: 'success',
          title: 'Success',
          message: `${selectedCustomer.value.full_name} has been blocked`
        });

        // Refresh data
        await fetchCustomers();

        // Close modal
        bsBlockModal.hide();
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: err.response?.data?.message || 'Failed to block customer'
        });
      } finally {
        isActionLoading.value = false;
      }
    };

    const unblockCustomer = async (customer) => {
      if (isActionLoading.value) return;

      try {
        isActionLoading.value = true;
        await store.dispatch('customers/unblockCustomer', customer.customer_id);

        window.showToast({
          type: 'success',
          title: 'Success',
          message: `${customer.full_name} has been unblocked`
        });

        // Refresh data
        await fetchCustomers();

        // Close modal if open
        if (bsCustomerModal && bsCustomerModal._isShown) {
          bsCustomerModal.hide();
        }
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: err.response?.data?.message || 'Failed to unblock customer'
        });
      } finally {
        isActionLoading.value = false;
      }
    };

    const changePage = (page) => {
      if (page < 1 || page > totalPages.value) return;
      currentPage.value = page;
      fetchCustomers();
    };

    const debouncedSearch = () => {
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value);
      }

      searchTimeout.value = setTimeout(() => {
        currentPage.value = 1;
        fetchCustomers();
      }, 500);
    };

    const debouncedFilter = () => {
      if (filterTimeout.value) {
        clearTimeout(filterTimeout.value);
      }

      filterTimeout.value = setTimeout(() => {
        currentPage.value = 1;
        fetchCustomers();
      }, 500);
    };

    const clearSearch = () => {
      filters.value.search = '';
      currentPage.value = 1;
      fetchCustomers();
    };

    const onFiltersChange = () => {
      currentPage.value = 1;
      fetchCustomers();
    };

    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      if (customerModal.value) {
        bsCustomerModal = new bootstrap.Modal(customerModal.value);
      }

      if (blockModal.value) {
        bsBlockModal = new bootstrap.Modal(blockModal.value);
      }

      // Fetch initial data
      await fetchCustomers();
    });

    return {
      customers,
      filters,
      selectedCustomer,
      customerStats,
      isLoading,
      isActionLoading,
      error,
      blockReason,
      blockReasonError,
      currentPage,
      totalPages,
      totalCustomers,
      displayedPages,
      blockedCount,
      showBlocked,
      customerModal,
      blockModal,
      fetchCustomers,
      formatDate,
      viewCustomer,
      showBlockModal,
      blockCustomer,
      unblockCustomer,
      changePage,
      debouncedSearch,
      debouncedFilter,
      clearSearch,
      onFiltersChange
    };
  }
};
</script>

<style scoped>
.avatar {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.avatar-lg {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.75rem;
}

.btn-group .btn {
  padding: 0.25rem 0.5rem;
}
</style>
