<!-- src/views/customer/ServiceSearch.vue -->
<template>
    <div class="container py-4">
        <h2>Search Services</h2>

        <div class="card shadow-sm mb-4">
            <div class="card-body">
                <form @submit.prevent="searchServices">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <input type="text" class="form-control" v-model="searchQuery" placeholder="Search by name">
                        </div>
                        <div class="col-md-4">
                            <input type="text" class="form-control" v-model="pinCode" placeholder="Search by PIN code">
                        </div>
                        <div class="col-md-4">
                            <button type="submit" class="btn btn-primary">Search</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <div v-if="loading" class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="services.length === 0" class="text-center">
            <p>No services found.</p>
        </div>

        <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
            <div v-for="service in services" :key="service.id" class="col">
                <div class="card h-100 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">{{ service.name }}</h5>
                        <p class="card-text">{{ service.description }}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="text-muted">{{ service.estimated_time }} mins</span>
                            <span class="text-primary fw-bold">₹{{ service.base_price }}</span>
                        </div>
                    </div>
                    <div class="card-footer text-center">
                        <button class="btn btn-primary" @click="bookService(service)">Book Now</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
    name: 'ServiceSearch',

    setup() {
        const searchQuery = ref('')
        const pinCode = ref('')
        const services = ref([])
        const loading = ref(false)

        const searchServices = async () => {
            try {
                loading.value = true
                const response = await axios.get('/api/services', {
                    params: {
                        search: searchQuery.value,
                        pin_code: pinCode.value
                    }
                })
                services.value = response.data.data
            } catch (error) {
                console.error('Error searching services:', error)
            } finally {
                loading.value = false
            }
        }

        const bookService = (service) => {
            // Navigate to service booking page with selected service
            // You can use Vue Router to pass the service as a parameter
            // Example: router.push({ name: 'BookService', params: { service } })
        }

        return {
            searchQuery,
            pinCode,
            services,
            loading,
            searchServices,
            bookService
        }
    }
}
</script>