<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">Admin Dashboard</h1>
        <p class="text-muted">Overview of platform metrics and activity</p>
      </div>
      <div class="col-auto">
        <div class="btn-group">
          <button class="btn btn-outline-primary" @click="refreshDashboard">
            <i class="bi bi-arrow-clockwise me-1"></i> Refresh
          </button>
          <button class="btn btn-outline-secondary" @click="openExportModal">
            <i class="bi bi-file-earmark-arrow-down me-1"></i> Export Report
          </button>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading dashboard...</span>
      </div>
      <p class="mt-3 text-muted">Loading dashboard data...</p>
    </div>

    <template v-else>
      <!-- Stats Cards -->
      <div class="row g-3 mb-4">
        <!-- Total Services -->
        <div class="col-xl-3 col-md-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="text-muted mb-1">Total Services</h6>
                  <h3 class="display-6 fw-bold mb-0">{{ stats.servicesCount || 0 }}</h3>
                </div>
                <div class="icon-rounded bg-primary-subtle text-primary">
                  <i class="bi bi-tools"></i>
                </div>
              </div>
              <div class="mt-3 d-flex justify-content-between">
                <span class="badge bg-success">{{ stats.activeServicesCount || 0 }} Active</span>
                <router-link to="/admin/services" class="small text-decoration-none"
                  >View All</router-link
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Total Professionals -->
        <div class="col-xl-3 col-md-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="text-muted mb-1">Professionals</h6>
                  <h3 class="display-6 fw-bold mb-0">{{ stats.professionalsCount || 0 }}</h3>
                </div>
                <div class="icon-rounded bg-info-subtle text-info">
                  <i class="bi bi-person-badge"></i>
                </div>
              </div>
              <div class="mt-3 d-flex justify-content-between">
                <div>
                  <span class="badge bg-warning me-1"
                    >{{ stats.pendingVerificationsCount || 0 }} Pending</span
                  >
                  <span class="badge bg-success"
                    >{{ stats.verifiedProfessionalsCount || 0 }} Verified</span
                  >
                </div>
                <router-link to="/admin/professionals" class="small text-decoration-none"
                  >View All</router-link
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Total Customers -->
        <div class="col-xl-3 col-md-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="text-muted mb-1">Customers</h6>
                  <h3 class="display-6 fw-bold mb-0">{{ stats.customersCount || 0 }}</h3>
                </div>
                <div class="icon-rounded bg-success-subtle text-success">
                  <i class="bi bi-people"></i>
                </div>
              </div>
              <div class="mt-3 d-flex justify-content-between">
                <span class="badge bg-primary">{{ stats.activeCustomersCount || 0 }} Active</span>
                <router-link to="/admin/customers" class="small text-decoration-none"
                  >View All</router-link
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Service Requests -->
        <div class="col-xl-3 col-md-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="text-muted mb-1">Service Requests</h6>
                  <h3 class="display-6 fw-bold mb-0">{{ stats.requestsCount || 0 }}</h3>
                </div>
                <div class="icon-rounded bg-warning-subtle text-warning">
                  <i class="bi bi-clipboard-check"></i>
                </div>
              </div>
              <div class="mt-3 d-flex justify-content-between">
                <div>
                  <span class="badge bg-info me-1"
                    >{{ stats.pendingRequestsCount || 0 }} Pending</span
                  >
                  <span class="badge bg-primary me-1"
                    >{{ stats.activeRequestsCount || 0 }} Active</span
                  >
                  <span class="badge bg-success"
                    >{{ stats.completedRequestsCount || 0 }} Completed</span
                  >
                </div>
                <router-link to="/admin/requests" class="small text-decoration-none"
                  >View All</router-link
                >
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Visualizations and Tables Row -->
      <div class="row g-4 mb-4">
        <!-- Service Request Trends -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white py-3">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Service Request Trends</h5>
                <div class="btn-group btn-group-sm">
                  <button
                    class="btn btn-outline-secondary"
                    @click="setChartPeriod('weekly')"
                    :class="{ active: chartPeriod === 'weekly' }"
                  >
                    Weekly
                  </button>
                  <button
                    class="btn btn-outline-secondary"
                    @click="setChartPeriod('monthly')"
                    :class="{ active: chartPeriod === 'monthly' }"
                  >
                    Monthly
                  </button>
                </div>
              </div>
            </div>
            <div class="card-body">
              <div class="chart-container" style="position: relative; height: 300px">
                <!-- Chart would go here - mockup chart display -->
                <div
                  v-if="isLoadingChart"
                  class="d-flex justify-content-center align-items-center h-100"
                >
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading chart...</span>
                  </div>
                </div>
                <div v-else-if="chartData.length > 0" class="h-100">
                  <div class="chart-mockup">
                    <div
                      class="chart-bar"
                      v-for="(value, index) in chartData"
                      :key="index"
                      :style="{ height: getBarHeight(value) + '%' }"
                    ></div>
                  </div>
                  <div class="d-flex justify-content-between mt-2">
                    <div
                      v-for="(label, index) in displayedLabels"
                      :key="index"
                      class="text-muted small text-center"
                      :style="{ width: 100 / displayedLabels.length + '%' }"
                    >
                      {{ label }}
                    </div>
                  </div>
                </div>
                <div v-else class="h-100 d-flex justify-content-center align-items-center">
                  <div class="text-center text-muted">
                    <i class="bi bi-bar-chart-line mb-3" style="font-size: 2rem"></i>
                    <p class="mb-0">No data available for this period</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pending Verifications -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white py-3">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Pending Verifications</h5>
                <span class="badge bg-warning">{{ pendingProfessionals.length }}</span>
              </div>
            </div>
            <div class="card-body p-0">
              <div v-if="isLoadingProfessionals" class="text-center py-4">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Loading professionals...</span>
                </div>
                <p class="mt-2 mb-0 text-muted">Loading pending verifications...</p>
              </div>
              <div v-else-if="pendingProfessionals.length === 0" class="p-4 text-center">
                <i class="bi bi-check-circle text-success mb-3" style="font-size: 2rem"></i>
                <p class="mb-0">No pending verifications</p>
              </div>
              <ul v-else class="list-group list-group-flush">
                <li
                  v-for="professional in pendingProfessionals.slice(0, 5)"
                  :key="professional.id"
                  class="list-group-item"
                >
                  <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                      <div class="avatar me-3 bg-light rounded-circle">
                        <i class="bi bi-person"></i>
                      </div>
                      <div>
                        <h6 class="mb-0">{{ professional.full_name }}</h6>
                        <div class="text-muted small">
                          {{ getServiceName(professional.service_type_id) }}
                        </div>
                      </div>
                    </div>
                    <button
                      class="btn btn-sm btn-outline-success"
                      @click="verifyProfessional(professional)"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>
                  </div>
                </li>
                <li v-if="pendingProfessionals.length > 5" class="list-group-item text-center">
                  <router-link
                    to="/admin/professionals?verified=false"
                    class="text-decoration-none"
                  >
                    View all {{ pendingProfessionals.length }} pending verifications
                  </router-link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity & Service Distribution -->
      <div class="row g-4">
        <!-- Recent Activity Logs -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white py-3">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Recent Activity</h5>
                <button class="btn btn-sm btn-outline-secondary" @click="fetchActivityLogs(true)">
                  <i class="bi bi-arrow-clockwise"></i>
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <div v-if="isLoadingActivity" class="text-center py-4">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Loading activity...</span>
                </div>
                <p class="mt-2 mb-0 text-muted">Loading recent activity...</p>
              </div>
              <div v-else-if="activityLogs.length === 0" class="p-4 text-center">
                <i class="bi bi-calendar-x text-muted mb-3" style="font-size: 2rem"></i>
                <p class="mb-0">No recent activity found</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Action</th>
                      <th>User</th>
                      <th>Description</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="log in activityLogs" :key="log.id">
                      <td>
                        <span class="badge" :class="getActionBadgeClass(log.action)">
                          <i class="bi me-1" :class="getActionIcon(log.action)"></i>
                          {{ formatActionType(log.action) }}
                        </span>
                      </td>
                      <td>{{ log.user_id || 'System' }}</td>
                      <td>{{ log.description }}</td>
                      <td>{{ formatRelativeTime(log.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="card-footer bg-white text-center">
              <button class="btn btn-sm btn-outline-primary" @click="loadMoreActivity">
                Load More Activity
              </button>
            </div>
          </div>
        </div>

        <!-- Top Services -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white py-3">
              <h5 class="mb-0">Top Services</h5>
            </div>
            <div class="card-body">
              <div v-if="isLoadingServices" class="text-center py-4">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Loading services...</span>
                </div>
                <p class="mt-2 mb-0 text-muted">Loading service distribution...</p>
              </div>
              <div v-else-if="servicesList.length === 0" class="text-center">
                <i class="bi bi-tools text-muted mb-3" style="font-size: 2rem"></i>
                <p class="mb-0">No services available</p>
              </div>
              <div v-else>
                <div
                  class="mb-3"
                  v-for="(service, index) in servicesList.slice(0, 5)"
                  :key="service.id"
                >
                  <div class="d-flex justify-content-between mb-1">
                    <span class="fw-medium">{{ service.name }}</span>
                    <span class="badge bg-primary">{{ service.requestCount || 0 }} requests</span>
                  </div>
                  <div class="progress" style="height: 10px">
                    <div
                      class="progress-bar"
                      :class="progressColors[index % progressColors.length]"
                      :style="{ width: getServicePercentage(service) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-footer bg-white text-center">
              <router-link to="/admin/services" class="btn btn-sm btn-outline-primary">
                Manage Services
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Export Report Modal -->
    <div
      class="modal fade"
      id="exportReportModal"
      tabindex="-1"
      aria-hidden="true"
      ref="exportModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-file-earmark-arrow-down me-2"></i>
              Generate Service Requests Report
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              :disabled="isExporting"
            ></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <i class="bi bi-info-circle-fill me-2"></i>
              Generate a CSV report of service requests. You can filter by professional and date
              range.
            </div>
            <div class="mb-3">
              <label for="reportProfessional" class="form-label">Professional</label>
              <select
                class="form-select"
                id="reportProfessional"
                v-model="exportOptions.professional_id"
              >
                <option value="">All Professionals</option>
                <option
                  v-for="professional in verifiedProfessionals"
                  :key="professional.professional_id"
                  :value="professional.professional_id"
                >
                  {{ professional.full_name }}
                </option>
              </select>
              <div class="form-text">
                Select a professional or leave empty to include all verified professionals.
              </div>
            </div>
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="startDate" class="form-label">Start Date</label>
                  <input
                    type="date"
                    class="form-control"
                    id="startDate"
                    v-model="exportOptions.start_date"
                  />
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="endDate" class="form-label">End Date</label>
                  <input
                    type="date"
                    class="form-control"
                    id="endDate"
                    v-model="exportOptions.end_date"
                  />
                </div>
              </div>
            </div>
            <!-- Export Status -->
            <div v-if="exportStatus" class="mt-4">
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h6 class="mb-0">Export Status</h6>
                  <span class="badge" :class="getExportStatusBadgeClass(exportStatus.state)">
                    {{ exportStatus.state }}
                  </span>
                </div>
                <div class="progress" style="height: 20px">
                  <div
                    class="progress-bar progress-bar-striped progress-bar-animated"
                    :class="{ 'bg-success': exportStatus.state === 'SUCCESS' }"
                    :style="{ width: getExportProgressPercentage() + '%' }"
                    role="progressbar"
                  >
                    {{ getExportProgressText() }}
                  </div>
                </div>
                <p class="mt-2 text-muted">{{ exportStatus.status || 'Preparing export...' }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
              :disabled="isExporting"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="generateReport"
              :disabled="isExporting || !isValidExportOptions"
            >
              <i
                class="bi"
                :class="isExporting ? 'bi-hourglass-split' : 'bi-file-earmark-arrow-down'"
              ></i>
              {{ isExporting ? 'Generating...' : 'Generate Report' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted, watch, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import * as bootstrap from 'bootstrap'
import { formatRelativeTime, formatDateTime } from '@/utils/date'
import { actionIcons, actionBadges } from '@/assets/actionTypes'
import { useLoading } from '@/composables/useLoading'

export default defineComponent({
  name: 'AdminDashboard',
  setup() {
    const store = useStore()
    const { isLoading, withLoading } = useLoading()

    // Dashboard state
    const stats = reactive({
      servicesCount: 0,
      activeServicesCount: 0,
      professionalsCount: 0,
      pendingVerificationsCount: 0,
      verifiedProfessionalsCount: 0,
      customersCount: 0,
      activeCustomersCount: 0,
      requestsCount: 0,
      pendingRequestsCount: 0,
      activeRequestsCount: 0,
      completedRequestsCount: 0,
    })

    // Component state
    const isLoadingChart = ref(false)
    const isLoadingProfessionals = ref(false)
    const isLoadingActivity = ref(false)
    const isLoadingServices = ref(false)
    const chartPeriod = ref('weekly')
    const servicesList = ref([])
    const pendingProfessionals = ref([])
    const activityLogs = ref([])
    const activityPage = ref(1)
    const hasMoreActivity = ref(true)

    // Export Modal
    const exportModal = ref(null)
    let bsExportModal = null
    const exportOptions = ref({
      professional_id: '',
      start_date: '',
      end_date: '',
    })
    const isExporting = ref(false)
    const exportStatus = ref(null)
    const exportTaskId = ref(null)
    let statusPollInterval = null
    const verifiedProfessionals = ref([])

    // Chart data - will be populated from API
    const chartData = ref([])
    const chartLabels = ref([])

    // Computed labels based on current period
    const displayedLabels = computed(() => chartLabels.value)

    // Colors for the progress bars
    const progressColors = ['bg-primary', 'bg-success', 'bg-info', 'bg-warning', 'bg-danger']

    // Export validation
    const isValidDateRange = computed(() => {
      if (!exportOptions.value.start_date || !exportOptions.value.end_date) {
        return true // Both dates are empty, which is allowed
      }
      const startDate = new Date(exportOptions.value.start_date)
      const endDate = new Date(exportOptions.value.end_date)
      return startDate <= endDate
    })

    const isValidExportOptions = computed(() => {
      return isValidDateRange.value
    })

    // Methods
    const refreshDashboard = async () => {
      await withLoading(fetchDashboardData(), 'Refreshing dashboard data...')
    }

    const fetchDashboardData = async () => {
      try {
        await Promise.all([
          fetchStats(),
          fetchServices(),
          fetchPendingProfessionals(),
          fetchActivityLogs(),
          fetchVerifiedProfessionals(),
        ])
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        window.showToast({
          type: 'danger',
          title: 'Error loading dashboard',
          message: 'Please try refreshing the page',
        })
      }
    }

    const fetchStats = async () => {
      try {
        // Fetch services stats
        const servicesResponse = await store.dispatch('services/fetchAllServices', {
          params: { per_page: 100 },
          forceRefresh: true,
        })
        servicesList.value = servicesResponse.data || []
        stats.servicesCount = servicesResponse.pagination?.total || servicesList.value.length
        stats.activeServicesCount = servicesList.value.filter((s) => s.is_active).length

        // Professionals stats
        const professionalsResponse = await store.dispatch('professionals/fetchProfessionals', {
          params: { per_page: 100 },
          forceRefresh: true,
        })
        const professionals = professionalsResponse.data || []
        stats.professionalsCount = professionalsResponse.pagination?.total || professionals.length
        stats.verifiedProfessionalsCount = professionals.filter((p) => p.is_verified).length
        stats.pendingVerificationsCount = professionals.filter((p) => !p.is_verified).length

        // Customers stats
        const customersResponse = await store.dispatch('customers/fetchCustomers', {
          params: { per_page: 100 },
          forceRefresh: true,
        })
        const customers = customersResponse.data || []
        stats.customersCount = customersResponse.pagination?.total || customers.length
        stats.activeCustomersCount = customers.filter((c) => c.is_active).length

        // Service requests stats - fetch from request service
        // Get customer requests summary stats
        const customerRequestsResponse = await store.dispatch('requests/fetchCustomerRequests', {
          params: { summary: true, per_page: 1 },
          forceRefresh: true,
        })

        if (customerRequestsResponse && customerRequestsResponse.data) {
          stats.requestsCount = customerRequestsResponse.data.total_requests || 0
          stats.completedRequestsCount = customerRequestsResponse.data.completed_requests || 0
          stats.activeRequestsCount = customerRequestsResponse.data.active_requests || 0
          stats.pendingRequestsCount =
            stats.requestsCount - (stats.completedRequestsCount + stats.activeRequestsCount)
        }
      } catch (error) {
        console.error('Error fetching stats:', error)
        throw error
      }
    }

    const fetchServices = async () => {
      try {
        isLoadingServices.value = true
        const response = await store.dispatch('services/fetchAllServices', {
          params: { per_page: 100 },
          forceRefresh: true,
        })
        servicesList.value = response.data || []

        // For each service, fetch request counts through the request API
        // We'll use Promise.all to fetch them in parallel
        const requests = servicesList.value.map(async (service) => {
          try {
            // Fetch requests associated with this service
            const requestsResponse = await store.dispatch('requests/fetchCustomerRequests', {
              params: {
                service_id: service.id,
                summary: true,
                per_page: 1,
              },
            })

            if (requestsResponse && requestsResponse.data) {
              service.requestCount = requestsResponse.data.total_requests || 0
            } else {
              service.requestCount = 0
            }
          } catch (err) {
            console.error(`Error fetching requests for service ${service.id}:`, err)
            service.requestCount = 0
          }
        })

        // Wait for all request counts to be fetched
        await Promise.all(requests)

        // Sort by request count (descending)
        servicesList.value.sort((a, b) => b.requestCount - a.requestCount)
      } catch (error) {
        console.error('Error fetching services:', error)
      } finally {
        isLoadingServices.value = false
      }
    }

    const fetchPendingProfessionals = async () => {
      try {
        isLoadingProfessionals.value = true
        const response = await store.dispatch('professionals/fetchProfessionals', {
          params: { verified: false, per_page: 10 },
          forceRefresh: true,
        })
        pendingProfessionals.value = response.data || []
      } catch (error) {
        console.error('Error fetching pending professionals:', error)
      } finally {
        isLoadingProfessionals.value = false
      }
    }

    const fetchVerifiedProfessionals = async () => {
      try {
        const response = await store.dispatch('professionals/fetchProfessionals', {
          params: { verified: true, per_page: 100 },
          forceRefresh: false,
        })
        verifiedProfessionals.value = response.data || []
      } catch (error) {
        console.error('Error fetching verified professionals:', error)
      }
    }

    const fetchActivityLogs = async (refresh = false) => {
      try {
        isLoadingActivity.value = true
        if (refresh) {
          activityPage.value = 1
          hasMoreActivity.value = true
        }

        const response = await store.dispatch('stats/fetchActivityLogs', {
          params: {
            page: activityPage.value,
            per_page: 10,
            action: 'all',
          },
          forceRefresh: refresh,
        })

        const logs = response.data || []

        if (refresh) {
          activityLogs.value = logs
        } else {
          activityLogs.value = [...activityLogs.value, ...logs]
        }

        // Check if there are more pages
        hasMoreActivity.value = response.pagination?.has_next || false
      } catch (error) {
        console.error('Error fetching activity logs:', error)
      } finally {
        isLoadingActivity.value = false
      }
    }

    const loadMoreActivity = () => {
      if (hasMoreActivity.value) {
        activityPage.value++
        fetchActivityLogs()
      }
    }

    const setChartPeriod = async (period) => {
      chartPeriod.value = period
      isLoadingChart.value = true

      try {
        // Fetch time-series data for service requests based on the selected period
        // Since we don't have a specific API endpoint for time-series data,
        // we'll aggregate the data from the available endpoints

        let params = {
          summary: true,
          per_page: 100,
        }

        // Add period-specific parameters
        if (period === 'weekly') {
          // Get data for the last 7 days
          const today = new Date()
          const lastWeek = new Date(today)
          lastWeek.setDate(today.getDate() - 7)

          params.start_date = lastWeek.toISOString().split('T')[0]
          params.end_date = today.toISOString().split('T')[0]

          // Prepare weekly labels
          const labels = []
          for (let i = 0; i < 7; i++) {
            const date = new Date(lastWeek)
            date.setDate(lastWeek.getDate() + i)
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }))
          }
          chartLabels.value = labels

          // Initialize empty data
          chartData.value = new Array(7).fill(0)

          // Fetch all service requests for the date range
          const response = await store.dispatch('requests/fetchCustomerRequests', { params })

          if (response && response.data) {
            // Process the requests and group by day
            response.data.forEach((request) => {
              const requestDate = new Date(request.date_of_request)
              const dayDiff = Math.floor((requestDate - lastWeek) / (24 * 60 * 60 * 1000))

              if (dayDiff >= 0 && dayDiff < 7) {
                chartData.value[dayDiff]++
              }
            })
          }
        } else {
          // Get data for the last 6 months
          const today = new Date()
          const lastSixMonths = new Date(today)
          lastSixMonths.setMonth(today.getMonth() - 6)

          params.start_date = lastSixMonths.toISOString().split('T')[0]
          params.end_date = today.toISOString().split('T')[0]

          // Prepare monthly labels
          const labels = []
          for (let i = 0; i <= 6; i++) {
            const date = new Date(lastSixMonths)
            date.setMonth(lastSixMonths.getMonth() + i)
            labels.push(date.toLocaleDateString('en-US', { month: 'short' }))
          }
          chartLabels.value = labels

          // Initialize empty data
          chartData.value = new Array(7).fill(0)

          // Fetch all service requests for the date range
          const response = await store.dispatch('requests/fetchCustomerRequests', { params })

          if (response && response.data) {
            // Process the requests and group by month
            response.data.forEach((request) => {
              const requestDate = new Date(request.date_of_request)
              const monthDiff =
                (requestDate.getFullYear() - lastSixMonths.getFullYear()) * 12 +
                requestDate.getMonth() -
                lastSixMonths.getMonth()

              if (monthDiff >= 0 && monthDiff < 7) {
                chartData.value[monthDiff]++
              }
            })
          }
        }
      } catch (error) {
        console.error(`Error fetching ${period} chart data:`, error)
        // Reset chart data on error
        chartData.value = []
        chartLabels.value = []
      } finally {
        isLoadingChart.value = false
      }
    }

    const verifyProfessional = async (professional) => {
      try {
        await store.dispatch('professionals/verifyProfessional', {
          id: professional.professional_id,
        })

        window.showToast({
          type: 'success',
          title: 'Professional Verified',
          message: `${professional.full_name} has been verified successfully`,
        })

        // Refresh the pending professionals list
        await fetchPendingProfessionals()

        // Update stats
        stats.pendingVerificationsCount--
        stats.verifiedProfessionalsCount++
      } catch (error) {
        console.error('Error verifying professional:', error)
        window.showToast({
          type: 'danger',
          title: 'Verification Failed',
          message: error.response?.data?.detail || 'Failed to verify professional',
        })
      }
    }

    const getServiceName = (serviceId) => {
      if (!serviceId || !servicesList.value || servicesList.value.length === 0) {
        return 'Unknown Service'
      }
      const service = servicesList.value.find((s) => s.id === serviceId)
      return service ? service.name : 'Unknown Service'
    }

    const getServicePercentage = (service) => {
      const max = Math.max(...servicesList.value.map((s) => s.requestCount || 0))
      if (max === 0) return 0
      return (service.requestCount / max) * 100
    }

    const formatActionType = (action) => {
      if (!action) return 'Unknown'
      // Convert snake_case to Title Case
      return action
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    }

    const getActionIcon = (action) => {
      return actionIcons[action] || 'bi-activity'
    }

    const getActionBadgeClass = (action) => {
      return actionBadges[action] || 'bg-secondary'
    }

    // Export functionality methods
    const openExportModal = () => {
      exportOptions.value = {
        professional_id: '',
        start_date: '',
        end_date: '',
      }
      exportStatus.value = null
      exportTaskId.value = null
      clearExportStatusInterval()
      bsExportModal.show()
    }

    const getExportStatusBadgeClass = (state) => {
      const statusClasses = {
        PENDING: 'bg-warning',
        STARTED: 'bg-info',
        PROGRESS: 'bg-primary',
        SUCCESS: 'bg-success',
        FAILURE: 'bg-danger',
      }
      return statusClasses[state] || 'bg-secondary'
    }

    const getExportProgressPercentage = () => {
      if (!exportStatus.value) return 0
      const stateProgress = {
        PENDING: 10,
        STARTED: 30,
        PROGRESS: 60,
        SUCCESS: 100,
        FAILURE: 100,
      }
      return stateProgress[exportStatus.value.state] || 0
    }

    const getExportProgressText = () => {
      if (!exportStatus.value) return ''
      const stateText = {
        PENDING: 'Pending...',
        STARTED: 'Started...',
        PROGRESS: 'In Progress...',
        SUCCESS: 'Complete!',
        FAILURE: 'Failed',
      }
      return stateText[exportStatus.value.state] || ''
    }

    const startExportStatusPolling = (taskId) => {
      clearExportStatusInterval()
      checkExportStatus(taskId)
      statusPollInterval = setInterval(() => {
        checkExportStatus(taskId)
      }, 2000)
    }

    const clearExportStatusInterval = () => {
      if (statusPollInterval) {
        clearInterval(statusPollInterval)
        statusPollInterval = null
      }
    }

    const checkExportStatus = async (taskId) => {
      try {
        const response = await store.dispatch('exports/checkExportStatus', { id: taskId })
        exportStatus.value = response.data

        if (['SUCCESS', 'FAILURE'].includes(response.data.state)) {
          clearExportStatusInterval()

          if (response.data.state === 'SUCCESS' && response.data.result?.filename) {
            await downloadExport(response.data.result.filename)

            window.showToast({
              type: 'success',
              title: 'Export Completed',
              message: `Successfully exported ${response.data.result.total_records} service requests`,
            })

            setTimeout(() => {
              bsExportModal.hide()
            }, 1500)
          } else if (response.data.state === 'FAILURE') {
            window.showToast({
              type: 'danger',
              title: 'Export Failed',
              message: response.data.error || 'Failed to generate the export',
            })
          }
        }
      } catch (error) {
        console.error('Error checking export status:', error)
        window.showToast({
          type: 'danger',
          title: 'Status Check Failed',
          message: 'Failed to check export status',
        })
        clearExportStatusInterval()
      }
    }

    const downloadExport = async (filename) => {
      try {
        await store.dispatch('exports/downloadReport', { data: filename })
      } catch (error) {
        console.error('Error downloading export:', error)
        window.showToast({
          type: 'danger',
          title: 'Download Failed',
          message: 'Failed to download the export file',
        })
      }
    }

    const generateReport = async () => {
      if (!isValidExportOptions.value) {
        window.showToast({
          type: 'warning',
          title: 'Invalid Options',
          message: 'Please check your export options',
        })
        return
      }

      try {
        isExporting.value = true

        const exportData = {
          ...(exportOptions.value.professional_id && {
            professional_id: parseInt(exportOptions.value.professional_id),
          }),
          ...(exportOptions.value.start_date && { start_date: exportOptions.value.start_date }),
          ...(exportOptions.value.end_date && { end_date: exportOptions.value.end_date }),
        }

        const response = await store.dispatch('exports/generateServiceReport', { data: exportData })

        if (response && response.data && response.data.task_id) {
          exportTaskId.value = response.data.task_id
          exportStatus.value = {
            state: 'PENDING',
            status: 'Export job submitted, waiting for processing...',
          }

          startExportStatusPolling(response.data.task_id)

          window.showToast({
            type: 'info',
            title: 'Export Started',
            message: 'The export job has been submitted and is being processed',
          })
        } else {
          throw new Error('Invalid response from export service')
        }
      } catch (error) {
        console.error('Error generating report:', error)
        window.showToast({
          type: 'danger',
          title: 'Export Failed',
          message: error.response?.data?.detail || 'Failed to start the export job',
        })
        isExporting.value = false
      }
    }

    // Watch for export status changes
    watch(
      () => exportStatus.value?.state,
      (newState) => {
        if (newState === 'SUCCESS' || newState === 'FAILURE') {
          isExporting.value = false
        }
      },
    )

    // Cleanup on component unmount
    onUnmounted(() => {
      clearExportStatusInterval()
    })

    // Initialize component
    onMounted(async () => {
      // Initialize Bootstrap modals
      if (exportModal.value) {
        bsExportModal = new bootstrap.Modal(exportModal.value)
      }

      // Load initial data
      await refreshDashboard()

      // Initialize chart
      setChartPeriod('weekly')
    })

    // Utility function to calculate height percentage for chart bars
    const getBarHeight = (value) => {
      const maxValue = Math.max(...chartData.value, 1)
      return value > 0 ? (value / maxValue) * 95 : 0 // Max height 95% to always show some bar
    }

    return {
      // State
      stats,
      isLoading,
      isLoadingChart,
      isLoadingProfessionals,
      isLoadingActivity,
      isLoadingServices,
      chartPeriod,
      servicesList,
      pendingProfessionals,
      activityLogs,
      chartData,
      displayedLabels,
      exportModal,
      exportOptions,
      isExporting,
      exportStatus,
      verifiedProfessionals,
      isValidExportOptions,
      progressColors,

      // Methods
      refreshDashboard,
      setChartPeriod,
      verifyProfessional,
      getServiceName,
      getServicePercentage,
      formatActionType,
      getActionIcon,
      getActionBadgeClass,
      loadMoreActivity,
      formatRelativeTime,
      formatDateTime,
      openExportModal,
      generateReport,
      getExportStatusBadgeClass,
      getExportProgressPercentage,
      getExportProgressText,
      getBarHeight,
    }
  },
})
</script>

<style scoped>
.icon-rounded {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
}

.icon-rounded i {
  font-size: 1.5rem;
}

.avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

/* Chart Mockup */
.chart-mockup {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 100%;
  padding-bottom: 10px;
}

.chart-bar {
  width: 12%;
  background-color: var(--bs-primary);
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .icon-rounded {
    width: 40px;
    height: 40px;
  }

  .icon-rounded i {
    font-size: 1.25rem;
  }

  .display-6 {
    font-size: 1.75rem;
  }
}
</style>
