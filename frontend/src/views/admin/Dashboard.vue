<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">Admin Dashboard</h1>
      <div class="btn-group">
        <button class="btn btn-outline-primary" @click="refreshDashboard">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
      </div>
    </div>

    <!-- Loading Indicator -->
    <Loading :show="isLoading" message="Loading dashboard data..." :overlay="true" />

    <!-- Dashboard Cards -->
    <div v-if="!isLoading && dashboardStats" class="row g-4">
      <!-- Service Professionals Stats -->
      <div class="col-md-6 col-lg-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                <i class="bi bi-person-badge fs-3 text-primary"></i>
              </div>
              <h5 class="card-title mb-0">Service Professionals</h5>
            </div>
            <div class="row g-3">
              <div class="col-6">
                <div class="border rounded p-3 h-100">
                  <div class="text-muted small mb-1">Total</div>
                  <div class="h4 mb-0">{{ dashboardStats.total_professionals || 0 }}</div>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded p-3 h-100">
                  <div class="text-muted small mb-1">Verified</div>
                  <div class="h4 mb-0">{{ dashboardStats.verified_professionals || 0 }}</div>
                </div>
              </div>
              <div class="col-12">
                <div class="border rounded p-3 bg-warning bg-opacity-10">
                  <div class="d-flex justify-content-between">
                    <div class="text-muted small mb-1">Pending Verification</div>
                    <span class="badge bg-warning">{{ dashboardStats.pending_verifications || 0
                    }}</span>
                  </div>
                  <router-link v-if="dashboardStats.pending_verifications > 0"
                    to="/admin/professionals?status=pending" class="btn btn-sm btn-warning mt-2">
                    Review Now
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Customers Stats -->
      <div class="col-md-6 col-lg-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                <i class="bi bi-people fs-3 text-success"></i>
              </div>
              <h5 class="card-title mb-0">Customers</h5>
            </div>
            <div class="row g-3">
              <div class="col-6">
                <div class="border rounded p-3 h-100">
                  <div class="text-muted small mb-1">Total</div>
                  <div class="h4 mb-0">{{ dashboardStats.total_customers || 0 }}</div>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded p-3 h-100">
                  <div class="text-muted small mb-1">Active</div>
                  <div class="h4 mb-0">{{ dashboardStats.active_customers || 0 }}</div>
                </div>
              </div>
              <div class="col-12">
                <div class="border rounded p-3">
                  <div class="text-muted small mb-1">Inactive</div>
                  <div class="h4 mb-0">{{ calculateInactiveCustomers }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Service Requests Stats -->
      <div class="col-md-6 col-lg-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-info bg-opacity-10 p-3 me-3">
                <i class="bi bi-list-check fs-3 text-info"></i>
              </div>
              <h5 class="card-title mb-0">Service Requests</h5>
            </div>
            <div class="row g-3">
              <div class="col-12">
                <div class="border rounded p-3">
                  <div class="text-muted small mb-1">Total</div>
                  <div class="h4 mb-0">{{ dashboardStats.service_requests?.total || 0 }}</div>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded p-3 h-100 bg-warning bg-opacity-10">
                  <div class="text-muted small mb-1">Pending</div>
                  <div class="h4 mb-0">{{ dashboardStats.service_requests?.pending || 0 }}</div>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded p-3 h-100 bg-success bg-opacity-10">
                  <div class="text-muted small mb-1">Completed</div>
                  <div class="h4 mb-0">{{ dashboardStats.service_requests?.completed || 0 }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Issues Requiring Attention -->
      <div class="col-md-6 col-lg-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-danger bg-opacity-10 p-3 me-3">
                <i class="bi bi-exclamation-triangle fs-3 text-danger"></i>
              </div>
              <h5 class="card-title mb-0">Issues Requiring Attention</h5>
            </div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between align-items-center">
                <span>
                  <i class="bi bi-flag-fill text-danger me-2"></i>
                  Reported Reviews
                </span>
                <span class="badge bg-danger">{{ dashboardStats.reported_reviews || 0 }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                <span>
                  <i class="bi bi-person-x-fill text-warning me-2"></i>
                  Pending Verifications
                </span>
                <span class="badge bg-warning">{{ dashboardStats.pending_verifications || 0
                }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="col-md-6 col-lg-8">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">Recent Activity</h5>
            <router-link to="/admin/reports" class="btn btn-sm btn-outline-primary">
              View All
            </router-link>
          </div>
          <div class="card-body p-0">
            <div v-if="isLoadingActivity" class="d-flex justify-content-center p-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="activityLogs.length === 0" class="text-center p-4 text-muted">
              <i class="bi bi-info-circle fs-3 mb-2"></i>
              <p>No recent activity found</p>
            </div>
            <ul v-else class="list-group list-group-flush">
              <li v-for="log in activityLogs" :key="log.id" class="list-group-item">
                <div class="d-flex">
                  <div class="activity-icon me-3">
                    <i :class="['bi', getActivityIcon(log.action)]"></i>
                  </div>
                  <div>
                    <p class="mb-1">{{ log.description }}</p>
                    <small class="text-muted">{{ formatDate(log.created_at) }}</small>
                  </div>
                </div>
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
      <button @click="refreshDashboard" class="btn btn-sm btn-outline-danger ms-2">
        Retry
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import moment from 'moment';
import { useLoading } from '@/composables/useLoading';

export default {
  name: 'AdminDashboard',
  setup() {
    const store = useStore();
    // eslint-disable-next-line no-unused-vars
    const { isLoading, showLoading, hideLoading, withLoading } = useLoading();

    const dashboardStats = ref(null);
    const activityLogs = ref([]);
    const error = ref(null);
    const isLoadingActivity = ref(false);

    // Computed properties
    const calculateInactiveCustomers = computed(() => {
      if (!dashboardStats.value) return 0;
      return (dashboardStats.value.total_customers || 0) - (dashboardStats.value.active_customers || 0);
    });

    // Methods
    const fetchDashboardStats = async () => {
      return withLoading(async () => {
        try {
          error.value = null;
          const response = await store.dispatch('stats/fetchDashboardStats');
          dashboardStats.value = response.data;
        } catch (err) {
          error.value = err.message || 'Failed to load dashboard statistics';
          console.error(err);
        }
      }, 'Loading dashboard data...');
    };

    const fetchActivityLogs = async () => {
      isLoadingActivity.value = true;
      try {
        const response = await store.dispatch('stats/fetchDetailedStats', {
          type: 'pending_verifications',
          page: 1,
          perPage: 5
        });
        activityLogs.value = response.data;
      } catch (err) {
        console.error('Failed to load activity logs:', err);
      } finally {
        isLoadingActivity.value = false;
      }
    };

    const refreshDashboard = async () => {
      await fetchDashboardStats();
      await fetchActivityLogs();
    };

    const formatDate = (dateString) => {
      return moment(dateString).fromNow();
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

    // Lifecycle hooks
    onMounted(async () => {
      await refreshDashboard();
    });

    return {
      dashboardStats,
      activityLogs,
      isLoading,
      isLoadingActivity,
      error,
      calculateInactiveCustomers,
      refreshDashboard,
      formatDate,
      getActivityIcon
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
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>
