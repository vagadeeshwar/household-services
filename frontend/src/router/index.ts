import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import NotFound from '../views/NotFound.vue';
import Register from '../views/Register.vue';

const routes = [
  { path: '/', name: 'Home', component: Login },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
