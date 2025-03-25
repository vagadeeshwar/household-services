export default [
  {
    path: 'dashboard',
    name: 'CustomerDashboard',
    component: () => import('@/views/customer/Dashboard.vue'),
    meta: { title: 'Customer Dashboard', requiresAuth: true, roles: ['customer'] },
  },
  {
    path: 'services',
    name: 'CustomerServices',
    component: () => import('@/views/customer/Services.vue'),
    meta: { title: 'Browse Services' },
  },
  {
    path: 'professionals',
    name: 'CustomerProfessionals',
    component: () => import('@/views/customer/Professionals.vue'),
    meta: { title: 'Browse Professionals' },
  },
  {
    path: 'requests',
    name: 'CustomerRequests',
    component: () => import('@/views/customer/Requests.vue'),
    meta: { title: 'My Requests' },
  },
  {
    path: 'profile',
    name: 'CustomerProfile',
    component: () => import('@/views/customer/Profile.vue'),
    meta: { title: 'My Profile' },
  },
]
