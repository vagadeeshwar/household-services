<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Service Management</h1>
        <p class="text-muted">Manage all household services from one place</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal">
        <i class="bi bi-plus-circle me-2"></i>Add Service
      </button>
    </div>

    <!-- Filters -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Search</label>
            <div class="input-group">
              <input
                type="text"
                class="form-control"
                placeholder="Search services..."
                v-model="filters.search"
                @input="debouncedSearch"
              />
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="clearSearch"
                :disabled="!filters.search"
              >
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>
          <div class="col-md-3">
            <label class="form-label">Status</label>
            <select class="form-select" v-model="filters.status" @change="applyFilters">
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Sort By</label>
            <select class="form-select" v-model="filters.sortBy" @change="applyFilters">
              <option value="id">ID</option>
              <option value="name">Name</option>
              <option value="base_price">Price</option>
              <option value="estimated_time">Duration</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Order</label>
            <div class="d-flex">
              <select class="form-select" v-model="filters.sortOrder" @change="applyFilters">
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
              <button class="btn btn-outline-secondary ms-2" @click="resetFilters">
                <i class="bi bi-arrow-counterclockwise"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
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
      <button @click="fetchServices(true)" class="btn btn-sm btn-outline-danger ms-2">Retry</button>
    </div>

    <!-- Services Table -->
    <div v-else class="card shadow-sm">
      <div class="card-header bg-white py-3">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Services</h5>
          <span class="badge bg-primary">{{ filteredServices.length }} services</span>
        </div>
      </div>

      <!-- Table for medium and larger screens -->
      <div class="table-responsive d-none d-md-block">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th scope="col" @click="sortBy('id')" class="sortable-header">
                ID
                <i v-if="filters.sortBy === 'id'" :class="getSortIcon()"></i>
              </th>
              <th scope="col" @click="sortBy('name')" class="sortable-header">
                Service Name
                <i v-if="filters.sortBy === 'name'" :class="getSortIcon()"></i>
              </th>
              <th scope="col" @click="sortBy('base_price')" class="sortable-header">
                Base Price
                <i v-if="filters.sortBy === 'base_price'" :class="getSortIcon()"></i>
              </th>
              <th scope="col" @click="sortBy('estimated_time')" class="sortable-header">
                Duration
                <i v-if="filters.sortBy === 'estimated_time'" :class="getSortIcon()"></i>
              </th>
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
              <td>
                <div class="d-flex align-items-center">
                  <i class="bi bi-tools me-2 text-muted"></i>
                  <div>
                    <div class="fw-semibold">{{ service.name }}</div>
                    <div class="small text-muted text-truncate" style="max-width: 250px">
                      {{ service.description }}
                    </div>
                  </div>
                </div>
              </td>
              <td>₹{{ service.base_price.toFixed(2) }}</td>
              <td>{{ formatDuration(service.estimated_time) }}</td>
              <td>
                <span
                  :class="[
                    'badge',
                    service.is_active ? 'bg-success' : 'bg-secondary',
                    'position-relative',
                  ]"
                >
                  {{ service.is_active ? 'Active' : 'Inactive' }}
                  <span
                    v-if="service.is_active"
                    class="position-absolute top-0 start-100 translate-middle p-1 bg-success border border-light rounded-circle"
                  >
                    <span class="visually-hidden">Active indicator</span>
                  </span>
                </span>
              </td>
              <td>
                <div class="d-flex justify-content-end">
                  <button
                    class="btn btn-sm btn-outline-primary me-1"
                    @click="showDetailsModal(service)"
                    title="View Details"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button
                    class="btn btn-sm btn-outline-secondary me-1"
                    @click="showEditModal(service)"
                    title="Edit Service"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button
                    class="btn btn-sm"
                    :class="[service.is_active ? 'btn-outline-warning' : 'btn-outline-success']"
                    @click="toggleServiceStatus(service)"
                    :title="service.is_active ? 'Deactivate Service' : 'Activate Service'"
                  >
                    <i
                      class="bi"
                      :class="[service.is_active ? 'bi-toggle-on' : 'bi-toggle-off']"
                    ></i>
                  </button>
                  <button
                    class="btn btn-sm btn-outline-danger ms-1"
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

      <!-- Card view for small screens -->
      <div class="d-md-none">
        <div v-if="filteredServices.length === 0" class="text-center py-4 text-muted">
          <i class="bi bi-search me-2"></i>No services found
        </div>
        <div v-else class="list-group list-group-flush">
          <div v-for="service in filteredServices" :key="service.id" class="list-group-item p-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="mb-0">{{ service.name }}</h6>
              <span :class="['badge', service.is_active ? 'bg-success' : 'bg-secondary']">
                {{ service.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <div class="small text-muted mb-2">{{ service.description }}</div>
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="badge bg-light text-dark me-2">
                  ₹{{ service.base_price.toFixed(2) }}
                </div>
                <div class="badge bg-light text-dark">
                  {{ formatDuration(service.estimated_time) }}
                </div>
              </div>
              <div class="btn-group">
                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="showDetailsModal(service)"
                  title="View Details"
                >
                  <i class="bi bi-eye"></i>
                </button>
                <button
                  class="btn btn-sm btn-outline-secondary"
                  @click="showEditModal(service)"
                  title="Edit Service"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button
                  class="btn btn-sm"
                  :class="[service.is_active ? 'btn-outline-warning' : 'btn-outline-success']"
                  @click="toggleServiceStatus(service)"
                >
                  <i class="bi" :class="[service.is_active ? 'bi-toggle-on' : 'bi-toggle-off']"></i>
                </button>
                <button
                  class="btn btn-sm btn-outline-danger"
                  @click="confirmDelete(service)"
                  :disabled="!canDelete(service)"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="card-footer bg-white py-3">
        <div class="row align-items-center">
          <div class="col-lg-4 col-md-6 text-muted mb-2 mb-md-0">
            Showing {{ filteredServices.length }} of {{ totalServices }} services
          </div>
          <div class="col-lg-8 col-md-6">
            <ul class="pagination mb-0 justify-content-md-end">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button @click="changePage(currentPage - 1)" class="page-link">
                  <i class="bi bi-chevron-left"></i>
                </button>
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
                <button @click="changePage(currentPage + 1)" class="page-link">
                  <i class="bi bi-chevron-right"></i>
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Service Modal -->
    <div class="modal fade" id="serviceModal" tabindex="-1" ref="serviceModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-tools me-2"></i>
              {{ isEditMode ? 'Edit Service' : 'Add New Service' }}
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveService" id="serviceForm">
              <div class="row mb-3">
                <div class="col-md-8">
                  <label for="serviceName" class="form-label"
                    >Service Name <span class="text-danger">*</span></label
                  >
                  <input
                    type="text"
                    class="form-control"
                    id="serviceName"
                    v-model="serviceForm.name"
                    :class="{ 'is-invalid': formErrors.name }"
                    required
                    autofocus
                  />
                  <div class="invalid-feedback">
                    {{ formErrors.name }}
                  </div>
                  <div class="form-text">Choose a clear, descriptive name for the service.</div>
                </div>
                <div class="col-md-4" v-if="isEditMode">
                  <label class="form-label d-block">Status</label>
                  <div class="form-check form-switch form-check-inline">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      id="statusSwitch"
                      v-model="serviceForm.is_active"
                      role="switch"
                    />
                    <label class="form-check-label" for="statusSwitch">
                      {{ serviceForm.is_active ? 'Active' : 'Inactive' }}
                    </label>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="description" class="form-label"
                  >Description <span class="text-danger">*</span></label
                >
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
                <div class="form-text">
                  Provide a detailed description of what the service includes.
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="basePrice" class="form-label"
                    >Base Price (₹) <span class="text-danger">*</span></label
                  >
                  <div class="input-group">
                    <span class="input-group-text">₹</span>
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
                  <div class="form-text">The starting price for this service.</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="estTime" class="form-label"
                    >Estimated Time (minutes) <span class="text-danger">*</span></label
                  >
                  <div class="input-group">
                    <input
                      type="number"
                      class="form-control"
                      id="estTime"
                      v-model="serviceForm.estimated_time"
                      :class="{ 'is-invalid': formErrors.estimated_time }"
                      min="1"
                      required
                    />
                    <span class="input-group-text">minutes</span>
                    <div class="invalid-feedback">
                      {{ formErrors.estimated_time }}
                    </div>
                  </div>
                  <div class="form-text">Average time required to complete this service.</div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="submit"
              form="serviceForm"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isEditMode ? 'Update Service' : 'Create Service' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Details Modal -->
    <div class="modal fade" id="detailsModal" tabindex="-1" ref="detailsModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><i class="bi bi-info-circle me-2"></i>Service Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body" v-if="selectedService">
            <div class="card">
              <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="card-title mb-0">{{ selectedService.name }}</h5>
                  <span
                    :class="['badge', selectedService.is_active ? 'bg-success' : 'bg-secondary']"
                  >
                    {{ selectedService.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>
              <div class="card-body">
                <div class="row mb-4">
                  <div class="col-md-6">
                    <div class="d-flex align-items-center mb-3">
                      <div class="icon-box bg-primary-subtle me-3">
                        <i class="bi bi-currency-rupee text-primary"></i>
                      </div>
                      <div>
                        <h6 class="mb-0 text-muted">Base Price</h6>
                        <div class="h4 mb-0">₹{{ selectedService.base_price.toFixed(2) }}</div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="d-flex align-items-center mb-3">
                      <div class="icon-box bg-success-subtle me-3">
                        <i class="bi bi-clock text-success"></i>
                      </div>
                      <div>
                        <h6 class="mb-0 text-muted">Estimated Time</h6>
                        <div class="h4 mb-0">
                          {{ formatDuration(selectedService.estimated_time) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <h6 class="text-muted mb-2">Description</h6>
                <p class="bg-light p-3 rounded">{{ selectedService.description }}</p>

                <div class="row mt-4">
                  <div class="col-md-6">
                    <div class="small text-muted mb-1">Service ID</div>
                    <p>{{ selectedService.id }}</p>
                  </div>
                  <div class="col-md-6">
                    <div class="small text-muted mb-1">Status</div>
                    <p>
                      <span
                        :class="[
                          'badge',
                          selectedService.is_active ? 'bg-success' : 'bg-secondary',
                        ]"
                      >
                        {{ selectedService.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </p>
                  </div>
                  <div class="col-md-6">
                    <div class="small text-muted mb-1">Created On</div>
                    <p>{{ formatDateTime(selectedService.created_at) }}</p>
                  </div>
                  <div class="col-md-6">
                    <div class="small text-muted mb-1">Last Updated</div>
                    <p>
                      {{
                        selectedService.updated_at
                          ? formatDateTime(selectedService.updated_at)
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
            <button
              type="button"
              class="btn btn-outline-primary"
              @click="showEditModal(selectedService)"
            >
              <i class="bi bi-pencil me-1"></i> Edit
            </button>
            <button
              type="button"
              class="btn"
              :class="[
                selectedService && selectedService.is_active
                  ? 'btn-outline-warning'
                  : 'btn-outline-success',
              ]"
              @click="toggleServiceStatus(selectedService)"
            >
              <i
                class="bi"
                :class="[
                  selectedService && selectedService.is_active ? 'bi-toggle-on' : 'bi-toggle-off',
                ]"
              ></i>
              {{ selectedService && selectedService.is_active ? 'Deactivate' : 'Activate' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              Confirm Delete
            </h5>
            <button
              type="button"
              class="btn-close btn-close-white"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="text-center mb-3">
              <i class="bi bi-trash-fill text-danger" style="font-size: 3rem"></i>
            </div>
            <p class="mb-1">Are you sure you want to delete this service?</p>
            <div class="alert alert-warning">
              <strong>{{ selectedService?.name }}</strong>
              <p class="small mb-0">
                This action cannot be undone. Only inactive services can be deleted.
              </p>
            </div>
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
              {{ isDeleting ? 'Deleting...' : 'Delete Service' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as bootstrap from 'bootstrap'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useStore } from 'vuex'
import { formatDateTime, formatDuration } from '@/utils/date'

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
    const isEditMode = ref(false)
    const isSubmitting = ref(false)
    const isDeleting = ref(false)
    const selectedService = ref(null)
    const filters = reactive({
      search: '',
      status: 'all',
      sortBy: 'id',
      sortOrder: 'asc',
    })

    // Search debounce timer
    let searchTimer = null

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

      // Filter by status
      if (filters.status !== 'all') {
        const isActive = filters.status === 'active'
        result = result.filter((service) => service.is_active === isActive)
      }

      // Filter by search term
      if (filters.search) {
        const query = filters.search.toLowerCase()
        result = result.filter(
          (service) =>
            service.name.toLowerCase().includes(query) ||
            service.description.toLowerCase().includes(query),
        )
      }

      // Sort services
      result = [...result].sort((a, b) => {
        let valA = a[filters.sortBy]
        let valB = b[filters.sortBy]

        // Handle string comparisons
        if (typeof valA === 'string') {
          valA = valA.toLowerCase()
          valB = valB.toLowerCase()
        }

        if (filters.sortOrder === 'asc') {
          return valA > valB ? 1 : -1
        } else {
          return valA < valB ? 1 : -1
        }
      })

      return result
    })

    const displayedPages = computed(() => {
      const pages = []
      const maxVisiblePages = 5
      const totalPg = totalPages.value || 1

      let startPage = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
      let endPage = Math.min(totalPg, startPage + maxVisiblePages - 1)

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1)
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      return pages
    })

    // Methods
    const fetchServices = async (forceRefresh = false) => {
      try {
        await store.dispatch('services/fetchAllServices', {
          params: {
            page: currentPage.value,
            per_page: perPage.value,
          },
          forceRefresh: forceRefresh,
        })
      } catch (err) {
        console.error('Error fetching services:', err)
      }
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
      } else if (serviceForm.name.length > 100) {
        formErrors.name = 'Service name cannot exceed 100 characters'
        isValid = false
      }

      // Description validation
      if (!serviceForm.description.trim()) {
        formErrors.description = 'Description is required'
        isValid = false
      } else if (serviceForm.description.length < 10) {
        formErrors.description =
          'Please provide a more detailed description (at least 10 characters)'
        isValid = false
      } else if (serviceForm.description.length > 1000) {
        formErrors.description = 'Description cannot exceed 1000 characters'
        isValid = false
      }

      // Price validation
      if (serviceForm.base_price <= 0) {
        formErrors.base_price = 'Base price must be greater than 0'
        isValid = false
      } else if (serviceForm.base_price > 100000) {
        formErrors.base_price = 'Base price cannot exceed ₹100,000'
        isValid = false
      }

      // Time validation
      if (serviceForm.estimated_time <= 0) {
        formErrors.estimated_time = 'Estimated time must be greater than 0'
        isValid = false
      } else if (serviceForm.estimated_time > 480) {
        formErrors.estimated_time = 'Estimated time cannot exceed 8 hours (480 minutes)'
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
              base_price: serviceForm.base_price,
              estimated_time: serviceForm.estimated_time,
              is_active: serviceForm.is_active,
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
            data: {
              name: serviceForm.name,
              description: serviceForm.description,
              base_price: serviceForm.base_price,
              estimated_time: serviceForm.estimated_time,
            },
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
        } else {
          window.showToast({
            type: 'error',
            title: 'Error',
            message: err.response?.data?.message || 'An error occurred while saving the service.',
          })
        }
      } finally {
        isSubmitting.value = false
      }
    }

    const toggleServiceStatus = async (service) => {
      if (!service) return

      try {
        await store.dispatch('services/toggleService', {
          id: service.id,
        })

        // If the details modal is open, update the selected service status
        if (selectedService.value && selectedService.value.id === service.id) {
          selectedService.value.is_active = !selectedService.value.is_active
        }

        window.showToast({
          type: 'success',
          title: service.is_active ? 'Service Deactivated' : 'Service Activated',
          message: `${service.name} has been ${service.is_active ? 'deactivated' : 'activated'} successfully.`,
        })

        fetchServices()
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message:
            err.response?.data?.message || 'An error occurred while updating service status.',
        })
      }
    }

    const deleteService = async () => {
      if (!selectedService.value) return

      isDeleting.value = true

      try {
        await store.dispatch('services/deleteService', {
          id: selectedService.value.id,
        })

        window.showToast({
          type: 'success',
          title: 'Service Deleted',
          message: `${selectedService.value.name} has been deleted successfully.`,
        })

        bsDeleteModal.hide()
        fetchServices()
      } catch (err) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: err.response?.data?.message || 'An error occurred while deleting the service.',
        })
      } finally {
        isDeleting.value = false
      }
    }

    const changePage = (page) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      fetchServices()
    }

    const debouncedSearch = () => {
      clearTimeout(searchTimer)
      searchTimer = setTimeout(() => {
        applyFilters()
      }, 300)
    }

    const clearSearch = () => {
      filters.search = ''
      applyFilters()
    }

    const resetFilters = () => {
      filters.search = ''
      filters.status = 'all'
      filters.sortBy = 'id'
      filters.sortOrder = 'asc'
      applyFilters()
    }

    const applyFilters = () => {
      currentPage.value = 1
      fetchServices()
    }

    const sortBy = (column) => {
      if (filters.sortBy === column) {
        // Toggle sort order if clicking on the same column
        filters.sortOrder = filters.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        // Set new sort column and default to ascending
        filters.sortBy = column
        filters.sortOrder = 'asc'
      }
      applyFilters()
    }

    const getSortIcon = () => {
      return filters.sortOrder === 'asc' ? 'bi-caret-up-fill' : 'bi-caret-down-fill'
    }

    const canDelete = (service) => {
      // Only allow deletion of inactive services
      return !service.is_active
    }

    // Watch for filter changes
    watch([() => filters.status, () => filters.sortBy, () => filters.sortOrder], () => {
      applyFilters()
    })

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
      serviceForm,
      formErrors,
      isEditMode,
      isSubmitting,
      isDeleting,
      filters,

      // Computed
      filteredServices,
      totalServices,
      displayedPages,

      // Methods
      fetchServices,
      formatDuration,
      formatDateTime,
      showCreateModal,
      showEditModal,
      showDetailsModal,
      saveService,
      confirmDelete,
      deleteService,
      toggleServiceStatus,
      changePage,
      debouncedSearch,
      clearSearch,
      resetFilters,
      applyFilters,
      sortBy,
      getSortIcon,
      canDelete,
    }
  },
}
</script>

<style scoped>
.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-box i {
  font-size: 1.5rem;
}

.sortable-header {
  cursor: pointer;
  user-select: none;
}

.sortable-header:hover {
  background-color: #f8f9fa;
}

.form-switch {
  padding-left: 2.5em;
}

/* Badge with dot indicator */
.badge.position-relative {
  padding-right: 1.5rem;
}

/* Custom form validation styles */
.form-control.is-invalid,
.form-select.is-invalid,
.form-check-input.is-invalid {
  border-color: #dc3545;
  box-shadow: 0 0 0 0.25rem rgba(220, 53, 69, 0.25);
}

/* Toast styles */
.toast {
  opacity: 1 !important;
}

/* For small screens */
@media (max-width: 768px) {
  .btn-group .btn {
    padding: 0.25rem 0.5rem;
  }

  .pagination {
    justify-content: center !important;
  }

  .icon-box {
    width: 40px;
    height: 40px;
  }

  .icon-box i {
    font-size: 1.25rem;
  }
}
</style>
