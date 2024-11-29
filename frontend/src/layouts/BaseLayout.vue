<!-- src/layouts/BaseLayout.vue -->
<template>
    <div class="layout-container">
        <TheNavbar />


        <!-- Main Content -->
        <main class="flex-grow-1">
            <router-view></router-view>
            <Toast />
        </main>

        <!-- Footer -->
        <footer class="footer mt-auto py-3 bg-light">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-md-6 text-center text-md-start">
                        <span class="text-muted">© 2024 Household Services. All rights reserved.</span>
                    </div>
                    <div class="col-md-6">
                        <ul class="list-inline mb-0 text-center text-md-end">
                            <li class="list-inline-item">
                                <router-link class="text-muted" to="/privacy">Privacy Policy</router-link>
                            </li>
                            <li class="list-inline-item">
                                <router-link class="text-muted" to="/terms">Terms of Service</router-link>
                            </li>
                            <li class="list-inline-item">
                                <router-link class="text-muted" to="/contact">Support</router-link>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </footer>

        <!-- Notifications Offcanvas -->
        <div class="offcanvas offcanvas-end" tabindex="-1" id="notificationsCanvas">
            <div class="offcanvas-header">
                <h5 class="offcanvas-title">Notifications</h5>
                <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
            </div>
            <div class="offcanvas-body">
                <!-- Add notifications content here -->
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { Offcanvas } from 'bootstrap';
import TheNavbar from '@/components/layout/TheNavbar.vue'

export default {
    name: 'BaseLayout',

    setup() {
        const store = useStore();
        const router = useRouter();
        const notificationsCanvas = ref(null);
        const unreadNotifications = ref(0);

        // Computed properties for auth state
        const isLoggedIn = computed(() => store.getters['auth/isLoggedIn']);
        const userName = computed(() => store.getters['auth/userName']);
        const userEmail = computed(() => store.getters['auth/userEmail']);
        const userRole = computed(() => store.getters['auth/userRole']);

        // Role-based computed properties
        const isAdmin = computed(() => userRole.value === 'admin');
        const isProfessional = computed(() => userRole.value === 'professional');
        const isCustomer = computed(() => userRole.value === 'customer');

        // Dynamic profile route based on user role
        const profileRoute = computed(() => {
            switch (userRole.value) {
                case 'admin':
                    return '/admin/profile';
                case 'professional':
                    return '/professional/profile';
                case 'customer':
                    return '/customer/profile';
                default:
                    return '/profile';
            }
        });

        const handleLogout = async () => {
            try {
                await store.dispatch('auth/logout');
                router.push('/login');
            } catch (error) {
                console.error('Logout error:', error);
            }
        };

        const toggleNotifications = () => {
            if (!notificationsCanvas.value) {
                notificationsCanvas.value = new Offcanvas(document.getElementById('notificationsCanvas'));
            }
            notificationsCanvas.value.show();
        };

        onMounted(() => {
            // Fetch initial notifications count
            // Add notification polling or websocket connection here
        });

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
            toggleNotifications
        };
    },
    components: {
        TheNavbar
    }
};
</script>

<style scoped>
.layout-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

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

.footer {
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
}

.list-inline-item:not(:last-child) {
    margin-right: 1.5rem;
}

/* Notification badge positioning */
.position-relative .badge {
    transform: translate(-50%, -50%);
}

/* Offcanvas customization */
.offcanvas {
    width: 350px;
}

@media (max-width: 576px) {
    .offcanvas {
        width: 100%;
    }

    .navbar-nav .dropdown-menu {
        position: static;
        float: none;
    }

    .footer {
        text-align: center;
    }

    .list-inline-item {
        display: block;
        margin-bottom: 0.5rem;
    }
}

/* Transitions for dropdown menus */
.dropdown-menu {
    display: block;
    opacity: 0;
    visibility: hidden;
    transform: translateY(10px);
    transition: all 0.2s ease;
}

.dropdown-menu.show {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
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

/* Hover effects */
.nav-link:hover {
    color: rgba(255, 255, 255, 0.9) !important;
}

.dropdown-item:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

/* Custom scrollbar for notifications */
.offcanvas-body {
    scrollbar-width: thin;
    scrollbar-color: #888 #f1f1f1;
}

.offcanvas-body::-webkit-scrollbar {
    width: 6px;
}

.offcanvas-body::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.offcanvas-body::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
}

.offcanvas-body::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* Profile dropdown customization */
.navbar-nav .dropdown-menu {
    min-width: 240px;
}

.dropdown-header {
    padding: 0.5rem 1rem;
}

/* Footer link hover effect */
.footer a {
    text-decoration: none;
    transition: color 0.2s ease;
}

.footer a:hover {
    color: #0d6efd !important;
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