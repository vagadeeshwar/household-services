<template>
  <div class="contact-page">
    <FormNavigationGuard :when="Object.values(form).some((value) => value !== '')" />

    <!-- Hero Section -->
    <div class="bg-primary text-white py-5 mb-5">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8 text-center">
            <h1 class="display-4 mb-3">Contact Us</h1>
            <p class="lead mb-0 opacity-75">
              We're here to help and answer any questions you might have
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="container pb-5">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <!-- Contact Form Card -->
          <div class="card shadow-sm">
            <div class="card-body p-4 p-lg-5">
              <form @submit.prevent="handleSubmit" novalidate>
                <div class="row g-3">
                  <!-- Name Field -->
                  <div class="col-md-6">
                    <label for="name" class="form-label">Name</label>
                    <input
                      type="text"
                      id="name"
                      v-model="form.name"
                      :class="['form-control', { 'is-invalid': v$.form.name.$error }]"
                      :disabled="submitting"
                      @input="v$.form.name.$touch()"
                    />
                    <div class="invalid-feedback" v-if="v$.form.name.$error">
                      {{ v$.form.name.$errors[0]?.$message }}
                    </div>
                  </div>

                  <!-- Email Field -->
                  <div class="col-md-6">
                    <label for="email" class="form-label">Email</label>
                    <input
                      type="email"
                      id="email"
                      v-model="form.email"
                      :class="['form-control', { 'is-invalid': v$.form.email.$error }]"
                      :disabled="submitting"
                      @input="v$.form.email.$touch()"
                    />
                    <div class="invalid-feedback" v-if="v$.form.email.$error">
                      {{ v$.form.email.$errors[0]?.$message }}
                    </div>
                  </div>

                  <!-- Subject Field -->
                  <div class="col-12">
                    <label for="subject" class="form-label">Subject</label>
                    <input
                      type="text"
                      id="subject"
                      v-model="form.subject"
                      :class="['form-control', { 'is-invalid': v$.form.subject.$error }]"
                      :disabled="submitting"
                      @input="v$.form.subject.$touch()"
                    />
                    <div class="invalid-feedback" v-if="v$.form.subject.$error">
                      {{ v$.form.subject.$errors[0]?.$message }}
                    </div>
                  </div>

                  <!-- Message Field -->
                  <div class="col-12">
                    <label for="message" class="form-label">Message</label>
                    <textarea
                      id="message"
                      v-model="form.message"
                      :class="['form-control', { 'is-invalid': v$.form.message.$error }]"
                      :disabled="submitting"
                      @input="v$.form.message.$touch()"
                      rows="5"
                    ></textarea>
                    <div class="invalid-feedback" v-if="v$.form.message.$error">
                      {{ v$.form.message.$errors[0]?.$message }}
                    </div>
                  </div>

                  <!-- Submit Button -->
                  <div class="col-12">
                    <button type="submit" class="btn btn-primary w-100" :disabled="submitting">
                      <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                      {{ submitting ? 'Sending Message...' : 'Send Message' }}
                    </button>
                  </div>
                </div>
              </form>

              <!-- Contact Information -->
              <div class="row mt-5 pt-4 border-top g-4">
                <div class="col-md-4">
                  <div class="contact-info-card">
                    <div class="icon-wrapper mb-3">
                      <i class="bi bi-envelope text-primary"></i>
                    </div>
                    <h5>Email</h5>
                    <p class="text-muted mb-0">support@example.com</p>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="contact-info-card">
                    <div class="icon-wrapper mb-3">
                      <i class="bi bi-telephone text-primary"></i>
                    </div>
                    <h5>Phone</h5>
                    <p class="text-muted mb-0">+91 999-888-7777</p>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="contact-info-card">
                    <div class="icon-wrapper mb-3">
                      <i class="bi bi-geo-alt text-primary"></i>
                    </div>
                    <h5>Address</h5>
                    <p class="text-muted mb-0">123 Service Street<br />Bangalore, 560001</p>
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
import { publicService } from '@/services'
import { useVuelidate } from '@vuelidate/core'
import { required, email, minLength } from '@vuelidate/validators'

export default {
  name: 'ContactPage',

  setup() {
    const submitting = ref(false)

    const initialForm = {
      name: '',
      email: '',
      subject: '',
      message: '',
    }

    const form = reactive({ ...initialForm })

    const rules = {
      form: {
        name: { required, minLength: minLength(2) },
        email: { required, email },
        subject: { required, minLength: minLength(5) },
        message: { required, minLength: minLength(10) },
      },
    }

    const v$ = useVuelidate(rules, { form })

    const resetForm = () => {
      Object.keys(form).forEach((key) => (form[key] = initialForm[key]))
      v$.value.$reset()
    }

    const handleSubmit = async () => {
      const isValid = await v$.value.$validate()
      if (!isValid) return

      submitting.value = true
      try {
        await publicService.submitContact(form)

        window.showToast({
          type: 'success',
          title: 'Thank you! Your message has been sent successfully.',
        })
        resetForm()
      } catch {
        window.showToast({
          type: 'error',
          title: 'Failed to send message. Please try again.',
        })
      } finally {
        submitting.value = false
      }
    }

    return {
      form,
      submitting,
      handleSubmit,
      v$,
    }
  },
}
</script>

<style scoped>
.contact-info-card {
  text-align: center;
  padding: 1.5rem;
  border-radius: 0.5rem;
  transition:
    transform 0.2s ease-in-out,
    box-shadow 0.2s ease-in-out;
}

.contact-info-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.08);
}

.icon-wrapper {
  font-size: 2rem;
  color: var(--bs-primary);
}

.form-control:focus {
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.25rem rgba(var(--bs-primary-rgb), 0.15);
}

@media (max-width: 768px) {
  .card-body {
    padding: 1.5rem !important;
  }
}
</style>
