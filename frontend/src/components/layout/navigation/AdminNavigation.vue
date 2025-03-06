<template>
  <div class="d-flex w-100">
    <!-- Left Side Links -->
    <ul class="navbar-nav me-auto">

      <li class="nav-item">
        <router-link class="nav-link" to="/admin/services">
          <i class="bi bi-tools me-1"></i>
          Services
        </router-link>
      </li>

      <!-- Dropdown for User Management -->
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
          <i class="bi bi-people me-1"></i>
          Users
        </a>
        <ul class="dropdown-menu">
          <li>
            <router-link class="dropdown-item" to="/admin/professionals">
              <i class="bi bi-person-badge me-2"></i>
              Professionals
            </router-link>
          </li>
          <li>
            <router-link class="dropdown-item" to="/admin/customers">
              <i class="bi bi-person me-2"></i>
              Customers
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Reports Link -->
      <li class="nav-item">
        <router-link class="nav-link" to="/admin/reports">
          <i class="bi bi-file-earmark-text me-1"></i>
          Reports
        </router-link>
      </li>
    </ul>

  </div>
</template>

<script>
export default {
  name: 'AdminNavigation'
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
