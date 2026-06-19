<template>
  <div class="flex h-screen bg-background text-text">
    <!-- Sidebar - 桌面版（仅登录后显示） -->
    <aside
      v-if="authStore.isAuthenticated"
      class="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:w-64 lg:flex lg:flex-col lg:bg-surface lg:border-r lg:border-border"
    >
      <div class="p-6 border-b border-border">
        <h1 class="text-2xl font-bold text-primary">Smart Bill</h1>
      </div>
      <nav class="flex-1 overflow-y-auto p-4">
        <router-link
          to="/"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200"
          :class="$route.path === '/' ? 'bg-primary text-background' : 'hover:bg-border text-text'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9m-9 0l1-3m6 3l-7-4" />
          </svg>
          <span>账单列表</span>
        </router-link>
        <router-link
          to="/categories"
          class="mt-2 flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200"
          :class="$route.path === '/categories' ? 'bg-primary text-background' : 'hover:bg-border text-text'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5a1.99 1.99 0 011.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.99 1.99 0 013 12V7a4 4 0 014-4z" />
          </svg>
          <span>分类管理</span>
        </router-link>
        <router-link
          to="/settings"
          class="mt-2 flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200"
          :class="$route.path === '/settings' ? 'bg-primary text-background' : 'hover:bg-border text-text'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span>设置</span>
        </router-link>
        <router-link
          v-if="authStore.isAdmin"
          to="/users"
          class="mt-2 flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200"
          :class="$route.path === '/users' ? 'bg-primary text-background' : 'hover:bg-border text-text'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span>用户管理</span>
        </router-link>
      </nav>
      <!-- 底部用户信息（点击跳转用户中心） -->
      <router-link
        to="/user"
        class="p-4 border-t border-border flex items-center gap-3 cursor-pointer transition-colors duration-200"
        :class="$route.path === '/user' ? 'bg-border/50' : 'hover:bg-border/40'"
        aria-label="进入用户中心"
      >
        <div class="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
          <svg class="w-4.5 h-4.5 w-[18px] h-[18px] text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-text truncate">{{ authStore.username }}</p>
          <p class="text-xs text-text-muted">用户中心</p>
        </div>
        <svg class="w-4 h-4 text-text-muted shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </router-link>
    </aside>

    <!-- 主容器 -->
    <div class="flex flex-col flex-1" :class="{ 'lg:ml-64': authStore.isAuthenticated }">
      <!-- Header（移动端，仅登录后显示） -->
      <header
        v-if="authStore.isAuthenticated"
        class="sticky top-0 z-40 border-b border-border bg-surface/80 backdrop-blur-md lg:hidden"
      >
        <div class="flex items-center justify-between h-16 px-4 sm:px-6">
          <h1 class="text-xl font-bold text-primary">Smart Bill</h1>
          <router-link
            to="/user"
            class="flex items-center justify-center w-9 h-9 rounded-full bg-primary/10 hover:bg-primary/20 cursor-pointer transition-colors duration-200"
            aria-label="进入用户中心"
          >
            <svg class="w-[18px] h-[18px] text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </router-link>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main class="flex-1 overflow-y-auto">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <!-- 移动底部导航（仅登录后显示） -->
    <nav
      v-if="authStore.isAuthenticated"
      class="fixed bottom-0 left-0 right-0 lg:hidden bg-surface border-t border-border"
    >
      <div class="flex items-center justify-around h-16">
        <router-link
          to="/"
          class="flex flex-col items-center justify-center gap-1 flex-1 h-full"
          :class="$route.path === '/' ? 'text-primary' : 'text-text-muted'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9m-9 0l1-3m6 3l-7-4" />
          </svg>
          <span class="text-xs">账单</span>
        </router-link>
        <router-link
          to="/categories"
          class="flex flex-col items-center justify-center gap-1 flex-1 h-full"
          :class="$route.path === '/categories' ? 'text-primary' : 'text-text-muted'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5a1.99 1.99 0 011.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.99 1.99 0 013 12V7a4 4 0 014-4z" />
          </svg>
          <span class="text-xs">分类</span>
        </router-link>
        <router-link
          to="/user"
          class="flex flex-col items-center justify-center gap-1 flex-1 h-full"
          :class="$route.path === '/user' ? 'text-primary' : 'text-text-muted'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span class="text-xs">用户</span>
        </router-link>
        <router-link
          to="/settings"
          class="flex flex-col items-center justify-center gap-1 flex-1 h-full"
          :class="$route.path === '/settings' ? 'text-primary' : 'text-text-muted'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span class="text-xs">设置</span>
        </router-link>
        <router-link
          v-if="authStore.isAdmin"
          to="/users"
          class="flex flex-col items-center justify-center gap-1 flex-1 h-full"
          :class="$route.path === '/users' ? 'text-primary' : 'text-text-muted'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span class="text-xs">用户</span>
        </router-link>
      </div>
    </nav>

    <!-- 移动端底部 nav 占位符 -->
    <div v-if="authStore.isAuthenticated" class="h-16 lg:hidden" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const categoriesStore = useCategoriesStore()

onMounted(() => {
  if (authStore.isAuthenticated) {
    categoriesStore.getOrFetch()
  }
})

// 登录后再加载分类
watch(
  () => authStore.isAuthenticated,
  (val) => {
    if (val) categoriesStore.getOrFetch()
  },
)
</script>

<style scoped>
</style>
