<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="row mb-4 align-items-center">
      <div class="col-lg-8">
        <h1 class="h3 mb-0">Professional Dashboard</h1>
        <p class="text-muted">Track your performance and manage upcoming service requests</p>
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
                  <i class="bi bi-briefcase"></i>
                </div>
              </div>
              <h2 class="card-title mb-0">{{ localDashboardData.total_requests || 0 }}</h2>
              <div v-if="localDashboardData.monthly_comparison" class="mt-2 small">
                <span
                  :class="
                    localDashboardData.monthly_comparison.change_percent > 0
                      ? 'text-success'
                      : 'text-danger'
                  "
                >
                  <i
                    class="bi"
                    :class="
                      localDashboardData.monthly_comparison.change_percent > 0
                        ? 'bi-arrow-up-right'
                        : 'bi-arrow-down-right'
                    "
                  >
                  </i>
                  {{ Math.abs(localDashboardData.monthly_comparison.change_percent).toFixed(1) }}%
                </span>
                <span class="text-muted ms-1"
                  >vs previous {{ localDashboardData.monthly_comparison.current_month }}</span
                >
              </div>
            </div>
          </div>
        </div>
        <!-- Completed Requests -->
        <div class="col-md-6 col-lg-3">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h6 class="card-subtitle text-muted fw-normal">Completed Requests</h6>
                <div class="icon-box bg-success-subtle text-success rounded-3">
                  <i class="bi bi-check2-all"></i>
                </div>
              </div>
              <h2 class="card-title mb-0">{{ localDashboardData.completed_requests || 0 }}</h2>
              <div class="mt-2 small">
                <span class="badge bg-success-subtle text-success">
                  {{ getCompletionRate() }}% Completion Rate
                </span>
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
              <h2 class="card-title mb-0">{{ localDashboardData.active_requests || 0 }}</h2>
              <div class="mt-2 small">
                <span
                  class="badge bg-warning-subtle text-warning"
                  v-if="localDashboardData.active_requests > 0"
                >
                  Ongoing Services
                </span>
                <span class="badge bg-success-subtle text-success" v-else>All Complete</span>
              </div>
            </div>
          </div>
        </div>
        <!-- Average Rating -->
        <div class="col-md-6 col-lg-3">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h6 class="card-subtitle text-muted fw-normal">Average Rating</h6>
                <div class="icon-box bg-info-subtle text-info rounded-3">
                  <i class="bi bi-star"></i>
                </div>
              </div>
              <h2 class="card-title mb-0">
                {{ localDashboardData.average_rating?.toFixed(1) || 'N/A' }}
              </h2>
              <div class="mt-2 small d-flex align-items-center">
                <template v-if="localDashboardData.average_rating">
                  <div class="stars-container me-2">
                    <i
                      v-for="i in 5"
                      :key="i"
                      class="bi"
                      :class="
                        i <= Math.round(localDashboardData.average_rating)
                          ? 'bi-star-fill text-warning'
                          : 'bi-star text-muted'
                      "
                    >
                    </i>
                  </div>
                  <span class="text-muted"
                    >{{ localDashboardData.total_reviews || 0 }} reviews</span
                  >
                </template>
                <span v-else class="text-muted">No reviews yet</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Charts and Tables Section -->
      <div class="row g-4 mb-4">
        <!-- Weekly Trend Chart -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Service Request Trend</h5>
              <p class="card-text text-muted small">Weekly request completion metrics</p>
            </div>
            <div class="card-body">
              <canvas id="weeklyTrendChart" height="250"></canvas>
            </div>
          </div>
        </div>
        <!-- Monthly Ratings Chart -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Monthly Ratings</h5>
              <p class="card-text text-muted small">Your performance over time</p>
            </div>
            <div class="card-body">
              <canvas id="monthlyRatingsChart" height="250"></canvas>
            </div>
          </div>
        </div>
      </div>
      <!-- Activity Patterns and Satisfaction Analysis -->
      <div class="row g-4 mb-4">
        <!-- Activity Patterns -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div
              class="card-header bg-transparent border-0 d-flex justify-content-between align-items-center"
            >
              <div>
                <h5 class="card-title mb-0">Activity Patterns</h5>
                <p class="card-text text-muted small">Your busiest working periods</p>
              </div>
              <div class="form-check form-switch">
                <input
                  class="form-check-input"
                  type="checkbox"
                  role="switch"
                  id="activitySwitch"
                  v-model="showHourlyPattern"
                />
                <label class="form-check-label" for="activitySwitch">
                  {{ showHourlyPattern ? 'Hourly' : 'Daily' }}
                </label>
              </div>
            </div>
            <div class="card-body">
              <canvas id="activityPatternsChart" height="250"></canvas>
            </div>
          </div>
        </div>
        <!-- Rating Distribution -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="card-title mb-0">Customer Satisfaction</h5>
              <p class="card-text text-muted small">Breakdown of ratings received</p>
            </div>
            <div class="card-body">
              <canvas id="ratingDistributionChart" height="250"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Service Type Info and Verification Status -->
      <div class="row g-4">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title">Service Information</h5>
              <div class="d-flex align-items-center mt-3 mb-2">
                <div class="flex-shrink-0">
                  <div class="service-type-icon rounded-circle bg-primary text-white">
                    <i class="bi bi-tools"></i>
                  </div>
                </div>
                <div class="flex-grow-1 ms-3">
                  <h6 class="mb-0">{{ localDashboardData.service_type || 'Not specified' }}</h6>
                  <p class="text-muted mb-0 small">Your service specialization</p>
                </div>
              </div>
              <hr />
              <div class="d-flex justify-content-between align-items-center mt-3">
                <div>
                  <span class="d-block fw-medium">Monthly Comparison</span>
                  <span class="text-muted small">vs Previous Month</span>
                </div>
                <div v-if="localDashboardData.monthly_comparison" class="text-end">
                  <span
                    class="d-block fw-medium"
                    :class="
                      localDashboardData.monthly_comparison.change_percent > 0
                        ? 'text-success'
                        : 'text-danger'
                    "
                  >
                    {{ localDashboardData.monthly_comparison.change_percent > 0 ? '+' : ''
                    }}{{ localDashboardData.monthly_comparison.change_percent.toFixed(1) }}%
                  </span>
                  <span class="text-muted small">
                    {{ localDashboardData.monthly_comparison.current_month_requests }} vs
                    {{ localDashboardData.monthly_comparison.prev_month_requests }}
                  </span>
                </div>
                <div v-else class="text-end">
                  <span class="text-muted">No data available</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title">Verification Status</h5>
              <div class="verification-status mt-3">
                <div class="d-flex align-items-center mb-3">
                  <div class="flex-shrink-0">
                    <div :class="['status-indicator rounded-circle', getVerificationStatusClass()]">
                      <i :class="['bi', getVerificationStatusIcon()]"></i>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="mb-0">{{ localDashboardData.verification_status || 'Pending' }}</h6>
                    <p class="text-muted mb-0 small">{{ getVerificationMessage() }}</p>
                  </div>
                </div>
                <div
                  class="alert alert-info mt-3"
                  v-if="localDashboardData.verification_status === 'Pending'"
                >
                  <i class="bi bi-info-circle-fill me-2"></i>
                  Your verification is pending review. You'll receive a notification once it's
                  approved.
                </div>
                <div
                  class="alert alert-success mt-3"
                  v-else-if="localDashboardData.verification_status === 'Verified'"
                >
                  <i class="bi bi-check-circle-fill me-2"></i>
                  Your account is verified. You're all set to accept service requests.
                </div>
                <div class="alert alert-warning mt-3" v-else>
                  <i class="bi bi-exclamation-triangle-fill me-2"></i>
                  Please update your verification documents from your profile page.
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
import { defineComponent, ref, reactive, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  BarElement,
  BarController,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { formatDateTime } from '@/utils/date'
// Register the Chart.js components we need
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  BarElement,
  BarController,
  Title,
  Tooltip,
  Legend,
  Filler,
)
export default defineComponent({
  name: 'ProfessionalDashboard',
  setup() {
    const store = useStore()
    // State
    const localDashboardData = ref({})
    const isLoading = ref(true)
    const selectedPeriod = ref('all')
    const showHourlyPattern = ref(false)
    // Chart instances
    const charts = reactive({
      weeklyTrend: null,
      monthlyRatings: null,
      activityPatterns: null,
      ratingDistribution: null,
    })
    // Available time periods
    const periods = [
      // { value: '7d', label: '7 Days' },
      // { value: '30d', label: '30 Days' },
      // { value: '90d', label: '90 Days' },
      // { value: 'all', label: 'All Time' },
    ]
    // Methods
    const fetchDashboardData = async () => {
      isLoading.value = true
      try {
        const params = { period: selectedPeriod.value }
        const response = await store.dispatch('professionals/getDashboard', { params })
        // Create a deep clone of the data to avoid Vuex state mutations
        if (response && response.data) {
          localDashboardData.value = JSON.parse(JSON.stringify(response.data || {}))
        } else {
          localDashboardData.value = {}
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        window.showToast({
          type: 'danger',
          title: 'Failed to load dashboard data',
        })
      } finally {
        isLoading.value = false
      }
    }
    const changePeriod = (period) => {
      selectedPeriod.value = period
      fetchDashboardData()
    }
    const getCompletionRate = () => {
      if (!localDashboardData.value || !localDashboardData.value.total_requests) return 0
      return Math.round(
        (localDashboardData.value.completed_requests / localDashboardData.value.total_requests) *
          100,
      )
    }
    const getVerificationStatusClass = () => {
      const status = localDashboardData.value?.verification_status
      if (status === 'Verified') return 'bg-success text-white'
      if (status === 'Pending') return 'bg-warning text-dark'
      return 'bg-danger text-white'
    }
    const getVerificationStatusIcon = () => {
      const status = localDashboardData.value?.verification_status
      if (status === 'Verified') return 'bi-check-lg'
      if (status === 'Pending') return 'bi-hourglass-split'
      return 'bi-x-lg'
    }
    const getVerificationMessage = () => {
      const status = localDashboardData.value?.verification_status
      if (status === 'Verified') return 'Your account is fully verified'
      if (status === 'Pending') return 'Awaiting admin verification'
      return 'Verification required'
    }
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
    // Chart rendering functions
    const renderWeeklyTrendChart = () => {
      const ctx = document.getElementById('weeklyTrendChart')
      if (!ctx) return

      const weeklyData = JSON.parse(JSON.stringify(localDashboardData.value.weekly_trend || []))
      if (charts.weeklyTrend) {
        charts.weeklyTrend.destroy()
      }
      charts.weeklyTrend = new Chart(ctx, {
        type: 'line',
        data: {
          labels: weeklyData.map((item) => item.period),
          datasets: [
            {
              label: 'Completed Requests',
              data: weeklyData.map((item) => item.completed),
              borderColor: '#0d6efd',
              backgroundColor: 'rgba(13, 110, 253, 0.1)',
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
              display: false,
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
    const renderMonthlyRatingsChart = () => {
      const ctx = document.getElementById('monthlyRatingsChart')
      if (!ctx) return

      const monthlyData = JSON.parse(JSON.stringify(localDashboardData.value.monthly_ratings || []))
      if (charts.monthlyRatings) {
        charts.monthlyRatings.destroy()
      }
      charts.monthlyRatings = new Chart(ctx, {
        type: 'line',
        data: {
          labels: monthlyData.map((item) => item.month),
          datasets: [
            {
              label: 'Average Rating',
              data: monthlyData.map((item) => item.rating),
              borderColor: '#ffc107',
              backgroundColor: 'rgba(255, 193, 7, 0.1)',
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
              display: false,
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `Rating: ${context.parsed.y.toFixed(1)}`
                },
              },
            },
          },
          scales: {
            y: {
              beginAtZero: false,
              min: 0,
              max: 5,
              grid: {
                drawBorder: false,
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
    const renderActivityPatternsChart = () => {
      const ctx = document.getElementById('activityPatternsChart')
      if (!ctx) return

      const patterns = JSON.parse(JSON.stringify(localDashboardData.value.activity_patterns || {}))
      const data = showHourlyPattern.value
        ? patterns.busiest_hours || []
        : patterns.busiest_days || []
      if (charts.activityPatterns) {
        charts.activityPatterns.destroy()
      }
      charts.activityPatterns = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map((item) => (showHourlyPattern.value ? item.hour : item.day)),
          datasets: [
            {
              label: 'Service Requests',
              data: data.map((item) => item.count),
              backgroundColor: 'rgba(111, 66, 193, 0.7)',
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
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `Requests: ${context.parsed.y} (${data[context.dataIndex].percentage}%)`
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
    const renderRatingDistributionChart = () => {
      const ctx = document.getElementById('ratingDistributionChart')
      if (!ctx) return

      const satisfaction = JSON.parse(
        JSON.stringify(localDashboardData.value.satisfaction_analysis || {}),
      )
      const distributionData = satisfaction.rating_distribution || [
        { rating: 5, count: 0, percentage: 0 },
        { rating: 4, count: 0, percentage: 0 },
        { rating: 3, count: 0, percentage: 0 },
        { rating: 2, count: 0, percentage: 0 },
        { rating: 1, count: 0, percentage: 0 },
      ]
      // Sort by rating for consistent display
      distributionData.sort((a, b) => b.rating - a.rating)
      if (charts.ratingDistribution) {
        charts.ratingDistribution.destroy()
      }
      const colors = [
        'rgba(25, 135, 84, 0.7)', // 5 stars - green
        'rgba(13, 202, 240, 0.7)', // 4 stars - info
        'rgba(255, 193, 7, 0.7)', // 3 stars - yellow
        'rgba(255, 153, 0, 0.7)', // 2 stars - orange
        'rgba(220, 53, 69, 0.7)', // 1 star - red
      ]
      charts.ratingDistribution = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: distributionData.map(
            (item) => `${item.rating} Star${item.rating !== 1 ? 's' : ''}`,
          ),
          datasets: [
            {
              label: 'Reviews',
              data: distributionData.map((item) => item.count),
              backgroundColor: colors,
              borderColor: colors.map((color) => color.replace('0.7', '1')),
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `Reviews: ${context.parsed.x} (${distributionData[context.dataIndex].percentage}%)`
                },
              },
            },
          },
          scales: {
            x: {
              beginAtZero: true,
              grid: {
                drawBorder: false,
              },
              ticks: {
                precision: 0,
              },
            },
            y: {
              grid: {
                display: false,
              },
            },
          },
        },
      })
    }
    // Set up watchers
    watch(
      () => showHourlyPattern.value,
      () => {
        renderActivityPatternsChart()
      },
    )
    // Lifecycle hooks
    onMounted(async () => {
      await fetchDashboardData()
      // Give the DOM time to update before rendering charts
      setTimeout(() => {
        renderWeeklyTrendChart()
        renderMonthlyRatingsChart()
        renderActivityPatternsChart()
        renderRatingDistributionChart()
      }, 100)
    })
    return {
      localDashboardData,
      isLoading,
      selectedPeriod,
      periods,
      showHourlyPattern,
      changePeriod,
      getCompletionRate,
      getVerificationStatusClass,
      getVerificationStatusIcon,
      getVerificationMessage,
      truncateText,
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
.service-type-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}
.status-indicator {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
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
  .form-switch {
    margin-top: 0.5rem;
  }
}
</style>
