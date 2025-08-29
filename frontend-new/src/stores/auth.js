import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref('')
  const refreshToken = ref('')
  const isLoading = ref(false)
  const systemName = ref('工程项目流水账')
  
  // 监控系统认证状态
  const monitoringUser = ref(null)
  const monitoringToken = ref('')

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isMonitoringAuthenticated = computed(() => !!monitoringToken.value)
  const username = computed(() => user.value?.profile?.name || user.value?.name || user.value?.username || '用户')
  const userId = computed(() => user.value?.id || '')
  const tenantId = computed(() => user.value?.tenant_id || '')
  const appTitle = computed(() => systemName.value)

  // 登录
  const login = async (credentials) => {
    try {
      isLoading.value = true
      const response = await authApi.login(credentials)
      
      if (response.access_token) {
        // 保存认证信息
        token.value = response.access_token
        refreshToken.value = response.refresh_token
        
        // 保存用户信息
        if (response.user && typeof response.user === 'object') {
          user.value = response.user
        } else {
          // 如果user不是对象，创建一个默认用户对象
          user.value = {
            id: 'unknown',
            name: '用户',
            email: credentials.email,
            username: credentials.email
          }
        }
        
        // 保存到localStorage
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('refresh_token', response.refresh_token)
        localStorage.setItem('user', JSON.stringify(user.value))
        
        return { success: true, message: '登录成功' }
      } else {
        throw new Error('登录响应格式错误')
      }
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 注册
  const register = async (userData) => {
    try {
      isLoading.value = true
      const response = await authApi.register(userData)
      return response
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 刷新token
  const refreshAccessToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('没有刷新token')
      }
      
      const response = await authApi.refreshToken(refreshToken.value)
      
      if (response.access_token) {
        token.value = response.access_token
        localStorage.setItem('token', response.access_token)
        return true
      }
      
      return false
    } catch (error) {
      console.error('刷新token失败:', error)
      // 刷新失败，清除所有认证信息
      logout()
      return false
    }
  }

  // 退出登录
  const logout = () => {
    try {
      // 清除状态
      user.value = null
      token.value = ''
      refreshToken.value = ''
      isLoading.value = false
      
      // 清除localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      
      // 清除sessionStorage
      sessionStorage.clear()
      
      // 清除所有cookie
      clearAllCookies()
      
      // 清除可能的其他存储
      if (window.indexedDB) {
        // 清除IndexedDB
        indexedDB.databases().then(databases => {
          databases.forEach(db => {
            indexedDB.deleteDatabase(db.name)
          })
        })
      }
      
      // 清除可能的localStorage键
      const keysToRemove = []
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key && (key.includes('auth') || key.includes('user') || key.includes('token'))) {
          keysToRemove.push(key)
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key))
      
      console.log('所有登录信息已清除')
      
    } catch (error) {
      console.error('清除登录信息时出错:', error)
    }
  }
  
  // 监控系统认证方法
  const setMonitoringAuth = (token, user) => {
    monitoringToken.value = token
    monitoringUser.value = user
    
    // 保存到localStorage
    localStorage.setItem('monitoring_token', token)
    localStorage.setItem('monitoring_user', JSON.stringify(user))
  }
  
  const clearMonitoringAuth = () => {
    monitoringToken.value = ''
    monitoringUser.value = null
    
    // 清除localStorage
    localStorage.removeItem('monitoring_token')
    localStorage.removeItem('monitoring_user')
  }

  // 清除所有cookie
  const clearAllCookies = () => {
    try {
      const cookies = document.cookie.split(';')
      
      cookies.forEach(cookie => {
        const eqPos = cookie.indexOf('=')
        const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim()
        
        // 清除cookie（设置过期时间为过去）
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=${window.location.hostname}`
        
        // 尝试清除可能的子域名cookie
        const hostname = window.location.hostname
        const parts = hostname.split('.')
        for (let i = 1; i < parts.length; i++) {
          const domain = parts.slice(i).join('.')
          document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=.${domain}`
        }
      })
    } catch (error) {
      console.error('清除cookie时出错:', error)
    }
  }

  // 初始化认证状态
  const initAuth = () => {
    try {
      const storedToken = localStorage.getItem('token')
      const storedRefreshToken = localStorage.getItem('refresh_token')
      const storedUser = localStorage.getItem('user')
      const storedSystemName = localStorage.getItem('systemName')
      
      if (storedToken && storedRefreshToken && storedUser) {
        token.value = storedToken
        refreshToken.value = storedRefreshToken
        
        try {
          user.value = JSON.parse(storedUser)
        } catch (e) {
          console.error('解析用户信息失败:', e)
          user.value = null
        }
        
        // 验证token是否有效
        validateToken()
      }
      
      // 加载系统名称
      if (storedSystemName) {
        systemName.value = storedSystemName
      }
      
      // 初始化监控系统认证状态
      const storedMonitoringToken = localStorage.getItem('monitoring_token')
      const storedMonitoringUser = localStorage.getItem('monitoring_user')
      
      if (storedMonitoringToken && storedMonitoringUser) {
        monitoringToken.value = storedMonitoringToken
        try {
          monitoringUser.value = JSON.parse(storedMonitoringUser)
        } catch (e) {
          console.error('解析监控系统用户信息失败:', e)
          monitoringUser.value = null
        }
      }
    } catch (error) {
      console.error('初始化认证状态失败:', error)
      logout()
    }
  }

  // 验证token有效性
  const validateToken = async () => {
    try {
      // TODO: 调用API验证token有效性
      // 如果token无效，尝试刷新
      // 如果刷新失败，自动退出登录
    } catch (error) {
      console.error('验证token失败:', error)
      logout()
    }
  }

  // 更新用户信息
  const updateUserInfo = (newUserInfo) => {
    if (newUserInfo && typeof newUserInfo === 'object') {
      // 深度合并用户信息
      const updatedUser = { ...user.value }
      
      // 处理顶层字段
      Object.keys(newUserInfo).forEach(key => {
        if (key === 'profile' && newUserInfo[key] && typeof newUserInfo[key] === 'object') {
          // 深度合并profile对象
          updatedUser.profile = { ...(updatedUser.profile || {}), ...newUserInfo.profile }
        } else {
          // 直接赋值其他字段
          updatedUser[key] = newUserInfo[key]
        }
      })
      
      user.value = updatedUser
      localStorage.setItem('user', JSON.stringify(user.value))
      
      console.log('Auth store用户信息已更新:', user.value)
    }
  }

  // 更新系统名称
  const updateSystemName = (newSystemName) => {
    if (newSystemName && typeof newSystemName === 'string') {
      systemName.value = newSystemName.trim()
      localStorage.setItem('systemName', systemName.value)
      console.log('系统名称已更新:', systemName.value)
    }
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    isLoading,
    systemName,
    monitoringUser,
    monitoringToken,
    
    // 计算属性
    isAuthenticated,
    isMonitoringAuthenticated,
    username,
    userId,
    tenantId,
    appTitle,
    
    // 方法
    login,
    register,
    refreshAccessToken,
    logout,
    initAuth,
    updateUserInfo,
    updateSystemName,
    setMonitoringAuth,
    clearMonitoringAuth
  }
})
