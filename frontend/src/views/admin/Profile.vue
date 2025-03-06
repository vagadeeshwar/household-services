<template>
  <div class="container py-5">
    <div class="row justify-content-center g-4">
      <!-- Admin Profile Information -->
      <div class="col-lg-8">
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-primary text-white p-4">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-white text-primary p-3">
                <i class="bi bi-person-circle fs-2"></i>
              </div>
              <div class="ms-3">
                <h4 class="mb-1">{{ user?.full_name }}</h4>
                <p class="mb-0 opacity-75">Administrator</p>
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
                    <label class="form-label text-muted">Username</label>
                    <p class="fw-medium">{{ user?.username }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Email</label>
                    <p class="fw-medium">{{ user?.email }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Full Name</label>
                    <p class="fw-medium">{{ user?.full_name }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Phone</label>
                    <p class="fw-medium">+91 {{ user?.phone }}</p>
                  </div>
                  <div class="col-12">
                    <label class="form-label text-muted">Address</label>
                    <p class="fw-medium">{{ user?.address }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">PIN Code</label>
                    <p class="fw-medium">{{ user?.pin_code }}</p>
                  </div>
                </div>
              </div>
              <!-- Account Information -->
              <div class="col-12">
                <h5 class="border-bottom pb-2">Account Information</h5>
                <div class="row g-3 mt-2">
                  <div class="col-md-6">
                    <label class="form-label text-muted">Account Status</label>
                    <p>
                      <span class="badge bg-success">Active</span>
                    </p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Last Login</label>
                    <p class="fw-medium">{{ formatDate(user?.last_login) }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Account Created</label>
                    <p class="fw-medium">{{ formatDate(user?.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Logs Section -->
      <div class="col-lg-8">
        <div class="card shadow-sm">
          <div class="card-header bg-white">
            <div class="d-flex flex-column">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Your Recent Activity</h5>
                <button class="btn btn-sm btn-outline-primary" @click="fetchActivityLogs">
                  <i class="bi bi-arrow-clockwise"></i>
                </button>
              </div>
              <div class="d-flex gap-2 mt-3">
                <!-- Action Filter -->
                <div class="flex-grow-1">
                  <label class="form-label text-muted small mb-1">Filter by Action</label>
                  <select v-model="activityFilters.action" class="form-select form-select-sm"
                    @change="fetchActivityLogs">
                    <option v-for="action in actionTypes" :key="action.value" :value="action.value">
                      {{ action.label }}
                    </option>
                  </select>
                </div>
                <!-- Date Range Filter -->
                <div class="flex-grow-1">
                  <label class="form-label text-muted small mb-1">Start Date</label>
                  <input type="date" class="form-control form-control-sm"
                    v-model="activityFilters.startDate" @change="fetchActivityLogs">
                </div>
                <div class="flex-grow-1">
                  <label class="form-label text-muted small mb-1">End Date</label>
                  <input type="date" class="form-control form-control-sm"
                    v-model="activityFilters.endDate" @change="fetchActivityLogs">
                </div>
                <div class="align-self-end">
                  <button class="btn btn-sm btn-outline-secondary" @click="clearFilters">
                    <i class="bi bi-x-circle me-1"></i>Clear
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="isLoadingActivity" class="card-body text-center p-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading activity logs...</p>
          </div>
          <div v-else-if="activityLogs.length === 0" class="card-body text-center p-5">
            <i class="bi bi-journal-text fs-2 text-muted mb-2"></i>
            <p class="text-muted">No activity logs found</p>
          </div>
          <ul v-else class="list-group list-group-flush">
            <li v-for="log in activityLogs" :key="log.id" class="list-group-item">
              <div class="d-flex">
                <div class="activity-icon me-3">
                  <i :class="['bi', getActivityIcon(log.action)]"></i>
                </div>
                <div class="flex-grow-1">
                  <p class="mb-1">{{ log.description }}</p>
                  <small class="text-muted">{{ formatActivityDate(log.created_at) }}</small>
                </div>
                <span :class="['badge align-self-start', getActivityBadgeClass(log.action)]">
                  {{ formatActionType(log.action) }}
                </span>
              </div>
            </li>
          </ul>

          <!-- Pagination -->
          <div class="card-footer bg-white py-3">
            <div class="row align-items-center">
              <div class="col-md-6 text-muted">
                Showing {{ activityLogs.length }} of {{ activityPagination.total || 0 }} logs
              </div>
              <div class="col-md-6">
                <ul class="pagination pagination-sm mb-0 justify-content-md-end">
                  <li class="page-item" :class="{ disabled: activityFilters.page === 1 }">
                    <button @click="changePage(activityFilters.page - 1)"
                      class="page-link">Previous</button>
                  </li>
                  <li v-for="pageNum in displayedPages" :key="pageNum" class="page-item"
                    :class="{ active: activityFilters.page === pageNum }">
                    <button @click="changePage(pageNum)" class="page-link">{{ pageNum }}</button>
                  </li>
                  <li class="page-item"
                    :class="{ disabled: activityFilters.page === activityPagination.pages }">
                    <button @click="changePage(activityFilters.page + 1)"
                      class="page-link">Next</button>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import moment from 'moment';

export default {
  name: 'AdminProfile',
  setup() {
    const store = useStore();
    const user = computed(() => store.getters['auth/currentUser']);

    // Activity logs
    const activityLogs = ref([]);
    const isLoadingActivity = ref(false);
    const activityPagination = ref({});
    const activityFilters = ref({
      action: "all",
      page: 1,
      perPage: 10,
      startDate: null,
      endDate: null
    });

    // Computed properties
    const displayedPages = computed(() => {
      const pages = [];
      const maxVisiblePages = 5;
      const totalPages = activityPagination.value?.pages || 1;

      let startPage = Math.max(1, activityFilters.value.page - Math.floor(maxVisiblePages / 2));
      let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      return pages;
    });

    // eslint-disable-next-line no-unused-vars
    let l = ["all", "customer_block", "customer_unblock", "professional_block", "document_update", "service_update", "professional_unblock", "professional_verify", "request_assign", "request_cancel", "request_complete", "request_create", "request_reviewed", "request_update", "review_dismiss", "review_remove", "review_report", "review_submit", "service_create", "service_delete", "service_restore", "service_update", "user_delete", "user_login", "password_change", "profile_update", "user_register"];

    // Action types for activity logs
    const actionTypes = [
      { value: "all", label: "All Actions" },
      { value: 'user_login', label: 'User Login' },
      { value: 'user_register', label: 'User Registration' },
      // { value: 'profile_update', label: 'Profile Update' },
      // { value: 'password_change', label: 'Password Change' },
      { value: 'professional_verify', label: 'Professional Verification' },
      { value: 'professional_block', label: 'Professional Block' },
      { value: 'professional_unblock', label: 'Professional Unblock' },
      { value: 'customer_block', label: 'Customer Block' },
      { value: 'customer_unblock', label: 'Customer Unblock' },
      { value: 'service_create', label: 'Service Create' },
      { value: 'service_update', label: 'Service Update' },
      { value: 'service_delete', label: 'Service Delete' },
      // { value: 'request_create', label: 'Request Create' },
      // { value: 'request_assign', label: 'Request Assignment' },
      // { value: 'request_complete', label: 'Request Completion' },
      // { value: 'review_submit', label: 'Review Submission' },
      // { value: 'review_report', label: 'Review Report' }
    ];

    // Methods
    const formatDate = (dateString) => {
      return dateString ? moment(dateString).format('MMM DD, YYYY hh:mm A') : 'N/A';
    };

    const formatActivityDate = (dateString) => {
      return dateString ? moment(dateString).fromNow() : 'N/A';
    };

    const formatActionType = (action) => {
      const found = actionTypes.find(a => a.value === action);
      return found ? found.label : action;
    };

    const getActivityIcon = (action) => {
      const iconMap = {
        'user_login': 'bi-box-arrow-in-right',
        'user_register': 'bi-person-plus',
        'profile_update': 'bi-pencil',
        'password_change': 'bi-key',
        'user_delete': 'bi-person-x',
        'professional_verify': 'bi-check-circle',
        'professional_block': 'bi-slash-circle',
        'professional_unblock': 'bi-check-circle',
        'document_update': 'bi-file-earmark-arrow-up',
        'service_update': 'bi-tools',
        'customer_block': 'bi-slash-circle',
        'customer_unblock': 'bi-check-circle',
        'service_create': 'bi-plus-circle',
        'service_delete': 'bi-trash',
        'service_restore': 'bi-arrow-counterclockwise',
        'request_create': 'bi-clipboard-plus',
        'request_assign': 'bi-person-check',
        'request_update': 'bi-pencil',
        'request_complete': 'bi-check2-all',
        'request_reviewed': 'bi-star',
        'request_cancel': 'bi-x-circle',
        'review_submit': 'bi-star',
        'review_report': 'bi-flag',
        'review_dismiss': 'bi-shield-check',
        'review_remove': 'bi-trash'
      };

      return iconMap[action] || 'bi-activity';
    };

    const getActivityBadgeClass = (action) => {
      const actionTypeMap = {
        user_login: 'bg-info',
        user_register: 'bg-success',
        profile_update: 'bg-primary',
        password_change: 'bg-secondary',
        user_delete: 'bg-danger',
        professional_verify: 'bg-success',
        professional_block: 'bg-danger',
        professional_unblock: 'bg-success',
        document_update: 'bg-info',
        service_update: 'bg-primary',
        customer_block: 'bg-danger',
        customer_unblock: 'bg-success',
        service_create: 'bg-success',
        service_delete: 'bg-danger',
        service_restore: 'bg-success',
        request_create: 'bg-success',
        request_assign: 'bg-primary',
        request_update: 'bg-info',
        request_complete: 'bg-success',
        request_reviewed: 'bg-info',
        request_cancel: 'bg-danger',
        review_submit: 'bg-success',
        review_report: 'bg-danger',
        review_dismiss: 'bg-primary',
        review_remove: 'bg-danger'
      };

      return actionTypeMap[action] || 'bg-secondary';
    };

    const fetchActivityLogs = async () => {
      isLoadingActivity.value = true;
      try {
        const response = await store.dispatch('stats/fetchActivityLogs', {
          action: activityFilters.value.action,
          page: activityFilters.value.page,
          perPage: activityFilters.value.perPage,
          startDate: activityFilters.value.startDate ? new Date(activityFilters.value.startDate).toISOString() : null,
          endDate: activityFilters.value.endDate ? new Date(activityFilters.value.endDate + 'T23:59:59').toISOString() : null
        });

        activityLogs.value = response.data || [];
        activityPagination.value = response.pagination || {};
      } catch (err) {
        console.error('Error fetching activity logs:', err);
      } finally {
        isLoadingActivity.value = false;
      }
    };

    const clearFilters = () => {
      activityFilters.value.action = 'all';
      activityFilters.value.startDate = null;
      activityFilters.value.endDate = null;
      activityFilters.value.page = 1;
      fetchActivityLogs();
    };

    const changePage = (page) => {
      if (page < 1 || page > activityPagination.value.pages) return;
      activityFilters.value.page = page;
      fetchActivityLogs();
    };

    // Watch for filter changes to reset pagination
    watch(() => activityFilters.value.action, (newVal, oldVal) => {
      if (newVal !== oldVal) {
        activityFilters.value.page = 1;
        activityFilters.value.startDate = null;
        activityFilters.value.endDate = null;
        // No need to call fetchActivityLogs here as it's called by @change
      }
    });

    watch(() => activityFilters.value.startDate, (newVal, oldVal) => {
      if (newVal !== oldVal) {
        activityFilters.value.page = 1;
        // No need to call fetchActivityLogs here as it's called by @change
      }
    });

    watch(() => activityFilters.value.endDate, (newVal, oldVal) => {
      if (newVal !== oldVal) {
        activityFilters.value.page = 1;
        // No need to call fetchActivityLogs here as it's called by @change
      }
    });

    // Lifecycle hooks
    onMounted(() => {
      // Fetch activity logs
      fetchActivityLogs();
    });

    return {
      user,
      formatDate,
      formatActivityDate,
      formatActionType,
      getActivityIcon,
      getActivityBadgeClass,
      activityLogs,
      activityFilters,
      activityPagination,
      isLoadingActivity,
      actionTypes,
      displayedPages,
      fetchActivityLogs,
      changePage,
      clearFilters
    };
  }
};
</script>

<style scoped>
.activity-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #f8f9fa;
}

.activity-icon i {
  font-size: 1.1rem;
  color: #6c757d;
}

.card {
  border: none;
}

.card-header {
  border-top-left-radius: 0.5rem !important;
  border-top-right-radius: 0.5rem !important;
}

.badge {
  font-weight: 500;
}
</style>
