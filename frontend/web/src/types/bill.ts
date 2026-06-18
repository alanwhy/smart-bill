export interface CategoryBrief {
  id: number
  name: string
  icon: string
  color: string
}

export interface Category extends CategoryBrief {
  sort_order: number
  created_at: string
  updated_at: string
}

export interface CreateCategoryRequest {
  name: string
  icon?: string
  color?: string
  sort_order?: number
}

export interface UpdateCategoryRequest {
  name?: string
  icon?: string
  color?: string
  sort_order?: number
}

export interface BillItem {
  value: number
  name: string
  date: string // ISO 8601 format
  category_id: number
  category: CategoryBrief
}

export interface BillRecord {
  id: number
  user_id: number
  value: number
  merchant_name: string
  transaction_date: string
  category_id: number
  category: CategoryBrief
  image_path?: string
  description?: string
  created_at: string
  updated_at: string
  isPlaceholder?: boolean
}

export interface UpdateBillRequest {
  value?: number
  merchant_name?: string
  transaction_date?: string
  category_id?: number
  description?: string
}

export interface CreateBillRequest {
  user_id: number
  value: number
  merchant_name: string
  transaction_date: string
  category_id: number
  description?: string
}

export interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}

export interface BillFilter {
  startDate?: string
  endDate?: string
  category_id?: number
  searchText?: string
}
