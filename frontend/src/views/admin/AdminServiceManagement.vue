<!-- src/views/admin/AdminServiceManagement.vue -->
<template>
    <div class="container py-4">
        <h2>Manage Services</h2>

        <div class="mb-3">
            <button class="btn btn-primary" @click="openCreateModal">Create New Service</button>
        </div>

        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Services</h5>
            </div>
            <div class="card-body">
                <div v-if="loading" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="services.length === 0" class="text-center">
                    <p>No services found.</p>
                </div>

                <div v-else>
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Description</th>
                                <th>Base Price</th>
                                <th>Time Required</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="service in services" :key="service.id">
                                <td>{{ service.name }}</td>
                                <td>{{ service.description }}</td>
                                <td>{{ service.base_price }}</td>
                                <td>{{ service.estimated_time }} minutes</td>
                                <td>
                                    <button class="btn btn-sm btn-primary me-2" @click="openEditModal(service)">
                                        Edit
                                    </button>
                                    <button class="btn btn-sm btn-danger" @click="deleteService(service.id)">
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Create Service Modal -->
        <div class="modal fade" id="createModal" tabindex="-1" ref="createModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Create New Service</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="createService">
                            <div class="mb-3">
                                <label class="form-label">Name</label>
                                <input type="text" class="form-control" v-model="newService.name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" v-model="newService.description" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Base Price</label>
                                <input type="number" class="form-control" v-model="newService.base_price" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Time Required (minutes)</label>
                                <input type="number" class="form-control" v-model="newService.estimated_time" required>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary me-2"
                                    data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" class="btn btn-primary">Create</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Edit Service Modal -->
        <div class="modal fade" id="editModal" tabindex="-1" ref="editModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Service</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="updateService">
                            <div class="mb-3">
                                <label class="form-label">Name</label>
                                <input type="text" class="form-control" v-model="editedService.name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" v-model="editedService.description" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Base Price</label>
                                <input type="number" class="form-control" v-model="editedService.base_price" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Time Required (minutes)</label>
                                <input type="number" class="form-control" v-model="editedService.estimated_time"
                                    required>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary me-2"
                                    data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" class="btn btn-primary">Update</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import axios from 'axios'

export default {
    name: 'AdminServiceManagement',

    setup() {
        const loading = ref(true)
        const services = ref([])
        const createModal = ref(null)
        const editModal = ref(null)
        const newService = ref({
            name: '',
            description: '',
            base_price: 0,
            estimated_time: 0
        })
        const editedService = ref({
            id: null,
            name: '',
            description: '',
            base_price: 0,
            estimated_time: 0
        })

        const fetchServices = async () => {
            try {
                loading.value = true
                const response = await axios.get('/api/services')
                services.value = response.data.data
            } catch (error) {
                console.error('Error fetching services:', error)
            } finally {
                loading.value = false
            }
        }

        const openCreateModal = () => {
            newService.value = {
                name: '',
                description: '',
                base_price: 0,
                estimated_time: 0
            }
            const modal = new Modal(createModal.value)
            modal.show()
        }

        const createService = async () => {
            try {
                await axios.post('/api/services', newService.value)
                await fetchServices()
                const modal = Modal.getInstance(createModal.value)
                modal.hide()
            } catch (error) {
                console.error('Error creating service:', error)
            }
        }

        const openEditModal = (service) => {
            editedService.value = { ...service }
            const modal = new Modal(editModal.value)
            modal.show()
        }

        const updateService = async () => {
            try {
                await axios.put(`/api/services/${editedService.value.id}`, editedService.value)
                await fetchServices()
                const modal = Modal.getInstance(editModal.value)
                modal.hide()
            } catch (error) {
                console.error('Error updating service:', error)
            }
        }

        const deleteService = async (serviceId) => {
            try {
                await axios.delete(`/api/services/${serviceId}`)
                await fetchServices()
            } catch (error) {
                console.error('Error deleting service:', error)
            }
        }

        onMounted(() => {
            fetchServices()
        })

        return {
            loading,
            services,
            createModal,
            editModal,
            newService,
            editedService,
            openCreateModal,
            createService,
            openEditModal,
            updateService,
            deleteService
        }
    }
}
</script>