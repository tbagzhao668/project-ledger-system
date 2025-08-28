<template>
  <div class="main-layout">
    <!-- 移动端遮罩层 -->
    <div 
      v-if="isMobile && !sidebarCollapsed" 
      class="sidebar-overlay"
      @click="closeSidebar"
    ></div>
    
    <!-- 侧边导航 -->
    <div class="sidebar" :class="{ 
      'sidebar-collapsed': sidebarCollapsed,
      'sidebar-mobile': isMobile,
      'sidebar-show': isMobile && !sidebarCollapsed
    }">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon class="logo-icon"><OfficeBuilding /></el-icon>
          <span v-show="!sidebarCollapsed" class="logo-text">{{ authStore.appTitle }}</span>
        </div>
        <el-button
          v-if="!isMobile"
          type="text"
          class="collapse-btn"
          @click="toggleSidebar"
        >
          <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </el-button>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="sidebarCollapsed"
        background-color="#001529"
        text-color="#ffffff"
        active-text-color="#ffffff"
        router
      >
        <!-- 仪表盘 -->
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <!-- 项目管理 -->
        <el-sub-menu index="projects">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>项目管理</span>
          </template>
          <el-menu-item index="/projects">项目列表</el-menu-item>
          <el-menu-item index="/projects/new">新建项目</el-menu-item>
        </el-sub-menu>
        
        <!-- 财务管理 -->
        <el-sub-menu index="finance">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>财务管理</span>
          </template>
          <el-menu-item index="/transactions">财务记录</el-menu-item>
          <el-menu-item index="/categories">分类管理</el-menu-item>
          <el-menu-item index="/reports">财务统计</el-menu-item>
        </el-sub-menu>
        
        <!-- 供应商管理 -->
        <el-menu-item index="/suppliers">
          <el-icon><List /></el-icon>
          <template #title>供应商管理</template>
        </el-menu-item>
        
        <!-- 系统设置 -->
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-content" :class="{ 'main-content-expanded': sidebarCollapsed }">
      <!-- 顶部导航 -->
      <div class="top-nav">
        <div class="top-nav-left">
          <!-- 移动端菜单按钮 -->
          <el-button
            v-if="isMobile"
            type="text"
            class="mobile-menu-btn"
            @click="toggleSidebar"
          >
            <el-icon><Menu /></el-icon>
          </el-button>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path">
              {{ item.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="top-nav-right">
          <!-- 用户菜单 -->
          <el-dropdown @command="handleUserCommand" trigger="click">
            <div class="user-info">
              <el-avatar :size="32" :src="userAvatar">
                {{ username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>

                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 页面内容 -->
      <div class="page-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'
import {
  OfficeBuilding,
  House,
  Document,
  Wallet,
  List,
  User,
  Setting,
  SwitchButton,
  ArrowDown,
  Fold,
  Expand,
  Menu
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式状态
const sidebarCollapsed = ref(false)
const isMobile = ref(false)

// 计算属性
const username = computed(() => authStore.username || '用户')
const userAvatar = computed(() => authStore.user?.avatar || '')

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑导航
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    name: item.meta.title,
    path: item.path
  }))
})

// 检查设备类型
const checkDevice = () => {
  isMobile.value = window.innerWidth <= 768
  if (isMobile.value) {
    sidebarCollapsed.value = true
  }
}

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 关闭侧边栏（移动端）
const closeSidebar = () => {
  if (isMobile.value) {
    sidebarCollapsed.value = true
  }
}

// 处理用户命令
const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break

    case 'logout':
      await handleLogout()
      break
  }
}

// 处理退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 清除认证状态
    authStore.logout()
    
    // 跳转到登录页
    router.push('/login')
    
  } catch (error) {
    // 用户取消
  }
}

// 监听窗口大小变化
const handleResize = () => {
  checkDevice()
}

// 监听路由变化，自动关闭侧边栏（移动端）
watch(route, () => {
  if (isMobile.value) {
    sidebarCollapsed.value = true
  }
})

