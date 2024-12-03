<template>
  <div class="container py-5">
    <!-- Hero Section -->
    <div class="text-center mb-5">
      <h1 class="display-4 mb-3">Our Services</h1>
      <p class="lead text-muted">Professional home services at your fingertips</p>
    </div>

    <!-- Services Grid -->
    <div class="row g-4">
      <!-- Loading State -->
      <div v-if="loading" class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mt-2">Loading services...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="col-12">
        <div class="alert alert-danger d-flex align-items-center" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          <div>{{ error }}</div>
        </div>
        <div class="text-center mt-3">
          <button @click="fetchServices" class="btn btn-primary">
            Try Again
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!services.length" class="col-12 text-center py-5">
        <div class="text-muted">
          <i class="bi bi-inbox fs-1"></i>
          <p class="mt-3">No services available at the moment.</p>
        </div>
      </div>

      <!-- Services List -->
      <div v-else v-for="service in services" :key="service.id" class="col-md-6 col-lg-4">
        <div class="card h-100 shadow-sm hover-shadow transition-all">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <i class="bi bi-tools fs-4 text-primary me-2"></i>
              <h5 class="card-title mb-0">{{ service.name }}</h5>
            </div>
            <p class="card-text text-muted">{{ service.description }}</p>
            <div class="d-flex justify-content-between align-items-center mt-3">
              <div class="d-flex align-items-center text-muted">
                <i class="bi bi-clock me-1"></i>
                <span>{{ service.estimated_time }} mins</span>
              </div>
              <div class="fw-bold text-primary">
                ₹{{ service.base_price }}
              </div>
            </div>
          </div>
          <div class="card-footer bg-transparent border-top-0 text-center p-3">
            <router-link :to="isAuthenticated ? '/customer/services' : '/register/customer'"
              class="btn btn-primary w-100">
              {{ isAuthenticated ? 'Book Service' : 'Book Now' }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { service } from '@/services' // Import the service directly

export default {
  name: 'ServicesPage',

  setup() {
    const store = useStore()
    const services = ref([])
    const loading = ref(true)
    const error = ref(null)

    const isAuthenticated = computed(() => store.getters['auth/isLoggedIn'])

    const fetchServices = async () => {
      try {
        loading.value = true
        error.value = null

        // Call the API service directly instead of using store
        const response = await service.getAll({
          is_active: true,
          page: 1,
          per_page: 50 // Adjust as needed
        })

        if (response?.data) {
          services.value = response.data
        } else {
          throw new Error('Invalid response format')
        }
      } catch (err) {
        console.error('Service fetch error:', err)
        error.value = err.response?.data?.message || 'Failed to load services. Please try again.'
        window.showToast({
          type: 'error',
          title: 'Error',
          message: error.value
        })
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchServices()
    })

    return {
      services,
      loading,
      error,
      isAuthenticated,
      fetchServices
    }
  }
}
</script>

<style scoped>
.hover-shadow:hover {
  transform: translateY(-5px);
  box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .15) !important;
}

.transition-all {
  transition: all .3s ease-in-out;
}
</style>
