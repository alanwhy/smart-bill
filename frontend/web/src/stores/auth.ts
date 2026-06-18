import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi } from "@/api/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(null);
  const userId = ref<number | null>(null);
  const username = ref<string | null>(null);
  const cycleStartDay = ref<number>(1);

  const isAuthenticated = computed(() => !!token.value);

  function initFromStorage() {
    const storedToken = localStorage.getItem("token");
    const storedUserId = localStorage.getItem("userId");
    const storedUsername = localStorage.getItem("username");

    if (storedToken && storedUserId && storedUsername) {
      token.value = storedToken;
      userId.value = parseInt(storedUserId);
      username.value = storedUsername;
    }
  }

  async function login(usernameInput: string, password: string) {
    const data = await authApi.login(usernameInput, password);
    token.value = data.token;
    userId.value = data.user_id;
    username.value = data.username;

    localStorage.setItem("token", data.token);
    localStorage.setItem("userId", String(data.user_id));
    localStorage.setItem("username", data.username);

    // 登录后自动拉取周期设置
    await fetchCycle();
  }

  function logout() {
    token.value = null;
    userId.value = null;
    username.value = null;
    cycleStartDay.value = 1;

    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    localStorage.removeItem("username");
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

  return { token, userId, username, cycleStartDay, isAuthenticated, initFromStorage, login, logout, fetchCycle, saveCycle };
});
