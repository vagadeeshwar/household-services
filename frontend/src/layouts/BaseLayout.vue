// frontend/src/layouts/BaseLayout.vue
<template>
    <div class="layout-container">
        <!-- Navigation Bar -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <router-link class="navbar-brand" to="/">Service Platform</router-link>

                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain"
                    aria-controls="navbarMain" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse" id="navbarMain">
                    <!-- Show these items only when user is logged in -->
                    <ul v-if="isLoggedIn" class="navbar-nav me-auto mb-2 mb-lg-0">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/dashboard">Dashboard</router-link>
                        </li>

                        <!-- Customer specific navigation -->
                        <li v-if="isCustomer" class="nav-item">
                            <router-link class="nav-link" to="/services">Services</router-link>
                        </li>
                        <li v-if="isCustomer" class="nav-item">
                            <router-link class="nav-link" to="/my-requests">My Requests</router-link>
                        </li>

                        <!-- Professional specific navigation -->
                        <li v-if="isProfessional" class="nav-item">
                            <router-link class="nav-link" to="/my-services">My Services</router-link>
                        </li>
                        <li v-if="isProfessional" class="nav-item">
                            <router-link class="nav-link" to="/requests">Service Requests</router-link>
                        </li>

                        <!-- Admin specific navigation -->
                        <li v-if="isAdmin" class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown"
                                aria-expanded="false">
                                Management
                            </a>
                            <ul class="dropdown-menu">
                                <li><router-link class="dropdown-item" to="/manage/services">Services</router-link></li>
                                <li><router-link class="dropdown-item"
                                        to="/manage/professionals">Professionals</router-link></li>
                                <li><router-link class="dropdown-item" to="/manage/customers">Customers</router-link>
                                </li>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li><router-link class="dropdown-item" to="/manage/requests">Requests</router-link></li>
                            </ul>
                        </li>
                    </ul>

                    <!-- User Menu -->
                    <ul class="navbar-nav ms-auto">
                        <template v-if="isLoggedIn">
                            <li class="nav-item dropdown">
                                <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown"
                                    aria-expanded="false">
                                    {{ userName }}
                                </a>
                                <ul class="dropdown-menu dropdown-menu-end">
                                    <li><router-link class="dropdown-item" to="/profile">My Profile</router-link></li>
                                    <li>
                                        <hr class="dropdown-divider">
                                    </li>
                                    <li><a class="dropdown-item" href="#" @click.prevent="handleLogout">Logout</a></li>
                                </ul>
                            </li>
                        </template>
                        <template v-else>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/login">Login</router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/register">Register</router-link>
                            </li>
                        </template>
                    </ul>
                </div>
            </div>
        </nav>

        <!-- Main Content Area -->
        <main class="container py-4">
            <router-view></router-view>
        </main>

        <!-- Footer -->
        <footer class="footer mt-auto py-3 bg-light">
            <div class="container text-center">
                <span class="text-muted">© 2024 Service Platform. All rights reserved.</span>
            </div>
        </footer>
    </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
    name: 'BaseLayout',

    setup() {
        const store = useStore()
        const router = useRouter()

        const isLoggedIn = computed(() => store.getters['auth/isLoggedIn'])
        const userName = computed(() => store.getters['auth/userName'])
        const userRole = computed(() => store.getters['auth/userRole'])

        const isCustomer = computed(() => userRole.value === 'customer')
        const isProfessional = computed(() => userRole.value === 'professional')
        const isAdmin = computed(() => userRole.value === 'admin')

        const handleLogout = async () => {
            await store.dispatch('auth/logout')
            router.push('/login')
        }

        return {
            isLoggedIn,
            userName,
            isCustomer,
            isProfessional,
            isAdmin,
            handleLogout
        }
    }
}
</script>

<style scoped>
.layout-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

main {
    flex: 1;
}

.navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, .1);
}

.footer {
    margin-top: auto;
    box-shadow: 0 -2px 4px rgba(0, 0, 0, .1);
}
</style>