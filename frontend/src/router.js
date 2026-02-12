import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('./views/DashboardView.vue'),
  },
  {
    path: '/secrets',
    name: 'Secrets',
    component: () => import('./views/SecretsView.vue'),
  },
  {
    path: '/secrets/:name',
    name: 'SecretDetail',
    component: () => import('./views/SecretDetailView.vue'),
    props: true,
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('./views/FavoritesView.vue'),
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('./views/CategoriesView.vue'),
  },
  {
    path: '/generator',
    name: 'Generator',
    component: () => import('./views/PasswordGeneratorView.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/SettingsView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/vault'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  // Ensure session is loaded
  if (!session.isLoggedIn && to.name !== 'Login') {
    await session.init()
  }
  next()
})

export default router
