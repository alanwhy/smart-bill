<template>
  <!-- ═══════════════════════════════════════════════════
       桌面端：水平单行筛选（isModal=false，PC only）
  ════════════════════════════════════════════════════ -->
  <div v-if="!isModal" class="flex items-center gap-2 flex-wrap">
    <!-- 日期范围选择器 -->
    <DateRangePicker
      :start-date="localFilters.startDate || undefined"
      :end-date="localFilters.endDate || undefined"
      placeholder="选择日期范围"
      @change="onDateRangeChange"
    />
    <p v-if="dateError" class="text-xs text-error w-full -mt-1">{{ dateError }}</p>

    <!-- 分类多选（桌面端专用 CategoryTreeSelect） -->
    <CategoryTreeSelect
      :model-value="localFilters.category_ids"
      placeholder="全部分类"
      @update:model-value="onCategoryIdsChange"
    />

    <!-- 商户搜索 -->
    <div class="relative flex items-center">
      <svg class="absolute left-2.5 w-3.5 h-3.5 text-text-muted pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        v-model="localFilters.searchText"
        type="text"
        placeholder="搜索商户..."
        class="h-8 pl-8 pr-3 text-sm w-36 rounded-lg border border-border bg-surface text-text focus:outline-none focus:ring-1 focus:ring-primary/60 focus:border-primary/60 transition-colors placeholder:text-text-muted"
        @input="onSearchInput"
      />
    </div>

    <!-- 重置 -->
    <button @click="handleClear" class="btn btn-ghost btn-sm h-8 px-2.5 text-xs text-text-muted hover:text-text">
      重置
    </button>
  </div>

  <!-- ═══════════════════════════════════════════════════
       移动端：竖向筛选（isModal=true，完全独立，单选分类）
  ════════════════════════════════════════════════════ -->
  <div v-if="isModal" class="space-y-4">
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

    <!-- 分类选择（移动端保持 CategoryDrillDown 单选，不变） -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-text">分类</label>
      <p v-if="categoriesStore.isLoading && allCategories.length === 0" class="text-xs text-text-muted">加载中...</p>
      <p v-else-if="allCategories.length === 0" class="text-xs text-text-muted">暂无分类</p>
      <div v-else>
        <CategoryDrillDown
          :model-value="mobileCategoryId"
          size="sm"
          :show-all="true"
          @select="onMobileCategorySelect"
          @clear="clearMobileCategory"
        />
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
      <button @click="handleClear" class="btn btn-secondary flex-1">
        重置筛选
      </button>
      <button @click="emit('close')" class="btn btn-ghost">
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
import CategoryDrillDown from '@/components/categories/CategoryDrillDown.vue'
import CategoryTreeSelect from '@/components/categories/CategoryTreeSelect.vue'
import DateRangePicker from '@/components/common/DateRangePicker.vue'

const props = defineProps<{
  isModal?: boolean
  /** 外部传入的 filters（用于统计页等脱离 uiStore 的场景），不传则默认绑 uiStore */
  externalFilters?: {
    startDate?: string
    endDate?: string
    category_ids?: number[]
    searchText?: string
  }
}>()

const emit = defineEmits<{
  apply: []
  close: []
  'update:externalFilters': [value: typeof props.externalFilters]
}>()

const uiStore = useUiStore()
const categoriesStore = useCategoriesStore()

const allCategories = computed(() => categoriesStore.sortedCategories)
const dateError = ref('')

// 是否使用外部 filters（统计页独立状态，不影响 uiStore）
const useExternal = computed(() => !!props.externalFilters)

const sourceFilters = computed(() => useExternal.value ? props.externalFilters! : uiStore.filters)

const localFilters = reactive({
  startDate: sourceFilters.value.startDate || '',
  endDate: sourceFilters.value.endDate || '',
  category_ids: (sourceFilters.value.category_ids || []) as number[],
  searchText: sourceFilters.value.searchText || '',
})

// 移动端：从 category_ids 取第一个作为单选值
const mobileCategoryId = computed(() =>
  localFilters.category_ids.length ? localFilters.category_ids[0] : undefined
)

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  categoriesStore.getOrFetch()
})

// 外部 filters 变化时同步（含 uiStore 快捷按钮切换）
watch(
  sourceFilters,
  (newFilters) => {
    localFilters.startDate = newFilters.startDate || ''
    localFilters.endDate = newFilters.endDate || ''
    localFilters.category_ids = newFilters.category_ids || []
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
  const payload = {
    startDate: localFilters.startDate || undefined,
    endDate: localFilters.endDate || undefined,
    category_ids: localFilters.category_ids.length ? localFilters.category_ids : undefined,
    searchText: localFilters.searchText || undefined,
  }
  if (useExternal.value) {
    emit('update:externalFilters', payload)
  } else {
    uiStore.setFilters(payload)
  }
  emit('apply')
}

const onStartDateChange = () => {
  if (localFilters.endDate && localFilters.startDate > localFilters.endDate) {
    localFilters.endDate = localFilters.startDate
  }
  applyFilters()
}

// DateRangePicker 回调（PC 端）
const onDateRangeChange = (start: string | undefined, end: string | undefined) => {
  localFilters.startDate = start || ''
  localFilters.endDate = end || ''
  dateError.value = ''
  applyFilters()
}

// 桌面端多选分类
const onCategoryIdsChange = (ids: number[]) => {
  localFilters.category_ids = ids
  applyFilters()
}

// 移动端单选分类
const onMobileCategorySelect = (id: number) => {
  localFilters.category_ids = [id]
  applyFilters()
}

const clearMobileCategory = () => {
  localFilters.category_ids = []
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
  localFilters.category_ids = []
  localFilters.searchText = ''
  dateError.value = ''
  if (useExternal.value) {
    emit('update:externalFilters', {})
  } else {
    uiStore.clearFilters()
  }
  emit('apply')
}
</script>

<style scoped>
.expand-sub-enter-active,
.expand-sub-leave-active {
  transition: max-height 0.2s ease, opacity 0.15s ease;
  max-height: 600px;
  overflow: hidden;
}
.expand-sub-enter-from,
.expand-sub-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
