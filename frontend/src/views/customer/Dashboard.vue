<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="row mb-4 align-items-center">
      <div class="col-lg-8">
        <h1 class="h3 mb-0">Customer Dashboard</h1>
        <p class="text-muted">Track your services, spending, and upcoming appointments</p>
      </div>
      <div class="col-lg-4 text-lg-end">
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
    <div v-if="isLoading" class="row">
      <div class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading dashboard data...</p>
      </div>
    </div>

    <template v-else>
      <!-- Key Metrics -->
      <div class="row g-4 mb-4">
        <!-- Total Requests -->
        <div class="col-md-6 col-lg-3">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h6 class="card-subtitle text-muted fw-normal">Total Requests</h6>
                <div class="icon-box bg-primary-subtle text-primary rounded-3">
                  <i class="bi bi-clipboard-check"></i>
                </div>
              </div>
              <h2 class="card-title mb-0">{{ dashboardData.total_requests || 0 }}</h2>
              <div v-if="dashboardData.monthly_comparison" class="mt-2 small">
                <span
                  :class="
                    dashboardData.monthly_comparison.change_percent > 0
                      ? 'text-success'
                      : 'text-danger'
                  "
                >
                  <i
                    class="bi"
                    :class="
                      dashboardData.monthly_comparison.change_percent > 0
                        ? 'bi-arrow-up-right'
                        : 'bi-arrow-down-right'
                    "
                  >
                  </i>
                  {{ Math.abs(dashboardData.monthly_comparison.change_percent).toFixed(1) }}%
                </span>
                <span class="text-muted ms-1"
                  >vs previous {{ dashboardData.monthly_comparison.current_month }}</span
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Active Requests -->
        <div class="col-md-6 col-lg-3">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h6 class="card-subtitle text-muted fw-normal">Active Requests</h6>
                <div class="icon-box bg-warning-subtle text-warning rounded-3">
                  <i class="bi bi-hourglass-split"></i>
                </div>
              </div>
              <h2 class="card-title mb-0">{{ dashboardData.active_requests || 0 }}</h2>
              <div class="mt-2 small">
                <span
                  v-if="dashboardData.active_requests > 0"
                  class="badge bg-warning-subtle text-warning"
                >
                  Ongoing Services
                </span>
                <span v-else class="badge bg-success-subtle text-success">All Complete</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Completed Requests -->
        <div class="col-md-6 col-lg-3">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h6 class="card-subtitle text-muted fw-normal">Completed Services</h6>
                <div class="icon-box bg-success-subtle text-success rounded-3">
                  <i class="bi bi-check2-all"></i>
                </div>
              </div>
              <h2 class="card-title mb-0">{{ dashboardData.completed_requests || 0 }}</h2>
              <div class="mt-2 small">
                <span class="badge bg-success-subtle text-success">
                  {{ getCompletionRate() }}% Completion Rate
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Spent -->
        <div class="col-md-6 col-lg-3">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h6 class="card-subtitle text-muted fw-normal">Total Spent</h6>
                <div class="icon-box bg-info-subtle text-info rounded-3">
                  <i class="bi bi-currency-rupee"></i>
                </div>
              </div>
              <h2 class="card-title mb-0">
                ₹{{ dashboardData.total_spent?.toFixed(2) || '0.00' }}
              </h2>
              <div class="mt-2 small" v-if="dashboardData.monthly_comparison">
                <span
                  :class="
                    dashboardData.monthly_comparison.change_percent > 0
                      ? 'text-success'
                      : 'text-success'
                  "
                >
                  <i class="bi bi-bar-chart-line"></i>
                  {{ Math.abs(dashboardData.monthly_comparison.current_month_spending).toFixed(0) }}
                  this month
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="row g-4 mb-4">
        <!-- Monthly Spending Chart -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Monthly Spending</h5>
              <p class="card-text text-muted small">Your spending across months</p>
            </div>
            <div class="card-body">
              <canvas id="monthlySpendingChart" height="250"></canvas>
            </div>
          </div>
        </div>

        <!-- Service Distribution Chart -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Service Distribution</h5>
              <p class="card-text text-muted small">Services by category</p>
            </div>
            <div class="card-body">
              <canvas id="serviceDistributionChart" height="250"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Charts Row -->
      <div class="row g-4 mb-4">
        <!-- Weekly Request Trend Chart -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Service Request Trend</h5>
              <p class="card-text text-muted small">Weekly request activity</p>
            </div>
            <div class="card-body">
              <canvas id="weeklyTrendChart" height="250"></canvas>
            </div>
          </div>
        </div>

        <!-- Favorite Services -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Your Favorite Services</h5>
              <p class="card-text text-muted small">Based on usage and ratings</p>
            </div>
            <div class="card-body p-0">
              <div
                v-if="
                  !dashboardData.favorite_services || dashboardData.favorite_services.length === 0
                "
                class="text-center py-5"
              >
                <i class="bi bi-star text-muted" style="font-size: 2rem"></i>
                <p class="mt-3 mb-0">No favorite services yet</p>
                <p class="text-muted small">Book more services to see your favorites here</p>
              </div>
              <ul v-else class="list-group list-group-flush">
                <li
                  v-for="service in dashboardData.favorite_services"
                  :key="service.service_id"
                  class="list-group-item border-start-0 border-end-0"
                >
                  <div class="d-flex align-items-center">
                    <div class="service-icon me-3">
                      <i class="bi bi-tools"></i>
                    </div>
                    <div class="flex-grow-1">
                      <h6 class="mb-0">{{ service.service_name }}</h6>
                      <div class="d-flex align-items-center mt-1">
                        <div class="me-3">
                          <i class="bi bi-clock text-muted me-1"></i>
                          <small>{{ formatDate(service.last_used) }}</small>
                        </div>
                        <div>
                          <i class="bi bi-star-fill text-warning me-1"></i>
                          <small>{{ service.avg_rating || 'No Rating' }}</small>
                        </div>
                      </div>
                    </div>
                    <div class="ms-auto">
                      <span class="badge bg-primary-subtle text-primary">
                        {{ service.usage_count }}x
                      </span>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Services -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-transparent border-0">
          <h5 class="card-title mb-0">Upcoming Services</h5>
          <p class="card-text text-muted small">Services scheduled in the coming days</p>
        </div>
        <div class="card-body p-0">
          <div
            v-if="!dashboardData.upcoming_services || dashboardData.upcoming_services.length === 0"
            class="text-center py-5"
          >
            <i class="bi bi-calendar-check text-muted" style="font-size: 2rem"></i>
            <p class="mt-3 mb-0">No upcoming services scheduled</p>
            <router-link to="/customer/services" class="btn btn-primary btn-sm mt-2">
              Book a Service
            </router-link>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Service</th>
                  <th>Professional</th>
                  <th>Scheduled Time</th>
                  <th>Status</th>
                  <th>Price</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="service in dashboardData.upcoming_services" :key="service.id">
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="service-icon me-2">
                        <i class="bi bi-tools"></i>
                      </div>
                      <div>{{ service.service_name }}</div>
                    </div>
                  </td>
                  <td>{{ service.professional_name || 'Pending Assignment' }}</td>
                  <td>{{ formatDateTime(service.preferred_time) }}</td>
                  <td>
                    <span class="badge" :class="getStatusBadgeClass(service.status)">
                      {{ getStatusLabel(service.status) }}
                    </span>
                  </td>
                  <td>₹{{ service.price?.toFixed(2) || '0.00' }}</td>
                  <td>
                    <div class="btn-group">
                      <router-link
                        :to="`/customer/requests?id=${service.id}`"
                        class="btn btn-sm btn-outline-primary"
                      >
                        <i class="bi bi-eye"></i>
                      </router-link>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Recent Services -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-transparent border-0">
          <h5 class="card-title mb-0">Recent Services</h5>
          <p class="card-text text-muted small">Your recently completed services</p>
        </div>
        <div class="card-body p-0">
          <div
            v-if="!dashboardData.recent_services || dashboardData.recent_services.length === 0"
            class="text-center py-5"
          >
            <i class="bi bi-clock-history text-muted" style="font-size: 2rem"></i>
            <p class="mt-3 mb-0">No recent services</p>
            <p class="text-muted small">Your completed services will appear here</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Service</th>
                  <th>Professional</th>
                  <th>Completion Date</th>
                  <th>Price</th>
                  <th>Rating</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="service in dashboardData.recent_services" :key="service.id">
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="service-icon me-2">
                        <i class="bi bi-tools"></i>
                      </div>
                      <div>{{ service.service_name }}</div>
                    </div>
                  </td>
                  <td>{{ service.professional_name }}</td>
                  <td>{{ formatDate(service.completion_date) }}</td>
                  <td>₹{{ service.price?.toFixed(2) || '0.00' }}</td>
                  <td>
                    <div v-if="service.has_review" class="d-flex align-items-center">
                      <div class="stars-container">
                        <i
                          v-for="i in 5"
                          :key="i"
                          class="bi"
                          :class="
                            i <= service.rating ? 'bi-star-fill text-warning' : 'bi-star text-muted'
                          "
                        ></i>
                      </div>
                    </div>
                    <span v-else class="badge bg-secondary">Not Rated</span>
                  </td>
                  <td>
                    <div class="btn-group">
                      <router-link
                        :to="`/customer/requests?id=${service.id}`"
                        class="btn btn-sm btn-outline-primary"
                      >
                        <i class="bi bi-eye"></i>
                      </router-link>
                      <button
                        v-if="!service.has_review"
                        class="btn btn-sm btn-outline-warning"
                        @click="reviewRequest(service)"
                      >
                        <i class="bi bi-star"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  BarElement,
  BarController,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  DoughnutController,
} from 'chart.js'
import { formatDate, formatDateTime } from '@/utils/date'
import { requestStatusBadges, statusLabels } from '@/assets/requestStatuses'

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  BarElement,
  BarController,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  DoughnutController,
)

