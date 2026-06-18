<template>
  <div class="space-y-4">
    <!-- 日期范围 -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-text">日期范围</label>
      <div class="grid grid-cols-2 gap-2">
        <input
          v-model="localFilters.startDate"
          type="date"
          class="input"
          placeholder="开始日期"
          @change="onStartDateChange"
        />
        <input
          v-model="localFilters.endDate"
          type="date"
          class="input"
          placeholder="结束日期"
          :min="localFilters.startDate || undefined"
          @change="applyFilters"
        />
      </div>
      <p v-if="dateError" class="text-xs text-error">{{ dateError }}</p>
    </div>

    <!-- 分类选择 -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-text">分类</label>
      <p v-if="categoriesStore.isLoading && categories.length === 0" class="text-xs text-text-muted">加载中...</p>
      <p v-else-if="categories.length === 0" class="text-xs text-text-muted">暂无分类</p>
      <div v-else class="grid grid-cols-4 md:grid-cols-4 lg:grid-cols-7 gap-2">
        <button
          v-for="cat in categories"
          :key="cat.id"
          @click="toggleCategory(cat.id)"
          :class="[
            'p-2 rounded-lg border-2 transition-all duration-200 flex flex-col items-center',
            localFilters.category_id === cat.id
              ? 'border-primary bg-primary/10'
              : 'border-border bg-surface hover:border-primary/50',
          ]"
        >
          <div class="text-base mb-0.5">{{ cat.icon }}</div>
          <div class="text-xs text-text-secondary">{{ cat.name }}</div>
        </button>
      </div>
    </div>

    <!-- 搜索文本 -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-text">商户名称</label>
      <input
        v-model="localFilters.searchText"
        type="text"
        placeholder="搜索商户..."
        class="input"
        @input="onSearchInput"
      />
    </div>

    <!-- 操作按钮 -->
    <div class="flex gap-2 pt-4 border-t border-border">
      <button
        @click="handleClear"
        class="btn btn-secondary flex-1"
      >
        重置筛选
      </button>
      <button
        v-if="isModal"
        @click="emit('close')"
        class="btn btn-ghost"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useCategoriesStore } from '@/stores/categories'

defineProps<{
  isModal?: boolean
}>()

const emit = defineEmits<{
  apply: []
  close: []
}>()

const uiStore = useUiStore()
const categoriesStore = useCategoriesStore()

const categories = computed(() => categoriesStore.sortedCategories)
const dateError = ref('')

const localFilters = reactive({
  startDate: uiStore.filters.startDate || '',
  endDate: uiStore.filters.endDate || '',
  category_id: uiStore.filters.category_id as number | undefined,
  searchText: uiStore.filters.searchText || '',
})

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  categoriesStore.getOrFetch()
})

// 当外部（如快捷按钮）更新 uiStore.filters 时，同步到本地 localFilters
watch(
  () => uiStore.filters,
  (newFilters) => {
    localFilters.startDate = newFilters.startDate || ''
    localFilters.endDate = newFilters.endDate || ''
    localFilters.category_id = newFilters.category_id
    localFilters.searchText = newFilters.searchText || ''
  },
  { deep: true }
)

const applyFilters = () => {
  dateError.value = ''
  if (localFilters.startDate && localFilters.endDate && localFilters.startDate > localFilters.endDate) {
    dateError.value = '结束日期不能早于开始日期'
    return
  }
  uiStore.setFilters({
    startDate: localFilters.startDate || undefined,
    endDate: localFilters.endDate || undefined,
    category_id: localFilters.category_id,
    searchText: localFilters.searchText || undefined,
  })
  emit('apply')
}

const onStartDateChange = () => {
  if (localFilters.endDate && localFilters.startDate > localFilters.endDate) {
    localFilters.endDate = localFilters.startDate
  }
  applyFilters()
}

const toggleCategory = (id: number) => {
  localFilters.category_id = localFilters.category_id === id ? undefined : id
  applyFilters()
}

const onSearchInput = () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    applyFilters()
  }, 400)
}

const handleClear = () => {
  localFilters.startDate = ''
  localFilters.endDate = ''
  localFilters.category_id = undefined
  localFilters.searchText = ''
  dateError.value = ''
  uiStore.clearFilters()
  emit('apply')
}
</script>
