<template>
  <div class="container py-5">
    <Loading v-if="!user" />
    <div v-else class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white p-4">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-white text-primary p-3">
                <i class="bi bi-person-circle fs-2"></i>
              </div>
              <div class="ms-3">
                <h4 class="mb-1">{{ user.full_name }}</h4>
                <p class="mb-0 opacity-75">Administrator</p>
              </div>
            </div>
          </div>
          <div class="card-body p-4">
            <div class="row g-4">
              <!-- Personal Information -->
              <div class="col-12">
                <h5 class="border-bottom pb-2">Personal Information</h5>
                <div class="row g-3 mt-2">
                  <div class="col-md-6">
                    <label class="form-label text-muted">Username</label>
                    <p class="fw-medium">{{ user.username }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Email</label>
                    <p class="fw-medium">{{ user.email }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Full Name</label>
                    <p class="fw-medium">{{ user.full_name }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Phone</label>
                    <p class="fw-medium">+91 {{ user.phone }}</p>
                  </div>
                  <div class="col-12">
                    <label class="form-label text-muted">Address</label>
                    <p class="fw-medium">{{ user.address }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">PIN Code</label>
                    <p class="fw-medium">{{ user.pin_code }}</p>
                  </div>
                </div>
              </div>

              <!-- Account Information -->
              <div class="col-12">
                <h5 class="border-bottom pb-2">Account Information</h5>
                <div class="row g-3 mt-2">
                  <div class="col-md-6">
                    <label class="form-label text-muted">Account Status</label>
                    <p>
                      <span class="badge bg-success">Active</span>
                    </p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Last Login</label>
                    <p class="fw-medium">{{ formatDate(user.last_login) }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted">Account Created</label>
                    <p class="fw-medium">{{ formatDate(user.created_at) }}</p>
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
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import moment from 'moment'

export default {
  name: 'AdminProfile',

  setup() {
    const isLoading = ref(true)

    const store = useStore()

    const user = computed(() => store.getters['auth/currentUser'])

    const formatDate = (date) => {
      return date ? moment(date).format('MMM DD, YYYY hh:mm A') : 'N/A'
    }

    return {
      user,
      formatDate,
      isLoading
    }
  }
}
</script>
