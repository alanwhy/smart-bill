import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi } from "@/api/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(null);
  const userId = ref<number | null>(null);
  const username = ref<string | null>(null);
  const role = ref<string>("user");
  const mustChangePassword = ref<boolean>(false);
  const cycleStartDay = ref<number>(1);

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => role.value === "admin");

  function persist() {
    if (token.value) localStorage.setItem("token", token.value);
    if (userId.value !== null) localStorage.setItem("userId", String(userId.value));
    if (username.value) localStorage.setItem("username", username.value);
    localStorage.setItem("role", role.value);
    localStorage.setItem("mustChangePassword", mustChangePassword.value ? "1" : "0");
  }

  function initFromStorage() {
    const storedToken = localStorage.getItem("token");
    const storedUserId = localStorage.getItem("userId");
    const storedUsername = localStorage.getItem("username");

    if (storedToken && storedUserId && storedUsername) {
      token.value = storedToken;
      userId.value = parseInt(storedUserId);
      username.value = storedUsername;
      role.value = localStorage.getItem("role") || "user";
      mustChangePassword.value = localStorage.getItem("mustChangePassword") === "1";
    }
  }

  async function login(usernameInput: string, password: string) {
    const data = await authApi.login(usernameInput, password);
    token.value = data.token;
    userId.value = data.user_id;
    username.value = data.username;
    role.value = data.role || "user";
    mustChangePassword.value = !!data.must_change_password;

    persist();

    // 强制改密的用户先不拉周期；改密后会进入 Dashboard，再由其它流程触发
    if (!mustChangePassword.value) {
      await fetchCycle();
    }
  }

  function logout() {
    token.value = null;
    userId.value = null;
    username.value = null;
    role.value = "user";
    mustChangePassword.value = false;
    cycleStartDay.value = 1;

    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
    localStorage.removeItem("mustChangePassword");
  }

  function markPasswordChanged() {
    mustChangePassword.value = false;
    localStorage.setItem("mustChangePassword", "0");
  }

  async function fetchCycle() {
    try {
      const data = await authApi.getCycle();
      cycleStartDay.value = data.cycle_start_day;
    } catch {
      // 静默失败，使用默认值 1
      cycleStartDay.value = 1;
    }
  }

  async function saveCycle(day: number) {
    const data = await authApi.updateCycle(day);
    cycleStartDay.value = data.cycle_start_day;
  }

  return {
    token,
    userId,
    username,
    role,
    mustChangePassword,
    cycleStartDay,
    isAuthenticated,
    isAdmin,
    initFromStorage,
    login,
    logout,
    markPasswordChanged,
    fetchCycle,
    saveCycle,
  };
});
