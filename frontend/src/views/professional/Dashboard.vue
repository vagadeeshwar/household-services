<template>
  <div class="container py-4">
    <div class="row g-4">
      <!-- Welcome Section -->
      <div class="col-12">
        <div class="card shadow-sm border-0 bg-primary bg-gradient text-white">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h2 class="mb-1">Welcome back, {{ userName }}!</h2>
                <p class="mb-0 opacity-75" v-if="profileStatus">
                  <span v-if="profileStatus.is_verified && profileStatus.is_active">
                    <i class="bi bi-check-circle-fill me-1"></i> Your account is verified and active
                  </span>
                  <span v-else-if="!profileStatus.is_verified" class="text-warning">
                    <i class="bi bi-exclamation-triangle-fill me-1"></i> Your account is pending
                    verification
                  </span>
                  <span v-else-if="!profileStatus.is_active" class="text-warning">
                    <i class="bi bi-exclamation-triangle-fill me-1"></i> Your account is inactive
                  </span>
                </p>
              </div>
              <div class="d-none d-md-block">
                <div class="text-end">
                  <p class="mb-0">{{ currentDate }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <template v-if="isLoading">
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading dashboard data...</p>
        </div>
      </template>

      <!-- Error State -->
      <template v-else-if="error">
        <div class="col-12">
          <div class="alert alert-danger d-flex align-items-center" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <div>{{ error }}</div>
          </div>
          <div class="text-center mt-3">
            <button @click="fetchDashboardData" class="btn btn-primary">Try Again</button>
          </div>
        </div>
      </template>

      <!-- Dashboard Content -->
      <template v-else>
        <!-- Stats Cards -->
        <div class="col-12">
          <div class="row g-3">
            <!-- Rating Card -->
            <div class="col-md-3 col-sm-6">
              <div class="card shadow-sm h-100">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="card-title mb-0 text-muted">Average Rating</h6>
                    <i class="bi bi-star-fill text-warning fs-4"></i>
                  </div>
                  <h2 class="mb-0">{{ profileStatus?.average_rating.toFixed(1) || '0.0' }}</h2>
                  <div
                    class="text-success small d-flex align-items-center mt-2"
                    v-if="profileStatus?.average_rating > 4"
                  >
                    <i class="bi bi-arrow-up-short"></i> Excellent
                  </div>
                  <div
                    class="text-warning small d-flex align-items-center mt-2"
                    v-else-if="profileStatus?.average_rating > 3"
                  >
                    <i class="bi bi-arrow-right-short"></i> Good
                  </div>
                  <div
                    class="text-danger small d-flex align-items-center mt-2"
                    v-else-if="profileStatus?.average_rating > 0"
                  >
                    <i class="bi bi-arrow-down-short"></i> Needs Improvement
                  </div>
                  <div class="text-muted small mt-2" v-else>No ratings yet</div>
                </div>
              </div>
            </div>

            <!-- Total Requests Card -->
            <div class="col-md-3 col-sm-6">
              <div class="card shadow-sm h-100">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="card-title mb-0 text-muted">Total Requests</h6>
                    <i class="bi bi-list-check text-primary fs-4"></i>
                  </div>
                  <h2 class="mb-0">{{ requestsData.total || '0' }}</h2>
                  <div class="text-muted small mt-2">All time service requests</div>
                </div>
              </div>
            </div>

            <!-- Active Requests Card -->
            <div class="col-md-3 col-sm-6">
              <div class="card shadow-sm h-100">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="card-title mb-0 text-muted">Active Jobs</h6>
                    <i class="bi bi-arrow-repeat text-info fs-4"></i>
                  </div>
                  <h2 class="mb-0">{{ requestsData.active || '0' }}</h2>
                  <div class="text-muted small mt-2">Ongoing services</div>
                </div>
              </div>
            </div>

            <!-- Completed Requests Card -->
            <div class="col-md-3 col-sm-6">
              <div class="card shadow-sm h-100">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="card-title mb-0 text-muted">Completed Jobs</h6>
                    <i class="bi bi-check-circle text-success fs-4"></i>
                  </div>
                  <h2 class="mb-0">{{ requestsData.completed || '0' }}</h2>
                  <div class="text-muted small mt-2">Successfully completed</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Service Requests -->
        <div class="col-md-8">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-white py-3">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0">Upcoming Services</h5>
                <router-link
                  to="/professional/requests?type=ongoing"
                  class="btn btn-sm btn-outline-primary"
                >
                  View All
                </router-link>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="list-group list-group-flush">
                <div v-if="upcomingRequests.length === 0" class="text-center py-4 text-muted">
                  <i class="bi bi-calendar-x fs-3 mb-2"></i>
                  <p class="mb-0">No upcoming services</p>
                  <p class="small">Browse available service requests to find work</p>
                  <router-link
                    to="/professional/requests?type=new"
                    class="btn btn-sm btn-outline-primary mt-2"
                  >
                    Browse Requests
                  </router-link>
                </div>
                <div v-for="request in upcomingRequests" :key="request.id" class="list-group-item">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 class="mb-1">{{ request.service.name }}</h6>
                      <p class="mb-1 text-muted small">
                        <i class="bi bi-geo-alt me-1"></i>
                        {{ request.customer.user.address }}
                      </p>
                      <div class="d-flex align-items-center">
                        <span class="badge bg-primary me-2">
                          <i class="bi bi-clock me-1"></i>
                          {{ formatDate(request.preferred_time) }}
                        </span>
                        <span class="badge bg-secondary">
                          <i class="bi bi-hourglass-split me-1"></i>
                          {{ formatDuration(request.service.estimated_time) }}
                        </span>
                      </div>
                    </div>
                    <div>
                      <router-link
                        :to="`/professional/requests/${request.id}`"
                        class="btn btn-sm btn-outline-primary"
                      >
                        Details
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Reviews -->
        <div class="col-md-4">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-white py-3">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0">Recent Reviews</h5>
                <router-link to="/professional/reviews" class="btn btn-sm btn-outline-primary">
                  View All
                </router-link>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="list-group list-group-flush">
                <div v-if="recentReviews.length === 0" class="text-center py-4 text-muted">
                  <i class="bi bi-star fs-3 mb-2"></i>
                  <p class="mb-0">No reviews yet</p>
                  <p class="small">Complete services to receive reviews</p>
                </div>
                <div v-for="review in recentReviews" :key="review.id" class="list-group-item">
                  <div class="d-flex align-items-center mb-2">
                    <div class="bg-light rounded-circle p-2 me-2">
                      <i class="bi bi-person text-primary"></i>
                    </div>
                    <div>
                      <h6 class="mb-0">{{ review.service_request.customer.user.full_name }}</h6>
                      <p class="mb-0 text-muted small">
                        {{ formatDate(review.created_at) }}
                      </p>
                    </div>
                  </div>
                  <div class="mb-2">
                    <span v-for="i in 5" :key="i" class="text-warning">
                      <i :class="['bi', i <= review.rating ? 'bi-star-fill' : 'bi-star']"></i>
                    </span>
                  </div>
                  <p class="small mb-0" v-if="review.comment">{{ review.comment }}</p>
                  <p class="small text-muted fst-italic mb-0" v-else>No comment provided</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-header bg-white py-3">
              <h5 class="card-title mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-3 col-sm-6">
                  <router-link
                    to="/professional/requests?type=new"
                    class="card h-100 bg-light text-center text-decoration-none"
                  >
                    <div class="card-body py-4">
                      <i class="bi bi-search-heart text-primary fs-3 mb-3"></i>
                      <h6 class="card-title mb-0">Find Work</h6>
                      <p class="small text-muted mb-0">Browse available requests</p>
                    </div>
                  </router-link>
                </div>
                
                <div class="col-md-3 col-sm-6">
                  <router-link
                    to="/professional/reviews"
                    class="card h-100 bg-light text-center text-decoration-none"
                  >
                    <div class="card-body py-4">
                      <i class="bi bi-star-half text-warning fs-3 mb-3"></i>
                      <h6 class="card-title mb-0">My Reviews</h6>
                      <p class="small text-muted mb-0">See what customers say</p>
                    </div>
                  </router-link>
                </div>
                <div class="col-md-3 col-sm-6">
                  <router-link
                    to="/professional/profile"
                    class="card h-100 bg-light text-center text-decoration-none"
                  >
                    <div class="card-body py-4">
                      <i class="bi bi-person-badge text-info fs-3 mb-3"></i>
                      <h6 class="card-title mb-0">My Profile</h6>
                      <p class="small text-muted mb-0">Update your information</p>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from 'vuex'
import moment from 'moment'

export default {
  name: 'ProfessionalDashboard',
  setup() {
    const store = useStore()

    // State
    const isLoading = ref(true)
    const error = ref(null)
    const dashboardData = ref(null)
    const upcomingRequests = ref([])
    const recentReviews = ref([])
    const refreshInterval = ref(null)

    // Computed properties
    const userName = computed(() => store.getters['auth/userName'] || 'Professional')
    const currentDate = computed(() => moment().format('dddd, MMMM D, YYYY'))

    const profileStatus = computed(() => {
      if (!dashboardData.value) return null
      return dashboardData.value.profile_status
    })

    const requestsData = computed(() => {
      if (!dashboardData.value) return { total: 0, active: 0, completed: 0 }
      return dashboardData.value.service_requests
    })

    // Methods
    const fetchDashboardData = async () => {
      isLoading.value = true
      error.value = null

      try {
        // Fetch dashboard overview data
        const response = await store.dispatch('professionals/fetchDashboard')
        dashboardData.value = response

        // Fetch upcoming requests (ongoing)
        const requestsResponse = await store.dispatch('requests/fetchProfessionalRequests', {
          type: 'ongoing',
          page: 1,
          perPage: 5,
        })
        upcomingRequests.value = requestsResponse.data

        // Fetch recent reviews
        const reviewsResponse = await store.dispatch('professionals/fetchReviews', {
          page: 1,
          perPage: 3,
        })
        recentReviews.value = reviewsResponse.data
      } catch (err) {
        error.value = 'Failed to load dashboard data. Please try again.'
        console.error('Dashboard error:', err)
      } finally {
        isLoading.value = false
      }
    }

    const formatDate = (dateString) => {
      const date = moment(dateString)
      // If today, show time only
      if (date.isSame(moment(), 'day')) {
        return `Today at ${date.format('h:mm A')}`
      }
      // If tomorrow, show "Tomorrow"
      if (date.isSame(moment().add(1, 'day'), 'day')) {
        return `Tomorrow at ${date.format('h:mm A')}`
      }
      // Otherwise show date and time
      return date.format('MMM D [at] h:mm A')
    }

    const formatDuration = (minutes) => {
      if (minutes < 60) {
        return `${minutes}m`
      }
      const hrs = Math.floor(minutes / 60)
      const mins = minutes % 60
      return mins > 0 ? `${hrs}h ${mins}m` : `${hrs}h`
    }

    // Setup automatic refresh every 5 minutes
    const setupRefreshInterval = () => {
      refreshInterval.value = setInterval(() => {
        fetchDashboardData()
      }, 300000) // 5 minutes
    }

    // Lifecycle hooks
    onMounted(() => {
      fetchDashboardData()
      setupRefreshInterval()
    })

    onBeforeUnmount(() => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
    })

    return {
      isLoading,
      error,
      dashboardData,
      upcomingRequests,
      recentReviews,
      userName,
      currentDate,
      profileStatus,
      requestsData,
      fetchDashboardData,
      formatDate,
      formatDuration,
    }
  },
}
</script>

<style scoped>
.card {
  transition:
    transform 0.2s ease-in-out,
    box-shadow 0.2s ease-in-out;
  border-radius: 0.5rem;
  overflow: hidden;
}

a.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.list-group-item {
  padding: 1rem;
  border-left: none;
  border-right: none;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}

.badge {
  font-weight: normal;
  padding: 0.35em 0.65em;
}

.bg-gradient {
  background-image: linear-gradient(135deg, #0d6efd, #0a58ca);
}
</style>
