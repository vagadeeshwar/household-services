export default [
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/public/NotFound.vue'),
    meta: { title: '404 Not Found' },
  },
]
