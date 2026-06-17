<template>
  <div class="flex h-screen bg-background text-text">
    <!-- Sidebar - 桌面版 -->
    <aside class="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:w-64 lg:flex lg:flex-col lg:bg-surface lg:border-r lg:border-border">
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
      </nav>
    </aside>

    <!-- 主容器 -->
    <div class="flex flex-col flex-1 lg:ml-64">
      <!-- Header -->
      <header class="sticky top-0 z-40 border-b border-border bg-surface/80 backdrop-blur-md">
        <div class="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
          <!-- Logo - 移动版 -->
          <div class="lg:hidden">
            <h1 class="text-xl font-bold text-primary">Smart Bill</h1>
          </div>

          <!-- 搜索框 -->
          <div class="flex flex-1 justify-center px-4 lg:px-8">
            <input
              type="text"
              placeholder="搜索账单..."
              class="input text-sm max-w-md"
            />
          </div>

          <!-- 用户菜单 -->
          <div class="flex items-center gap-4">
            <button class="p-2 hover:bg-border rounded-lg transition-colors duration-200">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>
    </div>

    <!-- 移动底部导航 -->
    <nav class="fixed bottom-0 left-0 right-0 lg:hidden bg-surface border-t border-border">
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
      </div>
    </nav>

    <!-- 移动端底部 nav 占位符 -->
    <div class="h-16 lg:hidden" />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
</style>
