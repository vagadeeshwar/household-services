// src/router/guards.js
import store from '@/store'

export const setupGuards = (router) => {
  router.beforeEach(async (to, from, next) => {
    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
    const guestOnly = to.matched.some((record) => record.meta.guestOnly)
    const isLoggedIn = store.getters['auth/isLoggedIn']
    const userRole = store.getters['auth/userRole']

    // For guest-only routes (like login)
    if (guestOnly && isLoggedIn) {
      const roleHomePage = {
        admin: '/admin/dashboard',
        professional: '/professional/dashboard',
        customer: '/customer/dashboard',
      }
      next(roleHomePage[userRole] || '/')
      return
    }

    // For auth required routes
    if (requiresAuth && !isLoggedIn) {
      next({ name: 'Login' })
      return
    }

    // Check role-based access
    if (requiresAuth && isLoggedIn) {
      const requiredRoles = to.matched.find((record) => record.meta.roles)?.meta.roles
      if (requiredRoles && !requiredRoles.includes(userRole)) {
        window.showToast({
          type: 'warning',
          title: 'Access Restricted',
          message: 'You do not have permission to access this page',
        })
        next({ name: 'NotFound' })
        return
      }
    }

    // If everything is fine, proceed
    next()
  })
}
