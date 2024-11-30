// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';

// Import components
import CustomerRegisterForm from '../components/auth/CustomerRegisterForm.vue';
import ProfessionalRegisterForm from '../components/auth/ProfessionalRegisterForm.vue';
import LoginForm from '../components/auth/LoginForm.vue';
import NotFound from '../views/NotFound.vue';
import ServicesPage from '../views/public/ServicesPage.vue';

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
  if (!store.getters['auth/isLoggedIn'] || store.getters['auth/userRole'] !== 'professional') {
    next({ name: 'NotFound' });
  } else {
    next();
  }
}

function requireCustomer(to, from, next) {
  if (!store.getters['auth/isLoggedIn'] || store.getters['auth/userRole'] !== 'customer') {
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
    path: '/services',
    name: 'PublicServices',
    component: ServicesPage,
    meta: { guestOnly: false }
  },
  {
    path: '/profile/:id?',
    name: 'Profile',
    component: () => import('@/views/profile/ProfilePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/public/AboutPage.vue'),
    meta: { guestOnly: false }
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/public/ContactPage.vue'),
    meta: { guestOnly: false }
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('../views/public/TermsPage.vue'),
    meta: { guestOnly: false }
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/public/PrivacyPage.vue'),
    meta: { guestOnly: false }
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
        name: 'CustomerServices',
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