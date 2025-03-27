<template>
  <div class="admin-nav w-100">
    <ul
      class="navbar-nav d-flex flex-row flex-lg-row align-items-center justify-content-start gap-1 gap-lg-3"
    >
      <!-- Services -->
      <li class="nav-item">
        <router-link
          class="nav-link px-3 py-2 rounded-3 d-flex align-items-center"
          to="/admin/services"
        >
          <i class="bi bi-tools me-2"></i>
          <span>Services</span>
        </router-link>
      </li>

      <!-- Users Group -->
      <li class="nav-item dropdown">
        <a
          class="nav-link dropdown-toggle px-3 py-2 rounded-3 d-flex align-items-center"
          href="#"
          role="button"
          data-bs-toggle="dropdown"
        >
          <i class="bi bi-people me-2"></i>
          <span>Users</span>
        </a>
        <ul class="dropdown-menu shadow border-0">
          <li>
            <router-link class="dropdown-item py-2" to="/admin/professionals">
              <i class="bi bi-person-badge me-2"></i>
              Professionals
            </router-link>
          </li>
          <li>
            <router-link class="dropdown-item py-2" to="/admin/customers">
              <i class="bi bi-person me-2"></i>
              Customers
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Service Requests -->
      <li class="nav-item">
        <router-link
          class="nav-link px-3 py-2 rounded-3 d-flex align-items-center"
          to="/admin/requests"
        >
          <i class="bi bi-briefcase me-2"></i>
          <span>Requests</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'AdminNavigation',
}
</script>

<style scoped>
.admin-nav {
  padding: 0.5rem 0;
}

.nav-link {
  color: #2c3e50;
  transition: all 0.2s ease;
  position: relative;
  white-space: nowrap;
}

.nav-link i {
  font-size: 1.1rem;
  opacity: 0.9;
}

.nav-link:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.25);
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.router-link-active {
  background-color: var(--bs-primary);
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.router-link-active i {
  opacity: 1;
}

.dropdown-menu {
  padding: 0.5rem 0;
  border-radius: 0.5rem;
}

.dropdown-item {
  padding-left: 1rem;
  padding-right: 1rem;
  display: flex;
  align-items: center;
  color: #2c3e50;
}

.dropdown-item i {
  width: 1.25rem;
  font-size: 1rem;
}

.dropdown-item.router-link-active {
  background-color: var(--bs-primary);
  color: white;
}

.dropdown-item:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.2);
  color: var(--bs-primary);
}

@media (max-width: 991.98px) {
  .navbar-nav {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }

  .nav-link span {
    display: none;
  }

  .nav-link i {
    margin-right: 0 !important;
    font-size: 1.2rem;
  }

  .dropdown-menu {
    position: absolute;
    background-color: white;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    border: none;
  }
}
</style>