export default defineComponent({
  name: 'CustomerDashboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    const isLoading = ref(true)
    const dashboardData = ref({})
    const selectedPeriod = ref('30d')

    // Chart instances
    const charts = {
      monthlySpending: null,
      weeklyTrend: null,
      serviceDistribution: null,
    }

    // Available time periods
    const periods = [
      { value: '30d', label: '30 Days' },
      // { value: '90d', label: '90 Days' },
      // { value: 'all', label: 'All Time' },
    ]

    // Methods
    const fetchDashboardData = async (forceRefresh = false) => {
      isLoading.value = true
      try {
        const params = { period: selectedPeriod.value }
        const response = await store.dispatch('customers/getDashboard', { params, forceRefresh })

        // Create a deep clone of the data to avoid Vuex state mutations
        if (response && response.data) {
          dashboardData.value = JSON.parse(JSON.stringify(response.data || {}))
        } else {
          dashboardData.value = {}
        }

        // Initialize charts after data is loaded
        setTimeout(() => {
          renderMonthlySpendingChart()
          renderWeeklyTrendChart()
          renderServiceDistributionChart()
        }, 100)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        window.showToast({
          type: 'danger',
          title: 'Failed to load dashboard data',
          message: error.response?.data?.detail || 'An unexpected error occurred',
        })
      } finally {
        isLoading.value = false
      }
    }

    const changePeriod = (period) => {
      selectedPeriod.value = period
      fetchDashboardData(true)
    }

    const getCompletionRate = () => {
      if (!dashboardData.value || !dashboardData.value.total_requests) return 0
      return Math.round(
        (dashboardData.value.completed_requests / dashboardData.value.total_requests) * 100,
      )
    }

    const getStatusBadgeClass = (status) => requestStatusBadges[status]
    const getStatusLabel = (status) => statusLabels[status]

    const reviewRequest = (service) => {
      router.push(`/customer/requests?id=${service.id}&action=review`)
    }

    // Chart rendering functions
    const renderMonthlySpendingChart = () => {
      const ctx = document.getElementById('monthlySpendingChart')
      if (!ctx) return

      const monthlyData = JSON.parse(JSON.stringify(dashboardData.value.monthly_spending || []))

      if (charts.monthlySpending) {
        charts.monthlySpending.destroy()
      }

      charts.monthlySpending = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: monthlyData.map((item) => item.month),
          datasets: [
            {
              label: 'Amount Spent (₹)',
              data: monthlyData.map((item) => item.amount),
              backgroundColor: 'rgba(13, 110, 253, 0.7)',
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
                  return `₹${context.parsed.y.toFixed(2)}`
                },
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                drawBorder: false,
              },
              ticks: {
                callback: function (value) {
                  return '₹' + value
                },
              },
            },
            x: {
              grid: {
                display: false,
              },
            },
          },
        },
      })
    }

    const renderWeeklyTrendChart = () => {
      const ctx = document.getElementById('weeklyTrendChart')
      if (!ctx) return

      const weeklyData = JSON.parse(JSON.stringify(dashboardData.value.weekly_trend || []))

      if (charts.weeklyTrend) {
        charts.weeklyTrend.destroy()
      }

      charts.weeklyTrend = new Chart(ctx, {
        type: 'line',
        data: {
          labels: weeklyData.map((item) => item.period),
          datasets: [
            {
              label: 'Requested',
              data: weeklyData.map((item) => item.requested),
              borderColor: '#fd7e14',
              backgroundColor: 'rgba(253, 126, 20, 0.1)',
              tension: 0.3,
              fill: true,
            },
            {
              label: 'Completed',
              data: weeklyData.map((item) => item.completed),
              borderColor: '#20c997',
              backgroundColor: 'rgba(32, 201, 151, 0.1)',
              tension: 0.3,
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
            tooltip: {
              mode: 'index',
              intersect: false,
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                drawBorder: false,
              },
              ticks: {
                precision: 0,
              },
            },
            x: {
              grid: {
                display: false,
              },
            },
          },
        },
      })
    }

    const renderServiceDistributionChart = () => {
      const ctx = document.getElementById('serviceDistributionChart')
      if (!ctx) return

      const distributionData = JSON.parse(
        JSON.stringify(dashboardData.value.service_distribution || []),
      )

      if (charts.serviceDistribution) {
        charts.serviceDistribution.destroy()
      }

      // Generate distinct colors for each service
      const generateColors = (count) => {
        const colors = []
        const baseColors = [
          'rgba(54, 162, 235, 0.7)', // blue
          'rgba(255, 99, 132, 0.7)', // red
          'rgba(255, 206, 86, 0.7)', // yellow
          'rgba(75, 192, 192, 0.7)', // green
          'rgba(153, 102, 255, 0.7)', // purple
          'rgba(255, 159, 64, 0.7)', // orange
          'rgba(199, 199, 199, 0.7)', // gray
          'rgba(83, 102, 255, 0.7)', // indigo
          'rgba(255, 99, 255, 0.7)', // pink
          'rgba(30, 130, 76, 0.7)', // green-blue
        ]

        for (let i = 0; i < count; i++) {
          colors.push(baseColors[i % baseColors.length])
        }

        return colors
      }

      const colors = generateColors(distributionData.length)

      charts.serviceDistribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: distributionData.map((item) => item.service_name),
          datasets: [
            {
              data: distributionData.map((item) => item.request_count),
              backgroundColor: colors,
              borderColor: colors.map((color) => color.replace('0.7', '1')),
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: {
                boxWidth: 12,
                padding: 15,
              },
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const item = distributionData[context.dataIndex]
                  return [
                    `${item.service_name}: ${item.request_count} requests`,
                    `Total spent: ₹${item.total_spent.toFixed(2)} (${item.percentage.toFixed(1)}%)`,
                  ]
                },
              },
            },
          },
          cutout: '60%',
        },
      })
    }

    // Lifecycle hooks
    onMounted(async () => {
      await fetchDashboardData()
    })

    // Watch for period changes
    watch(
      () => selectedPeriod.value,
      () => {
        fetchDashboardData(true)
      },
    )

    return {
      isLoading,
      dashboardData,
      selectedPeriod,
      periods,
      changePeriod,
      getCompletionRate,
      getStatusBadgeClass,
      getStatusLabel,
      reviewRequest,
      formatDate,
      formatDateTime,
    }
  },
})
</script>

<style scoped>
.icon-box {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
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

.stars-container {
  display: inline-flex;
  align-items: center;
}

.card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .btn-group {
    display: flex;
    width: 100%;
    margin-top: 1rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start !important;
  }
}
</style>
