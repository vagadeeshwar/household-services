<template>
  <div class="card shadow-sm">
    <div class="card-header bg-white">
      <div class="d-flex flex-column">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Activity Logs</h5>
          <button class="btn btn-sm btn-outline-primary" @click="fetchActivityLogs(true)">
            <i class="bi bi-arrow-clockwise"></i>
          </button>
        </div>
        <div class="d-flex gap-2 mt-3">
          <!-- Action Filter -->
          <div class="flex-grow-1">
            <label class="form-label text-muted small mb-1">Filter by Action</label>
            <select
              v-model="activityFilters.action"
              class="form-select form-select-sm"
              @change="fetchActivityLogs"
            >
              <option
                v-for="action in actionTypes[selectedUserRole]"
                :key="action.value"
                :value="action.value"
              >
                {{ action.label }}
              </option>
            </select>
          </div>
          <!-- Replace the user ID input with this select -->
          <div v-if="isAdmin" class="flex-grow-1">
            <label class="form-label text-muted small mb-1" for="user-filter">Select User</label>
            <select
              id="user-filter"
              class="form-select form-select-sm"
              v-model="activityFilters.userId"
              @change="fetchActivityLogs"
              :disabled="isLoadingUsers"
            >
              <option v-if="isLoadingUsers" value="">Loading users...</option>
              <optgroup label="Admin">
                <option v-for="user in getUsersByRole('admin')" :key="user.id" :value="user.id">
                  {{ user.name }}
                </option>
              </optgroup>
              <optgroup label="Professionals">
                <option
                  v-for="user in getUsersByRole('professional')"
                  :key="user.id"
                  :value="user.id"
                >
                  {{ user.name }}
                </option>
              </optgroup>
              <optgroup label="Customers">
                <option v-for="user in getUsersByRole('customer')" :key="user.id" :value="user.id">
                  {{ user.name }}
                </option>
              </optgroup>
            </select>
          </div>
          <!-- Date Range Filter -->
          <div class="flex-grow-1">
            <label class="form-label text-muted small mb-1">Start Date</label>
            <input
              type="date"
              class="form-control form-control-sm"
              v-model="activityFilters.startDate"
              @change="fetchActivityLogs"
            />
          </div>
          <div class="flex-grow-1">
            <label class="form-label text-muted small mb-1">End Date</label>
            <input
              type="date"
              class="form-control form-control-sm"
              v-model="activityFilters.endDate"
              @change="fetchActivityLogs"
            />
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
            <small class="text-muted">{{ formatRelativeTime(log.created_at) }}</small>
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
              <button @click="changePage(activityFilters.page - 1)" class="page-link">
                Previous
              </button>
            </li>
            <li
              v-for="pageNum in displayedPages"
              :key="pageNum"
              class="page-item"
              :class="{ active: activityFilters.page === pageNum }"
            >
              <button @click="changePage(pageNum)" class="page-link">{{ pageNum }}</button>
            </li>
            <li
              class="page-item"
              :class="{ disabled: activityFilters.page === activityPagination.pages }"
            >
              <button @click="changePage(activityFilters.page + 1)" class="page-link">Next</button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { actionTypes, actionBadges, actionIcons } from '@/assets/actionTypes'
import { formatRelativeTime } from '@/utils/date'

