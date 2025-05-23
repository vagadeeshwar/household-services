export default [
  {
    path: 'dashboard',
    name: 'ProfessionalDashboard',
    component: () => import('@/views/professional/Dashboard.vue'),
    meta: { title: 'Professional Dashboard', requiresAuth: true, roles: ['professional'] },
  },

  {
    path: 'requests',
    name: 'ProfessionalRequests',
    component: () => import('@/views/professional/Requests.vue'),
    meta: { title: 'Service Requests' },
  },
  {
    path: 'profile',
    name: 'ProfessionalProfile',
    component: () => import('@/views/professional/Profile.vue'),
    meta: { title: 'My Profile' },
  },
]
