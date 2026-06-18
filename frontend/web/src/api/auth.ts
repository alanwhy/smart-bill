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

export interface UserCycle {
  cycle_start_day: number
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

  async getCycle(): Promise<UserCycle> {
    return client.get('/auth/cycle')
  },

  async updateCycle(cycleStartDay: number): Promise<UserCycle> {
    return client.put('/auth/cycle', { cycle_start_day: cycleStartDay })
  },
}
