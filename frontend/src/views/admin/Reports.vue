<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">Reports & Analytics</h1>
      <div class="btn-group">
        <button class="btn btn-outline-primary" @click="refreshData">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
        <button class="btn btn-outline-success" @click="showExportModal">
          <i class="bi bi-file-earmark-arrow-down me-1"></i>Export
        </button>
      </div>
    </div>

    <!-- Report Navigation Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'activity' }"
          @click="activeTab = 'activity'"
        >
          <i class="bi bi-activity me-1"></i>
          Activity Logs
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'professionals' }"
          @click="activeTab = 'professionals'"
        >
          <i class="bi bi-person-badge me-1"></i>
          Professionals
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'requests' }"
          @click="activeTab = 'requests'"
        >
          <i class="bi bi-list-check me-1"></i>
          Service Requests
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'reviews' }"
          @click="activeTab = 'reviews'"
        >
          <i class="bi bi-star me-1"></i>
          Reviews
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'exports' }"
          @click="activeTab = 'exports'"
        >
          <i class="bi bi-file-earmark-arrow-down me-1"></i>
          Export History
        </button>
      </li>
    </ul>

    <!-- Activity Logs Tab Content -->
    <div v-if="activeTab === 'activity'" class="card shadow-sm">
      <div class="card-header bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-5">
            <h5 class="mb-0">Activity Logs</h5>
          </div>
          <div class="col-md-7">
            <div class="d-flex justify-content-md-end gap-2">
              <!-- Action Filter -->
              <select
                class="form-select form-select-sm"
                v-model="activityFilters.action"
                @change="fetchActivityLogs"
              >
                <option value="">All Actions</option>
                <option v-for="action in actionTypes" :key="action.value" :value="action.value">
                  {{ action.label }}
                </option>
              </select>

              <!-- Date Range Filter -->
              <div class="d-flex align-items-center">
                <input
                  type="date"
                  class="form-control form-control-sm"
                  v-model="activityFilters.startDate"
                  @change="fetchActivityLogs"
                />
                <span class="mx-1">to</span>
                <input
                  type="date"
                  class="form-control form-control-sm"
                  v-model="activityFilters.endDate"
                  @change="fetchActivityLogs"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading activity logs...</p>
      </div>

      <div v-else-if="activityLogs.length === 0" class="text-center py-5">
        <i class="bi bi-info-circle fs-2 text-muted"></i>
        <p class="mt-2 text-muted">No activity logs found for the selected filters</p>
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th scope="col">Timestamp</th>
              <th scope="col">User</th>
              <th scope="col">Action</th>
              <th scope="col">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in activityLogs" :key="log.id">
              <td class="text-nowrap">{{ formatDate(log.created_at) }}</td>
              <td>
                <div v-if="log.user_id">{{ log.user_name || 'User #' + log.user_id }}</div>
                <div v-else class="text-muted">System</div>
              </td>
              <td>
                <span :class="['badge', getActionBadgeClass(log.action)]">
                  {{ formatActionType(log.action) }}
                </span>
              </td>
              <td>{{ log.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="card-footer bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-6 text-muted">
            Showing {{ activityLogs.length }} of {{ activityPagination.total || 0 }} logs
          </div>
          <div class="col-md-6">
            <ul class="pagination pagination-sm mb-0 justify-content-md-end">
              <li class="page-item" :class="{ disabled: activityFilters.page === 1 }">
                <button @click="changePage(activityFilters.page - 1, 'activity')" class="page-link">
                  Previous
                </button>
              </li>
              <li
                v-for="pageNum in getDisplayedPages(activityFilters.page, activityPagination.pages)"
                :key="pageNum"
                class="page-item"
                :class="{ active: activityFilters.page === pageNum }"
              >
                <button @click="changePage(pageNum, 'activity')" class="page-link">
                  {{ pageNum }}
                </button>
              </li>
              <li
                class="page-item"
                :class="{ disabled: activityFilters.page === activityPagination.pages }"
              >
                <button @click="changePage(activityFilters.page + 1, 'activity')" class="page-link">
                  Next
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Professionals Tab Content -->
    <div v-if="activeTab === 'professionals'" class="card shadow-sm">
      <div class="card-header bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h5 class="mb-0">Professional Analytics</h5>
          </div>
          <div class="col-md-6">
            <div class="d-flex justify-content-md-end gap-2">
              <!-- Service Type Filter -->
              <select
                class="form-select form-select-sm"
                v-model="proFilters.serviceType"
                @change="fetchProfessionalStats"
              >
                <option value="">All Services</option>
                <option v-for="service in services" :key="service.id" :value="service.id">
                  {{ service.name }}
                </option>
              </select>

              <!-- Rating Filter -->
              <select
                class="form-select form-select-sm"
                v-model="proFilters.rating"
                @change="fetchProfessionalStats"
              >
                <option value="">All Ratings</option>
                <option value="5">5 Stars</option>
                <option value="4">4+ Stars</option>
                <option value="3">3+ Stars</option>
                <option value="2">2+ Stars</option>
                <option value="1">1+ Star</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading professional analytics...</p>
      </div>

      <div v-else class="card-body">
        <div class="row g-4">
          <!-- Professional Performance Chart -->
          <div class="col-12">
            <div class="card border shadow-sm">
              <div class="card-header bg-light">
                <h6 class="mb-0">Professional Performance Overview</h6>
              </div>
              <div class="card-body">
                <div class="row g-4">
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100">
                      <div class="text-muted small mb-1">Total Professionals</div>
                      <div class="h4 mb-0">{{ profStats.total || 0 }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100">
                      <div class="text-muted small mb-1">Verified</div>
                      <div class="h4 mb-0">{{ profStats.verified || 0 }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100">
                      <div class="text-muted small mb-1">Avg Rating</div>
                      <div class="h4 mb-0">{{ profStats.avg_rating?.toFixed(1) || 'N/A' }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100">
                      <div class="text-muted small mb-1">Avg Experience</div>
                      <div class="h4 mb-0">
                        {{ profStats.avg_experience?.toFixed(1) || 'N/A' }} yrs
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Chart placeholder - In a real app, you'd implement a proper chart here -->
                <div
                  class="mt-4 border rounded p-3 bg-light"
                  style="height: 250px; display: flex; align-items: center; justify-content: center"
                >
                  <div class="text-center text-muted">
                    <i class="bi bi-bar-chart-line fs-1 mb-2"></i>
                    <p>Professional performance chart would be displayed here</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Top Professionals Table -->
          <div class="col-12">
            <div class="card border shadow-sm">
              <div class="card-header bg-light">
                <h6 class="mb-0">Top Professionals</h6>
              </div>
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light">
                    <tr>
                      <th scope="col">Name</th>
                      <th scope="col">Service</th>
                      <th scope="col">Experience</th>
                      <th scope="col">Rating</th>
                      <th scope="col">Completed Jobs</th>
                      <th scope="col">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="topProfessionals.length === 0">
                      <td colspan="6" class="text-center py-4 text-muted">
                        No professionals data available
                      </td>
                    </tr>
                    <tr v-for="pro in topProfessionals" :key="pro.id">
                      <td>{{ pro.name }}</td>
                      <td>{{ pro.service }}</td>
                      <td>{{ pro.experience }} years</td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="stars me-2">
                            <i
                              v-for="i in 5"
                              :key="i"
                              class="bi"
                              :class="
                                i <= Math.round(pro.rating || 0)
                                  ? 'bi-star-fill text-warning'
                                  : 'bi-star'
                              "
                            ></i>
                          </div>
                          <span>{{ pro.rating.toFixed(1) }}</span>
                        </div>
                      </td>
                      <td>{{ pro.completed_jobs }}</td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary">
                          <i class="bi bi-eye"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Requests Tab Content -->
    <div v-if="activeTab === 'requests'" class="card shadow-sm">
      <div class="card-header bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-5">
            <h5 class="mb-0">Service Request Analytics</h5>
          </div>
          <div class="col-md-7">
            <div class="d-flex justify-content-md-end gap-2">
              <!-- Service Type Filter -->
              <select
                class="form-select form-select-sm"
                v-model="requestFilters.serviceType"
                @change="fetchRequestStats"
              >
                <option value="">All Services</option>
                <option v-for="service in services" :key="service.id" :value="service.id">
                  {{ service.name }}
                </option>
              </select>

              <!-- Status Filter -->
              <select
                class="form-select form-select-sm"
                v-model="requestFilters.status"
                @change="fetchRequestStats"
              >
                <option value="">All Statuses</option>
                <option value="created">Created</option>
                <option value="assigned">Assigned</option>
                <option value="completed">Completed</option>
              </select>

              <!-- Date Range Filter -->
              <select
                class="form-select form-select-sm"
                v-model="requestFilters.dateRange"
                @change="fetchRequestStats"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading service request analytics...</p>
      </div>

      <div v-else class="card-body">
        <div class="row g-4">
          <!-- Service Request Stats -->
          <div class="col-12">
            <div class="card border shadow-sm">
              <div class="card-header bg-light">
                <h6 class="mb-0">Service Request Overview</h6>
              </div>
              <div class="card-body">
                <div class="row g-4">
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100">
                      <div class="text-muted small mb-1">Total Requests</div>
                      <div class="h4 mb-0">{{ requestStats.total || 0 }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100 bg-info bg-opacity-10">
                      <div class="text-muted small mb-1">Pending</div>
                      <div class="h4 mb-0">{{ requestStats.pending || 0 }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100 bg-warning bg-opacity-10">
                      <div class="text-muted small mb-1">In Progress</div>
                      <div class="h4 mb-0">{{ requestStats.assigned || 0 }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100 bg-success bg-opacity-10">
                      <div class="text-muted small mb-1">Completed</div>
                      <div class="h4 mb-0">{{ requestStats.completed || 0 }}</div>
                    </div>
                  </div>
                </div>

                <!-- Chart placeholder - In a real app, you'd implement a proper chart here -->
                <div
                  class="mt-4 border rounded p-3 bg-light"
                  style="height: 250px; display: flex; align-items: center; justify-content: center"
                >
                  <div class="text-center text-muted">
                    <i class="bi bi-bar-chart-line fs-1 mb-2"></i>
                    <p>Service request trend chart would be displayed here</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Popular Services Table -->
          <div class="col-12">
            <div class="card border shadow-sm">
              <div class="card-header bg-light">
                <h6 class="mb-0">Popular Services</h6>
              </div>
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light">
                    <tr>
                      <th scope="col">Service</th>
                      <th scope="col">Total Requests</th>
                      <th scope="col">Completed</th>
                      <th scope="col">Average Rating</th>
                      <th scope="col">Average Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="popularServices.length === 0">
                      <td colspan="5" class="text-center py-4 text-muted">
                        No service request data available
                      </td>
                    </tr>
                    <tr v-for="service in popularServices" :key="service.id">
                      <td>{{ service.name }}</td>
                      <td>{{ service.total_requests }}</td>
                      <td>{{ service.completed_requests }}</td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="stars me-2">
                            <i
                              v-for="i in 5"
                              :key="i"
                              class="bi"
                              :class="
                                i <= Math.round(service.avg_rating || 0)
                                  ? 'bi-star-fill text-warning'
                                  : 'bi-star'
                              "
                            ></i>
                          </div>
                          <span>{{ service.avg_rating?.toFixed(1) || 'N/A' }}</span>
                        </div>
                      </td>
                      <td>₹{{ service.avg_price?.toFixed(2) || 'N/A' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reviews Tab Content -->
    <div v-if="activeTab === 'reviews'" class="card shadow-sm">
      <div class="card-header bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h5 class="mb-0">Reviews Analysis</h5>
          </div>
          <div class="col-md-6">
            <div class="d-flex justify-content-md-end gap-2">
              <!-- Service Type Filter -->
              <select
                class="form-select form-select-sm"
                v-model="reviewFilters.serviceType"
                @change="fetchReviewStats"
              >
                <option value="">All Services</option>
                <option v-for="service in services" :key="service.id" :value="service.id">
                  {{ service.name }}
                </option>
              </select>

              <!-- Rating Filter -->
              <select
                class="form-select form-select-sm"
                v-model="reviewFilters.rating"
                @change="fetchReviewStats"
              >
                <option value="">All Ratings</option>
                <option value="5">5 Stars</option>
                <option value="4">4 Stars</option>
                <option value="3">3 Stars</option>
                <option value="2">2 Stars</option>
                <option value="1">1 Star</option>
              </select>

              <!-- Reported Filter -->
              <select
                class="form-select form-select-sm"
                v-model="reviewFilters.reported"
                @change="fetchReviewStats"
              >
                <option :value="null">All Reviews</option>
                <option :value="true">Reported Only</option>
                <option :value="false">Not Reported</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading reviews analytics...</p>
      </div>

      <div v-else class="card-body">
        <div class="row g-4">
          <!-- Reviews Stats -->
          <div class="col-12">
            <div class="card border shadow-sm">
              <div class="card-header bg-light">
                <h6 class="mb-0">Reviews Overview</h6>
              </div>
              <div class="card-body">
                <div class="row g-4">
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100">
                      <div class="text-muted small mb-1">Total Reviews</div>
                      <div class="h4 mb-0">{{ reviewStats.total || 0 }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100">
                      <div class="text-muted small mb-1">Average Rating</div>
                      <div class="h4 mb-0">{{ reviewStats.avg_rating?.toFixed(1) || 'N/A' }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100">
                      <div class="text-muted small mb-1">5 Star Reviews</div>
                      <div class="h4 mb-0">{{ reviewStats.five_star || 0 }}</div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border rounded p-3 text-center h-100 bg-danger bg-opacity-10">
                      <div class="text-muted small mb-1">Reported Reviews</div>
                      <div class="h4 mb-0">{{ reviewStats.reported || 0 }}</div>
                    </div>
                  </div>
                </div>

                <!-- Rating Distribution placeholder - In a real app, you'd implement a proper chart here -->
                <div
                  class="mt-4 border rounded p-3 bg-light"
                  style="height: 200px; display: flex; align-items: center; justify-content: center"
                >
                  <div class="text-center text-muted">
                    <i class="bi bi-bar-chart-line fs-1 mb-2"></i>
                    <p>Rating distribution chart would be displayed here</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Reviews Table -->
          <div class="col-12">
            <div class="card border shadow-sm">
              <div class="card-header bg-light d-flex justify-content-between align-items-center">
                <h6 class="mb-0">Recent Reviews</h6>
                <button v-if="reviewFilters.reported" class="btn btn-sm btn-outline-danger">
                  <i class="bi bi-flag-fill me-1"></i>
                  Handle Reported Reviews
                </button>
              </div>
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light">
                    <tr>
                      <th scope="col">Date</th>
                      <th scope="col">Service</th>
                      <th scope="col">Professional</th>
                      <th scope="col">Customer</th>
                      <th scope="col">Rating</th>
                      <th scope="col">Status</th>
                      <th scope="col">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="recentReviews.length === 0">
                      <td colspan="7" class="text-center py-4 text-muted">
                        No reviews data available
                      </td>
                    </tr>
                    <tr v-for="review in recentReviews" :key="review.id">
                      <td>{{ formatDate(review.created_at) }}</td>
                      <td>{{ review.service_name }}</td>
                      <td>{{ review.professional_name }}</td>
                      <td>{{ review.customer_name }}</td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="stars me-2">
                            <i
                              v-for="i in 5"
                              :key="i"
                              class="bi"
                              :class="i <= review.rating ? 'bi-star-fill text-warning' : 'bi-star'"
                            ></i>
                          </div>
                          <span>{{ review.rating }}</span>
                        </div>
                      </td>
                      <td>
                        <span v-if="review.is_reported" class="badge bg-danger">Reported</span>
                        <span v-else class="badge bg-success">Active</span>
                      </td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary me-1">
                          <i class="bi bi-eye"></i>
                        </button>
                        <button v-if="review.is_reported" class="btn btn-sm btn-outline-danger">
                          <i class="bi bi-flag-fill"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!-- Pagination -->
              <div class="card-footer bg-white py-3">
                <div class="row align-items-center">
                  <div class="col-md-6 text-muted">
                    Showing {{ recentReviews.length }} of {{ reviewPagination.total || 0 }} reviews
                  </div>
                  <div class="col-md-6">
                    <ul class="pagination pagination-sm mb-0 justify-content-md-end">
                      <li class="page-item" :class="{ disabled: reviewFilters.page === 1 }">
                        <button
                          @click="changePage(reviewFilters.page - 1, 'review')"
                          class="page-link"
                        >
                          Previous
                        </button>
                      </li>
                      <li
                        v-for="pageNum in getDisplayedPages(
                          reviewFilters.page,
                          reviewPagination.pages,
                        )"
                        :key="pageNum"
                        class="page-item"
                        :class="{ active: reviewFilters.page === pageNum }"
                      >
                        <button @click="changePage(pageNum, 'review')" class="page-link">
                          {{ pageNum }}
                        </button>
                      </li>
                      <li
                        class="page-item"
                        :class="{ disabled: reviewFilters.page === reviewPagination.pages }"
                      >
                        <button
                          @click="changePage(reviewFilters.page + 1, 'review')"
                          class="page-link"
                        >
                          Next
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Exports Tab Content -->
    <div v-if="activeTab === 'exports'" class="card shadow-sm">
      <div class="card-header bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h5 class="mb-0">Export History</h5>
          </div>
          <div class="col-md-6 text-md-end">
            <button class="btn btn-success" @click="showExportModal">
              <i class="bi bi-file-earmark-arrow-down me-1"></i>
              New Export
            </button>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading exports...</p>
      </div>

      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th scope="col">Filename</th>
              <th scope="col">Type</th>
              <th scope="col">Created At</th>
              <th scope="col">Records</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="exports.length === 0">
              <td colspan="6" class="text-center py-4 text-muted">
                <i class="bi bi-info-circle me-2"></i>No export history found
              </td>
            </tr>
            <tr v-for="export_item in exports" :key="export_item.id">
              <td>{{ export_item.filename }}</td>
              <td>{{ formatExportType(export_item.type) }}</td>
              <td>{{ formatDate(export_item.created_at) }}</td>
              <td>{{ export_item.total_records }}</td>
              <td>
                <span :class="['badge', getExportStatusBadge(export_item.status)]">
                  {{ formatExportStatus(export_item.status) }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-sm btn-primary me-1"
                  @click="downloadExport(export_item)"
                  :disabled="export_item.status !== 'completed'"
                >
                  <i class="bi bi-download me-1"></i>
                  Download
                </button>
                <button
                  class="btn btn-sm btn-outline-danger"
                  @click="deleteExport(export_item)"
                  :disabled="isActionLoading"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Export Modal -->
    <div class="modal fade" id="exportModal" tabindex="-1" ref="exportModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-file-earmark-arrow-down me-1"></i>
              Export Data
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="generateExport">
              <div class="mb-3">
                <label class="form-label">Export Type</label>
                <select class="form-select" v-model="exportForm.type" required>
                  <option value="service_requests">Service Requests</option>
                  <option value="professional_performance">Professional Performance</option>
                  <option value="customer_activity">Customer Activity</option>
                  <option value="reviews">Reviews</option>
                </select>
              </div>

              <div class="mb-3" v-if="exportForm.type === 'service_requests'">
                <label class="form-label">Professional (Optional)</label>
                <select class="form-select" v-model="exportForm.professionalId">
                  <option value="">All Professionals</option>
                  <option v-for="pro in professionals" :key="pro.id" :value="pro.id">
                    {{ pro.name }}
                  </option>
                </select>
              </div>

              <div class="row g-3 mb-3">
                <div class="col-md-6">
                  <label class="form-label">Start Date</label>
                  <input type="date" class="form-control" v-model="exportForm.startDate" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">End Date</label>
                  <input type="date" class="form-control" v-model="exportForm.endDate" />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Format</label>
                <select class="form-select" v-model="exportForm.format" required>
                  <option value="csv">CSV</option>
                  <option value="excel">Excel</option>
                </select>
              </div>

              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="isExporting">
                  <span v-if="isExporting" class="spinner-border spinner-border-sm me-2"></span>
                  Generate Export
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Progress Modal -->
    <div
      class="modal fade"
      id="exportProgressModal"
      tabindex="-1"
      data-bs-backdrop="static"
      ref="exportProgressModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-arrow-repeat me-1"></i>
              Export in Progress
            </h5>
          </div>
          <div class="modal-body text-center">
            <div class="spinner-border text-primary mb-3" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p>Your export is being generated...</p>
            <div class="progress mb-3">
              <div
                class="progress-bar progress-bar-striped progress-bar-animated"
                role="progressbar"
                :style="{ width: exportProgress + '%' }"
              ></div>
            </div>
            <p class="small text-muted">
              This may take a few minutes depending on the amount of data.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as bootstrap from 'bootstrap'
import moment from 'moment'
import { onMounted, ref, watch } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'AdminReports',
  setup() {
    const store = useStore()

    // Modal refs
    const exportModal = ref(null)
    const exportProgressModal = ref(null)
    let bsExportModal = null
    let bsExportProgressModal = null

    // State
    const activeTab = ref('activity')
    const isLoading = ref(false)
    const isExporting = ref(false)
    const isActionLoading = ref(false)
    const exportProgress = ref(0)
    const error = ref(null)

    // Services data
    const services = ref([])
    const professionals = ref([])

    // Activity Logs
    const activityLogs = ref([])
    const activityPagination = ref({})
    const activityFilters = ref({
      action: '',
      startDate: '',
      endDate: '',
      page: 1,
      perPage: 10,
    })

    // Professionals Analytics
    const profStats = ref({})
    const topProfessionals = ref([])
    const proFilters = ref({
      serviceType: '',
      rating: '',
    })

    // Service Requests Analytics
    const requestStats = ref({})
    const popularServices = ref([])
    const requestFilters = ref({
      serviceType: '',
      status: '',
      dateRange: 'all',
    })

    // Reviews Analytics
    const reviewStats = ref({})
    const recentReviews = ref([])
    const reviewPagination = ref({})
    const reviewFilters = ref({
      serviceType: '',
      rating: '',
      reported: null,
      page: 1,
      perPage: 10,
    })

    // Exports
    const exports = ref([])
    const exportForm = ref({
      type: 'service_requests',
      professionalId: '',
      startDate: '',
      endDate: '',
      format: 'csv',
    })

    // Action types for activity log filtering
    const actionTypes = [
      { value: 'user_login', label: 'User Login' },
      { value: 'user_register', label: 'User Registration' },
      { value: 'profile_update', label: 'Profile Update' },
      { value: 'professional_verify', label: 'Professional Verification' },
      { value: 'professional_block', label: 'Professional Block' },
      { value: 'professional_unblock', label: 'Professional Unblock' },
      { value: 'customer_block', label: 'Customer Block' },
      { value: 'customer_unblock', label: 'Customer Unblock' },
      { value: 'service_create', label: 'Service Create' },
      { value: 'service_update', label: 'Service Update' },
      { value: 'service_delete', label: 'Service Delete' },
      { value: 'request_create', label: 'Request Create' },
      { value: 'request_assign', label: 'Request Assignment' },
      { value: 'request_complete', label: 'Request Completion' },
      { value: 'review_submit', label: 'Review Submission' },
      { value: 'review_report', label: 'Review Report' },
    ]

    // Watch for tab changes to load appropriate data
    watch(activeTab, (newTab) => {
      loadTabData(newTab)
    })

    // Methods
    const formatDate = (dateString, includeTime = true) => {
      if (!dateString) return 'N/A'
      return includeTime
        ? moment(dateString).format('MMM D, YYYY h:mm A')
        : moment(dateString).format('MMM D, YYYY')
    }

    const formatActionType = (action) => {
      const found = actionTypes.find((a) => a.value === action)
      return found ? found.label : action
    }

    const getActionBadgeClass = (action) => {
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
        review_remove: 'bg-danger',
      }

      return actionTypeMap[action] || 'bg-secondary'
    }

    const formatExportType = (type) => {
      const types = {
        service_requests: 'Service Requests',
        professional_performance: 'Professional Performance',
        customer_activity: 'Customer Activity',
        reviews: 'Reviews',
      }
      return types[type] || type
    }

    const formatExportStatus = (status) => {
      const statuses = {
        pending: 'Pending',
        processing: 'Processing',
        completed: 'Completed',
        failed: 'Failed',
      }
      return statuses[status] || status
    }

    const getExportStatusBadge = (status) => {
      const statusMap = {
        pending: 'bg-secondary',
        processing: 'bg-info',
        completed: 'bg-success',
        failed: 'bg-danger',
      }
      return statusMap[status] || 'bg-secondary'
    }

    const refreshData = () => {
      loadTabData(activeTab.value)
    }

    const loadTabData = async (tabName) => {
      switch (tabName) {
        case 'activity':
          await fetchActivityLogs()
          break
        case 'professionals':
          await fetchProfessionalStats()
          break
        case 'requests':
          await fetchRequestStats()
          break
        case 'reviews':
          await fetchReviewStats()
          break
        case 'exports':
          await fetchExports()
          break
      }
    }

    const showExportModal = () => {
      bsExportModal.show()
    }

    const generateExport = async () => {
      try {
        isExporting.value = true

        // Close the export modal and show the progress modal
        bsExportModal.hide()
        bsExportProgressModal.show()

        // Simulate progress updates (in a real app, this would come from the server)
        exportProgress.value = 0
        const progressInterval = setInterval(() => {
          exportProgress.value += 5
          if (exportProgress.value >= 100) {
            clearInterval(progressInterval)
          }
        }, 300)

        // Generate the export
        const response = await store.dispatch('exports/generateServiceReport', {
          professionalId: exportForm.value.professionalId || undefined,
          startDate: exportForm.value.startDate || undefined,
          endDate: exportForm.value.endDate || undefined,
        })

        // Clear interval and set to 100%
        clearInterval(progressInterval)
        exportProgress.value = 100

        // Close progress modal
        setTimeout(() => {
          bsExportProgressModal.hide()

          // Show success message
          window.showToast({
            type: 'success',
            title: 'Export Generated',
            message: `File ${response.filename} is ready for download`,
          })

          // Switch to exports tab and refresh
          activeTab.value = 'exports'
          fetchExports()
        }, 1000)
      } catch (err) {
        // Handle errors
        window.showToast({
          type: 'error',
          title: 'Export Failed',
          message: err.message || 'Failed to generate export',
        })

        bsExportProgressModal.hide()
      } finally {
        isExporting.value = false
      }
    }

    const downloadExport = async (exportItem) => {
      try {
        isActionLoading.value = true
        await store.dispatch('exports/downloadReport', exportItem.filename)

        window.showToast({
          type: 'success',
          title: 'Download Started',
          message: 'Your file should download shortly',
        })
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Download Failed',
          message: err.message || 'Failed to download file',
        })
      } finally {
        isActionLoading.value = false
      }
    }

    const deleteExport = async (exportItem) => {
      try {
        isActionLoading.value = true
        await store.dispatch('exports/deleteExport', exportItem.id)

        window.showToast({
          type: 'success',
          title: 'Export Deleted',
          message: 'The export file has been deleted',
        })

        fetchExports()
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Delete Failed',
          message: err.message || 'Failed to delete export',
        })
      } finally {
        isActionLoading.value = false
      }
    }

    const getDisplayedPages = (currentPage, totalPages) => {
      const pages = []
      const maxVisiblePages = 5
      let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2))
      let endPage = Math.min(totalPages || 1, startPage + maxVisiblePages - 1)

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1)
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      return pages
    }

    const changePage = (page, type) => {
      if (type === 'activity') {
        if (page < 1 || page > activityPagination.value.pages) return
        activityFilters.value.page = page
        fetchActivityLogs()
      } else if (type === 'review') {
        if (page < 1 || page > reviewPagination.value.pages) return
        reviewFilters.value.page = page
        fetchReviewStats()
      }
    }

    // Data fetching methods
    const fetchActiveServices = async () => {
      try {
        const response = await store.dispatch('services/fetchActiveServices')
        services.value = response.data || []
      } catch (err) {
        console.error('Error fetching services:', err)
      }
    }

    const fetchActivityLogs = async () => {
      isLoading.value = true
      try {
        const response = await store.dispatch('stats/fetchDetailedStats', {
          type: 'pending_verifications',
          page: activityFilters.value.page,
          perPage: activityFilters.value.perPage,
          action: activityFilters.value.action || undefined,
          startDate: activityFilters.value.startDate || undefined,
          endDate: activityFilters.value.endDate || undefined,
        })

        activityLogs.value = response.data || []
        activityPagination.value = response.pagination || {}
      } catch (err) {
        error.value = err.message || 'Failed to load activity logs'
        console.error(err)
      } finally {
        isLoading.value = false
      }
    }

    const fetchProfessionalStats = async () => {
      isLoading.value = true
      try {
        // In a real application, you would fetch this from the API
        // For now, we'll use dummy data

        // Mock data for professional stats
        profStats.value = {
          total: 42,
          verified: 35,
          avg_rating: 4.3,
          avg_experience: 4.8,
        }

        // Mock data for top professionals
        topProfessionals.value = [
          {
            id: 1,
            name: 'John Doe',
            service: 'Plumbing',
            experience: 5,
            rating: 4.8,
            completed_jobs: 87,
          },
          {
            id: 2,
            name: 'Sarah Kim',
            service: 'Electrical Work',
            experience: 7,
            rating: 4.9,
            completed_jobs: 122,
          },
          {
            id: 3,
            name: 'Mike Johnson',
            service: 'AC Repair',
            experience: 4,
            rating: 4.5,
            completed_jobs: 64,
          },
          {
            id: 4,
            name: 'Priya Sharma',
            service: 'House Painting',
            experience: 6,
            rating: 4.7,
            completed_jobs: 52,
          },
          {
            id: 5,
            name: 'David Wilson',
            service: 'Carpentry',
            experience: 8,
            rating: 4.6,
            completed_jobs: 93,
          },
        ]
      } catch (err) {
        error.value = err.message || 'Failed to load professional statistics'
        console.error(err)
      } finally {
        isLoading.value = false
      }
    }

    const fetchRequestStats = async () => {
      isLoading.value = true
      try {
        // Mock data for request stats
        requestStats.value = {
          total: 546,
          pending: 42,
          assigned: 38,
          completed: 466,
        }

        // Mock data for popular services
        popularServices.value = [
          {
            id: 1,
            name: 'Plumbing Service',
            total_requests: 212,
            completed_requests: 198,
            avg_rating: 4.6,
            avg_price: 850.75,
          },
          {
            id: 2,
            name: 'AC Repair & Service',
            total_requests: 187,
            completed_requests: 165,
            avg_rating: 4.4,
            avg_price: 1200.5,
          },
          {
            id: 3,
            name: 'Electrical Work',
            total_requests: 145,
            completed_requests: 132,
            avg_rating: 4.5,
            avg_price: 950.25,
          },
          {
            id: 4,
            name: 'House Painting',
            total_requests: 89,
            completed_requests: 76,
            avg_rating: 4.7,
            avg_price: 3200.0,
          },
          {
            id: 5,
            name: 'Carpentry',
            total_requests: 65,
            completed_requests: 58,
            avg_rating: 4.3,
            avg_price: 1150.5,
          },
        ]
      } catch (err) {
        error.value = err.message || 'Failed to load request statistics'
        console.error(err)
      } finally {
        isLoading.value = false
      }
    }

    const fetchReviewStats = async () => {
      isLoading.value = true
      try {
        // Mock data for review stats
        reviewStats.value = {
          total: 428,
          avg_rating: 4.5,
          five_star: 198,
          reported: 12,
        }

        // Mock data for recent reviews
        recentReviews.value = [
          {
            id: 1,
            created_at: new Date().toISOString(),
            service_name: 'Plumbing Service',
            professional_name: 'John Doe',
            customer_name: 'Alice Smith',
            rating: 5,
            is_reported: false,
          },
          {
            id: 2,
            created_at: new Date(Date.now() - 86400000).toISOString(),
            service_name: 'AC Repair & Service',
            professional_name: 'Mike Johnson',
            customer_name: 'Bob Miller',
            rating: 4,
            is_reported: false,
          },
          {
            id: 3,
            created_at: new Date(Date.now() - 172800000).toISOString(),
            service_name: 'Electrical Work',
            professional_name: 'Sarah Kim',
            customer_name: 'Charlie Davis',
            rating: 2,
            is_reported: true,
          },
          {
            id: 4,
            created_at: new Date(Date.now() - 259200000).toISOString(),
            service_name: 'House Painting',
            professional_name: 'Priya Sharma',
            customer_name: 'Dave Wilson',
            rating: 5,
            is_reported: false,
          },
          {
            id: 5,
            created_at: new Date(Date.now() - 345600000).toISOString(),
            service_name: 'Carpentry',
            professional_name: 'David Wilson',
            customer_name: 'Eve Jackson',
            rating: 3,
            is_reported: false,
          },
        ]

        // Mock pagination data
        reviewPagination.value = {
          total: 428,
          pages: 86,
          page: reviewFilters.value.page,
          perPage: reviewFilters.value.perPage,
        }
      } catch (err) {
        error.value = err.message || 'Failed to load review statistics'
        console.error(err)
      } finally {
        isLoading.value = false
      }
    }

    const fetchExports = async () => {
      isLoading.value = true
      try {
        // In a real application, you would fetch this from the API
        // For now, we'll use dummy data
        exports.value = [
          {
            id: 1,
            filename: 'service_requests_20250302_153012.csv',
            type: 'service_requests',
            created_at: new Date().toISOString(),
            total_records: 548,
            status: 'completed',
          },
          {
            id: 2,
            filename: 'professional_performance_20250301_092534.xlsx',
            type: 'professional_performance',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            total_records: 42,
            status: 'completed',
          },
          {
            id: 3,
            filename: 'reviews_20250228_142213.csv',
            type: 'reviews',
            created_at: new Date(Date.now() - 172800000).toISOString(),
            total_records: 354,
            status: 'completed',
          },
          {
            id: 4,
            filename: 'customer_activity_20250227_183045.xlsx',
            type: 'customer_activity',
            created_at: new Date(Date.now() - 259200000).toISOString(),
            total_records: 128,
            status: 'completed',
          },
        ]
      } catch (err) {
        error.value = err.message || 'Failed to load exports'
        console.error(err)
      } finally {
        isLoading.value = false
      }
    }

    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      if (exportModal.value) {
        bsExportModal = new bootstrap.Modal(exportModal.value)
      }

      if (exportProgressModal.value) {
        bsExportProgressModal = new bootstrap.Modal(exportProgressModal.value)
      }

      // Fetch services for filters
      await fetchActiveServices()

      // Load data for initial tab
      await loadTabData(activeTab.value)
    })

    return {
      // State
      activeTab,
      isLoading,
      isExporting,
      isActionLoading,
      exportProgress,
      error,
      services,
      professionals,

      // Activity logs
      activityLogs,
      activityPagination,
      activityFilters,
      actionTypes,

      // Professional stats
      profStats,
      topProfessionals,
      proFilters,

      // Request stats
      requestStats,
      popularServices,
      requestFilters,

      // Review stats
      reviewStats,
      recentReviews,
      reviewPagination,
      reviewFilters,

      // Exports
      exports,
      exportForm,
      exportModal,
      exportProgressModal,

      // Methods
      formatDate,
      formatActionType,
      getActionBadgeClass,
      formatExportType,
      formatExportStatus,
      getExportStatusBadge,
      refreshData,
      showExportModal,
      generateExport,
      downloadExport,
      deleteExport,
      getDisplayedPages,
      changePage,

      // Data fetching methods
      fetchActivityLogs,
      fetchProfessionalStats,
      fetchRequestStats,
      fetchReviewStats,
      fetchExports,
    }
  },
}
</script>

<style scoped>
.stars {
  font-size: 0.875rem;
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

.nav-tabs .nav-link {
  color: #6c757d;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  font-weight: 500;
}

.badge {
  font-weight: 500;
}

/* Export progress animation */
@keyframes progress {
  0% {
    width: 0%;
  }

  100% {
    width: 100%;
  }
}
</style>
