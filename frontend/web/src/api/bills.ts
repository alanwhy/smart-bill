import client from './client'
import type { BillItem, BillRecord, CreateBillRequest, UpdateBillRequest } from '@/types/bill'

export interface BatchCreateBillItem {
  value: number
  merchant_name: string
  transaction_date: string
  category_id: number
  description?: string
}

export interface BatchCreateBillRequest {
  user_id: number
  items: BatchCreateBillItem[]
}

export const billApi = {
  /**
   * 上传图片识别账单
   */
  async uploadBills(files: File[], userId: number): Promise<BillItem[]> {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    formData.append('user_id', String(userId))

    const response = await client.post<any, any>('/bills/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response
  },

  /**
   * 查询账单列表
   */
  async listBills(userId: number, params?: {
    startDate?: string
    endDate?: string
    category_id?: number
    searchText?: string
  }): Promise<BillRecord[]> {
    const response = await client.get('/bills', {
      params: {
        user_id: userId,
        start_date: params?.startDate,
        end_date: params?.endDate,
        category_id: params?.category_id,
        merchant_name: params?.searchText || undefined,
      },
    })

    return response || []
  },

  /**
   * 获取单个账单
   */
  async getBill(billId: number): Promise<BillRecord> {
    const response = await client.get(`/bills/${billId}`)
    return response
  },

  /**
   * 手动创建账单
   */
  async createBill(data: CreateBillRequest): Promise<BillRecord> {
    const response = await client.post('/bills', data)
    return response
  },

  /**
   * 修改账单
   */
  async updateBill(billId: number, data: UpdateBillRequest): Promise<BillRecord> {
    const response = await client.put(`/bills/${billId}`, data)
    return response
  },

  /**
   * 删除账单
   */
  async deleteBill(billId: number): Promise<void> {
    await client.delete(`/bills/${billId}`)
  },

  /**
   * 批量导入账单
   */
  async batchCreateBills(data: BatchCreateBillRequest): Promise<{ created_count: number }> {
    const response = await client.post('/bills/batch', data)
    return response
  },
}
