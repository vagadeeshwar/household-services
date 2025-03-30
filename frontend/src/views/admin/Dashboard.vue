<template>
  <div class="admin-dashboard">
    <div class="row mb-4 align-items-center">
      <div class="col-md-6">
        <h1 class="h3 mb-0">Admin Dashboard</h1>
        <p class="text-muted">Overview of platform performance and metrics</p>
      </div>
      <div class="col-md-6 text-md-end">
        <div class="btn-group" role="group">
          <button
            v-for="period in periods"
            :key="period.value"
            :class="[
              'btn',
              selectedPeriod === period.value ? 'btn-primary' : 'btn-outline-primary',
            ]"
            @click="changePeriod(period.value)"
          >
            {{ period.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading dashboard data...</span>
      </div>
      <p class="mt-3 text-muted">Loading dashboard data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <div class="d-flex align-items-center">
        <i class="bi bi-exclamation-triangle-fill me-2 fs-4"></i>
        <div>
          <h5 class="alert-heading">Failed to load dashboard data</h5>
          <p class="mb-0">{{ error }}</p>
        </div>
      </div>
      <button class="btn btn-danger mt-3" @click="fetchDashboardData(true)">
        <i class="bi bi-arrow-clockwise me-1"></i> Retry
      </button>
    </div>

    <template v-else>
      <!-- Top Summary Cards -->
      <div class="row g-4 mb-4">
        <!-- User Stats Card -->
        <div class="col-xl-3 col-md-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <h6 class="text-muted fw-normal mb-0">Users</h6>
                <div class="icon-box bg-primary-subtle text-primary rounded-3">
                  <i class="bi bi-people"></i>
                </div>
              </div>
              <h2 class="mb-0">{{ dashboardData.total_users || 0 }}</h2>
              <div class="d-flex align-items-center mt-2">
                <div class="flex-fill">
                  <span class="badge bg-primary-subtle text-primary me-1">
                    {{ dashboardData.customer_count || 0 }} Customers
                  </span>
                  <span class="badge bg-success-subtle text-success">
                    {{ dashboardData.professional_count || 0 }} Professionals
                  </span>
                </div>
                <div class="active-indicator text-success">
                  <i class="bi bi-circle-fill me-1 small"></i>
                  <span class="small">{{ dashboardData.active_users || 0 }} Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Request Stats Card -->
        <div class="col-xl-3 col-md-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <h6 class="text-muted fw-normal mb-0">Service Requests</h6>
                <div class="icon-box bg-warning-subtle text-warning rounded-3">
                  <i class="bi bi-clipboard-check"></i>
                </div>
              </div>
              <h2 class="mb-0">{{ dashboardData.total_requests || 0 }}</h2>
              <div class="d-flex align-items-center mt-2">
                <div class="request-pills">
                  <span class="badge bg-success"
                    >{{ dashboardData.completed_requests || 0 }} Completed</span
                  >
                  <span class="badge bg-warning text-dark"
                    >{{ dashboardData.active_requests || 0 }} Active</span
                  >
                  <span class="badge bg-secondary"
                    >{{ dashboardData.pending_requests || 0 }} Pending</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Revenue Stats Card -->
        <div class="col-xl-3 col-md-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <h6 class="text-muted fw-normal mb-0">Revenue</h6>
                <div class="icon-box bg-success-subtle text-success rounded-3">
                  <i class="bi bi-currency-rupee"></i>
                </div>
              </div>
              <h2 class="mb-0">₹{{ formatCurrency(dashboardData.total_revenue) }}</h2>
              <div class="d-flex align-items-center mt-2">
                <div class="flex-fill">
                  <span class="text-success">
                    <i class="bi bi-currency-rupee"></i>
                    {{ formatCurrency(dashboardData.avg_revenue_per_request) }} / request
                  </span>
                </div>
                <div
                  v-if="dashboardData.period_comparison?.revenue_change_pct !== undefined"
                  class="change-indicator"
                >
                  <span :class="getChangeClass(dashboardData.period_comparison.revenue_change_pct)">
                    <i
                      :class="getChangeIcon(dashboardData.period_comparison.revenue_change_pct)"
                    ></i>
                    {{ formatPercentage(dashboardData.period_comparison.revenue_change_pct) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="row g-4 mb-4">
        <!-- Monthly Revenue Chart -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div
              class="card-header bg-transparent border-0 d-flex justify-content-between align-items-center"
            >
              <div>
                <h5 class="card-title mb-0">Monthly Revenue</h5>
                <p class="text-muted small mb-0">Revenue trend over time</p>
              </div>
              <div class="dropdown">
                <button
                  class="btn btn-sm btn-outline-secondary dropdown-toggle"
                  type="button"
                  data-bs-toggle="dropdown"
                >
                  <i class="bi bi-sliders me-1"></i> Options
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li>
                    <button class="dropdown-item" @click="refreshChart('monthly-revenue')">
                      Refresh Data
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            <div class="card-body">
              <canvas id="monthlyRevenueChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Request Distribution Chart -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Request Status</h5>
              <p class="text-muted small mb-0">Current service request distribution</p>
            </div>
            <div class="card-body d-flex align-items-center justify-content-center">
              <canvas id="requestStatusChart" height="300"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Data Tables Row -->
      <div class="row g-4 mb-4">
        <!-- Recent Requests Table -->
        <div class="col-xl-6">
          <div class="card border-0 shadow-sm h-100">
            <div
              class="card-header bg-transparent border-0 d-flex justify-content-between align-items-center"
            >
              <div>
                <h5 class="card-title mb-0">Recent Requests</h5>
                <p class="text-muted small mb-0">Latest service requests from customers</p>
              </div>
              <router-link to="/admin/requests" class="btn btn-sm btn-outline-primary">
                View All
              </router-link>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th scope="col">#</th>
                      <th scope="col">Service</th>
                      <th scope="col">Customer</th>
                      <th scope="col">Professional</th>
                      <th scope="col">Status</th>
                      <th scope="col">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-if="
                        !dashboardData.recent_requests || dashboardData.recent_requests.length === 0
                      "
                    >
                      <td colspan="6" class="text-center py-3">No recent requests found</td>
                    </tr>
                    <tr
                      v-for="request in dashboardData.recent_requests?.slice(0, 5)"
                      :key="request.id"
                      class="align-middle"
                    >
                      <td>{{ request.id }}</td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="service-icon me-2">
                            <i class="bi bi-tools"></i>
                          </div>
                          <span>{{ request.service_name }}</span>
                        </div>
                      </td>
                      <td>{{ request.customer_name }}</td>
                      <td>{{ request.professional_name || 'Unassigned' }}</td>
                      <td>
                        <span :class="getStatusBadgeClass(request.status)">
                          {{ getStatusLabel(request.status) }}
                        </span>
                      </td>
                      <td>{{ formatDate(request.date_of_request) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Third Row -->
      <div class="row g-4 mb-4">
        <!-- Popular Services -->
        <div class="col-xl-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Popular Services</h5>
              <p class="text-muted small mb-0">Most requested services on the platform</p>
            </div>
            <div class="card-body">
              <div
                v-if="
                  !dashboardData.popular_services || dashboardData.popular_services.length === 0
                "
                class="text-center py-4"
              >
                <i class="bi bi-bar-chart text-muted" style="font-size: 3rem"></i>
                <p class="mt-3 mb-0">No service data available</p>
              </div>
              <div v-else>
                <div
                  v-for="(service, index) in dashboardData.popular_services?.slice(0, 5)"
                  :key="service.id"
                  class="popular-service-item mb-3"
                >
                  <div class="d-flex align-items-center mb-2">
                    <div class="service-rank me-3">{{ index + 1 }}</div>
                    <div class="flex-grow-1">
                      <h6 class="mb-0">{{ service.name }}</h6>
                    </div>
                    <div class="text-end">
                      <div class="fw-bold">{{ service.request_count }}</div>
                      <small class="text-muted">requests</small>
                    </div>
                  </div>
                  <div class="progress" style="height: 8px">
                    <div
                      class="progress-bar bg-primary"
                      :style="{ width: `${service.percentage}%` }"
                      role="progressbar"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Metrics Row -->
      <div class="row g-4">
        <!-- Period Comparison -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Period Comparison</h5>
              <p class="text-muted small mb-0">Comparing with previous period</p>
            </div>
            <div class="card-body">
              <div v-if="!dashboardData.period_comparison" class="text-center py-4">
                <i class="bi bi-arrow-left-right text-muted" style="font-size: 2rem"></i>
                <p class="mt-3 mb-0">No comparison data available</p>
              </div>
              <div v-else>
                <div class="row g-4">
                  <!-- Total Requests Comparison -->
                  <div class="col-md-6">
                    <div class="comparison-card p-3 border rounded-3">
                      <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted">Total Requests</span>
                        <span
                          :class="
                            getChangeClass(
                              dashboardData.period_comparison.total_requests_change_pct,
                            )
                          "
                        >
                          <i
                            :class="
                              getChangeIcon(
                                dashboardData.period_comparison.total_requests_change_pct,
                              )
                            "
                          ></i>
                          {{
                            formatPercentage(
                              dashboardData.period_comparison.total_requests_change_pct,
                            )
                          }}
                        </span>
                      </div>
                      <div class="d-flex align-items-end">
                        <div class="h4 mb-0 me-3">{{ dashboardData.total_requests }}</div>
                        <div class="text-muted small">
                          vs {{ dashboardData.period_comparison.prev_total_requests }}
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Completed Requests Comparison -->
                  <div class="col-md-6">
                    <div class="comparison-card p-3 border rounded-3">
                      <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted">Completed Requests</span>
                        <span
                          :class="
                            getChangeClass(
                              dashboardData.period_comparison.completed_requests_change_pct,
                            )
                          "
                        >
                          <i
                            :class="
                              getChangeIcon(
                                dashboardData.period_comparison.completed_requests_change_pct,
                              )
                            "
                          ></i>
                          {{
                            formatPercentage(
                              dashboardData.period_comparison.completed_requests_change_pct,
                            )
                          }}
                        </span>
                      </div>
                      <div class="d-flex align-items-end">
                        <div class="h4 mb-0 me-3">{{ dashboardData.completed_requests }}</div>
                        <div class="text-muted small">
                          vs {{ dashboardData.period_comparison.prev_completed_requests }}
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Average Rating Comparison -->
                  <div class="col-md-6">
                    <div class="comparison-card p-3 border rounded-3">
                      <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted">Average Rating</span>
                        <span
                          :class="getChangeClass(dashboardData.period_comparison.rating_change_pct)"
                        >
                          <i
                            :class="
                              getChangeIcon(dashboardData.period_comparison.rating_change_pct)
                            "
                          ></i>
                          {{ formatPercentage(dashboardData.period_comparison.rating_change_pct) }}
                        </span>
                      </div>
                      <div class="d-flex align-items-end">
                        <div class="h4 mb-0 me-3">
                          {{ dashboardData.average_rating?.toFixed(1) }}
                        </div>
                        <div class="text-muted small">
                          vs {{ dashboardData.period_comparison.prev_avg_rating?.toFixed(1) }}
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Revenue Comparison -->
                  <div class="col-md-6">
                    <div class="comparison-card p-3 border rounded-3">
                      <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted">Revenue</span>
                        <span
                          :class="
                            getChangeClass(dashboardData.period_comparison.revenue_change_pct)
                          "
                        >
                          <i
                            :class="
                              getChangeIcon(dashboardData.period_comparison.revenue_change_pct)
                            "
                          ></i>
                          {{ formatPercentage(dashboardData.period_comparison.revenue_change_pct) }}
                        </span>
                      </div>
                      <div class="d-flex align-items-end">
                        <div class="h4 mb-0 me-3">
                          ₹{{ formatCurrency(dashboardData.total_revenue) }}
                        </div>
                        <div class="text-muted small">vs previous period</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Stats -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Performance Metrics</h5>
              <p class="text-muted small mb-0">Key performance indicators</p>
            </div>
            <div class="card-body">
              <div class="row g-4">
                <!-- Customer Retention -->
                <div class="col-md-6">
                  <div class="stat-card p-3 border rounded-3">
                    <div class="d-flex align-items-center mb-3">
                      <div class="icon-box bg-success-subtle text-success me-3">
                        <i class="bi bi-people-fill"></i>
                      </div>
                      <div>
                        <h6 class="mb-0">Customer Retention</h6>
                      </div>
                    </div>
                    <div class="text-center">
                      <div class="display-6 fw-bold">
                        {{ dashboardData.customer_retention_rate?.toFixed(1) || 0 }}%
                      </div>
                      <div class="text-muted small">of customers return</div>
                    </div>
                  </div>
                </div>

                <!-- Avg Completion Time -->
                <div class="col-md-6">
                  <div class="stat-card p-3 border rounded-3">
                    <div class="d-flex align-items-center mb-3">
                      <div class="icon-box bg-warning-subtle text-warning me-3">
                        <i class="bi bi-stopwatch"></i>
                      </div>
                      <div>
                        <h6 class="mb-0">Avg Service Time</h6>
                      </div>
                    </div>
                    <div class="text-center">
                      <div class="display-6 fw-bold">
                        {{ dashboardData.avg_completion_time_hours?.toFixed(1) || 0 }}
                      </div>
                      <div class="text-muted small">hours to completion</div>
                    </div>
                  </div>
                </div>

                <!-- Professional Productivity -->
                <div class="col-md-6">
                  <div class="stat-card p-3 border rounded-3">
                    <div class="d-flex align-items-center mb-3">
                      <div class="icon-box bg-primary-subtle text-primary me-3">
                        <i class="bi bi-lightning-charge"></i>
                      </div>
                      <div>
                        <h6 class="mb-0">Pro Productivity</h6>
                      </div>
                    </div>
                    <div class="text-center">
                      <div class="display-6 fw-bold">
                        {{ dashboardData.avg_completed_per_professional?.toFixed(1) || 0 }}
                      </div>
                      <div class="text-muted small">services per professional</div>
                    </div>
                  </div>
                </div>

                <!-- Service Fulfillment -->
                <div class="col-md-6">
                  <div class="stat-card p-3 border rounded-3">
                    <div class="d-flex align-items-center mb-3">
                      <div class="icon-box bg-info-subtle text-info me-3">
                        <i class="bi bi-check2-circle"></i>
                      </div>
                      <div>
                        <h6 class="mb-0">Fulfillment Rate</h6>
                      </div>
                    </div>
                    <div class="text-center">
                      <div class="display-6 fw-bold">
                        {{ dashboardData.service_fulfillment_rate?.toFixed(1) || 0 }}%
                      </div>
                      <div class="text-muted small">requests fulfilled</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { useStore } from 'vuex'
import { formatDate, formatDateTime } from '@/utils/date'
import { requestStatusBadges, statusLabels } from '@/assets/requestStatuses'
import Chart from 'chart.js/auto'

export default defineComponent({
  name: 'AdminDashboard',
  setup() {
    const store = useStore()
    const dashboardData = ref({})
    const isLoading = ref(true)
    const error = ref(null)
    const selectedPeriod = ref('30d')

    // Chart instances for cleanup
    const charts = {
      monthlyRevenue: null,
      requestStatus: null,
      registrationTrend: null,
      serviceUtilization: null,
    }

    // Available time periods
    const periods = [
      { value: '7d', label: '7 Days' },
      { value: '30d', label: '30 Days' },
      { value: '90d', label: '90 Days' },
      { value: 'all', label: 'All Time' },
    ]

    // Fetch dashboard data
    const fetchDashboardData = async (forceRefresh = false) => {
      isLoading.value = true
      error.value = null

      try {
        const params = {
          period: selectedPeriod.value,
          compare_to: 'prev_period',
        }

        const response = await store.dispatch('auth/getDashboard', { params, forceRefresh })

        if (response && response.data) {
          dashboardData.value = response.data
        } else {
          dashboardData.value = {}
        }

        // Render charts after data is loaded
        setTimeout(() => {
          renderCharts()
        }, 100)
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
        error.value =
          err.response?.data?.detail || 'Failed to load dashboard data. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    const changePeriod = (period) => {
      selectedPeriod.value = period
    }

    // Chart rendering functions
    const renderCharts = () => {
      renderMonthlyRevenueChart()
      renderRequestStatusChart()
      renderRegistrationTrendChart()
      renderServiceUtilizationChart()
    }

    const renderMonthlyRevenueChart = () => {
      const ctx = document.getElementById('monthlyRevenueChart')
      if (!ctx) return

      const monthlyData = dashboardData.value.monthly_revenue_trend || []

      if (charts.monthlyRevenue) {
        charts.monthlyRevenue.destroy()
      }

      charts.monthlyRevenue = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: monthlyData.map((item) => item.month),
          datasets: [
            {
              label: 'Revenue (₹)',
              data: monthlyData.map((item) => item.revenue),
              backgroundColor: 'rgba(13, 110, 253, 0.8)',
              borderColor: 'rgb(13, 110, 253)',
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `₹${context.parsed.y.toLocaleString('en-IN')}`
                },
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function (value) {
                  return '₹' + value.toLocaleString('en-IN')
                },
              },
            },
          },
        },
      })
    }

    const renderRequestStatusChart = () => {
      const ctx = document.getElementById('requestStatusChart')
      if (!ctx) return

      const data = [
        dashboardData.value.completed_requests || 0,
        dashboardData.value.active_requests || 0,
        dashboardData.value.pending_requests || 0,
      ]

      if (charts.requestStatus) {
        charts.requestStatus.destroy()
      }

      charts.requestStatus = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Completed', 'Active', 'Pending'],
          datasets: [
            {
              data: data,
              backgroundColor: [
                'rgba(25, 135, 84, 0.8)', // green
                'rgba(255, 193, 7, 0.8)', // yellow
                'rgba(108, 117, 125, 0.8)', // gray
              ],
              borderColor: ['rgb(25, 135, 84)', 'rgb(255, 193, 7)', 'rgb(108, 117, 125)'],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.label || ''
                  const value = context.parsed || 0
                  const total = data.reduce((a, b) => a + b, 0)
                  const percentage = total ? Math.round((value / total) * 100) : 0
                  return `${label}: ${value} (${percentage}%)`
                },
              },
            },
          },
          cutout: '70%',
        },
      })
    }

    const renderRegistrationTrendChart = () => {
      const ctx = document.getElementById('registrationTrendChart')
      if (!ctx) return

      const trendData = dashboardData.value.weekly_registration_trend || []

      if (charts.registrationTrend) {
        charts.registrationTrend.destroy()
      }

      charts.registrationTrend = new Chart(ctx, {
        type: 'line',
        data: {
          labels: trendData.map((item) => item.period),
          datasets: [
            {
              label: 'Customers',
              data: trendData.map((item) => item.customer_count || 0),
              borderColor: 'rgba(13, 110, 253, 0.8)',
              backgroundColor: 'rgba(13, 110, 253, 0.1)',
              tension: 0.4,
              fill: true,
            },
            {
              label: 'Professionals',
              data: trendData.map((item) => item.professional_count || 0),
              borderColor: 'rgba(25, 135, 84, 0.8)',
              backgroundColor: 'rgba(25, 135, 84, 0.1)',
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0,
              },
            },
          },
        },
      })
    }

    const renderServiceUtilizationChart = () => {
      const ctx = document.getElementById('serviceUtilizationChart')
      if (!ctx) return

      const utilizationData = dashboardData.value.service_utilization_by_day || []

      // Sort days of week properly
      const daysOrder = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
      ]
      utilizationData.sort((a, b) => daysOrder.indexOf(a.day) - daysOrder.indexOf(b.day))

      if (charts.serviceUtilization) {
        charts.serviceUtilization.destroy()
      }

      charts.serviceUtilization = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: utilizationData.map((item) => item.day),
          datasets: [
            {
              label: 'Service Requests',
              data: utilizationData.map((item) => item.count),
              backgroundColor: 'rgba(111, 66, 193, 0.8)',
              borderColor: 'rgb(111, 66, 193)',
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0,
              },
            },
          },
        },
      })
    }

    // Helper formatting functions
    const formatCurrency = (value) => {
      if (value === undefined || value === null) return '0.00'
      return parseFloat(value).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    }

    const formatPercentage = (value) => {
      if (value === undefined || value === null) return '0%'
      return (value > 0 ? '+' : '') + value.toFixed(1) + '%'
    }

    const getChangeClass = (value) => {
      if (value === undefined || value === null) return 'text-muted'
      return value > 0 ? 'text-success' : value < 0 ? 'text-danger' : 'text-muted'
    }

    const getChangeIcon = (value) => {
      if (value === undefined || value === null) return 'bi-dash'
      return value > 0 ? 'bi-arrow-up me-1' : value < 0 ? 'bi-arrow-down me-1' : 'bi-dash me-1'
    }

    const getStatusBadgeClass = (status) => {
      return requestStatusBadges[status] || 'bg-secondary'
    }

    const getStatusLabel = (status) => {
      return statusLabels[status] || status
    }

    const refreshChart = (chartId) => {
      if (chartId === 'monthly-revenue') {
        renderMonthlyRevenueChart()
      } else if (chartId === 'request-status') {
        renderRequestStatusChart()
      } else if (chartId === 'registration-trend') {
        renderRegistrationTrendChart()
      } else if (chartId === 'service-utilization') {
        renderServiceUtilizationChart()
      }
    }

    // Watch for period changes
    watch(
      () => selectedPeriod.value,
      () => {
        fetchDashboardData(true)
      },
    )

    // Initialize on mount
    onMounted(() => {
      fetchDashboardData()
    })

    // Clean up charts on unmount
    onBeforeUnmount(() => {
      Object.values(charts).forEach((chart) => {
        if (chart) chart.destroy()
      })
    })

    return {
      dashboardData,
      isLoading,
      error,
      selectedPeriod,
      periods,
      fetchDashboardData,
      changePeriod,
      formatCurrency,
      formatPercentage,
      getChangeClass,
      getChangeIcon,
      getStatusBadgeClass,
      getStatusLabel,
      formatDate,
      formatDateTime,
      refreshChart,
    }
  },
})
</script>

<style scoped>
.admin-dashboard {
  padding: 0 1rem;
}

/* Icons and badges */
.icon-box {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  border-radius: 8px;
}

.task-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  border-radius: 8px;
}

.service-icon {
  width: 32px;
  height: 32px;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  color: var(--bs-primary);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.service-rank {
  width: 28px;
  height: 28px;
  background-color: var(--bs-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* Cards */
.card {
  border-radius: 8px;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.card-header {
  background-color: transparent;
  border-bottom: none;
  padding: 1.25rem 1.25rem 0.5rem;
}

.card-body {
  padding: 1.25rem;
}

/* Popular service items */
.popular-service-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

/* Comparison and stat cards */
.comparison-card,
.stat-card {
  height: 100%;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.comparison-card:hover,
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.05);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .icon-box {
    width: 36px;
    height: 36px;
    font-size: 1.1rem;
  }

  .request-pills span {
    display: block;
    margin-bottom: 0.25rem;
  }

  .btn-group {
    width: 100%;
    margin-top: 1rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start !important;
  }

  .card-header .btn {
    margin-top: 0.5rem;
  }
}
</style>
