import client from './client'
import type { Category, CategoryTree, CreateCategoryRequest, UpdateCategoryRequest } from '@/types/bill'

export const categoryApi = {
  /** 查询全部分类（平铺列表） */
  async list(): Promise<Category[]> {
    const response = await client.get('/categories')
    return response || []
  },

  /** 查询树形分类列表（根节点含 children 嵌套） */
  async listTree(): Promise<CategoryTree[]> {
    const response = await client.get('/categories/tree')
    return response || []
  },

  /** 获取单个分类 */
  async get(categoryId: number): Promise<Category> {
    return await client.get(`/categories/${categoryId}`)
  },

  /** 新建分类 */
  async create(data: CreateCategoryRequest): Promise<Category> {
    return await client.post('/categories', data)
  },

  /** 更新分类 */
  async update(categoryId: number, data: UpdateCategoryRequest): Promise<Category> {
    return await client.put(`/categories/${categoryId}`, data)
  },

  /** 删除分类 */
  async remove(categoryId: number): Promise<void> {
    await client.delete(`/categories/${categoryId}`)
  },
}
