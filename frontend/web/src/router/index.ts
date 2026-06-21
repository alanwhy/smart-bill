import { createRouter, createWebHistory } from "vue-router";
import DashboardPage from "@/pages/DashboardPage.vue";
import StatsPage from "@/pages/StatsPage.vue";
import SettingsPage from "@/pages/SettingsPage.vue";
import CategoriesPage from "@/pages/CategoriesPage.vue";
import LoginPage from "@/pages/LoginPage.vue";
import UserPage from "@/pages/UserPage.vue";
import ForceChangePasswordPage from "@/pages/ForceChangePasswordPage.vue";
import UsersAdminPage from "@/pages/UsersAdminPage.vue";
import { useAuthStore } from "@/stores/auth";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
    meta: { requiresAuth: false },
  },
  {
    path: "/force-change-password",
    name: "ForceChangePassword",
    component: ForceChangePasswordPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/",
    name: "Dashboard",
    component: DashboardPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/stats",
    name: "Stats",
    component: StatsPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/categories",
    name: "Categories",
    component: CategoriesPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/settings",
    name: "Settings",
    component: SettingsPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/user",
    name: "User",
    component: UserPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/users",
    name: "UsersAdmin",
    component: UsersAdminPage,
    meta: { requiresAuth: true, adminOnly: true },
  },
];

const router = createRouter({
  history: createWebHistory("/"),
  routes,
});

router.beforeEach((to) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: "Login" };
  }

  if (to.name === "Login" && authStore.isAuthenticated) {
    return { name: "Dashboard" };
  }

  // 强制改密：除 ForceChangePassword 和 Login 外一律拦截
  if (
    authStore.isAuthenticated &&
    authStore.mustChangePassword &&
    to.name !== "ForceChangePassword" &&
    to.name !== "Login"
  ) {
    return { name: "ForceChangePassword" };
  }

  // 仅管理员可访问的页面
  if (to.meta.adminOnly && !authStore.isAdmin) {
    return { name: "Dashboard" };
  }
});

export default router;
