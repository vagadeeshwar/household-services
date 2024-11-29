# src/components/layout/TheNavbar.vue
<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <!-- Brand -->
            <router-link class="navbar-brand d-flex align-items-center" to="/">
                <i class="bi bi-tools me-2"></i>
                Household Services
            </router-link>

            <!-- Mobile Toggle -->
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav">
                <span class="navbar-toggler-icon"></span>
            </button>

            <!-- Navigation Links -->
            <div class="collapse navbar-collapse" id="mainNav">
                <!-- Authenticated Navigation -->
                <template v-if="isLoggedIn">
                    <!-- Admin Links -->
                    <ul v-if="isAdmin" class="navbar-nav me-auto">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin/dashboard">
                                <i class="bi bi-speedometer2 me-1"></i>
                                Dashboard
                            </router-link>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="bi bi-gear me-1"></i>
                                Management
                            </a>
                            <ul class="dropdown-menu">
                                <li>
                                    <router-link class="dropdown-item" to="/admin/services">
                                        <i class="bi bi-tools me-2"></i>
                                        Services
                                    </router-link>
                                </li>
                                <li>
                                    <router-link class="dropdown-item" to="/admin/professionals">
                                        <i class="bi bi-person-badge me-2"></i>
                                        Professionals
                                    </router-link>
                                </li>
                                <li>
                                    <router-link class="dropdown-item" to="/admin/customers">
                                        <i class="bi bi-people me-2"></i>
                                        Customers
                                    </router-link>
                                </li>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li>
                                    <router-link class="dropdown-item" to="/admin/reports">
                                        <i class="bi bi-file-earmark-text me-2"></i>
                                        Reports
                                    </router-link>
                                </li>
                            </ul>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin/requests">
                                <i class="bi bi-list-check me-1"></i>
                                Requests
                            </router-link>
                        </li>
                    </ul>

                    <!-- Professional Links -->
                    <ul v-else-if="isProfessional" class="navbar-nav me-auto">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional/dashboard">
                                <i class="bi bi-speedometer2 me-1"></i>
                                Dashboard
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional/requests">
                                <i class="bi bi-list-check me-1"></i>
                                Service Requests
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional/schedule">
                                <i class="bi bi-calendar3 me-1"></i>
                                Schedule
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional/reviews">
                                <i class="bi bi-star me-1"></i>
                                Reviews
                            </router-link>
                        </li>
                    </ul>

                    <!-- Customer Links -->
                    <ul v-else-if="isCustomer" class="navbar-nav me-auto">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/customer/dashboard">
                                <i class="bi bi-speedometer2 me-1"></i>
                                Dashboard
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/customer/services">
                                <i class="bi bi-tools me-1"></i>
                                Services
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/customer/requests">
                                <i class="bi bi-list-check me-1"></i>
                                My Requests
                            </router-link>
                        </li>
                    </ul>

                    <!-- Right Side Navigation (Authenticated) -->
                    <ul class="navbar-nav ms-auto">
                        <!-- Notifications -->
                        <li class="nav-item">
                            <a class="nav-link position-relative" href="#" @click.prevent="toggleNotifications">
                                <i class="bi bi-bell"></i>
                                <span v-if="unreadNotifications"
                                    class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                                    {{ unreadNotifications }}
                                </span>
                            </a>
                        </li>

                        <!-- User Menu Dropdown -->
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button"
                                data-bs-toggle="dropdown">
                                <div class="avatar bg-light text-primary rounded-circle d-flex align-items-center justify-content-center me-2"
                                    style="width: 32px; height: 32px;">
                                    <i class="bi bi-person-fill"></i>
                                </div>
                                {{ userName }}
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li class="dropdown-header">
                                    <div class="text-muted small">Signed in as</div>
                                    <div class="fw-medium">{{ userEmail }}</div>
                                </li>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li>
                                    <router-link class="dropdown-item" :to="profileRoute">
                                        <i class="bi bi-person-circle me-2"></i>
                                        Profile
                                    </router-link>
                                </li>
                                <li>
                                    <router-link class="dropdown-item" to="/settings">
                                        <i class="bi bi-gear me-2"></i>
                                        Settings
                                    </router-link>
                                </li>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li>
                                    <a class="dropdown-item text-danger" href="#" @click.prevent="handleLogout">
                                        <i class="bi bi-box-arrow-right me-2"></i>
                                        Sign Out
                                    </a>
                                </li>
                            </ul>
                        </li>
                    </ul>
                </template>

                <!-- Unauthenticated Navigation -->
                <template v-else>
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/services">
                                <i class="bi bi-tools me-1"></i>
                                Our Services
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/about">
                                <i class="bi bi-info-circle me-1"></i>
                                About Us
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/contact">
                                <i class="bi bi-envelope me-1"></i>
                                Contact
                            </router-link>
                        </li>
                    </ul>

                    <!-- Right Side Navigation (Unauthenticated) -->
                    <ul class="navbar-nav ms-auto">
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
                </template>
            </div>
        </div>
    </nav>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Modal } from 'bootstrap'

export default {
    name: 'TheNavbar',

    setup() {
        const store = useStore()
        const router = useRouter()
        const notificationsCanvas = ref(null)
        const unreadNotifications = ref(0)

        // Computed properties for auth state
        const isLoggedIn = computed(() => store.getters['auth/isLoggedIn'])
        const userName = computed(() => store.getters['auth/userName'])
        const userEmail = computed(() => store.getters['auth/userEmail'])
        const userRole = computed(() => store.getters['auth/userRole'])

        // Role-based computed properties
        const isAdmin = computed(() => userRole.value === 'admin')
        const isProfessional = computed(() => userRole.value === 'professional')
        const isCustomer = computed(() => userRole.value === 'customer')

        // Dynamic profile route based on user role
        const profileRoute = computed(() => {
            switch (userRole.value) {
                case 'admin':
                    return '/admin/profile'
                case 'professional':
                    return '/professional/profile'
                case 'customer':
                    return '/customer/profile'
                default:
                    return '/profile'
            }
        })

        // Handle logout
        const handleLogout = async () => {
            try {
                await store.dispatch('auth/logout')
                router.push('/login')
            } catch (error) {
                console.error('Logout error:', error)
            }
        }


        // Toggle notifications
        const toggleNotifications = () => {
            if (!notificationsCanvas.value) {
                notificationsCanvas.value = new Modal(document.getElementById('notificationsCanvas'))
            }
            notificationsCanvas.value.show()
        }

        return {
            isLoggedIn,
            userName,
            userEmail,
            userRole,
            isAdmin,
            isProfessional,
            isCustomer,
            profileRoute,
            unreadNotifications,
            handleLogout,
            toggleNotifications,
        }
    }
}
</script>

<style scoped>
.navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, .1);
}

.navbar-brand {
    font-weight: 600;
}

.nav-link {
    padding: 0.5rem 1rem;
}

.dropdown-item {
    padding: 0.5rem 1rem;
}

.dropdown-item i {
    width: 1.25rem;
}

.avatar {
    font-size: 1.25rem;
}

/* Active link styling */
.nav-link.router-link-active {
    color: #fff !important;
    font-weight: 500;
}

.dropdown-item.router-link-active {
    color: #0d6efd;
    background-color: rgba(13, 110, 253, 0.1);
}

/* Mobile optimization */
@media (max-width: 992px) {
    .navbar-collapse {
        background-color: #0d6efd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
    }

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

    .dropdown-divider {
        border-color: rgba(255, 255, 255, 0.1);
    }
}
</style>