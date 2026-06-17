import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BillFilter } from '@/types/bill'

export const useUiStore = defineStore('ui', () => {
  const filters = ref<BillFilter>({
    startDate: undefined,
    endDate: undefined,
    category: undefined,
    searchText: undefined,
  })

  const isFilterSheetOpen = ref(false)

  // 设置筛选条件
  const setFilters = (newFilters: Partial<BillFilter>) => {
    filters.value = {
      ...filters.value,
      ...newFilters,
    }
  }

  // 清除筛选条件
  const clearFilters = () => {
    filters.value = {
      startDate: undefined,
      endDate: undefined,
      category: undefined,
      searchText: undefined,
    }
  }

  // 切换筛选面板
  const toggleFilterSheet = () => {
    isFilterSheetOpen.value = !isFilterSheetOpen.value
  }

  // 打开筛选面板
  const openFilterSheet = () => {
    isFilterSheetOpen.value = true
  }

  // 关闭筛选面板
  const closeFilterSheet = () => {
    isFilterSheetOpen.value = false
  }

  return {
    filters,
    isFilterSheetOpen,
    setFilters,
    clearFilters,
    toggleFilterSheet,
    openFilterSheet,
    closeFilterSheet,
  }
})
