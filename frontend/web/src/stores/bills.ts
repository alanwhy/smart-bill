import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { billApi } from '@/api/bills'
import type { BillRecord, BillFilter } from '@/types/bill'

export const useBillsStore = defineStore('bills', () => {
  const bills = ref<BillRecord[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 获取账单列表
  const fetchBills = async (userId: number, filters?: BillFilter) => {
    isLoading.value = true
    error.value = null

    try {
      const params = {
        startDate: filters?.startDate,
        endDate: filters?.endDate,
        category_id: filters?.category_id,
      }

      bills.value = await billApi.listBills(userId, params)
    } catch (e) {
      error.value = (e as Error).message
      bills.value = []
    } finally {
      isLoading.value = false
    }
  }

  // 上传账单
  const uploadBills = async (userId: number, files: File[]) => {
    isLoading.value = true
    error.value = null

    try {
      const newBills = await billApi.uploadBills(files, userId)
      // 上传后重新获取列表
      await fetchBills(userId)
      return newBills
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // 更新账单
  const updateBill = async (billId: number, data: any) => {
    isLoading.value = true
    error.value = null

    try {
      const updated = await billApi.updateBill(billId, data)
      const index = bills.value.findIndex((b) => b.id === billId)
      if (index !== -1) {
        bills.value[index] = updated
      }
      return updated
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // 删除账单
  const deleteBill = async (billId: number) => {
    isLoading.value = true
    error.value = null

    try {
      await billApi.deleteBill(billId)
      bills.value = bills.value.filter((b) => b.id !== billId)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // 按分类分组（按 category_id）
  const billsByCategory = computed(() => {
    const grouped: Record<number, BillRecord[]> = {}
    bills.value.forEach((bill) => {
      if (!grouped[bill.category_id]) {
        grouped[bill.category_id] = []
      }
      grouped[bill.category_id].push(bill)
    })
    return grouped
  })

  // 总消费
  const totalExpense = computed(() => {
    return bills.value.reduce((sum, bill) => sum + bill.value, 0)
  })

  // 分类统计（按 category_id）
  const expenseByCategory = computed(() => {
    const result: Record<number, number> = {}
    bills.value.forEach((bill) => {
      result[bill.category_id] = (result[bill.category_id] || 0) + bill.value
    })
    return result
  })

  return {
    bills,
    isLoading,
    error,
    fetchBills,
    uploadBills,
    updateBill,
    deleteBill,
    billsByCategory,
    totalExpense,
    expenseByCategory,
  }
})
