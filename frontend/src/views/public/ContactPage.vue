<template>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <h1 class="text-center mb-4">Contact Us</h1>
                <div class="card shadow-sm">
                    <div class="card-body">
                        <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
                            <div class="mb-3">
                                <label for="name" class="form-label">Your Name</label>
                                <input type="text" class="form-control" id="name" v-model="form.name" required>
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="email" v-model="form.email" required>
                            </div>
                            <div class="mb-3">
                                <label for="subject" class="form-label">Subject</label>
                                <input type="text" class="form-control" id="subject" v-model="form.subject" required>
                            </div>
                            <div class="mb-3">
                                <label for="message" class="form-label">Message</label>
                                <textarea class="form-control" id="message" rows="5" v-model="form.message"
                                    required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary" :disabled="submitting">
                                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                                {{ submitting ? 'Sending...' : 'Send Message' }}
                            </button>
                        </form>

                        <hr class="my-5">

                        <h5 class="mb-4">Other Ways to Reach Us</h5>
                        <div class="row g-4">
                            <div class="col-md-6">
                                <div class="d-flex align-items-start">
                                    <i class="bi bi-envelope fs-4 text-primary me-3"></i>
                                    <div>
                                        <h6>Email</h6>
                                        <p class="text-muted mb-0">support@householdservices.com</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="d-flex align-items-start">
                                    <i class="bi bi-telephone fs-4 text-primary me-3"></i>
                                    <div>
                                        <h6>Phone</h6>
                                        <p class="text-muted mb-0">+91 1234567890</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, reactive } from 'vue'

export default {
    name: 'ContactPage',
    setup() {
        const submitting = ref(false)
        const form = reactive({
            name: '',
            email: '',
            subject: '',
            message: ''
        })

        const handleSubmit = async () => {
            submitting.value = true
            // Add your form submission logic here
            await new Promise(resolve => setTimeout(resolve, 1000))
            alert('Message sent successfully!')
            submitting.value = false
        }

        return {
            form,
            submitting,
            handleSubmit
        }
    }
}
</script>