<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-text mb-2">设置</h1>
        <p class="text-text-muted">管理您的应用设置</p>
      </div>

      <!-- 月度周期设置 -->
      <div class="card p-6 mb-6">
        <h2 class="text-lg font-semibold text-text mb-1">月度账单周期</h2>
        <p class="text-sm text-text-muted mb-4">设置每月账单统计的起始日，支持 1 到 28 号。</p>
        <div class="flex items-center gap-3 mb-3">
          <div class="flex items-center gap-2 flex-1">
            <label class="text-sm text-text-secondary whitespace-nowrap">起始日</label>
            <input
              v-model.number="cycleInputDay"
              type="number"
              min="1"
              max="28"
              class="input w-20 text-center"
              @input="onCycleInput"
            />
            <span class="text-sm text-text-secondary">号</span>
          </div>
          <button
            @click="saveCycleSettings"
            :disabled="isSaving || !!cycleError"
            class="btn btn-primary btn-sm"
          >
            {{ isSaving ? '保存中...' : '保存' }}
          </button>
        </div>
        <p v-if="cycleError" class="text-xs text-error mb-2">{{ cycleError }}</p>
        <p class="text-xs text-text-muted">
          预览：每月 <span class="text-primary font-medium">{{ cycleInputDay }} 号</span>
          到次月 <span class="text-primary font-medium">{{ cycleEndDay }} 号</span> 为一个周期
        </p>
        <p v-if="saveSuccess" class="text-xs text-green-500 mt-2">✓ 已保存</p>
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
import { computed, onMounted, ref } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'

const categoriesStore = useCategoriesStore()
const authStore = useAuthStore()
const categories = computed(() => categoriesStore.sortedCategories)

const cycleInputDay = ref(authStore.cycleStartDay)
const cycleError = ref('')
const isSaving = ref(false)
const saveSuccess = ref(false)

// 预览：结束日 = 起始日 - 1（同月），起始日为 1 时结束日显示"月末"
const cycleEndDay = computed(() => {
  const d = cycleInputDay.value
  if (d === 1) return '月末'
  return `${d - 1}`
})

onMounted(async () => {
  categoriesStore.getOrFetch()
  await authStore.fetchCycle()
  cycleInputDay.value = authStore.cycleStartDay
})

const onCycleInput = () => {
  saveSuccess.value = false
  const d = cycleInputDay.value
  if (!d || d < 1 || d > 28) {
    cycleError.value = '起始日必须在 1 到 28 之间'
  } else {
    cycleError.value = ''
  }
}

const saveCycleSettings = async () => {
  onCycleInput()
  if (cycleError.value) return
  isSaving.value = true
  try {
    await authStore.saveCycle(cycleInputDay.value)
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch (e) {
    cycleError.value = `保存失败: ${(e as Error).message}`
  } finally {
    isSaving.value = false
  }
}
</script>
