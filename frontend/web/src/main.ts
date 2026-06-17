import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./styles/main.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// 在挂载前同步读取 localStorage，确保路由守卫和模板都能拿到正确的认证状态
import { useAuthStore } from "@/stores/auth";
const authStore = useAuthStore();
authStore.initFromStorage();

app.mount("#app");
