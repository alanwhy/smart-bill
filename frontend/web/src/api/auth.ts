import client from './client'

export interface LoginResponse {
  token: string
  user_id: number
  username: string
}

export interface UserInfo {
  user_id: number
  username: string
}

export const authApi = {
  async login(username: string, password: string): Promise<LoginResponse> {
    return client.post('/auth/login', { username, password })
  },

  async getMe(): Promise<UserInfo> {
    return client.get('/auth/me')
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    return client.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  },
}