// 生命周期
onMounted(() => {
  checkDevice()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边导航 */
.sidebar {
  width: 240px;
  background-color: #001529;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  z-index: 1000;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

.sidebar-collapsed {
  width: 64px;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background-color: #002140;
  border-bottom: 1px solid #1890ff;
}

.logo {
  display: flex;
  align-items: center;
  color: #fff;
}

.logo-icon {
  font-size: 24px;
  margin-right: 12px;
  color: #409eff;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.collapse-btn {
  color: #bfcbd9;
  padding: 8px;
}

.collapse-btn:hover {
  color: #fff;
}

.sidebar-menu {
  flex: 1;
  border: none;
}

.sidebar-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #1890ff;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #1890ff;
  color: #ffffff !important;
}

.sidebar-menu .el-sub-menu.is-active .el-sub-menu__title {
  color: #1890ff !important;
}

/* 确保所有菜单项文字都清晰可见 */
.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  color: #ffffff !important;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  color: #ffffff !important;
}

.sidebar-menu .el-menu-item.is-active {
  color: #ffffff !important;
}

/* 子菜单项样式 */
.sidebar-menu .el-menu-item {
  color: #ffffff !important;
}

.sidebar-menu .el-menu-item:hover {
  color: #ffffff !important;
}

.sidebar-menu .el-sub-menu__title {
  height: 50px;
  line-height: 50px;
}

.sidebar-menu .el-sub-menu__title:hover {
  background-color: #1890ff;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s;
}

.main-content-expanded {
  margin-left: 0;
}

/* 顶部导航 */
.top-nav {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.top-nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mobile-menu-btn {
  color: #666;
  padding: 8px;
  margin-right: 8px;
}

.mobile-menu-btn:hover {
  color: #409eff;
}

.top-nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-badge {
  margin-right: 8px;
}

.nav-btn {
  color: #666;
  padding: 8px;
}

.nav-btn:hover {
  color: #409eff;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  color: #333;
  font-size: 14px;
}

/* 页面内容 */
.page-content {
  flex: 1;
  padding: 24px;
  background-color: #f0f2f5;
  overflow-y: auto;
}

/* 移动端遮罩层 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sidebar {
    width: 200px;
  }
  
  .sidebar-collapsed {
    width: 64px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 1000;
  }
  
  .sidebar-mobile.sidebar-show {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
    width: 100%;
  }
  
  .top-nav {
    padding: 0 16px;
    height: 56px;
  }
  
  .page-content {
    padding: 16px;
  }
  
  .username {
    display: none;
  }
  
  .top-nav-right {
    gap: 8px;
  }
  
  .breadcrumb {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .top-nav {
    padding: 0 12px;
    height: 52px;
  }
  
  .page-content {
    padding: 12px;
  }
  
  .sidebar-header {
    padding: 0 12px;
    height: 56px;
  }
  
  .logo-text {
    font-size: 14px;
  }
  
  .sidebar-menu .el-menu-item,
  .sidebar-menu .el-sub-menu__title {
    height: 44px;
    line-height: 44px;
    font-size: 14px;
  }
}

/* iPhone 安全区域适配 */
@supports (padding: max(0px)) {
  .main-layout {
    padding-top: max(0px, env(safe-area-inset-top));
    padding-bottom: max(0px, env(safe-area-inset-bottom));
  }
  
  .sidebar {
    padding-top: max(0px, env(safe-area-inset-top));
    padding-bottom: max(0px, env(safe-area-inset-bottom));
  }
  
  .top-nav {
    padding-top: max(8px, env(safe-area-inset-top));
    padding-bottom: max(8px, env(safe-area-inset-bottom));
  }
}

/* 平板设备优化 */
@media (min-width: 769px) and (max-width: 1024px) {
  .sidebar {
    width: 200px;
  }
  
  .sidebar-collapsed {
    width: 64px;
  }
  
  .page-content {
    padding: 20px;
  }
}

/* 大屏幕优化 */
@media (min-width: 1440px) {
  .sidebar {
    width: 260px;
  }
  
  .page-content {
    padding: 32px;
  }
}

/* 横屏模式优化 */
@media (orientation: landscape) and (max-height: 600px) {
  .sidebar-header {
    height: 50px;
  }
  
  .top-nav {
    height: 50px;
  }
  
  .sidebar-menu .el-menu-item,
  .sidebar-menu .el-sub-menu__title {
    height: 40px;
    line-height: 40px;
  }
}

/* 高分辨率屏幕优化 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .sidebar {
    box-shadow: 0 0 1px rgba(0, 0, 0, 0.1);
  }
}
</style>
