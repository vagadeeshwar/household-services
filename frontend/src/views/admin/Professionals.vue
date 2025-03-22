<template>
  <div class="container py-4">
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-0">Manage Professionals</h1>
        <p class="text-muted">Verify, block, and manage service professionals</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label for="verificationStatus" class="form-label">Verification Status</label>
            <select id="verificationStatus" class="form-select" v-model="filters.verified"
              @change="applyFilters">
              <option value="">All Statuses</option>
              <option :value="true">Verified</option>
              <option :value="false">Unverified</option>
            </select>
          </div>
          <div class="col-md-3">
            <label for="serviceType" class="form-label">Service Type</label>
            <select id="serviceType" class="form-select" v-model="filters.service_type"
              @change="applyFilters">
              <option value="">All Services</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <label for="searchTerm" class="form-label">Search</label>
            <div class="input-group">
              <input type="text" id="searchTerm" class="form-control"
                placeholder="Search by name or email" v-model="searchTerm"
                @input="handleSearchInput" />
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
          <i class="bi bi-people text-muted" style="font-size: 3rem;"></i>
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
                  <span class="badge bg-info">{{ getServiceName(professional.service_type_id)
                    }}</span>
                </td>
                <td>{{ professional.experience_years }} years</td>
                <td>
                  <span :class="[
                    'badge',
                    professional.is_verified ? 'bg-success' : 'bg-warning',
                    'me-2'
                  ]">
                    {{ professional.is_verified ? 'Verified' : 'Pending' }}
                  </span>
                  <span :class="[
                    'badge',
                    professional.is_active ? 'bg-success' : 'bg-danger'
                  ]">
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
                    <button class="btn btn-sm btn-outline-primary"
                      @click="viewProfessional(professional)" title="View details">
                      <i class="bi bi-eye"></i>
                    </button>
                    <!-- Only show verify for unverified -->
                    <button v-if="!professional.is_verified" class="btn btn-sm btn-outline-success"
                      @click="confirmVerify(professional)" title="Verify professional">
                      <i class="bi bi-check-circle"></i>
                    </button>
                    <!-- Only show block/unblock for verified professionals -->
                    <button v-if="professional.is_verified" class="btn btn-sm"
                      :class="professional.is_active ? 'btn-outline-danger' : 'btn-outline-success'"
                      @click="toggleBlockStatus(professional)"
                      :title="professional.is_active ? 'Block account' : 'Unblock account'">
                      <i class="bi"
                        :class="professional.is_active ? 'bi-slash-circle' : 'bi-unlock'"></i>
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
          <span class="text-muted">Showing {{ professionals.length }} of {{ pagination.total || 0 }}
            professionals</span>
        </div>
        <nav aria-label="Professionals pagination" v-if="pagination.pages > 1">
          <ul class="pagination pagination-sm mb-0">
            <li class="page-item" :class="{ disabled: !pagination.has_prev }">
              <a class="page-link" href="#" @click.prevent="changePage(pagination.current_page - 1)"
                aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
              </a>
            </li>
            <li v-for="page in paginationRange" :key="page" class="page-item"
              :class="{ active: page === pagination.current_page }">
              <a class="page-link" href="#" @click.prevent="changePage(page)">
                {{ page }}
              </a>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.has_next }">
              <a class="page-link" href="#" @click.prevent="changePage(pagination.current_page + 1)"
                aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Professional Detail Modal -->
    <div class="modal fade" id="professionalDetailModal" tabindex="-1"
      aria-labelledby="professionalDetailModalLabel" aria-hidden="true" ref="detailModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedProfessional">
          <div class="modal-header">
            <h5 class="modal-title" id="professionalDetailModalLabel">
              Professional Details
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"
              aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-4 mb-3">
                <div class="text-center">
                  <div
                    class="avatar mx-auto mb-3 bg-light rounded-circle d-flex align-items-center justify-content-center"
                    style="width: 100px; height: 100px">
                    <i class="bi bi-person-circle" style="font-size: 3rem"></i>
                  </div>
                  <h5 class="mb-1">{{ selectedProfessional.full_name }}</h5>
                  <p class="text-muted mb-1">{{ getServiceName(selectedProfessional.service_type_id)
                    }}</p>
                  <div class="d-flex justify-content-center align-items-center">
                    <span :class="[
                      'badge',
                      selectedProfessional.is_verified ? 'bg-success' : 'bg-warning',
                      'me-2'
                    ]">
                      {{ selectedProfessional.is_verified ? 'Verified' : 'Pending' }}
                    </span>
                    <span :class="[
                      'badge',
                      selectedProfessional.is_active ? 'bg-success' : 'bg-danger'
                    ]">
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

            <hr>

            <div class="row">
              <div class="col-12">
                <h6 class="mb-3">Professional Description</h6>
                <p>{{ selectedProfessional.description || 'No description provided.' }}</p>
              </div>
            </div>

            <hr>

            <div class="row">
              <div class="col-12">
                <h6 class="mb-3">Verification Document</h6>
                <div v-if="selectedProfessional.verification_documents">
                  <p class="mb-2">
                    <i class="bi bi-file-earmark-text me-2"></i>
                    {{ selectedProfessional.verification_documents }}
                  </p>
                  <button class="btn btn-sm btn-outline-primary"
                    @click="downloadDocument(selectedProfessional.professional_id)">
                    <i class="bi bi-download me-1"></i> Download Document
                  </button>
                </div>
                <p v-else class="text-muted">No verification document uploaded.</p>
              </div>
            </div>

            <hr>

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
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Modals -->
    <div class="modal fade" id="confirmActionModal" tabindex="-1"
      aria-labelledby="confirmActionModalLabel" aria-hidden="true" ref="confirmModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="confirmActionModalLabel">
              {{ confirmAction.title }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"
              aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>{{ confirmAction.message }}</p>
            <div v-if="confirmAction.type === 'block'">
              <label for="blockReason" class="form-label">Reason for blocking</label>
              <textarea id="blockReason" class="form-control" rows="3" v-model="blockReason"
                placeholder="Please provide a reason for blocking this professional"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button type="button" :class="['btn', confirmAction.buttonClass]"
              @click="executeConfirmedAction">
              {{ confirmAction.buttonText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
// import { useRouter } from 'vue-router';
import * as bootstrap from 'bootstrap';
import { formatDate, formatDateTime } from '@/utils/date';
import { useLoading } from '@/composables/useLoading';

export default defineComponent({
  name: 'AdminProfessionals',
  setup() {
    const store = useStore();
    // const router = useRouter();
    const { isLoading, showLoading, hideLoading, withLoading } = useLoading();

    // References to modals
    const detailModal = ref(null);
    const confirmModal = ref(null);
    let bsDetailModal = null;
    let bsConfirmModal = null;

    // State
    const professionals = computed(() => store.getters['professionals/allProfessionals']);
    const pagination = computed(() => store.getters['professionals/pagination']);
    const services = ref([]);
    const selectedProfessional = ref(null);
    const searchTerm = ref('');
    const filters = ref({
      verified: '',
      service_type: '',
      page: 1,
      per_page: 10
    });
    const confirmAction = ref({
      title: '',
      message: '',
      buttonText: '',
      buttonClass: '',
      type: '',
      callback: null
    });
    const blockReason = ref('');

    // Computed
    const paginationRange = computed(() => {
      const current = pagination.value.current_page;
      const total = pagination.value.pages;
      const range = [];

      // Show 5 pages at most
      const maxPages = 5;
      const start = Math.max(1, current - Math.floor(maxPages / 2));
      const end = Math.min(total, start + maxPages - 1);

      for (let i = start; i <= end; i++) {
        range.push(i);
      }

      return range;
    });

    const filteredProfessionals = computed(() => {
      if (!searchTerm.value.trim()) {
        return professionals.value;
      }

      const term = searchTerm.value.toLowerCase().trim();
      return professionals.value.filter(professional => {
        const fullName = professional.full_name?.toLowerCase() || '';
        const email = professional.email?.toLowerCase() || '';
        const username = professional.username?.toLowerCase() || '';

        return fullName.includes(term) ||
          email.includes(term) ||
          username.includes(term);
      });
    });

    // Methods
    const fetchProfessionals = async (forceRefresh = false) => {
      // Start with empty params object
      const params = {};

      // Only add non-empty filters
      Object.entries(filters.value).forEach(([key, value]) => {
        // Include parameters that have values (not empty strings, null, or undefined)
        if (value !== '' && value !== null && value !== undefined) {
          params[key] = value;
        }
      });

      // Only include search term if it's not empty
      if (searchTerm.value.trim()) {
        params.search = searchTerm.value.trim();
      }

      await withLoading(
        store.dispatch('professionals/fetchProfessionals', { params, forceRefresh }),
        'Loading professionals...'
      );
    };

    const fetchServices = async () => {
      try {
        const response = await store.dispatch('services/fetchAllServices', { params: { per_page: 100 } });
        services.value = response.data || [];
      } catch (error) {
        console.error('Error fetching services:', error);
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to load services. Please try again.'
        });
      }
    };

    const getServiceName = (serviceId) => {
      if (!serviceId) return 'Unknown Service';
      const service = services.value.find(s => s.id === serviceId);
      return service ? service.name : 'Unknown Service';
    };

    const viewProfessional = (professional) => {
      selectedProfessional.value = professional;
      bsDetailModal.show();
    };

    const downloadDocument = async (professionalId) => {
      try {
        showLoading('Downloading document...');
        const response = await fetch(`${store.state.apiURL}/professionals/${professionalId}/document`, {
          headers: {
            'Authorization': `Bearer ${store.getters['auth/token']}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to download document');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `professional-${professionalId}-verification.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);

        window.showToast({
          type: 'success',
          title: 'Document downloaded successfully'
        });
      } catch (error) {
        console.error('Error downloading document:', error);
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to download document. Please try again.'
        });
      } finally {
        hideLoading();
      }
    };

    const confirmVerify = (professional) => {
      confirmAction.value = {
        title: 'Verify Professional',
        message: `Are you sure you want to verify ${professional.full_name}? This will give them full access to accept service requests.`,
        buttonText: 'Verify',
        buttonClass: 'btn-success',
        type: 'verify',
        callback: () => verifyProfessional(professional)
      };
      bsConfirmModal.show();
    };

    const verifyProfessional = async (professional) => {
      try {
        showLoading('Verifying professional...');
        await store.dispatch('professionals/verifyProfessional', { id: professional.professional_id });

        window.showToast({
          type: 'success',
          title: `${professional.full_name} has been verified successfully`
        });

        // Refresh the professionals list
        await fetchProfessionals(true);

        // Hide modals
        bsConfirmModal.hide();
        if (bsDetailModal && bsDetailModal._isShown) {
          selectedProfessional.value.is_verified = true;
        }
      } catch (error) {
        console.error('Error verifying professional:', error);
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to verify professional.'
        });
      } finally {
        hideLoading();
      }
    };

    const toggleBlockStatus = (professional) => {
      if (professional.is_active) {
        confirmAction.value = {
          title: 'Block Professional',
          message: `Are you sure you want to block ${professional.full_name}? This will prevent them from accessing the platform.`,
          buttonText: 'Block',
          buttonClass: 'btn-danger',
          type: 'block',
          callback: () => blockProfessional(professional, blockReason.value)
        };
      } else {
        confirmAction.value = {
          title: 'Unblock Professional',
          message: `Are you sure you want to unblock ${professional.full_name}? This will restore their access to the platform.`,
          buttonText: 'Unblock',
          buttonClass: 'btn-success',
          type: 'unblock',
          callback: () => unblockProfessional(professional)
        };
      }
      blockReason.value = '';
      bsConfirmModal.show();
    };

    const blockUnblockProfessional = (professional) => {
      toggleBlockStatus(professional);
    };

    const blockProfessional = async (professional, reason) => {
      if (!reason.trim()) {
        window.showToast({
          type: 'warning',
          title: 'Please provide a reason for blocking this professional'
        });
        return;
      }

      try {
        showLoading('Blocking professional...');
        await store.dispatch('professionals/blockProfessional', {
          id: professional.professional_id,
          data: { reason: reason.trim() }
        });

        window.showToast({
          type: 'success',
          title: `${professional.full_name} has been blocked`
        });

        // Refresh the professionals list
        await fetchProfessionals(true);

        // Hide modals
        bsConfirmModal.hide();
        if (bsDetailModal && bsDetailModal._isShown) {
          selectedProfessional.value.user.is_active = false;
        }
      } catch (error) {
        console.error('Error blocking professional:', error);
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to block professional.'
        });
      } finally {
        hideLoading();
      }
    };

    const unblockProfessional = async (professional) => {
      try {
        showLoading('Unblocking professional...');
        await store.dispatch('professionals/unblockProfessional', {
          id: professional.professional_id,
        });

        window.showToast({
          type: 'success',
          title: `${professional.full_name} has been unblocked`
        });

        // Refresh the professionals list
        await fetchProfessionals(true);

        // Hide modals
        bsConfirmModal.hide();
        if (bsDetailModal && bsDetailModal._isShown) {
          selectedProfessional.value.user.is_active = true;
        }
      } catch (error) {
        console.error('Error unblocking professional:', error);
        window.showToast({
          type: 'danger',
          title: error.response?.data?.detail || 'Failed to unblock professional. Please try again.'
        });
      } finally {
        hideLoading();
      }
    };

    const executeConfirmedAction = () => {
      if (confirmAction.value.callback) {
        confirmAction.value.callback();
      }
    };

    const applyFilters = () => {
      filters.value.page = 1;
      fetchProfessionals();
    };

    const handleSearchInput = () => {
      filters.value.page = 1;

    };

    const resetFilters = () => {
      filters.value = {
        verified: '',
        service_type: '',
        page: 1,
        per_page: 10
      };
      searchTerm.value = '';
      fetchProfessionals(true);
    };

    const changePage = (page) => {
      if (page < 1 || page > pagination.value.pages) return;
      filters.value.page = page;
      fetchProfessionals();
    };

    // Lifecycle Hooks
    onMounted(async () => {
      // Initialize modals
      if (detailModal.value) {
        bsDetailModal = new bootstrap.Modal(detailModal.value);
      }

      if (confirmModal.value) {
        bsConfirmModal = new bootstrap.Modal(confirmModal.value);
      }

      // Fetch initial data
      await Promise.all([
        fetchProfessionals(),
        fetchServices()
      ]);
    });

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

      // Refs
      detailModal,
      confirmModal,

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
      filteredProfessionals
    };
  }
});
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
