<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <!-- Brand -->
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <i class="bi bi-tools me-2"></i>
        Household Services
      </router-link>

      <!-- Mobile Toggle -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#mainNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navigation Links -->
      <div class="collapse navbar-collapse" id="mainNav">
        <template v-if="isLoggedIn">
          <!-- Role-based Navigation -->
          <component :is="currentNavigation" />

          <!-- User Menu -->
          <ul class="navbar-nav ms-auto">
            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle d-flex align-items-center"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
              >
                <div class="avatar">
                  <i class="bi bi-person-fill"></i>
                </div>
                <span class="ms-2">{{ userName }}</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li class="dropdown-header">
                  <small class="text-muted">Signed in as</small>
                  <div class="fw-medium">{{ userEmail }}</div>
                </li>
                <li>
                  <hr class="dropdown-divider" />
                </li>
                <li>
                  <router-link class="dropdown-item" :to="profileRoute">
                    <i class="bi bi-person-circle me-2"></i>Profile
                  </router-link>
                </li>
                <li>
                  <hr class="dropdown-divider" />
                </li>
                <li>
                  <button class="dropdown-item text-danger" @click="handleLogout">
                    <i class="bi bi-box-arrow-right me-2"></i>Sign Out
                  </button>
                </li>
              </ul>
            </li>
          </ul>
        </template>

        <!-- Guest Navigation -->
        <template v-else>
          <GuestNavigation />
        </template>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed, defineAsyncComponent } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

// Navigation Components
const AdminNavigation = defineAsyncComponent(() => import('./navigation/AdminNavigation.vue'))
const ProfessionalNavigation = defineAsyncComponent(
  () => import('./navigation/ProfessionalNavigation.vue'),
)
const CustomerNavigation = defineAsyncComponent(() => import('./navigation/CustomerNavigation.vue'))
const GuestNavigation = defineAsyncComponent(() => import('./navigation/GuestNavigation.vue'))

export default {
  name: 'TheNavbar',

  components: {
    AdminNavigation,
    ProfessionalNavigation,
    CustomerNavigation,
    GuestNavigation,
  },

  setup() {
    const store = useStore()
    const router = useRouter()

    // Computed Properties
    const isLoggedIn = computed(() => store.getters['auth/isLoggedIn'])
    const userName = computed(() => store.getters['auth/userName'])
    const userEmail = computed(() => store.getters['auth/userEmail'])
    const userRole = computed(() => store.getters['auth/userRole'])

    // Dynamic navigation component based on role
    const currentNavigation = computed(() => {
      switch (userRole.value) {
        case 'admin':
          return AdminNavigation
        case 'professional':
          return ProfessionalNavigation
        case 'customer':
          return CustomerNavigation
        default:
          return null
      }
    })

    // Dynamic profile route
    const profileRoute = computed(() => `/${userRole.value}/profile`)

    const handleLogout = async () => {
      try {
        await store.dispatch('auth/logout')
        router.push('/login')
        // The redirect is now handled in the store action
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    return {
      isLoggedIn,
      userName,
      userEmail,
      currentNavigation,
      profileRoute,
      handleLogout,
    }
  },
}
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.avatar {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dropdown-item i {
  width: 1.25rem;
}

/* Active state styling */
.router-link-active {
  font-weight: 500;
}

.dropdown-item.router-link-active {
  color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.1);
}

/* Mobile optimizations */
@media (max-width: 991.98px) {
  .navbar-collapse {
    background-color: var(--bs-primary);
    margin-top: 0.5rem;
    padding: 1rem;
    border-radius: 0.5rem;
  }

  .dropdown-menu {
    background-color: rgba(0, 0, 0, 0.1);
    border: none;
  }

  .dropdown-item {
    color: rgba(255, 255, 255, 0.8);
  }
}
</style>
