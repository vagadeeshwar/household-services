<template>
  <div class="container py-4">
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">Find Professionals</h1>
        <p class="text-muted">Browse through our verified service professionals</p>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label for="serviceType" class="form-label">Service Type</label>
            <select
              id="serviceType"
              class="form-select"
              v-model="filters.service_type"
              @change="applyFilters"
            >
              <option value="">All Services</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>

          <div class="col-md-4">
            <label for="searchTerm" class="form-label">Search</label>
            <div class="input-group">
              <input
                type="text"
                id="searchTerm"
                class="form-control"
                placeholder="Search professionals"
                v-model="searchTerm"
                @input="handleSearchInput"
              />
              <button class="btn btn-outline-secondary" type="button" @click="applyFilters">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          <div class="col-md-4">
            <label class="form-label d-block">&nbsp;</label>
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <Loading :show="isLoading" message="Finding professionals..." :overlay="false" />

    <!-- Professionals Grid View -->
    <div v-if="!isLoading">
      <!-- No results message -->
      <div v-if="filteredProfessionals.length === 0" class="text-center py-5">
        <div class="mb-3">
          <i class="bi bi-people text-muted" style="font-size: 3rem"></i>
        </div>
        <h5 class="text-muted">No professionals found</h5>
        <p class="text-muted">Try adjusting your filters or search criteria</p>
        <button class="btn btn-primary" @click="resetFilters">
          <i class="bi bi-arrow-counterclockwise me-1"></i> Reset Filters
        </button>
      </div>

      <!-- Professionals Cards -->
      <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4 mb-4">
        <div
          v-for="professional in filteredProfessionals"
          :key="professional.professional_id"
          class="col"
        >
          <div class="card h-100 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center mb-3">
                <div class="avatar me-3 bg-light rounded-circle">
                  <i class="bi bi-person-circle"></i>
                </div>
                <div>
                  <h5 class="card-title mb-0">{{ professional.full_name }}</h5>
                  <p class="text-muted mb-0 small">
                    <span class="badge bg-info me-2">{{
                      getServiceName(professional.service_type_id)
                    }}</span>
                    <span class="text-muted">{{ professional.experience_years }} years exp.</span>
                  </p>
                </div>
              </div>
              <div>
                <div class="mb-2 d-flex align-items-center">
                  <i class="bi bi-geo-alt text-muted me-2"></i>
                  <span>{{ professional.address }}</span>
                </div>
                <div class="mb-2 d-flex align-items-center">
                  <i class="bi bi-star-fill text-warning me-2"></i>
                  <span>{{ professional.average_rating || 'No ratings yet' }}</span>
                </div>
                <p v-if="professional.description" class="card-text mt-3">
                  {{ truncateDescription(professional.description, 120) }}
                </p>
              </div>
            </div>
            <div class="card-footer bg-white border-top-0">
              <div class="d-grid">
                <button class="btn btn-primary" @click="viewProfessional(professional)">
                  <i class="bi bi-eye me-1"></i> View Details
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <nav
        v-if="pagination.pages > 1"
        aria-label="Professionals pagination"
        class="d-flex justify-content-center"
      >
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: !pagination.has_prev }">
            <a
              class="page-link"
              href="#"
              @click.prevent="changePage(pagination.current_page - 1)"
              aria-label="Previous"
            >
              <span aria-hidden="true">&laquo;</span>
            </a>
          </li>
          <li
            v-for="page in paginationRange"
            :key="page"
            class="page-item"
            :class="{ active: page === pagination.current_page }"
          >
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: !pagination.has_next }">
            <a
              class="page-link"
              href="#"
              @click.prevent="changePage(pagination.current_page + 1)"
              aria-label="Next"
            >
              <span aria-hidden="true">&raquo;</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>

    <!-- Professional Detail Modal -->
    <div
      class="modal fade"
      id="professionalDetailModal"
      tabindex="-1"
      aria-labelledby="professionalDetailModalLabel"
      aria-hidden="true"
      ref="detailModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedProfessional">
          <div class="modal-header">
            <h5 class="modal-title" id="professionalDetailModalLabel">Professional Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-4 mb-3">
                <div class="text-center">
                  <div
                    class="avatar mx-auto mb-3 bg-light rounded-circle d-flex align-items-center justify-content-center"
                    style="width: 100px; height: 100px"
                  >
                    <i class="bi bi-person-circle" style="font-size: 3rem"></i>
                  </div>
                  <h5 class="mb-1">{{ selectedProfessional.full_name }}</h5>
                  <p class="text-muted mb-1">
                    {{ getServiceName(selectedProfessional.service_type_id) }}
                  </p>
                  <div class="d-flex justify-content-center mb-2">
                    <div class="badge bg-primary">
                      <i class="bi bi-star-fill me-1"></i>
                      {{ selectedProfessional.average_rating || 'No ratings' }}
                    </div>
                  </div>
                  <p class="text-muted small">
                    <i class="bi bi-award me-1"></i>
                    {{ selectedProfessional.experience_years }} years experience
                  </p>
                </div>
              </div>
              <div class="col-md-8">
                <h6 class="text-primary mb-3">Contact Information</h6>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Phone</label>
                      <div>{{ selectedProfessional.phone }}</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Email</label>
                      <div>{{ selectedProfessional.email }}</div>
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label text-muted small">Address</label>
                  <div>{{ selectedProfessional.address }}</div>
                </div>
                <div class="mb-3">
                  <label class="form-label text-muted small">PIN Code</label>
                  <div>{{ selectedProfessional.pin_code }}</div>
                </div>
              </div>
            </div>
            <hr />
            <div class="row">
              <div class="col-12">
                <h6 class="text-primary mb-3">About Professional</h6>
                <p>{{ selectedProfessional.description || 'No description provided.' }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="createServiceRequest">
              <i class="bi bi-calendar-plus me-1"></i> Request Service
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import * as bootstrap from 'bootstrap'
import { useLoading } from '@/composables/useLoading'

export default defineComponent({
  name: 'CustomerProfessionals',
  setup() {
    const store = useStore()
    const router = useRouter()
    const { isLoading, withLoading } = useLoading()

    // References
    const detailModal = ref(null)
    let bsDetailModal = null

    // State
    const professionals = computed(() => store.getters['professionals/allProfessionals'])
    const pagination = computed(() => store.getters['professionals/pagination'])
    const services = ref([])
    const selectedProfessional = ref(null)
    const searchTerm = ref('')
    const filters = ref({
      service_type: '',
      page: 1,
      per_page: 9,
    })

    // Computed
    const paginationRange = computed(() => {
      const current = pagination.value.current_page
      const total = pagination.value.pages
      const range = []
      // Show 5 pages at most
      const maxPages = 5
      const start = Math.max(1, current - Math.floor(maxPages / 2))
      const end = Math.min(total, start + maxPages - 1)
      for (let i = start; i <= end; i++) {
        range.push(i)
      }
      return range
    })

    // Add computed property for filtered professionals
    const filteredProfessionals = computed(() => {
      if (!searchTerm.value.trim()) {
        return professionals.value
      }
      const term = searchTerm.value.toLowerCase().trim()
      return professionals.value.filter((professional) => {
        const fullName = professional.full_name?.toLowerCase() || ''
        const email = professional.email?.toLowerCase() || ''
        const username = professional.username?.toLowerCase() || ''
        const address = professional.address?.toLowerCase() || ''
        return (
          fullName.includes(term) ||
          email.includes(term) ||
          username.includes(term) ||
          address.includes(term)
        )
      })
    })

    // Methods
    const fetchProfessionals = async (forceRefresh = false) => {
      const params = {
        per_page: filters.value.per_page,
        page: filters.value.page,
      }

      searchTerm.value = ''

      if (filters.value.service_type) {
        params.service_type = filters.value.service_type
      }

      await withLoading(
        store.dispatch('professionals/fetchProfessionals', { params, forceRefresh }),
        'Loading professionals...',
      )
    }

    const fetchServices = async () => {
      try {
        const response = await store.dispatch('services/fetchActiveServices', {
          params: { per_page: 100 },
        })
        services.value = response.data || []
      } catch (error) {
        console.error('Error fetching services:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load services. Please try again.',
        })
      }
    }

    const getServiceName = (serviceId) => {
      if (!serviceId) return 'Unknown Service'
      const service = services.value.find((s) => s.id === serviceId)
      return service ? service.name : 'Unknown Service'
    }

    const viewProfessional = (professional) => {
      selectedProfessional.value = professional
      bsDetailModal.show()
    }

    const createServiceRequest = () => {
      // Navigate to the service request page with the professional ID
      router.push({
        name: 'CustomerRequests',
        query: {
          professional_id: selectedProfessional.value.professional_id,
          service_id: selectedProfessional.value.service_type_id,
        },
      })
      bsDetailModal.hide()
    }

    const applyFilters = () => {
      filters.value.page = 1
      fetchProfessionals()
    }

    const handleSearchInput = () => {
      // Debounce implementation could be added here
      filters.value.page = 1
    }

    const resetFilters = () => {
      filters.value = {
        service_type: '',
        page: 1,
        per_page: 9,
      }
      searchTerm.value = ''
      fetchProfessionals(true)
    }

    const changePage = (page) => {
      if (page < 1 || page > pagination.value.pages) return
      filters.value.page = page
      fetchProfessionals()
    }

    const truncateDescription = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.slice(0, length) + '...' : text
    }

    // Lifecycle hooks
    onMounted(async () => {
      // Initialize modal
      if (detailModal.value) {
        bsDetailModal = new bootstrap.Modal(detailModal.value)
      }

      // Fetch initial data
      await Promise.all([fetchProfessionals(), fetchServices()])
    })

    return {
      // State
      professionals,
      services,
      selectedProfessional,
      pagination,
      paginationRange,
      filters,
      searchTerm,
      isLoading,

      // Refs
      detailModal,

      // Methods
      fetchProfessionals,
      viewProfessional,
      createServiceRequest,
      getServiceName,
      applyFilters,
      resetFilters,
      handleSearchInput,
      changePage,
      truncateDescription,
      filteredProfessionals,
    }
  },
})
</script>

<style scoped>
.avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--bs-primary);
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

.badge {
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .card {
    margin-bottom: 1rem;
  }
}
</style>
