import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { billApi } from '@/api/bills'
import { useCategoriesStore } from '@/stores/categories'
import type { BillRecord } from '@/types/bill'

export interface StatsFilter {
  startDate?: string
  endDate?: string
  category_ids?: number[]
  searchText?: string
}

export interface CategoryStat {
  id: number
  name: string
  color: string
  icon: string
  expense: number
  income: number
}

export interface DayTrend {
  date: string
  expense: number
  income: number
}

export interface MerchantRank {
  name: string
  value: number
}

export const useStatsStore = defineStore('stats', () => {
  const bills = ref<BillRecord[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const fetchBills = async (userId: number, filters?: StatsFilter) => {
    isLoading.value = true
    error.value = null
    try {
      const params = {
        startDate: filters?.startDate,
        endDate: filters?.endDate,
        category_ids: filters?.category_ids,
        searchText: filters?.searchText,
      }
      bills.value = await billApi.listBills(userId, params)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  // 总支出（绝对值）
  const totalExpense = computed(() =>
    bills.value
      .filter((b) => !b.isPlaceholder && b.value < 0)
      .reduce((s, b) => s + Math.abs(b.value), 0)
  )

  // 总收入
  const totalIncome = computed(() =>
    bills.value
      .filter((b) => !b.isPlaceholder && b.value > 0)
      .reduce((s, b) => s + b.value, 0)
  )

  // 按一级分类聚合收支
  const statsByRootCategory = computed((): CategoryStat[] => {
    const categoriesStore = useCategoriesStore()
    const map = new Map<number, CategoryStat>()

    bills.value.forEach((bill) => {
      if (bill.isPlaceholder) return
      // 找一级分类：如果 category.parent_id 为 null/undefined，则自身就是一级
      let rootId = bill.category_id
      let rootCat = bill.category

      if (rootCat.parent_id) {
        // 向上找根节点
        let current = categoriesStore.byId.get(rootCat.parent_id)
        while (current && current.parent_id) {
          current = categoriesStore.byId.get(current.parent_id)
        }
        if (current) {
          rootId = current.id
          rootCat = current
        }
      }

      if (!map.has(rootId)) {
        map.set(rootId, {
          id: rootId,
          name: rootCat.name,
          color: rootCat.color,
          icon: rootCat.icon,
          expense: 0,
          income: 0,
        })
      }
      const stat = map.get(rootId)!
      if (bill.value < 0) {
        stat.expense += Math.abs(bill.value)
      } else {
        stat.income += bill.value
      }
    })

    return Array.from(map.values()).sort((a, b) => b.expense - a.expense)
  })

  // 按日期聚合趋势（升序）
  const trendByDay = computed((): DayTrend[] => {
    const map = new Map<string, DayTrend>()

    bills.value.forEach((bill) => {
      if (bill.isPlaceholder) return
      // transaction_date 可能带时间，截取 YYYY-MM-DD
      const date = bill.transaction_date.substring(0, 10)
      if (!map.has(date)) {
        map.set(date, { date, expense: 0, income: 0 })
      }
      const day = map.get(date)!
      if (bill.value < 0) {
        day.expense += Math.abs(bill.value)
      } else {
        day.income += bill.value
      }
    })

    return Array.from(map.values()).sort((a, b) => a.date.localeCompare(b.date))
  })

  // 商户支出 TOP 10（降序）
  const topMerchants = computed((): MerchantRank[] => {
    const map = new Map<string, number>()

    bills.value.forEach((bill) => {
      if (bill.isPlaceholder || bill.value >= 0) return
      const name = bill.merchant_name
      map.set(name, (map.get(name) || 0) + Math.abs(bill.value))
    })

    return Array.from(map.entries())
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
  })

  return {
    bills,
    isLoading,
    error,
    fetchBills,
    totalExpense,
    totalIncome,
    statsByRootCategory,
    trendByDay,
    topMerchants,
  }
})
