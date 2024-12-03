export default [
  {
    path: 'dashboard',
    name: 'ProfessionalDashboard',
    component: () => import('@/views/professional/Dashboard.vue'),
    meta: { title: 'Professional Dashboard', requiresAuth: true, roles: ['professional'] },
  },

  // {
  //   path: 'requests',
  //   name: 'ProfessionalRequests',
  //   component: () => import('@/views/professional/ServiceRequests.vue'),
  //   meta: { title: 'Service Requests' },
  // },
  // {
  //   path: 'schedule',
  //   name: 'ProfessionalSchedule',
  //   component: () => import('@/views/professional/Schedule.vue'),
  //   meta: { title: 'My Schedule' },
  // },
  // {
  //   path: 'reviews',
  //   name: 'ProfessionalReviews',
  //   component: () => import('@/views/professional/Reviews.vue'),
  //   meta: { title: 'My Reviews' },
  // },
  {
    path: 'profile',
    name: 'ProfessionalProfile',
    component: () => import('@/views/professional/Profile.vue'),
    meta: { title: 'My Profile' },
  },
]
