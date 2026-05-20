import { createRouter, createWebHistory } from 'vue-router'

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
    path: '/favorites',
    name: 'Favorites',
    component: () => import('./views/FavoritesView.vue'),
  },
  {
    path: '/shared',
    name: 'SharedWithMe',
    component: () => import('./views/SharedWithMeView.vue'),
  },
  {
    path: '/shared/:token',
    name: 'SharedLink',
    component: () => import('./views/SharedLinkView.vue'),
    meta: { public: true },
  },
  {
    path: '/generator',
    name: 'Generator',
    component: () => import('./views/PasswordGeneratorView.vue'),
  },
  {
    path: '/audit',
    name: 'AuditLog',
    component: () => import('./views/AuditLogView.vue'),
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

export default router
