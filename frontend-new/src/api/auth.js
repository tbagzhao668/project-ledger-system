import request from '@/utils/request'

export const authApi = {
  // 用户登录
  login: (data) => {
    return request({
      url: '/api/v1/login',
      method: 'post',
      data
    })
  },

  // 刷新token
  refreshToken: (refreshToken) => {
    return request({
      url: '/api/v1/auth/refresh',
      method: 'post',
      data: { refresh_token: refreshToken }
    })
  },

  // 用户注册
  register: (data) => {
    return request({
      url: '/api/v1/auth/register',
      method: 'post',
      data
    })
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return request({
      url: '/api/v1/auth/me',
      method: 'get'
    })
  }
}
