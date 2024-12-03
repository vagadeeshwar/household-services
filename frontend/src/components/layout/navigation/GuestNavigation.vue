<template>
  <div class="d-flex w-100">
    <!-- Left Side Links -->
    <ul class="navbar-nav me-auto">
      <li class="nav-item">
        <router-link class="nav-link" to="/services">
          <i class="bi bi-box-seam"></i> Browse Services
        </router-link>
      </li>
    </ul>

    <!-- Right Side Links -->
    <ul class="navbar-nav">
      <li class="nav-item">
        <router-link class="nav-link" to="/login">
          <i class="bi bi-box-arrow-in-right me-1"></i>
          Sign In
        </router-link>
      </li>
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
          <i class="bi bi-person-plus me-1"></i>
          Register
        </a>
        <ul class="dropdown-menu dropdown-menu-end">
          <li>
            <router-link class="dropdown-item" to="/register/customer">
              <i class="bi bi-person me-2"></i>
              As Customer
            </router-link>
          </li>
          <li>
            <router-link class="dropdown-item" to="/register/professional">
              <i class="bi bi-person-badge me-2"></i>
              As Professional
            </router-link>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'GuestNavigation'
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
