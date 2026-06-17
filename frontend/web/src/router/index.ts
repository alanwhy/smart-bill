import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '@/pages/DashboardPage.vue'
import SettingsPage from '@/pages/SettingsPage.vue'
import CategoriesPage from '@/pages/CategoriesPage.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardPage,
  },
  {
    path: '/categories',
    name: 'Categories',
    component: CategoriesPage,
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage,
  },
]

const router = createRouter({
  history: createWebHistory('/'),
  routes,
})

export default router
