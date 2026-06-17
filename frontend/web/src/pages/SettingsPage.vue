<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-text mb-2">设置</h1>
        <p class="text-text-muted">管理您的应用设置</p>
      </div>

      <!-- 用户信息 -->
      <div class="card p-6 mb-6">
        <h2 class="text-lg font-semibold text-text mb-4">用户信息</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-text-secondary mb-2">用户 ID</label>
            <div class="flex gap-2">
              <input
                v-model="userId"
                type="number"
                min="1"
                class="input flex-1"
              />
              <button
                @click="saveUserId"
                :disabled="isSaving"
                class="btn btn-primary"
              >
                {{ isSaving ? '保存中...' : '保存' }}
              </button>
            </div>
            <p class="text-xs text-text-muted mt-2">当前已保存的 ID: {{ savedUserId }}</p>
          </div>
        </div>
      </div>

      <!-- 账单分类 -->
      <div class="card p-6 mb-6">
        <h2 class="text-lg font-semibold text-text mb-4">账单分类</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div
            v-for="category in categories"
            :key="category.value"
            class="p-4 rounded-lg bg-surface border border-border text-center"
          >
            <div class="text-2xl mb-2">{{ category.icon }}</div>
            <div class="text-sm text-text-secondary">{{ category.label }}</div>
          </div>
        </div>
        <p class="text-xs text-text-muted mt-4">分类由系统定义，后续版本将支持自定义</p>
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
import { ref, onMounted, computed } from 'vue'
import { BILL_CATEGORIES } from '@/types/bill'

const userId = ref<number>(1)
const isSaving = ref(false)

const categories = BILL_CATEGORIES

const savedUserId = computed(() => {
  return localStorage.getItem('userId') || '1'
})

onMounted(() => {
  const stored = localStorage.getItem('userId')
  if (stored) {
    userId.value = parseInt(stored)
  }
})

const saveUserId = async () => {
  isSaving.value = true
  try {
    localStorage.setItem('userId', String(userId.value))
    alert('用户 ID 已保存')
  } catch (e) {
    alert(`保存失败: ${(e as Error).message}`)
  } finally {
    isSaving.value = false
  }
}
</script>
