<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 mb-0">Service Management</h1>
      <button class="btn btn-primary" @click="showCreateModal">
        <i class="bi bi-plus-circle me-2"></i>Add Service
      </button>
    </div>

    <!-- Status Indicator -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading services...</p>
    </div>

    <!-- Error Alert -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button @click="fetchServices" class="btn btn-sm btn-outline-danger ms-2">Retry</button>
    </div>

    <!-- Services Table -->
    <div v-else class="card shadow-sm">
      <div class="card-header bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h5 class="mb-0">Service Management</h5>
          </div>
          <div class="col-md-6">
            <div class="d-flex justify-content-md-end align-items-center">
              <div class="input-group" style="max-width: 200px">
                <input
                  type="text"
                  class="form-control form-control-sm"
                  placeholder="Search..."
                  v-model="searchQuery"
                  @input="handleSearch"
                />
                <button class="btn btn-sm btn-outline-secondary" type="button" @click="clearSearch">
                  <i class="bi bi-x"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th scope="col">#</th>
              <th scope="col">Service Name</th>
              <th scope="col">Base Price</th>
              <th scope="col">Duration</th>
              <th scope="col">Status</th>
              <th scope="col" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredServices.length === 0">
              <td colspan="6" class="text-center py-4 text-muted">
                <i class="bi bi-search me-2"></i>No services found
              </td>
            </tr>
            <tr v-for="service in filteredServices" :key="service.id">
              <td>{{ service.id }}</td>
              <td>{{ service.name }}</td>
              <td>₹{{ service.base_price.toFixed(2) }}</td>
              <td>{{ formatTime(service.estimated_time) }}</td>
              <td>
                <span :class="['badge', service.is_active ? 'bg-success' : 'bg-secondary']">
                  {{ service.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="text-end">
                <div class="btn-group">
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="showEditModal(service)"
                    title="Edit Service"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button
                    class="btn btn-sm btn-outline-info"
                    @click="showDetailsModal(service)"
                    title="View Details"
                  >
                    <i class="bi bi-info-circle"></i>
                  </button>
                  <button
                    class="btn btn-sm"
                    :class="[service.is_active ? 'btn-outline-warning' : 'btn-outline-success']"
                    @click="toggleServiceStatus(service)"
                    :title="service.is_active ? 'Deactivate Service' : 'Activate Service'"
                  >
                    <i
                      class="bi"
                      :class="[service.is_active ? 'bi-pause-circle' : 'bi-play-circle']"
                    ></i>
                  </button>
                  <button
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmDelete(service)"
                    title="Delete Service"
                    :disabled="!canDelete(service)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="card-footer bg-white py-3">
        <div class="row align-items-center">
          <div class="col-md-6 text-muted">
            Showing {{ filteredServices.length }} of {{ totalServices }} services
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

    <!-- Create/Edit Service Modal -->
    <div class="modal fade" id="serviceModal" tabindex="-1" ref="serviceModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditMode ? 'Edit Service' : 'Add New Service' }}</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveService">
              <div class="mb-3">
                <label for="serviceName" class="form-label">Service Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="serviceName"
                  v-model="serviceForm.name"
                  :class="{ 'is-invalid': formErrors.name }"
                  required
                />
                <div class="invalid-feedback">
                  {{ formErrors.name }}
                </div>
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea
                  class="form-control"
                  id="description"
                  rows="3"
                  v-model="serviceForm.description"
                  :class="{ 'is-invalid': formErrors.description }"
                  required
                ></textarea>
                <div class="invalid-feedback">
                  {{ formErrors.description }}
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="basePrice" class="form-label">Base Price (₹)</label>
                  <input
                    type="number"
                    class="form-control"
                    id="basePrice"
                    v-model="serviceForm.base_price"
                    :class="{ 'is-invalid': formErrors.base_price }"
                    min="0"
                    step="0.01"
                    required
                  />
                  <div class="invalid-feedback">
                    {{ formErrors.base_price }}
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="estTime" class="form-label">Estimated Time (minutes)</label>
                  <input
                    type="number"
                    class="form-control"
                    id="estTime"
                    v-model="serviceForm.estimated_time"
                    :class="{ 'is-invalid': formErrors.estimated_time }"
                    min="1"
                    required
                  />
                  <div class="invalid-feedback">
                    {{ formErrors.estimated_time }}
                  </div>
                </div>
              </div>
              <div class="form-check form-switch mb-3" v-if="isEditMode">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="statusSwitch"
                  v-model="serviceForm.is_active"
                />
                <label class="form-check-label" for="statusSwitch">Active</label>
              </div>
              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isEditMode ? 'Update Service' : 'Create Service' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Details Modal -->
    <div class="modal fade" id="detailsModal" tabindex="-1" ref="detailsModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Service Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body" v-if="selectedService">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0">{{ selectedService.name }}</h5>
                <span :class="['badge', selectedService.is_active ? 'bg-success' : 'bg-secondary']">
                  {{ selectedService.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="card-body">
                <p class="card-text">{{ selectedService.description }}</p>
                <div class="row">
                  <div class="col-md-6">
                    <p class="mb-1"><strong>Base Price:</strong></p>
                    <p class="text-primary h5">₹{{ selectedService.base_price.toFixed(2) }}</p>
                  </div>
                  <div class="col-md-6">
                    <p class="mb-1"><strong>Estimated Time:</strong></p>
                    <p class="text-primary h5">{{ formatTime(selectedService.estimated_time) }}</p>
                  </div>
                </div>
                <hr />
                <div class="row">
                  <div class="col-md-6">
                    <p class="mb-1 text-muted"><small>Created On:</small></p>
                    <p>{{ formatDate(selectedService.created_at) }}</p>
                  </div>
                  <div class="col-md-6">
                    <p class="mb-1 text-muted"><small>Last Updated:</small></p>
                    <p>
                      {{
                        selectedService.updated_at
                          ? formatDate(selectedService.updated_at)
                          : 'Never'
                      }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="showEditModal(selectedService)">
              <i class="bi bi-pencil me-1"></i> Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">Confirm Delete</h5>
            <button
              type="button"
              class="btn-close btn-close-white"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>
              Are you sure you want to delete <strong>{{ selectedService?.name }}</strong
              >?
            </p>
            <p class="text-danger small">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-danger"
              @click="deleteService"
              :disabled="isDeleting"
            >
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as bootstrap from 'bootstrap'
import moment from 'moment'
import { computed, onMounted, reactive, ref } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'AdminServices',
  setup() {
    const store = useStore()

    // Modal refs for Bootstrap
    const serviceModal = ref(null)
    const detailsModal = ref(null)
    const deleteModal = ref(null)
    let bsServiceModal = null
    let bsDetailsModal = null
    let bsDeleteModal = null

    // State
    const services = computed(() => store.getters['services/allServices'] || [])
    const isLoading = computed(() => store.getters['services/isLoading'])
    const error = computed(() => store.getters['services/error'])
    const pagination = computed(() => store.getters['services/pagination'])

    const currentPage = ref(1)
    const perPage = ref(10)
    const searchQuery = ref('')
    const isEditMode = ref(false)
    const isSubmitting = ref(false)
    const isDeleting = ref(false)
    const selectedService = ref(null)

    // Form state
    const serviceForm = reactive({
      name: '',
      description: '',
      base_price: 0,
      estimated_time: 60,
      is_active: true,
    })

    const formErrors = reactive({
      name: '',
      description: '',
      base_price: '',
      estimated_time: '',
    })

    // Computed properties
    const totalServices = computed(() => pagination.value?.total || 0)
    const totalPages = computed(() => pagination.value?.pages || 1)

    const filteredServices = computed(() => {
      if (!services.value) return []

      let result = [...services.value]

      // Filter by search term
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(
          (service) =>
            service.name.toLowerCase().includes(query) ||
            service.description.toLowerCase().includes(query),
        )
      }

      return result
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

    // Methods
    const fetchServices = async () => {
      await store.dispatch('services/fetchAllServices', {
        page: currentPage.value,
        perPage: perPage.value,
      })
    }

    const formatTime = (minutes) => {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60

      if (hours > 0) {
        return `${hours}h${mins > 0 ? ` ${mins}m` : ''}`
      }

      return `${mins}m`
    }

    const formatDate = (dateString) => {
      return moment(dateString).format('MMM DD, YYYY h:mm A')
    }

    const resetForm = () => {
      serviceForm.name = ''
      serviceForm.description = ''
      serviceForm.base_price = 0
      serviceForm.estimated_time = 60
      serviceForm.is_active = true

      // Clear validation errors
      Object.keys(formErrors).forEach((key) => {
        formErrors[key] = ''
      })
    }

    const showCreateModal = () => {
      resetForm()
      isEditMode.value = false
      bsServiceModal.show()
    }

    const showEditModal = (service) => {
      // If coming from details modal, close it first
      if (bsDetailsModal._isShown) {
        bsDetailsModal.hide()
      }

      resetForm()
      isEditMode.value = true

      // Populate form with service data
      serviceForm.name = service.name
      serviceForm.description = service.description
      serviceForm.base_price = service.base_price
      serviceForm.estimated_time = service.estimated_time
      serviceForm.is_active = service.is_active

      selectedService.value = service
      bsServiceModal.show()
    }

    const showDetailsModal = (service) => {
      selectedService.value = service
      bsDetailsModal.show()
    }

    const confirmDelete = (service) => {
      selectedService.value = service
      bsDeleteModal.show()
    }

    const validateForm = () => {
      let isValid = true

      // Reset validation errors
      Object.keys(formErrors).forEach((key) => {
        formErrors[key] = ''
      })

      // Name validation
      if (!serviceForm.name.trim()) {
        formErrors.name = 'Service name is required'
        isValid = false
      } else if (serviceForm.name.length < 4) {
        formErrors.name = 'Service name must be at least 4 characters'
        isValid = false
      }

      // Description validation
      if (!serviceForm.description.trim()) {
        formErrors.description = 'Description is required'
        isValid = false
      }

      // Price validation
      if (serviceForm.base_price <= 0) {
        formErrors.base_price = 'Base price must be greater than 0'
        isValid = false
      }

      // Time validation
      if (serviceForm.estimated_time <= 0) {
        formErrors.estimated_time = 'Estimated time must be greater than 0'
        isValid = false
      }

      return isValid
    }

    const saveService = async () => {
      if (!validateForm()) return

      isSubmitting.value = true

      try {
        if (isEditMode.value) {
          // Update existing service
          await store.dispatch('services/updateService', {
            id: selectedService.value.id,
            data: {
              name: serviceForm.name,
              description: serviceForm.description,
              basePrice: serviceForm.base_price,
              estimatedTime: serviceForm.estimated_time,
              isActive: serviceForm.is_active,
            },
          })

          window.showToast({
            type: 'success',
            title: 'Service Updated',
            message: `${serviceForm.name} has been updated successfully.`,
          })
        } else {
          // Create new service
          await store.dispatch('services/createService', {
            name: serviceForm.name,
            description: serviceForm.description,
            basePrice: serviceForm.base_price,
            estimatedTime: serviceForm.estimated_time,
          })

          window.showToast({
            type: 'success',
            title: 'Service Created',
            message: `${serviceForm.name} has been added successfully.`,
          })
        }

        bsServiceModal.hide()
        fetchServices()
      } catch (err) {
        // Handle specific errors
        if (err.response?.data?.error_type === 'DuplicateService') {
          formErrors.name = 'A service with this name already exists'
        }
      } finally {
        isSubmitting.value = false
      }
    }

    const toggleServiceStatus = async (service) => {
      await store.dispatch('services/toggleService', service.id)

      window.showToast({
        type: 'success',
        title: service.is_active ? 'Service Deactivated' : 'Service Activated',
        message: `${service.name} has been ${service.is_active ? 'deactivated' : 'activated'} successfully.`,
      })

      fetchServices()
    }

    const deleteService = async () => {
      if (!selectedService.value) return

      isDeleting.value = true

      try {
        await store.dispatch('services/deleteService', selectedService.value.id)

        window.showToast({
          type: 'success',
          title: 'Service Deleted',
          message: `${selectedService.value.name} has been deleted successfully.`,
        })

        bsDeleteModal.hide()
        fetchServices()
        // eslint-disable-next-line no-unused-vars
      } catch (err) {
        // Error toast is shown via API response handler
      } finally {
        isDeleting.value = false
      }
    }

    const changePage = (page) => {
      if (page < 1 || page > totalPages.value) return

      currentPage.value = page
      fetchServices()
    }

    const handleSearch = () => {
      if (searchQuery.value.length > 2 || searchQuery.value.length === 0) {
        currentPage.value = 1
        fetchServices()
      }
    }

    const clearSearch = () => {
      searchQuery.value = ''
      fetchServices()
    }

    const canDelete = (service) => {
      // Only allow deletion of services that have never been used
      // In a real app, you might check if the service has any associated requests
      return !service.is_active
    }

    // Lifecycle hooks
    onMounted(() => {
      // Initialize Bootstrap modals
      if (serviceModal.value) {
        bsServiceModal = new bootstrap.Modal(serviceModal.value)
      }

      if (detailsModal.value) {
        bsDetailsModal = new bootstrap.Modal(detailsModal.value)
      }

      if (deleteModal.value) {
        bsDeleteModal = new bootstrap.Modal(deleteModal.value)
      }

      // Initial data fetch
      fetchServices()
    })

    return {
      // Refs and state
      services,
      isLoading,
      error,
      serviceModal,
      detailsModal,
      deleteModal,
      currentPage,
      totalPages,
      selectedService,
      searchQuery,
      serviceForm,
      formErrors,
      isEditMode,
      isSubmitting,
      isDeleting,

      // Computed
      filteredServices,
      totalServices,
      displayedPages,

      // Methods
      fetchServices,
      formatTime,
      formatDate,
      showCreateModal,
      showEditModal,
      showDetailsModal,
      saveService,
      confirmDelete,
      deleteService,
      toggleServiceStatus,
      changePage,
      handleSearch,
      clearSearch,
      canDelete,
    }
  },
}
</script>

<style scoped>
.badge {
  font-size: 0.8rem;
}

.btn-group .btn {
  padding: 0.25rem 0.5rem;
}

.form-switch {
  padding-left: 2.5em;
}

.dropdown-menu .dropdown-item {
  padding: 0.25rem 1rem;
}

.description-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 400px;
}

/* Loading spinner animations */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.table td,
.table th {
  padding: 0.75rem;
}
</style>
