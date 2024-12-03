export default [
  {
    path: 'dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { title: 'Admin Dashboard', requiresAuth: true, roles: ['admin'] },
  },

  {
    path: 'services',
    name: 'AdminServices',
    component: () => import('@/views/admin/Services.vue'),
    meta: { title: 'Manage Services' },
  },
  // {
  //   path: 'professionals',
  //   name: 'AdminProfessionals',
  //   component: () => import('@/views/admin/Professionals.vue'),
  //   meta: { title: 'Manage Professionals' },
  // },
  // {
  //   path: 'customers',
  //   name: 'AdminCustomers',
  //   component: () => import('@/views/admin/Customers.vue'),
  //   meta: { title: 'Manage Customers' },
  // },
  // {
  //   path: 'reports',
  //   name: 'AdminReports',
  //   component: () => import('@/views/admin/Reports.vue'),
  //   meta: { title: 'Reports' },
  // },
  {
    path: 'profile',
    name: 'AdminProfile',
    component: () => import('@/views/admin/Profile.vue'),
    meta: { title: 'My Profile' },
  },
]
