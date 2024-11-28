import { createRouter, createWebHistory } from 'vue-router';
import store from '../store'; // Import the Vuex store directly

// Import components
import CustomerRegisterForm from '../components/auth/CustomerRegisterForm.vue';
import ProfessionalRegisterForm from '../components/auth/ProfessionalRegisterForm.vue';
import LoginForm from '../components/auth/LoginForm.vue';
import NotFound from '../views/NotFound.vue';

// Route Guards
function requireAuth(to, from, next) {
  if (!store.getters['auth/isLoggedIn']) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else {
    next();
  }
}

function requireAdmin(to, from, next) {
  if (!store.getters['auth/isLoggedIn'] || store.getters['auth/userRole'] !== 'admin') {
    next({ name: 'NotFound' });
  } else {
    next();
  }
}

function requireProfessional(to, from, next) {
  if (
    !store.getters['auth/isLoggedIn'] ||
    store.getters['auth/userRole'] !== 'professional'
  ) {
    next({ name: 'NotFound' });
  } else {
    next();
  }
}

function requireCustomer(to, from, next) {
  if (
    !store.getters['auth/isLoggedIn'] ||
    store.getters['auth/userRole'] !== 'customer'
  ) {
    next({ name: 'NotFound' });
  } else {
    next();
  }
}

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: to => {
      if (!store.getters['auth/isLoggedIn']) return { name: 'Login' };

      // Redirect based on user role
      switch (store.getters['auth/userRole']) {
        case 'admin':
          return { name: 'AdminDashboard' };
        case 'professional':
          return { name: 'ProfessionalDashboard' };
        case 'customer':
          return { name: 'CustomerDashboard' };
        default:
          return { name: 'Login' };
      }
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginForm,
    meta: { guestOnly: true }
  },
  {
    path: '/register/customer',
    name: 'CustomerRegister',
    component: CustomerRegisterForm,
    meta: { guestOnly: true }
  },
  {
    path: '/register/professional',
    name: 'ProfessionalRegister',
    component: ProfessionalRegisterForm,
    meta: { guestOnly: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    redirect: { name: 'AdminDashboard' },
    beforeEnter: requireAdmin,
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/Dashboard.vue')
      }
      // Add other admin routes here
    ]
  },
  {
    path: '/professional',
    name: 'Professional',
    redirect: { name: 'ProfessionalDashboard' },
    beforeEnter: requireProfessional,
    children: [
      {
        path: 'dashboard',
        name: 'ProfessionalDashboard',
        component: () => import('../views/professional/Dashboard.vue')
      }
      // Add other professional routes here
    ]
  },
  {
    path: '/customer',
    name: 'Customer',
    redirect: { name: 'CustomerDashboard' },
    beforeEnter: requireCustomer,
    children: [
      {
        path: 'dashboard',
        name: 'CustomerDashboard',
        component: () => import('../views/customer/Dashboard.vue')
      },
      {
        path: 'services',
        name: 'Services',
        component: () => import('../views/customer/ServiceBrowser.vue'),
        meta: {
          requiresAuth: true,
          roles: ['customer']
        }
      },
      {
        path: 'my-requests',
        name: 'MyRequests',
        component: () => import('../views/customer/ServiceRequests.vue'),
        meta: {
          requiresAuth: true,
          roles: ['customer']
        }
      }
      // Add other customer routes here
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Global navigation guard
router.beforeEach((to, from, next) => {
  const isLoggedIn = store.getters['auth/isLoggedIn'];

  // Handle routes that should only be accessible to guests
  if (to.meta.guestOnly && isLoggedIn) {
    return next({ name: 'Home' });
  }

  // Handle routes that require authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      return next({
        name: 'Login',
        query: { redirect: to.fullPath }
      });
    }
  }

  next();
});

export default router;
