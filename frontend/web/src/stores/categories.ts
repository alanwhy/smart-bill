import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { categoryApi } from '@/api/categories'
import type { Category, CategoryBrief, CreateCategoryRequest, UpdateCategoryRequest } from '@/types/bill'

const FALLBACK_BRIEF: CategoryBrief = {
  id: 0,
  name: '未知分类',
  icon: '📦',
  color: '#6B7280',
}

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const isLoaded = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const byId = computed(() => {
    const map = new Map<number, Category>()
    categories.value.forEach((c) => map.set(c.id, c))
    return map
  })

  const sortedCategories = computed(() => {
    return [...categories.value].sort((a, b) => {
      if (a.sort_order !== b.sort_order) return a.sort_order - b.sort_order
      return a.id - b.id
    })
  })

  const fetchAll = async () => {
    isLoading.value = true
    error.value = null
    try {
      categories.value = await categoryApi.list()
      isLoaded.value = true
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  const getOrFetch = async () => {
    if (!isLoaded.value && !isLoading.value) {
      await fetchAll()
    }
  }

  const briefOf = (categoryId: number): CategoryBrief => {
    const found = byId.value.get(categoryId)
    if (found) {
      return { id: found.id, name: found.name, icon: found.icon, color: found.color }
    }
    return FALLBACK_BRIEF
  }

  const createCategory = async (data: CreateCategoryRequest): Promise<Category> => {
    isLoading.value = true
    error.value = null
    try {
      const created = await categoryApi.create(data)
      categories.value.push(created)
      return created
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const updateCategory = async (categoryId: number, data: UpdateCategoryRequest): Promise<Category> => {
    isLoading.value = true
    error.value = null
    try {
      const updated = await categoryApi.update(categoryId, data)
      const index = categories.value.findIndex((c) => c.id === categoryId)
      if (index !== -1) categories.value[index] = updated
      return updated
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const removeCategory = async (categoryId: number): Promise<void> => {
    isLoading.value = true
    error.value = null
    try {
      await categoryApi.remove(categoryId)
      categories.value = categories.value.filter((c) => c.id !== categoryId)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return {
    categories,
    sortedCategories,
    isLoaded,
    isLoading,
    error,
    byId,
    briefOf,
    fetchAll,
    getOrFetch,
    createCategory,
    updateCategory,
    removeCategory,
  }
})
