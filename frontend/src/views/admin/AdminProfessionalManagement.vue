<!-- src/views/admin/AdminProfessionalManagement.vue -->
<template>
    <div class="container py-4">
        <h2>Manage Service Professionals</h2>

        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Service Professionals</h5>
            </div>
            <div class="card-body">
                <div v-if="loading" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="professionals.length === 0" class="text-center">
                    <p>No service professionals found.</p>
                </div>

                <div v-else>
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Service Type</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="professional in professionals" :key="professional.id">
                                <td>{{ professional.user.full_name }}</td>
                                <td>{{ professional.user.email }}</td>
                                <td>{{ professional.service_type.name }}</td>
                                <td>
                                    <span v-if="professional.is_verified" class="badge bg-success">Verified</span>
                                    <span v-else class="badge bg-warning">Pending</span>
                                </td>
                                <td>
                                    <button v-if="!professional.is_verified" class="btn btn-sm btn-primary me-2"
                                        @click="openVerificationModal(professional)">
                                        Review Documents
                                    </button>
                                    <button class="btn btn-sm btn-danger" @click="blockProfessional(professional.id)">
                                        Block
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Verification Modal -->
        <div class="modal fade" id="verificationModal" tabindex="-1" ref="verificationModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Review Verification Documents</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div v-if="selectedProfessional">
                            <p><strong>Professional:</strong> {{ selectedProfessional.user.full_name }}</p>
                            <p><strong>Service Type:</strong> {{ selectedProfessional.service_type.name }}</p>
                            <p><strong>Experience:</strong> {{ selectedProfessional.experience_years }} years</p>
                            <p><strong>Description:</strong> {{ selectedProfessional.description }}</p>

                            <div class="mb-3">
                                <label class="form-label">Verification Documents</label>
                                <ul>
                                    <li v-for="(doc, index) in selectedProfessional.verification_documents"
                                        :key="index">
                                        <a :href="doc.url" target="_blank">{{ doc.name }}</a>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-success" @click="approveProfessional">Approve</button>
                        <button type="button" class="btn btn-danger" @click="rejectProfessional">Reject</button>
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
    name: 'AdminProfessionalManagement',

    setup() {
        const loading = ref(true)
        const professionals = ref([])
        const verificationModal = ref(null)
        const selectedProfessional = ref(null)

        const fetchProfessionals = async () => {
            try {
                loading.value = true
                const response = await axios.get('/api/professionals')
                professionals.value = response.data.data
            } catch (error) {
                console.error('Error fetching professionals:', error)
            } finally {
                loading.value = false
            }
        }

        const openVerificationModal = (professional) => {
            selectedProfessional.value = professional
            const modal = new Modal(verificationModal.value)
            modal.show()
        }

        const approveProfessional = async () => {
            try {
                await axios.post(`/api/professionals/${selectedProfessional.value.id}/verify`)
                await fetchProfessionals()
                const modal = Modal.getInstance(verificationModal.value)
                modal.hide()
            } catch (error) {
                console.error('Error approving professional:', error)
            }
        }

        const rejectProfessional = async () => {
            try {
                await axios.post(`/api/professionals/${selectedProfessional.value.id}/reject`)
                await fetchProfessionals()
                const modal = Modal.getInstance(verificationModal.value)
                modal.hide()
            } catch (error) {
                console.error('Error rejecting professional:', error)
            }
        }

        const blockProfessional = async (professionalId) => {
            try {
                await axios.post(`/api/professionals/${professionalId}/block`)
                await fetchProfessionals()
            } catch (error) {
                console.error('Error blocking professional:', error)
            }
        }

        onMounted(() => {
            fetchProfessionals()
        })

        return {
            loading,
            professionals,
            verificationModal,
            selectedProfessional,
            openVerificationModal,
            approveProfessional,
            rejectProfessional,
            blockProfessional
        }
    }
}
</script>