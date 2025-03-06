<template>
  <div class="d-flex w-100">
    <!-- Left Side Links -->
    <ul class="navbar-nav me-auto">
      <!-- Services -->
      <li class="nav-item">
        <router-link class="nav-link" to="/customer/services">
          <i class="bi bi-tools me-1"></i>
          Browse Services
        </router-link>
      </li>

      <!-- Service Requests -->
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
          <i class="bi bi-list-check me-1"></i>
          My Requests
        </a>
        <ul class="dropdown-menu">
          <li>
            <router-link class="dropdown-item" to="/customer/requests?status=created">
              <i class="bi bi-hourglass-split me-2"></i>
              Pending
            </router-link>
          </li>
          <li>
            <router-link class="dropdown-item" to="/customer/requests?status=assigned">
              <i class="bi bi-arrow-repeat me-2"></i>
              In Progress
            </router-link>
          </li>
          <li>
            <router-link class="dropdown-item" to="/customer/requests?status=completed">
              <i class="bi bi-check2-circle me-2"></i>
              Completed
            </router-link>
          </li>
        </ul>
      </li>
    </ul>

    <!-- Right Side Links -->
    <ul class="navbar-nav">
      <!-- Professionals -->
      <li class="nav-item">
        <router-link class="nav-link" to="/customer/professionals">
          <i class="bi bi-person-badge me-1"></i>
          Find Professionals
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'CustomerNavigation',
}
</script>

<style scoped>
.dropdown-item i {
  width: 1.25rem;
}

@media (max-width: 991.98px) {
  .dropdown-menu {
    background-color: rgba(0, 0, 0, 0.1);
    border: none;
  }

  .dropdown-item {
    color: rgba(255, 255, 255, 0.8);
  }

  .dropdown-item:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #fff;
  }
}
</style>
