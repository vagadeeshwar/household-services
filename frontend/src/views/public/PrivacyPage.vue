<template>
  <div class="privacy-page">
    <!-- Hero Section -->
    <div class="bg-primary text-white py-5 mb-5">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8 text-center">
            <h1 class="display-4 mb-3">Privacy Policy</h1>
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
              <!-- Introduction -->
              <section class="mb-5">
                <h2 class="h4">Your Privacy Matters</h2>
                <p class="text-muted">
                  This Privacy Policy outlines how Household Services collects, uses, and protects your
                  personal information when you use our services.
                </p>
              </section>

              <!-- Information Collection -->
              <section class="mb-5">
                <h2 class="h4">Information We Collect</h2>
                <div class="list-group list-group-flush">
                  <div class="list-group-item d-flex align-items-center py-3">
                    <i class="bi bi-person-badge text-primary me-3 fs-4"></i>
                    <div>
                      <h6 class="mb-1">Personal Information</h6>
                      <p class="text-muted mb-0 small">Name, contact details, and service preferences</p>
                    </div>
                  </div>
                  <div class="list-group-item d-flex align-items-center py-3">
                    <i class="bi bi-geo-alt text-primary me-3 fs-4"></i>
                    <div>
                      <h6 class="mb-1">Location Data</h6>
                      <p class="text-muted mb-0 small">Service address and delivery locations</p>
                    </div>
                  </div>
                  <div class="list-group-item d-flex align-items-center py-3">
                    <i class="bi bi-credit-card text-primary me-3 fs-4"></i>
                    <div>
                      <h6 class="mb-1">Payment Information</h6>
                      <p class="text-muted mb-0 small">Transaction and payment method details</p>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Usage -->
              <section class="mb-5">
                <h2 class="h4">How We Use Your Information</h2>
                <div class="table-responsive">
                  <table class="table table-bordered">
                    <tbody>
                      <tr>
                        <td class="bg-light">Service Delivery</td>
                        <td>To provide and improve our services</td>
                      </tr>
                      <tr>
                        <td class="bg-light">Communication</td>
                        <td>To send service updates and notifications</td>
                      </tr>
                      <tr>
                        <td class="bg-light">Quality Assurance</td>
                        <td>To maintain and improve service quality</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              <!-- Rights -->
              <section>
                <h2 class="h4">Your Rights</h2>
                <div class="row g-4">
                  <div class="col-md-6">
                    <div class="border rounded p-3">
                      <h6 class="mb-2">Access Rights</h6>
                      <p class="text-muted small mb-0">Request access to your personal data</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="border rounded p-3">
                      <h6 class="mb-2">Correction Rights</h6>
                      <p class="text-muted small mb-0">Update or correct your information</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="border rounded p-3">
                      <h6 class="mb-2">Deletion Rights</h6>
                      <p class="text-muted small mb-0">Request deletion of your data</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="border rounded p-3">
                      <h6 class="mb-2">Portability Rights</h6>
                      <p class="text-muted small mb-0">Receive a copy of your data</p>
                    </div>
                  </div>
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
