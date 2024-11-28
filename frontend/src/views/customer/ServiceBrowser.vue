<!-- src/views/customer/ServiceBrowser.vue -->
<template>
    <div class="container py-4">
        <!-- Search and Filter Section -->
        <div class="card shadow-sm mb-4">
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-md-8">
                        <div class="input-group">
                            <span class="input-group-text">
                                <i class="bi bi-search"></i>
                            </span>
                            <input type="text" class="form-control" placeholder="Search services..."
                                v-model="searchQuery">
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="input-group">
                            <span class="input-group-text">
                                <i class="bi bi-geo-alt"></i>
                            </span>
                            <input type="text" class="form-control" placeholder="PIN Code" v-model="pinCode"
                                maxlength="6" pattern="[0-9]*">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Services Grid -->
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="filteredServices.length === 0" class="text-center py-5">
            <i class="bi bi-inbox fs-1 text-muted"></i>
            <p class="mt-2 mb-0">No services found</p>
        </div>

        <div v-else class="row g-4">
            <div v-for="service in filteredServices" :key="service.id" class="col-md-6 col-lg-4">
                <div class="card h-100 shadow-sm hover-shadow">
                    <div class="card-body">
                        <h5 class="card-title">{{ service.name }}</h5>
                        <p class="card-text text-muted">{{ service.description }}</p>
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <div class="text-muted">
                                <i class="bi bi-clock me-1"></i>
                                {{ service.estimated_time }} mins
                            </div>
                            <div class="text-primary fw-bold">
                                ₹{{ service.base_price }}
                            </div>
                        </div>
                        <button class="btn btn-primary w-100" @click="openBookingModal(service)"
                            :disabled="!service.is_active">
                            Book Now
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Booking Modal -->
        <div class="modal fade" id="bookingModal" tabindex="-1" ref="bookingModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            Book {{ selectedService?.name }}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form @submit.prevent="handleBooking">
                        <div class="modal-body">
                            <!-- Error Alert -->
                            <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                                {{ error }}
                                <button type="button" class="btn-close" @click="error = ''"></button>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Preferred Date</label>
                                <input type="date" class="form-control" v-model="bookingForm.preferred_date"
                                    :min="minDate" :max="maxDate" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Preferred Time</label>
                                <input type="time" class="form-control" v-model="bookingForm.preferred_time" min="09:00"
                                    max="17:00" required>
                                <div class="form-text">
                                    Business hours: 9 AM to 5 PM
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Service Description</label>
                                <textarea class="form-control" v-model="bookingForm.description" rows="3"
                                    placeholder="Please describe your service requirement..." required></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-primary" :disabled="isBooking">
                                <span v-if="isBooking" class="spinner-border spinner-border-sm me-2"></span>
                                {{ isBooking ? 'Booking...' : 'Confirm Booking' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import { useRouter } from 'vue-router'
import axios from 'axios'
import moment from 'moment'

export default {
    name: 'ServiceBrowser',

    setup() {
        const router = useRouter()
        const loading = ref(true)
        const services = ref([])
        const searchQuery = ref('')
        const pinCode = ref('')
        const error = ref('')
        const bookingModal = ref(null)
        const selectedService = ref(null)
        const isBooking = ref(false)

        const bookingForm = ref({
            preferred_date: '',
            preferred_time: '',
            description: ''
        })

        // Computed properties for date constraints
        const minDate = computed(() => moment().format('YYYY-MM-DD'))
        const maxDate = computed(() => moment().add(7, 'days').format('YYYY-MM-DD'))

        // Filter services based on search query and pin code
        const filteredServices = computed(() => {
            let filtered = services.value

            if (searchQuery.value) {
                const query = searchQuery.value.toLowerCase()
                filtered = filtered.filter(service =>
                    service.name.toLowerCase().includes(query) ||
                    service.description.toLowerCase().includes(query)
                )
            }

            // Add pin code filtering when backend supports it
            return filtered
        })

        // Fetch services from backend
        const fetchServices = async () => {
            try {
                loading.value = true
                const response = await axios.get('/api/services')
                services.value = response.data.data
            } catch (err) {
                console.error('Error fetching services:', err)
                error.value = 'Failed to load services. Please try again.'
            } finally {
                loading.value = false
            }
        }

        // Handle booking modal
        const openBookingModal = (service) => {
            selectedService.value = service
            // Reset form
            bookingForm.value = {
                preferred_date: '',
                preferred_time: '',
                description: ''
            }
            error.value = ''

            // Initialize and show modal
            if (!bookingModal.value) {
                bookingModal.value = new Modal(document.getElementById('bookingModal'))
            }
            bookingModal.value.show()
        }

        // Handle booking submission
        const handleBooking = async () => {
            if (!selectedService.value) return

            try {
                isBooking.value = true
                error.value = ''

                // Combine date and time
                const preferredTime = moment(
                    `${bookingForm.value.preferred_date} ${bookingForm.value.preferred_time}`
                ).format('YYYY-MM-DD HH:mm:ss')

                const requestData = {
                    service_id: selectedService.value.id,
                    preferred_time: preferredTime,
                    description: bookingForm.value.description
                }

                await axios.post('/api/requests', requestData)

                // Close modal and redirect to requests page
                bookingModal.value.hide()
                router.push({
                    path: '/customer/requests',
                    query: {
                        success: 'true',
                        message: 'Service request created successfully!'
                    }
                })
            } catch (err) {
                error.value = err.response?.data?.detail || 'Failed to create service request'
            } finally {
                isBooking.value = false
            }
        }

        onMounted(() => {
            fetchServices()
        })

        return {
            loading,
            services,
            searchQuery,
            pinCode,
            error,
            bookingModal,
            selectedService,
            bookingForm,
            isBooking,
            filteredServices,
            minDate,
            maxDate,
            openBookingModal,
            handleBooking
        }
    }
}
</script>

<style scoped>
.hover-shadow {
    transition: box-shadow 0.3s ease-in-out;
}

.hover-shadow:hover {
    box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .15) !important;
}

.modal-dialog {
    max-width: 500px;
}
</style>