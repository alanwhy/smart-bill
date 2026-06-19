import client from './client'

export interface AdminUser {
  id: number
  username: string
  role: string
  must_change_password: boolean
  created_at: string
  updated_at: string
}

export interface ResetPasswordResult {
  user_id: number
  username: string
  temp_password: string
}

export const usersApi = {
  async list(): Promise<AdminUser[]> {
    return client.get('/users')
  },

  async create(payload: { username: string; password: string; role?: 'admin' | 'user' }): Promise<AdminUser> {
    return client.post('/users', payload)
  },

  async updateUsername(userId: number, username: string): Promise<AdminUser> {
    return client.put(`/users/${userId}/username`, { username })
  },

  async resetPassword(userId: number): Promise<ResetPasswordResult> {
    return client.post(`/users/${userId}/reset-password`)
  },
}
