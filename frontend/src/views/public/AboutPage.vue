<template>
  <div class="about-page">
    <!-- Hero Section -->
    <div class="bg-primary text-white py-5 mb-5">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8 text-center">
            <h1 class="display-4 mb-3">About Us</h1>
            <p class="lead mb-0 opacity-75">Your Trusted Partner for Home Services</p>
          </div>
        </div>
      </div>
    </div>

    <div class="container pb-5">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <!-- Mission Section -->
          <div class="card shadow-sm mb-5">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <div class="mission-icon mb-3">
                  <i class="bi bi-bullseye fs-1 text-primary"></i>
                </div>
                <h2>Our Mission</h2>
                <p class="lead text-muted mt-3">
                  To provide exceptional home services by connecting skilled professionals with
                  homeowners, ensuring quality, reliability, and satisfaction in every service
                  interaction.
                </p>
              </div>
            </div>
          </div>

          <!-- Features Grid -->
          <div class="row g-4">
            <div class="col-md-6">
              <div class="feature-card h-100">
                <div class="icon-wrapper text-success">
                  <i class="bi bi-check-circle-fill"></i>
                </div>
                <h3 class="h5 mb-3">Verified Professionals</h3>
                <p class="text-muted mb-0">
                  All our service providers undergo thorough verification and background checks
                </p>
              </div>
            </div>

            <div class="col-md-6">
              <div class="feature-card h-100">
                <div class="icon-wrapper text-primary">
                  <i class="bi bi-shield-check"></i>
                </div>
                <h3 class="h5 mb-3">Quality Assured</h3>
                <p class="text-muted mb-0">
                  We maintain high standards through regular quality checks and customer feedback
                </p>
              </div>
            </div>

            <div class="col-md-6">
              <div class="feature-card h-100">
                <div class="icon-wrapper text-warning">
                  <i class="bi bi-clock-history"></i>
                </div>
                <h3 class="h5 mb-3">Timely Service</h3>
                <p class="text-muted mb-0">
                  Punctual and efficient service delivery with real-time tracking
                </p>
              </div>
            </div>

            <div class="col-md-6">
              <div class="feature-card h-100">
                <div class="icon-wrapper text-info">
                  <i class="bi bi-cash-stack"></i>
                </div>
                <h3 class="h5 mb-3">Transparent Pricing</h3>
                <p class="text-muted mb-0">
                  Clear upfront pricing with no hidden charges or surprises
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mission-icon {
  width: 80px;
  height: 80px;
  background: rgba(var(--bs-primary-rgb), 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.feature-card {
  background: #fff;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: transform 0.2s ease-in-out;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.icon-wrapper {
  font-size: 2rem;
  margin-bottom: 1rem;
}
</style>
