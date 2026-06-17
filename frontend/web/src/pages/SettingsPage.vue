<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-text mb-2">设置</h1>
        <p class="text-text-muted">管理您的应用设置</p>
      </div>

      <!-- 账单分类 -->
      <div class="card p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-text">账单分类</h2>
          <router-link to="/categories" class="btn btn-secondary btn-sm">管理分类</router-link>
        </div>
        <p v-if="categoriesStore.isLoading && categories.length === 0" class="text-xs text-text-muted">加载中...</p>
        <p v-else-if="categories.length === 0" class="text-xs text-text-muted">暂无分类</p>
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div
            v-for="cat in categories"
            :key="cat.id"
            class="p-4 rounded-lg bg-surface border border-border text-center"
          >
            <div class="text-2xl mb-2">{{ cat.icon }}</div>
            <div class="text-sm text-text-secondary">{{ cat.name }}</div>
          </div>
        </div>
      </div>

      <!-- 关于 -->
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-text mb-4">关于</h2>
        <div class="space-y-3 text-sm text-text-secondary">
          <div class="flex justify-between">
            <span>应用名称</span>
            <span class="text-text">Smart Bill</span>
          </div>
          <div class="flex justify-between">
            <span>版本</span>
            <span class="text-text">0.1.0</span>
          </div>
          <div class="flex justify-between">
            <span>描述</span>
            <span class="text-text">智能账单识别和管理应用</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useCategoriesStore } from '@/stores/categories'

const categoriesStore = useCategoriesStore()
const categories = computed(() => categoriesStore.sortedCategories)

onMounted(() => {
  categoriesStore.getOrFetch()
})
</script>
