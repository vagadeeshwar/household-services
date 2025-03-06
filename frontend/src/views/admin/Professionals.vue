<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">Professional Management</h1>
      <div class="d-flex gap-2">
        <div class="btn-group">
          <button
            class="btn btn-outline-primary"
            :class="{ active: !showPendingOnly }"
            @click="showPendingOnly = false"
          >
            All Professionals
          </button>
          <button
            class="btn btn-outline-warning"
            :class="{ active: showPendingOnly }"
            @click="showPendingOnly = true"
          >
            Pending Verification
            <span v-if="pendingCount > 0" class="badge bg-warning ms-1">{{ pendingCount }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Service Type</label>
            <select class="form-select" v-model="filters.serviceType" @change="onFiltersChange">
              <option value="">All Services</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Verification Status</label>
            <select class="form-select" v-model="filters.verified" @change="onFiltersChange">
              <option :value="null">All</option>
              <option :value="true">Verified</option>
              <option :value="false">Unverified</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Search</label>
            <div class="input-group">
              <input
                type="text"
                class="form-control"
                placeholder="Search by name or email..."
                v-model="filters.search"
                @input="debouncedSearch"
              />
              <button class="btn btn-outline-secondary" type="button" @click="clearSearch">
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <Loading :show="isLoading" message="Loading professionals..." :overlay="true" />

    <!-- Professionals Table -->
    <div v-if="!isLoading" class="card shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Service</th>
              <th scope="col">Experience</th>
              <th scope="col">Rating</th>
              <th scope="col">Status</th>
              <th scope="col" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="professionals.length === 0">
              <td colspan="7" class="text-center py-4 text-muted">
                <i class="bi bi-search me-2"></i>No professionals found
              </td>
            </tr>
            <tr v-for="pro in professionals" :key="pro.id">
              <td>{{ pro.professional_id }}</td>
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar bg-primary text-white me-2">
                    <i class="bi bi-person-fill"></i>
                  </div>
                  <div>
                    <div class="fw-medium">{{ pro.full_name }}</div>
                    <div class="small text-muted">{{ pro.email }}</div>
                  </div>
                </div>
              </td>
              <td>{{ getServiceName(pro.service_type_id) }}</td>
              <td>{{ pro.experience_years }} years</td>
              <td>
                <div class="d-flex align-items-center">
                  <div class="stars me-2">
                    <i
                      v-for="i in 5"
                      :key="i"
                      class="bi"
                      :class="
                        i <= Math.round(pro.average_rating || 0)
                          ? 'bi-star-fill text-warning'
                          : 'bi-star'
                      "
                    ></i>
                  </div>
                  <span>{{ pro.average_rating ? pro.average_rating.toFixed(1) : 'N/A' }}</span>
                </div>
              </td>
              <td>
                <div class="d-flex align-items-center gap-2">
                  <span :class="['badge', pro.is_verified ? 'bg-success' : 'bg-warning']">
                    {{ pro.is_verified ? 'Verified' : 'Pending' }}
                  </span>
                  <span v-if="!pro.is_active" class="badge bg-danger"> Blocked </span>
                </div>
              </td>
              <td class="text-end">
                <div class="btn-group">
                  <button class="btn btn-sm btn-outline-primary" @click="viewProfessional(pro)">
                    <i class="bi bi-eye"></i>
                  </button>
                  <button
                    v-if="!pro.is_verified"
                    class="btn btn-sm btn-outline-success"
                    @click="verifyProfessional(pro)"
                    :disabled="isActionLoading"
                  >
                    <i class="bi bi-check-circle"></i>
                  </button>
                  <button
                    v-if="pro.is_active"
                    class="btn btn-sm btn-outline-danger"
                    @click="showBlockModal(pro)"
                    :disabled="isActionLoading"
                  >
                    <i class="bi bi-slash-circle"></i>
                  </button>
                  <button
                    v-else
                    class="btn btn-sm btn-outline-success"
                    @click="unblockProfessional(pro)"
                    :disabled="isActionLoading"
                  >
                    <i class="bi bi-check-circle"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div class="card-footer bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-6 text-muted">
            Showing {{ professionals.length }} of {{ totalProfessionals }} professionals
          </div>
          <div class="col-md-6">
            <ul class="pagination mb-0 justify-content-md-end">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button @click="changePage(currentPage - 1)" class="page-link">Previous</button>
              </li>
              <li
                v-for="pageNum in displayedPages"
                :key="pageNum"
                class="page-item"
                :class="{ active: currentPage === pageNum }"
              >
                <button @click="changePage(pageNum)" class="page-link">{{ pageNum }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button @click="changePage(currentPage + 1)" class="page-link">Next</button>
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
      <button @click="fetchProfessionals" class="btn btn-sm btn-outline-danger ms-2">Retry</button>
    </div>

    <!-- Professional Details Modal -->
    <div class="modal fade" id="professionalModal" tabindex="-1" ref="professionalModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedProfessional">
          <div class="modal-header">
            <h5 class="modal-title">Professional Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="card">
              <div class="card-header p-4">
                <div class="d-flex align-items-center">
                  <div class="avatar-lg bg-primary text-white me-4">
                    <i class="bi bi-person-fill"></i>
                  </div>
                  <div>
                    <h4 class="mb-1">{{ selectedProfessional.full_name }}</h4>
                    <p class="mb-0 text-muted">
                      {{ getServiceName(selectedProfessional.service_type_id) }} Professional
                      <span v-if="selectedProfessional.is_verified" class="badge bg-success ms-2"
                        >Verified</span
                      >
                      <span v-else class="badge bg-warning ms-2">Pending Verification</span>
                      <span v-if="!selectedProfessional.is_active" class="badge bg-danger ms-2"
                        >Blocked</span
                      >
                    </p>
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
                        <div class="fw-medium mb-1">Email</div>
                        <div>{{ selectedProfessional.email }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Phone</div>
                        <div>+91 {{ selectedProfessional.phone }}</div>
                      </div>
                      <div class="col-12">
                        <div class="fw-medium mb-1">Address</div>
                        <div>{{ selectedProfessional.address }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">PIN Code</div>
                        <div>{{ selectedProfessional.pin_code }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- Professional Information -->
                  <div class="col-12">
                    <h5 class="border-bottom pb-2">Professional Information</h5>
                    <div class="row g-3 mt-2">
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Service Type</div>
                        <div>{{ getServiceName(selectedProfessional.service_type_id) }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Experience</div>
                        <div>{{ selectedProfessional.experience_years }} years</div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Average Rating</div>
                        <div class="d-flex align-items-center">
                          <div class="stars me-2">
                            <i
                              v-for="i in 5"
                              :key="i"
                              class="bi"
                              :class="
                                i <= Math.round(selectedProfessional.average_rating || 0)
                                  ? 'bi-star-fill text-warning'
                                  : 'bi-star'
                              "
                            ></i>
                          </div>
                          <span>{{
                            selectedProfessional.average_rating
                              ? selectedProfessional.average_rating.toFixed(1)
                              : 'N/A'
                          }}</span>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="fw-medium mb-1">Account Status</div>
                        <div>
                          <span
                            :class="[
                              'badge',
                              selectedProfessional.is_active ? 'bg-success' : 'bg-danger',
                            ]"
                          >
                            {{ selectedProfessional.is_active ? 'Active' : 'Blocked' }}
                          </span>
                        </div>
                      </div>
                      <div class="col-12">
                        <div class="fw-medium mb-1">Description</div>
                        <div>{{ selectedProfessional.description }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- Verification Documents (Only admins can see) -->
                  <div class="col-12" v-if="selectedProfessional.verification_documents">
                    <h5 class="border-bottom pb-2">Verification Documents</h5>
                    <div class="mt-3 border rounded p-3 bg-light">
                      <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                          <i class="bi bi-file-earmark-text me-2"></i>
                          {{ selectedProfessional.verification_documents }}
                        </div>
                        <a
                          :href="getDocumentUrl(selectedProfessional.verification_documents)"
                          target="_blank"
                          class="btn btn-sm btn-primary"
                        >
                          <i class="bi bi-download me-1"></i>
                          Download
                        </a>
                      </div>
                      <div v-if="docPreviewUrl" class="mt-3 text-center">
                        <div class="border rounded bg-white p-2">
                          <img :src="docPreviewUrl" alt="Document Preview" class="img-fluid" />
                        </div>
                      </div>
                      <div v-if="selectedProfessional.verification_document_content" class="mt-3">
                        <div class="alert alert-info">
                          <i class="bi bi-info-circle me-2"></i>
                          Document content is available for preview.
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button
              v-if="!selectedProfessional.is_verified"
              type="button"
              class="btn btn-success"
              @click="verifyProfessional(selectedProfessional)"
              :disabled="isActionLoading"
            >
              <i class="bi bi-check-circle me-1"></i>
              Verify Professional
            </button>
            <button
              v-if="selectedProfessional.is_active"
              type="button"
              class="btn btn-danger"
              @click="showBlockModal(selectedProfessional)"
              :disabled="isActionLoading"
            >
              <i class="bi bi-slash-circle me-1"></i>
              Block Professional
            </button>
            <button
              v-else
              type="button"
              class="btn btn-success"
              @click="unblockProfessional(selectedProfessional)"
              :disabled="isActionLoading"
            >
              <i class="bi bi-check-circle me-1"></i>
              Unblock Professional
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Block Professional Modal -->
    <div class="modal fade" id="blockModal" tabindex="-1" ref="blockModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">
              <i class="bi bi-slash-circle me-2"></i>
              Block Professional
            </h5>
            <button
              type="button"
              class="btn-close btn-close-white"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>
              Are you sure you want to block <strong>{{ selectedProfessional?.full_name }}</strong
              >?
            </p>
            <p class="text-muted">This will prevent them from accepting new service requests.</p>
            <div class="mb-3">
              <label for="blockReason" class="form-label">Reason for blocking</label>
              <textarea
                class="form-control"
                id="blockReason"
                rows="3"
                v-model="blockReason"
                placeholder="Please provide a reason..."
                :class="{ 'is-invalid': blockReasonError }"
              ></textarea>
              <div class="invalid-feedback">{{ blockReasonError }}</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-danger"
              @click="blockProfessional"
              :disabled="isActionLoading"
            >
              <span v-if="isActionLoading" class="spinner-border spinner-border-sm me-2"></span>
              Block Professional
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useLoading } from '@/composables/useLoading'
import * as bootstrap from 'bootstrap'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
  name: 'AdminProfessionals',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const { isLoading, showLoading, hideLoading, withLoading } = useLoading()

    // Modal refs
    const professionalModal = ref(null)
    const blockModal = ref(null)
    let bsProfessionalModal = null
    let bsBlockModal = null

    // State
    const professionals = computed(() => store.getters['professionals/allProfessionals'] || [])
    const services = ref([])
    const selectedProfessional = ref(null)
    const error = ref(null)
    const isActionLoading = ref(false)
    const blockReason = ref('')
    const blockReasonError = ref('')
    const docPreviewUrl = ref(null)
    const searchTimeout = ref(null)
    const showPendingOnly = ref(false)

    // Pagination
    const currentPage = ref(1)
    const perPage = ref(10)
    const totalProfessionals = computed(() => store.getters['professionals/pagination']?.total || 0)
    const totalPages = computed(() => store.getters['professionals/pagination']?.pages || 1)

    // Filters
    const filters = ref({
      serviceType: '',
      verified: null,
      search: '',
    })

    // Computed
    const pendingCount = computed(() => {
      return professionals.value.filter((p) => !p.is_verified).length
    })

    const displayedPages = computed(() => {
      const pages = []
      const maxVisiblePages = 5
      let startPage = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
      let endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1)

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1)
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      return pages
    })

    const fetchActiveServices = async () => {
      try {
        const response = await store.dispatch('services/fetchActiveServices', { isActive: true })
        services.value = response.data
      } catch (err) {
        console.error('Error fetching services:', err)
      }
    }

    const fetchProfessionals = async () => {
      return withLoading(async () => {
        try {
          error.value = null
          await store.dispatch('professionals/fetchProfessionals', {
            page: currentPage.value,
            perPage: perPage.value,
            serviceType: filters.value.serviceType || undefined,
            verified: filters.value.verified,
            search: filters.value.search || undefined,
          })
        } catch (err) {
          error.value = err.message || 'Failed to load professionals'
          console.error(err)
        }
      }, 'Loading professionals...')
    }

    // Watch for query params
    watch(
      () => route.query,
      (newQuery) => {
        if (newQuery.status === 'pending') {
          showPendingOnly.value = true
          filters.value.verified = false
        }

        fetchProfessionals()
      },
      { immediate: true },
    )

    // Watch for status filter
    watch(
      () => showPendingOnly.value,
      (newValue) => {
        filters.value.verified = newValue ? false : null
        currentPage.value = 1
        fetchProfessionals()

        // Update URL without reloading
        const query = newValue ? { status: 'pending' } : {}
        router.replace({ query })
      },
    )

    const getServiceName = (serviceId) => {
      const service = services.value.find((s) => s.id === serviceId)
      return service ? service.name : 'Unknown Service'
    }

    const viewProfessional = async (professional) => {
      try {
        showLoading('Loading professional details...')
        // Get detailed information about the professional
        const response = await store.dispatch(
          'professionals/fetchProfessionalById',
          professional.professional_id,
        )
        selectedProfessional.value = response.data

        // Set document preview URL if available
        if (selectedProfessional.value.verification_documents) {
          docPreviewUrl.value = getDocumentUrl(selectedProfessional.value.verification_documents)
        } else {
          docPreviewUrl.value = null
        }

        bsProfessionalModal.show()
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: 'Failed to load professional details',
        })
        console.error(err)
      } finally {
        hideLoading()
      }
    }

    const getDocumentUrl = (filename) => {
      // This will need to match your backend URL for document access
      return `/static/uploads/verification_docs/${filename}`
    }

    const verifyProfessional = async (professional) => {
      if (isActionLoading.value) return

      try {
        isActionLoading.value = true
        await store.dispatch('professionals/verifyProfessional', professional.professional_id)

        window.showToast({
          type: 'success',
          title: 'Success',
          message: `${professional.full_name} has been verified successfully`,
        })

        // Refresh data
        await fetchProfessionals()

        // Close modal if open
        if (bsProfessionalModal && bsProfessionalModal._isShown) {
          bsProfessionalModal.hide()
        }
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: err.response?.data?.message || 'Failed to verify professional',
        })
      } finally {
        isActionLoading.value = false
      }
    }

    const showBlockModal = (professional) => {
      selectedProfessional.value = professional
      blockReason.value = ''
      blockReasonError.value = ''

      // Close details modal if open
      if (bsProfessionalModal && bsProfessionalModal._isShown) {
        bsProfessionalModal.hide()
      }

      bsBlockModal.show()
    }

    const blockProfessional = async () => {
      if (isActionLoading.value) return

      // Validate reason
      if (!blockReason.value.trim()) {
        blockReasonError.value = 'Please provide a reason for blocking'
        return
      }

      try {
        isActionLoading.value = true
        await store.dispatch('professionals/blockProfessional', {
          id: selectedProfessional.value.professional_id,
          reason: blockReason.value,
        })

        window.showToast({
          type: 'success',
          title: 'Success',
          message: `${selectedProfessional.value.full_name} has been blocked`,
        })

        // Refresh data
        await fetchProfessionals()

        // Close modal
        bsBlockModal.hide()
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: err.response?.data?.message || 'Failed to block professional',
        })
      } finally {
        isActionLoading.value = false
      }
    }

    const unblockProfessional = async (professional) => {
      if (isActionLoading.value) return

      try {
        isActionLoading.value = true
        await store.dispatch('professionals/unblockProfessional', professional.professional_id)

        window.showToast({
          type: 'success',
          title: 'Success',
          message: `${professional.full_name} has been unblocked`,
        })

        // Refresh data
        await fetchProfessionals()

        // Close modal if open
        if (bsProfessionalModal && bsProfessionalModal._isShown) {
          bsProfessionalModal.hide()
        }
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: err.response?.data?.message || 'Failed to unblock professional',
        })
      } finally {
        isActionLoading.value = false
      }
    }

    const changePage = (page) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      fetchProfessionals()
    }

    const debouncedSearch = () => {
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value)
      }

      searchTimeout.value = setTimeout(() => {
        currentPage.value = 1
        fetchProfessionals()
      }, 500)
    }

    const clearSearch = () => {
      filters.value.search = ''
      currentPage.value = 1
      fetchProfessionals()
    }

    const onFiltersChange = () => {
      currentPage.value = 1
      fetchProfessionals()
    }

    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      if (professionalModal.value) {
        bsProfessionalModal = new bootstrap.Modal(professionalModal.value)
      }

      if (blockModal.value) {
        bsBlockModal = new bootstrap.Modal(blockModal.value)
      }

      // Fetch initial data
      await fetchActiveServices()
      await fetchProfessionals()
    })

    return {
      professionals,
      services,
      filters,
      selectedProfessional,
      isLoading,
      isActionLoading,
      error,
      blockReason,
      blockReasonError,
      docPreviewUrl,
      currentPage,
      totalPages,
      totalProfessionals,
      displayedPages,
      pendingCount,
      showPendingOnly,
      professionalModal,
      blockModal,
      fetchProfessionals,
      getServiceName,
      viewProfessional,
      verifyProfessional,
      showBlockModal,
      blockProfessional,
      unblockProfessional,
      changePage,
      debouncedSearch,
      clearSearch,
      onFiltersChange,
      getDocumentUrl,
    }
  },
}
</script>

<style scoped>
.avatar {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
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

.stars {
  font-size: 0.875rem;
}

.btn-group .btn {
  padding: 0.25rem 0.5rem;
}
</style>