export default {
  name: 'ActivityLogs',
  setup() {
    const store = useStore()
    // Add to setup()
    const allUsers = ref([])
    const isLoadingUsers = ref(false)

    // Get current user from store
    const currentUser = computed(() => store.getters['auth/currentUser'])
    const userRole = computed(() => store.getters['auth/userRole'])
    const isAdmin = computed(() => userRole.value === 'admin')

    // Activity logs
    const activityLogs = ref([])
    const isLoadingActivity = ref(false)
    const activityPagination = ref({})
    const activityFilters = ref({
      action: 'all',
      page: 1,
      perPage: 10,
      startDate: null,
      endDate: null,
      userId: currentUser.value.id, // Only used by admins
    })

    // Function to fetch users for dropdown
    const fetchAllUsers = async () => {
      isLoadingUsers.value = true
      try {
        // Fetch professionals
        const profResponse = await store.dispatch('professionals/fetchProfessionals', {
          params: {
            per_page: 100,
          },
        })

        // Fetch customers
        const custResponse = await store.dispatch('customers/fetchCustomers', {
          params: {
            per_page: 100,
          },
        })

        // Format user lists
        const professionals = (profResponse.data || []).map((prof) => ({
          id: prof.professional_id,
          name: prof.full_name,
          role: 'professional',
        }))

        const customers = (custResponse.data || []).map((cust) => ({
          id: cust.customer_id,
          name: cust.full_name,
          role: 'customer',
        }))

        // Add current admin
        const admins = [
          {
            id: currentUser.value.id,
            name: `${currentUser.value.full_name} (You)`,
            role: 'admin',
          },
        ]

        // Combine all users
        allUsers.value = [...admins, ...professionals, ...customers]
      } catch (err) {
        console.error('Error fetching users:', err)
      } finally {
        isLoadingUsers.value = false
      }
    }

    // Computed properties
    const displayedPages = computed(() => {
      const pages = []
      const maxVisiblePages = 5
      const totalPages = activityPagination.value?.pages || 1

      let startPage = Math.max(1, activityFilters.value.page - Math.floor(maxVisiblePages / 2))
      let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1)

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1)
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      return pages
    })

    const selectedUserRole = computed(() => {
      if (!isAdmin.value || activityFilters.value.userId === currentUser.value.id) {
        return userRole.value // Current user's role
      }

      // Find the selected user's role in the allUsers list
      const selectedUser = allUsers.value.find((user) => user.id === activityFilters.value.userId)
      return selectedUser ? selectedUser.role : 'customer' // Default to customer if not found
    })

    const formatActionType = (action) => {
      const found = actionTypes[userRole.value].find((a) => a.value === action)
      return found ? found.label : action
    }

    const getActivityIcon = (action) => {
      return actionIcons[action] || 'bi-activity'
    }

    const getActivityBadgeClass = (action) => {
      return actionBadges[action] || 'bg-secondary'
    }

    const fetchActivityLogs = async (forceRefresh = false) => {
      isLoadingActivity.value = true

      const params = {
        action: activityFilters.value.action,
        page: activityFilters.value.page,
        per_page: activityFilters.value.perPage,
        start_date: activityFilters.value.startDate
          ? new Date(activityFilters.value.startDate).toISOString()
          : null,
        end_date: activityFilters.value.endDate
          ? new Date(activityFilters.value.endDate + 'T23:59:59').toISOString()
          : null,
      }

      try {
        // Admin viewing other user's logs
        if (isAdmin.value && activityFilters.value.userId) {
          const response = await store.dispatch('stats/fetchOthersActivityLogs', {
            params: params,
            id: activityFilters.value.userId,
            forceRefresh: forceRefresh,
          })
          activityLogs.value = response.data || []
          activityPagination.value = response.pagination || {}
        }
        // User viewing their own logs
        else {
          const response = await store.dispatch('stats/fetchActivityLogs', {
            params: params,
            forceRefresh: forceRefresh,
          })
          activityLogs.value = response.data || []
          activityPagination.value = response.pagination || {}
        }
      } catch (err) {
        console.error('Error fetching activity logs:', err)
      } finally {
        isLoadingActivity.value = false
      }
    }

    // Helper to get users filtered by role
    const getUsersByRole = (role) => {
      return allUsers.value.filter((user) => user.role === role)
    }

    const clearFilters = () => {
      activityFilters.value.action = 'all'
      activityFilters.value.startDate = null
      activityFilters.value.endDate = null
      activityFilters.value.page = 1

      if (isAdmin.value) {
        activityFilters.value.userId = currentUser.value.id
      }

      fetchActivityLogs()
    }

    const changePage = (page) => {
      if (page < 1 || page > activityPagination.value.pages) return
      activityFilters.value.page = page
      fetchActivityLogs()
    }

    // Watch for filter changes to reset pagination
    watch(
      () => activityFilters.value.action,
      (newVal, oldVal) => {
        if (newVal !== oldVal) {
          activityFilters.value.page = 1
          activityFilters.value.startDate = null
          activityFilters.value.endDate = null
          // No need to call fetchActivityLogs here as it's called by @change
        }
      },
    )

    watch(
      () => activityFilters.value.startDate,
      (newVal, oldVal) => {
        if (
          newVal &&
          activityFilters.value.endDate &&
          new Date(newVal) > new Date(activityFilters.value.endDate)
        ) {
          activityFilters.value.endDate = null
        }

        if (newVal !== oldVal) {
          activityFilters.value.page = 1
          // No need to call fetchActivityLogs here as it's called by @change
        }
      },
    )

    watch(
      () => activityFilters.value.endDate,
      (newVal, oldVal) => {
        if (
          newVal &&
          activityFilters.value.startDate &&
          new Date(newVal) < new Date(activityFilters.value.startDate)
        ) {
          activityFilters.value.startDate = null
        }

        if (newVal !== oldVal) {
          activityFilters.value.page = 1
          // No need to call fetchActivityLogs here as it's called by @change
        }
      },
    )

    watch(
      () => activityFilters.value.userId,
      (newVal, oldVal) => {
        if (newVal !== oldVal) {
          activityFilters.value.page = 1
          activityFilters.value.startDate = null
          activityFilters.value.endDate = null
          activityFilters.value.action = 'all'
          // No need to call fetchActivityLogs here as it's called by @change
        }
      },
    )

    // Lifecycle hooks
    onMounted(() => {
      if (isAdmin.value) {
        fetchAllUsers()
      }

      // Fetch activity logs
      fetchActivityLogs()
    })

    return {
      currentUser,
      userRole,
      isAdmin,
      activityLogs,
      isLoadingActivity,
      activityPagination,
      activityFilters,
      displayedPages,
      actionTypes,
      formatRelativeTime,
      formatActionType,
      getActivityIcon,
      getActivityBadgeClass,
      fetchActivityLogs,
      changePage,
      clearFilters,
      allUsers,
      isLoadingUsers,
      getUsersByRole,
      selectedUserRole,
    }
  },
}
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

.badge {
  font-weight: 500;
}
</style>
