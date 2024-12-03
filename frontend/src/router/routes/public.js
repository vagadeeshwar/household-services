export default [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/public/ServicesPage.vue'),
    meta: { title: 'Home' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/public/Login.vue'),
    meta: { title: 'Login', guestOnly: true },
  },
  {
    path: '/register',
    children: [
      {
        path: 'customer',
        name: 'CustomerRegister',
        component: () => import('@/views/public/CustomerRegister.vue'),
        meta: { title: 'Register as Customer', guestOnly: true },
      },
      {
        path: 'professional',
        name: 'ProfessionalRegister',
        component: () => import('@/views/public/ProfessionalRegister.vue'),
        meta: { title: 'Register as Professional', guestOnly: true },
      },
    ],
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/public/AboutPage.vue'),
    meta: { title: 'About Us' },
  },
  {
    path: '/services',
    name: 'Services',
    component: () => import('@/views/public/ServicesPage.vue'),
    meta: { title: 'Browse Services' },
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('@/views/public/ContactPage.vue'),
    meta: { title: 'Contact Us' },
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('@/views/public/PrivacyPage.vue'),
    meta: { title: 'Privacy Policy' },
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('@/views/public/TermsPage.vue'),
    meta: { title: 'Terms of Service' },
  },
]
