<template>
  <div class="d-flex w-100">
    <!-- Left Side Links -->
    <ul class="navbar-nav me-auto">

      <li class="nav-item">
        <router-link class="nav-link" to="/professional/services">
          <i class="bi bi-tools me-1"></i>
          Browse Services
        </router-link>
      </li>

      <!-- Service Requests -->
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
          <i class="bi bi-list-check me-1"></i>
          Service Requests
        </a>
        <ul class="dropdown-menu">
          <li>
            <router-link class="dropdown-item" to="/professional/requests?type=new">
              <i class="bi bi-star me-2"></i>
              New Requests
            </router-link>
          </li>
          <li>
            <router-link class="dropdown-item" to="/professional/requests?type=ongoing">
              <i class="bi bi-arrow-repeat me-2"></i>
              Ongoing
            </router-link>
          </li>
          <li>
            <router-link class="dropdown-item" to="/professional/requests?type=completed">
              <i class="bi bi-check2-circle me-2"></i>
              Completed
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Schedule -->
      <li class="nav-item">
        <router-link class="nav-link" to="/professional/schedule">
          <i class="bi bi-calendar-week me-1"></i>
          Schedule
        </router-link>
      </li>
    </ul>

    <!-- Right Side Links -->
    <ul class="navbar-nav">
      <!-- Reviews -->
      <li class="nav-item">
        <router-link class="nav-link" to="/professional/reviews">
          <i class="bi bi-star-half me-1"></i>
          Reviews
        </router-link>
      </li>

      <!-- Document Update -->
      <li class="nav-item">
        <router-link class="nav-link" to="/professional/documents">
          <i class="bi bi-file-earmark-text me-1"></i>
          Documents
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'ProfessionalNavigation'
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
