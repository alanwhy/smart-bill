export interface BillItem {
  value: number
  name: string
  date: string // ISO 8601 format
  category: string
}

export interface BillRecord extends BillItem {
  id: number
  user_id: number
  merchant_name: string
  transaction_date: string
  image_path?: string
  created_at: string
  updated_at: string
}

export interface UpdateBillRequest {
  value?: number
  merchant_name?: string
  transaction_date?: string
  category?: string
}

export interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}

export const BILL_CATEGORIES = [
  { value: '餐饮', label: '餐饮', icon: '🍽️' },
  { value: '交通', label: '交通', icon: '🚗' },
  { value: '购物', label: '购物', icon: '🛍️' },
  { value: '娱乐', label: '娱乐', icon: '🎬' },
  { value: '医疗', label: '医疗', icon: '🏥' },
  { value: '住房', label: '住房', icon: '🏠' },
  { value: '其他', label: '其他', icon: '📦' },
] as const

export type BillCategory = typeof BILL_CATEGORIES[number]['value']

export interface BillFilter {
  startDate?: string
  endDate?: string
  category?: string
  searchText?: string
}
