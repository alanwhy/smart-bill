import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi } from "@/api/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(null);
  const userId = ref<number | null>(null);
  const username = ref<string | null>(null);

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
  }

  function logout() {
    token.value = null;
    userId.value = null;
    username.value = null;

    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    localStorage.removeItem("username");
  }

  return { token, userId, username, isAuthenticated, initFromStorage, login, logout };
});
