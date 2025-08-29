import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false, title: '注册' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true, title: '仪表盘', layout: true }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/Projects.vue'),
    meta: { requiresAuth: true, title: '项目列表', layout: true }
  },
  {
    path: '/projects/new',
    name: 'NewProject',
    component: () => import('@/views/NewProject.vue'),
    meta: { requiresAuth: true, title: '新建项目', layout: true }
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { requiresAuth: true, title: '项目详情', layout: true }
  },
  {
    path: '/projects/:id/edit',
    name: 'EditProject',
    component: () => import('@/views/EditProject.vue'),
    meta: { requiresAuth: true, title: '编辑项目', layout: true }
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/views/Transactions.vue'),
    meta: { requiresAuth: true, title: '财务记录', layout: true }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/views/Categories.vue'),
    meta: { requiresAuth: true, title: '分类管理', layout: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports.vue'),
    meta: { requiresAuth: true, title: '财务统计', layout: true }
  },
  {
    path: '/suppliers',
    name: 'Suppliers',
    component: () => import('@/views/Suppliers.vue'),
    meta: { requiresAuth: true, title: '供应商管理', layout: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true, title: '系统设置', layout: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true, title: '个人资料', layout: true }
  },
  
  // 监控系统路由
  {
    path: '/monitoring/login',
    name: 'MonitoringLogin',
    component: () => import('@/views/MonitoringLogin.vue'),
    meta: { requiresAuth: false, title: '监控系统登录' }
  },
  {
    path: '/monitoring/dashboard',
    name: 'MonitoringDashboard',
    component: () => import('@/views/MonitoringDashboard.vue'),
    meta: { requiresMonitoringAuth: true, title: '监控仪表盘' }
  },
  {
    path: '/monitoring/tenants',
    name: 'MonitoringTenants',
    component: () => import('@/views/MonitoringTenants.vue'),
    meta: { requiresMonitoringAuth: true, title: '租户管理' }
  },
  {
    path: '/monitoring/logs',
    name: 'MonitoringLogs',
    component: () => import('@/views/MonitoringLogs.vue'),
    meta: { requiresMonitoringAuth: true, title: '操作日志' }
  },
  {
    path: '/monitoring/health',
    name: 'MonitoringHealth',
    component: () => import('@/views/MonitoringHealth.vue'),
    meta: { requiresMonitoringAuth: true, title: '健康检查' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 获取认证状态
  const token = localStorage.getItem('token')
  const monitoringToken = localStorage.getItem('monitoring_token')
  const isAuthenticated = !!token
  const isMonitoringAuthenticated = !!monitoringToken
  
  // 根路径 / 已经在路由定义中重定向到 /login，这里不需要处理
  
  // 如果访问需要认证的页面
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      // 未认证，重定向到登录页
      next('/login')
      return
    }
  }
  
  // 如果访问需要监控系统认证的页面
  if (to.meta.requiresMonitoringAuth) {
    if (!isMonitoringAuthenticated) {
      // 未认证，重定向到监控系统登录页
      next('/monitoring/login')
      return
    }
  }
  
  // 如果已登录用户访问登录页或注册页，重定向到仪表板
  if (isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    next('/dashboard')
    return
  }
  
  // 如果已登录监控系统用户访问监控登录页，重定向到监控仪表盘
  if (isMonitoringAuthenticated && to.path === '/monitoring/login') {
    next('/monitoring/dashboard')
    return
  }
  
  // 其他情况正常通过
  next()
})

export default router
