<template>
  <div class="terms-page">
    <!-- Hero Section -->
    <div class="bg-primary text-white py-5 mb-5">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8 text-center">
            <h1 class="display-4 mb-3">Terms of Service</h1>
            <p class="lead mb-0 opacity-75">Last Updated: March 2024</p>
          </div>
        </div>
      </div>
    </div>

    <div class="container pb-5">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="card shadow-sm">
            <div class="card-body p-4 p-lg-5">
              <!-- Service Terms -->
              <section class="mb-5">
                <h2 class="h4 mb-4">Service Terms</h2>
                <div class="row g-4">
                  <div class="col-md-6">
                    <div class="service-term-card">
                      <div class="icon text-success mb-3">
                        <i class="bi bi-check-circle-fill"></i>
                      </div>
                      <h5 class="mb-3">Professional Verification</h5>
                      <p class="text-muted mb-0">All service providers undergo thorough verification</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="service-term-card">
                      <div class="icon text-primary mb-3">
                        <i class="bi bi-calendar-check"></i>
                      </div>
                      <h5 class="mb-3">Booking Terms</h5>
                      <p class="text-muted mb-0">Services subject to availability and scheduling</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="service-term-card">
                      <div class="icon text-warning mb-3">
                        <i class="bi bi-clock-history"></i>
                      </div>
                      <h5 class="mb-3">Cancellation Policy</h5>
                      <p class="text-muted mb-0">Free cancellation up to 24 hours before service</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="service-term-card">
                      <div class="icon text-info mb-3">
                        <i class="bi bi-credit-card"></i>
                      </div>
                      <h5 class="mb-3">Payment Terms</h5>
                      <p class="text-muted mb-0">Secure payment processing with clear pricing</p>
                    </div>
                  </div>
                </div>
              </section>

              <!-- User Responsibilities -->
              <section class="mb-5">
                <h2 class="h4 mb-4">Your Responsibilities</h2>
                <div class="list-group">
                  <div class="list-group-item py-3">
                    <div class="d-flex">
                      <div class="number me-3">1</div>
                      <div>
                        <h6 class="mb-1">Accurate Information</h6>
                        <p class="text-muted mb-0 small">Provide accurate and complete information when using our
                          services</p>
                      </div>
                    </div>
                  </div>
                  <div class="list-group-item py-3">
                    <div class="d-flex">
                      <div class="number me-3">2</div>
                      <div>
                        <h6 class="mb-1">Service Access</h6>
                        <p class="text-muted mb-0 small">Ensure proper access and safety for service providers</p>
                      </div>
                    </div>
                  </div>
                  <div class="list-group-item py-3">
                    <div class="d-flex">
                      <div class="number me-3">3</div>
                      <div>
                        <h6 class="mb-1">Timely Communication</h6>
                        <p class="text-muted mb-0 small">Communicate changes or issues in a timely manner</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Disclaimers -->
              <section>
                <h2 class="h4 mb-4">Disclaimers</h2>
                <div class="alert alert-light">
                  <p class="small mb-0">
                    Services are provided "as is" without warranty of any kind. While we strive for excellence,
                    we cannot guarantee availability of specific service providers or exact service times.
                  </p>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.service-term-card {
  background: #fff;
  border-radius: 1rem;
  padding: 2rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  height: 100%;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.service-term-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.08);
}

.icon {
  font-size: 2rem;
}

.number {
  width: 24px;
  height: 24px;
  background: var(--bs-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.list-group-item:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.02);
}

.table {
  margin-bottom: 0;
}

.table td {
  padding: 1rem;
}

.table td.bg-light {
  width: 30%;
  font-weight: 500;
}

.border.rounded {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.border.rounded:hover {
  transform: translateY(-3px);
  box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
  .card-body {
    padding: 1.5rem !important;
  }

  .service-term-card {
    padding: 1.5rem;
  }

  .table td.bg-light {
    width: 40%;
  }
}
</style>
