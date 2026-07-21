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
    path: '/secrets/:name',
    name: 'SecretDetail',
    component: () => import('./views/SecretDetailView.vue'),
    props: true,
  },
  {
    path: '/bookmarks',
    name: 'Bookmarks',
    component: () => import('./views/BookmarksView.vue'),
  },
  {
    path: '/shared',
    name: 'SharedWithMe',
    component: () => import('./views/SharedWithMeView.vue'),
  },
  {
    path: '/shares',
    name: 'ManageShares',
    component: () => import('./views/ManageSharesView.vue'),
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
]

const router = createRouter({
  history: createWebHistory('/vault'),
  routes,
})

export default router
