import { createRouter, createWebHistory } from 'vue-router'
import { setupGuards } from './guards'

// Route Configurations
import publicRoutes from './routes/public'
import customerRoutes from './routes/customer'
import professionalRoutes from './routes/professional'
import adminRoutes from './routes/admin'
import errorRoutes from './routes/error'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/BaseLayout.vue'),
    children: [
      {
        path: '',
        name: 'Root',
        beforeEnter: (to, from, next) => {
          const store = window?.__store__ // Access Vuex store
          if (store?.getters['auth/isLoggedIn']) {
            const role = store.getters['auth/userRole']
            switch (role) {
              case 'admin':
                next('/admin/dashboard')
                break
              case 'professional':
                next('/professional/dashboard')
                break
              case 'customer':
                next('/customer/dashboard')
                break
              default:
                next('/login')
            }
          } else {
            next('/login')
          }
        },
      },
      // Public routes
      ...publicRoutes,

      // Admin routes
      {
        path: '/admin',
        meta: { requiresAuth: true, roles: ['admin'] },
        children: adminRoutes,
      },

      // Professional routes
      {
        path: '/professional',
        meta: { requiresAuth: true, roles: ['professional'] },
        children: professionalRoutes,
      },

      // Customer routes
      {
        path: '/customer',
        meta: { requiresAuth: true, roles: ['customer'] },
        children: customerRoutes,
      },

      // Error routes
      ...errorRoutes,
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// Setup navigation guards
setupGuards(router)

export default router
