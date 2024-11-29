<template>
  <div class="container py-5">
    <h1 class="mb-4">Our Services</h1>
    <div class="row g-4">
      <div v-if="loading" class="col-12 text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else class="col-md-4" v-for="service in services" :key="service.id">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title">{{ service.name }}</h5>
            <p class="card-text text-muted">{{ service.description }}</p>
            <div class="d-flex justify-content-between align-items-center">
              <div class="text-muted">
                <i class="bi bi-clock me-1"></i>
                {{ service.estimated_time }} mins
              </div>
              <div class="fw-bold text-primary">
                ₹{{ service.base_price }}
              </div>
            </div>
          </div>
          <div class="card-footer bg-transparent text-center">
            <router-link to="/register/customer" class="btn btn-primary">Book Now</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'ServicesPage',
  setup() {
    const services = ref([])
    const loading = ref(true)

    const fetchServices = async () => {
      try {
        const response = await axios.get('/api/services')
        services.value = response.data.data
      } catch (error) {
        console.error('Error fetching services:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(fetchServices)

    return {
      services,
      loading
    }
  }
}
</script>