import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { billApi } from '@/api/bills'
import type { BillRecord, BillFilter, CreateBillRequest } from '@/types/bill'

export const useBillsStore = defineStore('bills', () => {
  const bills = ref<BillRecord[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 轮询状态
  let _pollingTimer: ReturnType<typeof setTimeout> | null = null
  let _pollingDeadline = 0
  let _realCountBeforeUpload = 0
  const POLL_INTERVAL = 2000   // 2s 轮询一次
  const POLL_TIMEOUT  = 30000  // 30s 超时兜底

  // 获取账单列表
  const fetchBills = async (userId: number, filters?: BillFilter) => {
    isLoading.value = true
    error.value = null

    try {
      const params = {
        startDate: filters?.startDate,
        endDate: filters?.endDate,
        category_id: filters?.category_id,
        searchText: filters?.searchText,
      }

      const freshBills = await billApi.listBills(userId, params)
      // 保留 placeholder 条目，将真实数据放前面
      const placeholders = bills.value.filter((b) => b.isPlaceholder)
      bills.value = [...placeholders, ...freshBills]
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  // 插入 N 个 placeholder 条目到列表头部
  const addPlaceholders = (count: number) => {
    const now = Date.now()
    const newPlaceholders: BillRecord[] = Array.from({ length: count }, (_, i) => ({
      id: -(now + i),
      user_id: 0,
      value: 0,
      merchant_name: '',
      transaction_date: '',
      category_id: 0,
      category: { id: 0, name: '', icon: '', color: '' },
      created_at: '',
      updated_at: '',
      isPlaceholder: true,
    }))
    bills.value = [...newPlaceholders, ...bills.value]
  }

  // 移除所有 placeholder 条目
  const removePlaceholders = () => {
    bills.value = bills.value.filter((b) => !b.isPlaceholder)
  }

  // 开始轮询
  // expectedCount: 本次上传的文件数，轮询直到新增条目数 >= expectedCount 才停止
  const startPolling = (userId: number, expectedCount: number, filters?: BillFilter) => {
    stopPolling()
    _realCountBeforeUpload = bills.value.filter((b) => !b.isPlaceholder).length
    _pollingDeadline = Date.now() + POLL_TIMEOUT

    const poll = async () => {
      if (Date.now() > _pollingDeadline) {
        // 超时，移除 placeholder 并停止
        removePlaceholders()
        return
      }

      const params = {
        startDate: filters?.startDate,
        endDate: filters?.endDate,
        category_id: filters?.category_id,
        searchText: filters?.searchText,
      }

      try {
        const freshBills = await billApi.listBills(userId, params)
        const newCount = freshBills.length - _realCountBeforeUpload
        // 更新列表（保留 placeholder，让用户看到已有的新数据）
        if (newCount > 0) {
          const placeholders = bills.value.filter((b) => b.isPlaceholder)
          bills.value = [...placeholders, ...freshBills]
        }
        if (newCount >= expectedCount) {
          // 所有图片都识别完毕，停止轮询并移除剩余 placeholder
          removePlaceholders()
          return
        }
      } catch (_) {
        // 网络错误时继续轮询，直到超时
      }

      _pollingTimer = setTimeout(poll, POLL_INTERVAL)
    }

    _pollingTimer = setTimeout(poll, POLL_INTERVAL)
  }

  // 停止轮询
  const stopPolling = () => {
    if (_pollingTimer !== null) {
      clearTimeout(_pollingTimer)
      _pollingTimer = null
    }
  }

  // 上传账单（提交后立即返回，由调用方负责插入 placeholder 和启动轮询）
  const uploadBills = async (userId: number, files: File[]) => {
    error.value = null
    try {
      const newBills = await billApi.uploadBills(files, userId)
      return newBills
    } catch (e) {
      error.value = (e as Error).message
      throw e
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

  // 手动创建账单
  const createBill = async (data: CreateBillRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const newBill = await billApi.createBill(data)
      bills.value = [newBill, ...bills.value]
      return newBill
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // 删除账单
  const deleteBill = async (billId: number) => {    isLoading.value = true
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
      if (bill.isPlaceholder) return
      if (!grouped[bill.category_id]) {
        grouped[bill.category_id] = []
      }
      grouped[bill.category_id].push(bill)
    })
    return grouped
  })

  // 总支出（仅汇总 value < 0 的账单，取绝对值；展示为正数）
  const totalExpense = computed(() => {
    return bills.value
      .filter((b) => !b.isPlaceholder && b.value < 0)
      .reduce((sum, bill) => sum + Math.abs(bill.value), 0)
  })

  // 总收入（仅汇总 value > 0 的账单）
  const totalIncome = computed(() => {
    return bills.value
      .filter((b) => !b.isPlaceholder && b.value > 0)
      .reduce((sum, bill) => sum + bill.value, 0)
  })

  // 分类统计（按 category_id，金额取绝对值方便饼图展示）
  const expenseByCategory = computed(() => {
    const result: Record<number, number> = {}
    bills.value.forEach((bill) => {
      if (bill.isPlaceholder) return
      if (bill.value >= 0) return
      result[bill.category_id] = (result[bill.category_id] || 0) + Math.abs(bill.value)
    })
    return result
  })

  return {
    bills,
    isLoading,
    error,
    fetchBills,
    uploadBills,
    createBill,
    updateBill,
    deleteBill,
    addPlaceholders,
    removePlaceholders,
    startPolling,
    stopPolling,
    billsByCategory,
    totalExpense,
    totalIncome,
    expenseByCategory,
  }
})
