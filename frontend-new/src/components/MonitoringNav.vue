<template>
  <nav class="monitoring-nav">
    <div class="nav-container">
      <div class="nav-brand">
        <h2>系统监控后台</h2>
      </div>
      
      <div class="nav-menu">
        <router-link 
          to="/monitoring/dashboard" 
          class="nav-item"
          :class="{ active: $route.path === '/monitoring/dashboard' }"
        >
          <span class="nav-icon">📊</span>
          <span class="nav-text">仪表盘</span>
        </router-link>
        
        <router-link 
          to="/monitoring/tenants" 
          class="nav-item"
          :class="{ active: $route.path === '/monitoring/tenants' }"
        >
          <span class="nav-icon">👥</span>
          <span class="nav-text">租户管理</span>
        </router-link>
        
        <router-link 
          to="/monitoring/logs" 
          class="nav-item"
          :class="{ active: $route.path === '/monitoring/logs' }"
        >
          <span class="nav-icon">📋</span>
          <span class="nav-text">操作日志</span>
        </router-link>
        
        <router-link 
          to="/monitoring/health" 
          class="nav-item"
          :class="{ active: $route.path === '/monitoring/health' }"
        >
          <span class="nav-icon">❤️</span>
          <span class="nav-text">健康检查</span>
        </router-link>
      </div>
      
      <div class="nav-user">
        <div class="user-info">
          <span class="user-avatar">👤</span>
          <span class="user-name">{{ userInfo.name || '管理员' }}</span>
        </div>
        <button @click="logout" class="logout-btn">
          <span class="logout-icon">🚪</span>
          <span class="logout-text">退出</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'MonitoringNav',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const userInfo = computed(() => authStore.monitoringUser || {})
    
    const logout = () => {
      authStore.clearMonitoringAuth()
      router.push('/monitoring/login')
    }
    
    return {
      userInfo,
      logout
    }
  }
}
</script>

<style scoped>
.monitoring-nav {
  background: #2c3e50;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.nav-brand h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #ecf0f1;
}

.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #bdc3c7;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ecf0f1;
}

.nav-item.active {
  background: #3498db;
  color: white;
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  font-size: 14px;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  font-size: 20px;
}

.user-name {
  font-size: 14px;
  color: #ecf0f1;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.logout-btn:hover {
  background: #c0392b;
}

.logout-icon {
  font-size: 16px;
}

.logout-text {
  font-size: 14px;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 16px;
    height: 56px;
  }
  
  .nav-brand h2 {
    font-size: 18px;
  }
  
  .nav-menu {
    gap: 4px;
  }
  
  .nav-item {
    padding: 8px 12px;
  }
  
  .nav-text {
    display: none;
  }
  
  .user-name {
    display: none;
  }
  
  .logout-text {
    display: none;
  }
}

@media (max-width: 480px) {
  .nav-container {
    flex-direction: column;
    height: auto;
    padding: 16px;
    gap: 16px;
  }
  
  .nav-menu {
    order: 2;
    width: 100%;
    justify-content: center;
  }
  
  .nav-user {
    order: 3;
    width: 100%;
    justify-content: center;
  }
}
</style>
