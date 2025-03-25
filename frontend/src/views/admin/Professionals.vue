<template>
  <div class="container py-4">
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">Manage Professionals</h1>
        <p class="text-muted">Verify, block, and manage service professionals</p>
      </div>
      <!-- Add Export Report Button -->
      <div class="col-auto">
        <button class="btn btn-outline-primary" @click="openExportModal">
          <i class="bi bi-file-earmark-arrow-down me-1"></i> Generate Service Report
        </button>
      </div>
    </div>
    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label for="verificationStatus" class="form-label">Verification Status</label>
            <select
              id="verificationStatus"
              class="form-select"
              v-model="filters.verified"
              @change="applyFilters"
            >
              <option value="">All Statuses</option>
              <option :value="true">Verified</option>
              <option :value="false">Unverified</option>
            </select>
          </div>
          <div class="col-md-3">
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
                placeholder="Search by name or email"
                v-model="searchTerm"
                @input="handleSearchInput"
              />
              <button class="btn btn-outline-secondary" type="button" @click="applyFilters">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label d-block">&nbsp;</label>
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- Professionals Table -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="isLoading" class="text-center p-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading professionals...</p>
        </div>
        <div v-else-if="professionals.length === 0" class="text-center p-5">
          <i class="bi bi-people text-muted" style="font-size: 3rem"></i>
          <p class="mt-3 mb-0">No professionals found matching the criteria.</p>
          <button class="btn btn-link mt-2" @click="resetFilters">Reset filters</button>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover table-striped mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th scope="col">Service</th>
                <th scope="col">Experience</th>
                <th scope="col">Verification</th>
                <th scope="col">Rating</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="professional in filteredProfessionals" :key="professional.professional_id">
                <td>{{ professional.professional_id }}</td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar me-2 bg-light rounded-circle">
                      <i class="bi bi-person"></i>
                    </div>
                    <div>
                      <div class="fw-bold">{{ professional.full_name }}</div>
                      <small class="text-muted">{{ professional.email }}</small>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="badge bg-info">{{
                    getServiceName(professional.service_type_id)
                  }}</span>
                </td>
                <td>{{ professional.experience_years }} years</td>
                <td>
                  <span
                    :class="[
                      'badge',
                      professional.is_verified ? 'bg-success' : 'bg-warning',
                      'me-2',
                    ]"
                  >
                    {{ professional.is_verified ? 'Verified' : 'Pending' }}
                  </span>
                  <span :class="['badge', professional.is_active ? 'bg-success' : 'bg-danger']">
                    {{ professional.is_active ? 'Active' : 'Blocked' }}
                  </span>
                </td>
                <td>
                  <div class="d-flex align-items-center">
                    <i class="bi bi-star-fill text-warning me-1"></i>
                    <span>{{ professional.average_rating || 'N/A' }}</span>
                  </div>
                </td>
                <td>
                  <div class="btn-group">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="viewProfessional(professional)"
                      title="View details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <!-- Only show verify for unverified -->
                    <button
                      v-if="!professional.is_verified"
                      class="btn btn-sm btn-outline-success"
                      @click="confirmVerify(professional)"
                      title="Verify professional"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>
                    <!-- Only show block/unblock for verified professionals -->
                    <button
                      v-if="professional.is_verified"
                      class="btn btn-sm"
                      :class="professional.is_active ? 'btn-outline-danger' : 'btn-outline-success'"
                      @click="toggleBlockStatus(professional)"
                      :title="professional.is_active ? 'Block account' : 'Unblock account'"
                    >
                      <i
                        class="bi"
                        :class="professional.is_active ? 'bi-slash-circle' : 'bi-unlock'"
                      ></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <!-- Pagination -->
      <div class="card-footer bg-white d-flex justify-content-between align-items-center">
        <div>
          <span class="text-muted"
            >Showing {{ professionals.length }} of {{ pagination.total || 0 }} professionals</span
          >
        </div>
        <nav aria-label="Professionals pagination" v-if="pagination.pages > 1">
          <ul class="pagination pagination-sm mb-0">
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
              <a class="page-link" href="#" @click.prevent="changePage(page)">
                {{ page }}
              </a>
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
                  <div class="d-flex justify-content-center align-items-center">
                    <span
                      :class="[
                        'badge',
                        selectedProfessional.is_verified ? 'bg-success' : 'bg-warning',
                        'me-2',
                      ]"
                    >
                      {{ selectedProfessional.is_verified ? 'Verified' : 'Pending' }}
                    </span>
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
              </div>
              <div class="col-md-8">
                <h6 class="mb-3">Account Information</h6>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Email</label>
                      <div>{{ selectedProfessional.email }}</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Phone</label>
                      <div>{{ selectedProfessional.phone }}</div>
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label text-muted small">Address</label>
                  <div>{{ selectedProfessional.address }}</div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">PIN Code</label>
                      <div>{{ selectedProfessional.pin_code }}</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Experience</label>
                      <div>{{ selectedProfessional.experience_years }} years</div>
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label text-muted small">Rating</label>
                  <div class="d-flex align-items-center">
                    <div class="me-2">
                      <i class="bi bi-star-fill text-warning"></i>
                      <strong>{{ selectedProfessional.average_rating || 'N/A' }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <hr />
            <div class="row">
              <div class="col-12">
                <h6 class="mb-3">Professional Description</h6>
                <p>{{ selectedProfessional.description || 'No description provided.' }}</p>
              </div>
            </div>
            <hr />
            <div class="row">
              <div class="col-12">
                <h6 class="mb-3">Verification Document</h6>
                <div v-if="selectedProfessional.verification_documents">
                  <p class="mb-2">
                    <i class="bi bi-file-earmark-text me-2"></i>
                    {{ selectedProfessional.verification_documents }}
                  </p>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="downloadDocument(selectedProfessional.professional_id)"
                  >
                    <i class="bi bi-download me-1"></i> Download Document
                  </button>
                </div>
                <p v-else class="text-muted">No verification document uploaded.</p>
              </div>
            </div>
            <hr />
            <div class="row">
              <div class="col-12">
                <h6 class="mb-3">Additional Information</h6>
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Member Since</label>
                      <div>{{ formatDate(selectedProfessional.created_at) }}</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-2">
                      <label class="form-label text-muted small">Last Login</label>
                      <div>{{ formatDateTime(selectedProfessional.last_login) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <hr class="my-4" />
          <!-- Recent Service Requests -->
          <div class="row">
            <div class="col-12 px-4">
              <!-- Added px-4 for horizontal padding -->
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="mb-0">Recent Service Requests</h6>
                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="viewAllProfessionalRequests"
                  v-if="professionalRequests.length > 0"
                >
                  <i class="bi bi-eye me-1"></i> View All
                </button>
              </div>
              <div v-if="isLoadingRequests" class="text-center py-4">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted mt-2 mb-0">Loading service requests...</p>
              </div>
              <div v-else-if="professionalRequests.length === 0" class="alert alert-info py-3">
                <i class="bi bi-info-circle me-2"></i>
                This professional has no service requests yet.
              </div>
              <div v-else class="table-responsive mt-2 mb-3">
                <!-- Added mb-3 for bottom margin -->
                <table class="table table-sm table-hover border">
                  <thead class="table-light">
                    <tr>
                      <th class="px-3 py-2">ID</th>
                      <th class="px-3 py-2">Service</th>
                      <th class="px-3 py-2">Date</th>
                      <th class="px-3 py-2">Customer</th>
                      <th class="px-3 py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="request in professionalRequests"
                      :key="request.id"
                      class="align-middle"
                    >
                      <td class="px-3 py-2">#{{ request.id }}</td>
                      <td class="px-3 py-2">
                        <div class="d-flex align-items-center">
                          <div>
                            <div class="fw-medium">{{ request.service_name }}</div>
                            <small class="text-muted">₹{{ request.service_price }}</small>
                          </div>
                        </div>
                      </td>
                      <td class="px-3 py-2">
                        <div>{{ formatDate(request.date_of_request) }}</div>
                        <small class="text-muted">{{ formatTime(request.preferred_time) }}</small>
                      </td>
                      <td class="px-3 py-2">
                        <div v-if="request.customer">{{ request.customer.full_name }}</div>
                        <span v-else class="text-muted">Unknown Customer</span>
                      </td>
                      <td class="px-3 py-2">
                        <span class="badge" :class="getStatusBadgeClass(request.status)">
                          {{ getStatusLabel(request.status) }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
    <!-- Confirmation Modals -->
    <div
      class="modal fade"
      id="confirmActionModal"
      tabindex="-1"
      aria-labelledby="confirmActionModalLabel"
      aria-hidden="true"
      ref="confirmModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="confirmActionModalLabel">
              {{ confirmAction.title }}
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p>{{ confirmAction.message }}</p>
            <div v-if="confirmAction.type === 'block'">
              <label for="blockReason" class="form-label">Reason for blocking</label>
              <textarea
                id="blockReason"
                class="form-control"
                rows="3"
                v-model="blockReason"
                placeholder="Please provide a reason for blocking this professional"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              :class="['btn', confirmAction.buttonClass]"
              @click="executeConfirmedAction"
            >
              {{ confirmAction.buttonText }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Report Modal -->
    <div
      class="modal fade"
      id="exportReportModal"
      tabindex="-1"
      aria-labelledby="exportReportModalLabel"
      aria-hidden="true"
      ref="exportModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exportReportModalLabel">
              <i class="bi bi-file-earmark-arrow-down me-2"></i>
              Generate Service Requests Report
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
              :disabled="isExporting"
            ></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <i class="bi bi-info-circle-fill me-2"></i>
              Generate a CSV report of service requests. You can filter by professional and date
              range.
            </div>

            <div class="mb-3">
              <label for="reportProfessional" class="form-label">Professional</label>
              <select
                class="form-select"
                id="reportProfessional"
                v-model="exportOptions.professional_id"
              >
                <option value="">All Professionals</option>
                <option
                  v-for="professional in verifiedProfessionals"
                  :key="professional.professional_id"
                  :value="professional.professional_id"
                >
                  {{ professional.full_name }}
                </option>
              </select>
              <div class="form-text">
                Select a professional or leave empty to include all verified professionals.
              </div>
            </div>

            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="startDate" class="form-label">Start Date</label>
                  <input
                    type="date"
                    class="form-control"
                    id="startDate"
                    v-model="exportOptions.start_date"
                  />
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="endDate" class="form-label">End Date</label>
                  <input
                    type="date"
                    class="form-control"
                    id="endDate"
                    v-model="exportOptions.end_date"
                  />
                </div>
              </div>
            </div>

            <!-- Export Status -->
            <div v-if="exportStatus" class="mt-4">
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h6 class="mb-0">Export Status</h6>
                  <span class="badge" :class="getExportStatusBadgeClass(exportStatus.state)">
                    {{ exportStatus.state }}
                  </span>
                </div>
                <div class="progress" style="height: 20px">
                  <div
                    class="progress-bar progress-bar-striped progress-bar-animated"
                    :class="{ 'bg-success': exportStatus.state === 'SUCCESS' }"
                    :style="{ width: getExportProgressPercentage() + '%' }"
                    role="progressbar"
                    aria-valuemin="0"
                    aria-valuemax="100"
                  >
                    {{ getExportProgressText() }}
                  </div>
                </div>
                <p class="mt-2 text-muted">{{ exportStatus.status || 'Preparing export...' }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
              :disabled="isExporting"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="generateReport"
              :disabled="isExporting || !isValidExportOptions"
            >
              <i
                class="bi"
                :class="isExporting ? 'bi-hourglass-split' : 'bi-file-earmark-arrow-down'"
              ></i>
              {{ isExporting ? 'Generating...' : 'Generate Report' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { defineComponent, ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

import * as bootstrap from 'bootstrap'
import { requestStatusBadges, statusLabels } from '@/assets/requestStatuses'
import { formatDate, formatDateTime, formatTime } from '@/utils/date'
import { useLoading } from '@/composables/useLoading'
export default defineComponent({
  name: 'AdminProfessionals',
  setup() {
    const store = useStore()
    const { isLoading, showLoading, hideLoading, withLoading } = useLoading()
    // References to modals
    const detailModal = ref(null)
    const confirmModal = ref(null)
    const exportModal = ref(null)
    let bsDetailModal = null
    let bsConfirmModal = null
    let bsExportModal = null

    const router = useRouter()

    // State
    const professionals = computed(() => store.getters['professionals/allProfessionals'])
    const pagination = computed(() => store.getters['professionals/pagination'])
    const professionalRequests = computed(() => store.getters['requests/allRequests'])
    const isLoadingRequests = computed(() => store.getters['requests/isLoading'])
    const services = ref([])
    const selectedProfessional = ref(null)
    const searchTerm = ref('')
    const filters = ref({
      verified: '',
      service_type: '',
      page: 1,
      per_page: 10,
    })
    const confirmAction = ref({
      title: '',
      message: '',
      buttonText: '',
      buttonClass: '',
      type: '',
      callback: null,
    })
    const blockReason = ref('')

    // Export functionality state
    const exportOptions = ref({
      professional_id: '',
      start_date: '',
      end_date: '',
    })
    const isExporting = ref(false)
    const exportStatus = ref(null)
    const exportTaskId = ref(null)
    let statusPollInterval = null

    // Verify date range is valid
    const isValidDateRange = computed(() => {
      if (!exportOptions.value.start_date || !exportOptions.value.end_date) {
        return true // Both dates are empty, which is allowed
      }

      const startDate = new Date(exportOptions.value.start_date)
      const endDate = new Date(exportOptions.value.end_date)

      // Ensure start date is not after end date
      return startDate <= endDate
    })

    const isValidExportOptions = computed(() => {
      return isValidDateRange.value
    })

    // Filter for only verified professionals
    const verifiedProfessionals = computed(() => {
      return professionals.value.filter((p) => p.is_verified)
    })

    // Export functionality methods
    const openExportModal = () => {
      // Reset export state
      exportOptions.value = {
        professional_id: '',
        start_date: '',
        end_date: '',
      }
      exportStatus.value = null
      exportTaskId.value = null
      clearExportStatusInterval()

      bsExportModal.show()
    }

    const getExportStatusBadgeClass = (state) => {
      const statusClasses = {
        PENDING: 'bg-warning',
        STARTED: 'bg-info',
        PROGRESS: 'bg-primary',
        SUCCESS: 'bg-success',
        FAILURE: 'bg-danger',
      }
      return statusClasses[state] || 'bg-secondary'
    }

    const getExportProgressPercentage = () => {
      if (!exportStatus.value) return 0

      const stateProgress = {
        PENDING: 10,
        STARTED: 30,
        PROGRESS: 60,
        SUCCESS: 100,
        FAILURE: 100,
      }

      return stateProgress[exportStatus.value.state] || 0
    }

    const getExportProgressText = () => {
      if (!exportStatus.value) return ''

      const stateText = {
        PENDING: 'Pending...',
        STARTED: 'Started...',
        PROGRESS: 'In Progress...',
        SUCCESS: 'Complete!',
        FAILURE: 'Failed',
      }

      return stateText[exportStatus.value.state] || ''
    }

    const startExportStatusPolling = (taskId) => {
      // Clear any existing interval
      clearExportStatusInterval()

      // Check status immediately
      checkExportStatus(taskId)

      // Then set up polling interval (every 2 seconds)
      statusPollInterval = setInterval(() => {
        checkExportStatus(taskId)
      }, 2000)
    }

    const clearExportStatusInterval = () => {
      if (statusPollInterval) {
        clearInterval(statusPollInterval)
        statusPollInterval = null
      }
    }

    const checkExportStatus = async (taskId) => {
      try {
        const response = await store.dispatch('exports/checkExportStatus', { id: taskId })
        exportStatus.value = response.data

        // If the export is complete (success or failure), stop polling
        if (['SUCCESS', 'FAILURE'].includes(response.data.state)) {
          clearExportStatusInterval()

          if (response.data.state === 'SUCCESS' && response.data.result?.filename) {
            // Automatically download the file
            await downloadExport(response.data.result.filename)

            // Show success notification
            window.showToast({
              type: 'success',
              title: 'Export Completed',
              message: `Successfully exported ${response.data.result.total_records} service requests`,
            })

            // Close the modal after successful download
            setTimeout(() => {
              bsExportModal.hide()
            }, 1500)
          } else if (response.data.state === 'FAILURE') {
            // Show error notification
            window.showToast({
              type: 'danger',
              title: 'Export Failed',
              message: response.data.error || 'Failed to generate the export',
            })
          }
        }
      } catch (error) {
        console.error('Error checking export status:', error)
        window.showToast({
          type: 'danger',
          title: 'Status Check Failed',
          message: 'Failed to check export status',
        })
        clearExportStatusInterval()
      }
    }

    const downloadExport = async (filename) => {
      try {
        await store.dispatch('exports/downloadReport', { data: filename })
      } catch (error) {
        console.error('Error downloading export:', error)
        window.showToast({
          type: 'danger',
          title: 'Download Failed',
          message: 'Failed to download the export file',
        })
      }
    }

    const generateReport = async () => {
      if (!isValidExportOptions.value) {
        window.showToast({
          type: 'warning',
          title: 'Invalid Options',
          message: 'Please check your export options',
        })
        return
      }

      try {
        isExporting.value = true

        // Prepare data for the export
        const exportData = {
          ...(exportOptions.value.professional_id && {
            professional_id: parseInt(exportOptions.value.professional_id),
          }),
          ...(exportOptions.value.start_date && { start_date: exportOptions.value.start_date }),
          ...(exportOptions.value.end_date && { end_date: exportOptions.value.end_date }),
        }

        // Start the export job
        const response = await store.dispatch('exports/generateServiceReport', { data: exportData })

        if (response && response.data && response.data.task_id) {
          exportTaskId.value = response.data.task_id
          exportStatus.value = {
            state: 'PENDING',
            status: 'Export job submitted, waiting for processing...',
          }

          // Start polling for status updates
          startExportStatusPolling(response.data.task_id)

          window.showToast({
            type: 'info',
            title: 'Export Started',
            message: 'The export job has been submitted and is being processed',
          })
        } else {
          throw new Error('Invalid response from export service')
        }
      } catch (error) {
        console.error('Error generating report:', error)
        window.showToast({
          type: 'danger',
          title: 'Export Failed',
          message: error.response?.data?.detail || 'Failed to start the export job',
        })
        isExporting.value = false
      }
    }

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
    const filteredProfessionals = computed(() => {
      if (!searchTerm.value.trim()) {
        return professionals.value
      }
      const term = searchTerm.value.toLowerCase().trim()
      return professionals.value.filter((professional) => {
        const fullName = professional.full_name?.toLowerCase() || ''
        const email = professional.email?.toLowerCase() || ''
        const username = professional.username?.toLowerCase() || ''
        return fullName.includes(term) || email.includes(term) || username.includes(term)
      })
    })
    // Methods
    const fetchProfessionals = async (forceRefresh = false) => {
      // Start with empty params object
      searchTerm.value = ''
      const params = {}
      // Only add non-empty filters
      Object.entries(filters.value).forEach(([key, value]) => {
        // Include parameters that have values (not empty strings, null, or undefined)
        if (value !== '' && value !== null && value !== undefined) {
          params[key] = value
        }
      })

      await withLoading(
        store.dispatch('professionals/fetchProfessionals', { params, forceRefresh }),
        'Loading professionals...',
      )
    }
    const fetchProfessionalRequests = async (professionalId) => {
      try {
        await store.dispatch('requests/fetchProfessionalRequestsById', {
          id: professionalId,
          params: {
            page: 1,
            per_page: 5, // Limit to 5 recent requests
            summary: false,
          },
          forceRefresh: false,
        })
      } catch (error) {
        console.error('Error fetching professional requests:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load professional requests',
        })
      }
    }
    const viewAllProfessionalRequests = () => {
      if (selectedProfessional.value) {
        router.push({
          name: 'AdminRequests',
          query: {
            professional_id: selectedProfessional.value.professional_id,
            professional_name: selectedProfessional.value.full_name,
          },
        })
        // Close the modal
        bsDetailModal.hide()
      }
    }
    const getStatusBadgeClass = (status) => requestStatusBadges[status]
    const getStatusLabel = (status) => statusLabels[status]
    const fetchServices = async () => {
      try {
        const response = await store.dispatch('services/fetchAllServices', {
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
      fetchProfessionalRequests(professional.professional_id)
    }
    const downloadDocument = async (professionalId) => {
      try {
        showLoading('Downloading document...')
        const response = await fetch(
          `${store.state.apiURL}/professionals/${professionalId}/document`,
          {
            headers: {
              Authorization: `Bearer ${store.getters['auth/token']}`,
            },
          },
        )
        if (!response.ok) {
          throw new Error('Failed to download document')
        }
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `professional-${professionalId}-verification.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        window.showToast({
          type: 'success',
          title: 'Document downloaded successfully',
        })
      } catch (error) {
        console.error('Error downloading document:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to download document. Please try again.',
        })
      } finally {
        hideLoading()
      }
    }
    const confirmVerify = (professional) => {
      confirmAction.value = {
        title: 'Verify Professional',
        message: `Are you sure you want to verify ${professional.full_name}? This will give them full access to accept service requests.`,
        buttonText: 'Verify',
        buttonClass: 'btn-success',
        type: 'verify',
        callback: () => verifyProfessional(professional),
      }
      bsConfirmModal.show()
    }
    const verifyProfessional = async (professional) => {
      try {
        showLoading('Verifying professional...')
        await store.dispatch('professionals/verifyProfessional', {
          id: professional.professional_id,
        })
        window.showToast({
          type: 'success',
          title: `${professional.full_name} has been verified successfully`,
        })
        // Refresh the professionals list
        await fetchProfessionals(true)
        // Hide modals
        bsConfirmModal.hide()
        if (bsDetailModal && bsDetailModal._isShown) {
          selectedProfessional.value.is_verified = true
        }
      } catch (error) {
        console.error('Error verifying professional:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to verify professional.',
        })
      } finally {
        hideLoading()
      }
    }
    const toggleBlockStatus = (professional) => {
      if (professional.is_active) {
        confirmAction.value = {
          title: 'Block Professional',
          message: `Are you sure you want to block ${professional.full_name}? This will prevent them from accessing the platform.`,
          buttonText: 'Block',
          buttonClass: 'btn-danger',
          type: 'block',
          callback: () => blockProfessional(professional, blockReason.value),
        }
      } else {
        confirmAction.value = {
          title: 'Unblock Professional',
          message: `Are you sure you want to unblock ${professional.full_name}? This will restore their access to the platform.`,
          buttonText: 'Unblock',
          buttonClass: 'btn-success',
          type: 'unblock',
          callback: () => unblockProfessional(professional),
        }
      }
      blockReason.value = ''
      bsConfirmModal.show()
    }
    const blockUnblockProfessional = (professional) => {
      toggleBlockStatus(professional)
    }
    const blockProfessional = async (professional, reason) => {
      if (!reason.trim()) {
        window.showToast({
          type: 'warning',
          title: 'Please provide a reason for blocking this professional',
        })
        return
      }
      try {
        showLoading('Blocking professional...')
        await store.dispatch('professionals/blockProfessional', {
          id: professional.professional_id,
          data: { reason: reason.trim() },
        })
        window.showToast({
          type: 'success',
          title: `${professional.full_name} has been blocked`,
        })
        // Refresh the professionals list
        await fetchProfessionals(true)
        // Hide modals
        bsConfirmModal.hide()
        if (bsDetailModal && bsDetailModal._isShown) {
          selectedProfessional.value.user.is_active = false
        }
      } catch (error) {
        console.error('Error blocking professional:', error)
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to block professional.',
        })
      } finally {
        hideLoading()
      }
    }
    const unblockProfessional = async (professional) => {
      try {
        showLoading('Unblocking professional...')
        await store.dispatch('professionals/unblockProfessional', {
          id: professional.professional_id,
        })
        window.showToast({
          type: 'success',
          title: `${professional.full_name} has been unblocked`,
        })
        // Refresh the professionals list
        await fetchProfessionals(true)
        // Hide modals
        bsConfirmModal.hide()
        if (bsDetailModal && bsDetailModal._isShown) {
          selectedProfessional.value.user.is_active = true
        }
      } catch (error) {
        console.error('Error unblocking professional:', error)
        window.showToast({
          type: 'danger',
          title:
            error.response?.data?.detail || 'Failed to unblock professional. Please try again.',
        })
      } finally {
        hideLoading()
      }
    }
    const executeConfirmedAction = () => {
      if (confirmAction.value.callback) {
        confirmAction.value.callback()
      }
    }
    const applyFilters = () => {
      filters.value.page = 1
      fetchProfessionals()
    }
    const handleSearchInput = () => {
      filters.value.page = 1
    }
    const resetFilters = () => {
      filters.value = {
        verified: '',
        service_type: '',
        page: 1,
        per_page: 10,
      }
      searchTerm.value = ''
      fetchProfessionals(true)
    }
    const changePage = (page) => {
      if (page < 1 || page > pagination.value.pages) return
      filters.value.page = page
      fetchProfessionals()
    }

    // Watch for export status changes
    watch(
      () => exportStatus.value?.state,
      (newState) => {
        if (newState === 'SUCCESS') {
          isExporting.value = false
        } else if (newState === 'FAILURE') {
          isExporting.value = false
        }
      },
    )

    // Cleanup on component unmount
    onUnmounted(() => {
      clearExportStatusInterval()
    })

    // Lifecycle Hooks
    onMounted(async () => {
      // Initialize modals
      if (detailModal.value) {
        bsDetailModal = new bootstrap.Modal(detailModal.value)
      }
      if (confirmModal.value) {
        bsConfirmModal = new bootstrap.Modal(confirmModal.value)
      }
      if (exportModal.value) {
        bsExportModal = new bootstrap.Modal(exportModal.value)
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
      confirmAction,
      blockReason,
      isLoading,
      // Export state
      exportOptions,
      isExporting,
      exportStatus,
      verifiedProfessionals,
      isValidExportOptions,
      // Refs
      detailModal,
      confirmModal,
      exportModal,
      // Methods
      fetchProfessionals,
      viewProfessional,
      getServiceName,
      confirmVerify,
      verifyProfessional,
      toggleBlockStatus,
      blockUnblockProfessional,
      downloadDocument,
      executeConfirmedAction,
      applyFilters,
      resetFilters,
      handleSearchInput,
      changePage,
      formatDate,
      formatDateTime,
      filteredProfessionals,
      professionalRequests,
      isLoadingRequests,
      fetchProfessionalRequests,
      viewAllProfessionalRequests,
      getStatusBadgeClass,
      getStatusLabel,
      formatTime,
      // Export methods
      openExportModal,
      generateReport,
      getExportStatusBadgeClass,
      getExportProgressPercentage,
      getExportProgressText,
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
}
.table th,
.table td {
  vertical-align: middle;
}
.form-label {
  font-weight: 500;
}
/* Responsive adjustments */
@media (max-width: 768px) {
  .btn-group {
    display: flex;
    flex-direction: column;
  }
  .btn-group .btn {
    border-radius: 0.25rem !important;
    margin-bottom: 0.25rem;
  }
}
</style>
