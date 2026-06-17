import axios, { AxiosInstance, AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types/bill'

const client: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应拦截器
client.interceptors.response.use(
  (response: AxiosResponse) => {
    const data = response.data as ApiResponse

    // 如果 code 不为 0，视为错误
    if (data.code !== 0) {
      return Promise.reject(new Error(data.msg || '请求失败'))
    }

    return data.data
  },
  (error) => {
    const message = error.response?.data?.msg || error.message || '网络错误，请重试'
    return Promise.reject(new Error(message))
  },
)

export default client
