<template>
  <div class="min-vh-100 bg-light d-flex align-items-center justify-content-center py-12 px-4">
    <div class="text-center">
      <div class="card shadow-lg">
        <div class="card-body p-5">
          <!-- Warning Icon Container -->
          <div class="mx-auto d-flex align-items-center justify-content-center rounded-circle bg-danger bg-opacity-10"
            style="width: 96px; height: 96px;">
            <span style="font-size: 3rem;">⚠️</span>
          </div>

          <!-- Error Message -->
          <h2 class="mt-4 fw-bold">
            Oops! Page Not Found
          </h2>

          <p class="mt-3 text-muted fs-5">
            The page you're looking for doesn't exist or has been moved.
          </p>

          <!-- Home Button -->
          <div class="mt-4">
            <button @click="goHome" class="btn btn-primary d-inline-flex align-items-center gap-2">
              <i class="bi bi-house-fill"></i>
              Back to Home
            </button>
          </div>

          <!-- Error Code -->
          <div class="mt-4">
            <p class="text-muted small">
              Error Code: 404
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';

export default {
  setup() {
    const router = useRouter();

    const goHome = () => {
      router.push('/');
    };

    return {
      goHome,
    };
  },
};
</script>