import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例
const service = axios.create({
  // 使用相对路径，自动使用当前访问的域名
  baseURL: '',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers['Authorization'] = `Bearer ${authStore.token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果响应包含错误信息，显示错误
    if (res.error || res.detail) {
      const errorMsg = res.error || res.detail || '请求失败'
      ElMessage.error(errorMsg)
      return Promise.reject(new Error(errorMsg))
    }
    
    return res
  },
  async error => {
    const { response } = error
    
    if (response?.status === 401) {
      // Token过期，尝试刷新
      const authStore = useAuthStore()
      const refreshed = await authStore.refreshAccessToken()
      
      if (refreshed) {
        // 重新发送原请求
        const config = error.config
        config.headers['Authorization'] = `Bearer ${authStore.token}`
        return service(config)
      } else {
        // 刷新失败，跳转登录页
        authStore.logout()
        window.location.href = '/login'
      }
    } else if (response?.status === 403) {
      ElMessage.error('权限不足')
    } else if (response?.status === 404) {
      ElMessage.error('请求的资源不存在')
    } else if (response?.status >= 500) {
      ElMessage.error('服务器内部错误')
    } else {
      ElMessage.error(error.message || '网络错误')
    }
    
    return Promise.reject(error)
  }
)

export default service
