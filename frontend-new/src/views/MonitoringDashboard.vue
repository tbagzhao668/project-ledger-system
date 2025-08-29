<template>
  <div class="monitoring-dashboard">
    <MonitoringNav />
    
    <div class="dashboard-header">
      <h1>系统监控仪表盘</h1>
      <div class="header-actions">
        <span class="last-update">最后更新: {{ formatTime(lastUpdate) }}</span>
        <button @click="refreshData" :disabled="loading" class="refresh-btn">
          <span v-if="loading">刷新中...</span>
          <span v-else>刷新</span>
        </button>
      </div>
    </div>
    
    <!-- 系统概览卡片 -->
    <div class="overview-cards">
      <div class="overview-card">
        <div class="card-icon tenants">
          <span class="icon">👥</span>
        </div>
        <div class="card-content">
          <h3>总租户数</h3>
          <div class="card-value">{{ overview.total_tenants || 0 }}</div>
          <div class="card-change">
            <span class="change-label">今日新增:</span>
            <span class="change-value positive">+{{ overview.today_new_tenants || 0 }}</span>
          </div>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="card-icon projects">
          <span class="icon">📁</span>
        </div>
        <div class="card-content">
          <h3>总项目数</h3>
          <div class="card-value">{{ overview.total_projects || 0 }}</div>
          <div class="card-change">
            <span class="change-label">活跃项目:</span>
            <span class="change-value">{{ overview.active_tenants || 0 }}</span>
          </div>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="card-icon transactions">
          <span class="icon">💰</span>
        </div>
        <div class="card-content">
          <h3>财务记录</h3>
          <div class="card-value">{{ overview.total_transactions || 0 }}</div>
          <div class="card-change">
            <span class="change-label">总用户:</span>
            <span class="change-value">{{ overview.total_users || 0 }}</span>
          </div>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="card-icon system">
          <span class="icon">⚙️</span>
        </div>
        <div class="card-content">
          <h3>系统状态</h3>
          <div class="card-value status-healthy">健康</div>
          <div class="card-change">
            <span class="change-label">运行时间:</span>
            <span class="change-value">{{ formatUptime(overview.system_uptime) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>快速操作</h2>
      <div class="action-buttons">
        <button @click="goToTenants" class="action-btn">
          <span class="action-icon">👥</span>
          <span>租户管理</span>
        </button>
        <button @click="goToLogs" class="action-btn">
          <span class="action-icon">📋</span>
          <span>操作日志</span>
        </button>
        <button @click="goToHealth" class="action-btn">
          <span class="action-icon">❤️</span>
          <span>健康检查</span>
        </button>
        <button @click="logout" class="action-btn logout">
          <span class="action-icon">🚪</span>
          <span>退出登录</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MonitoringNav from '@/components/MonitoringNav.vue'

export default {
  name: 'MonitoringDashboard',
  components: {
    MonitoringNav
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const loading = ref(false)
    const overview = ref({})
    const lastUpdate = ref(Date.now())
    let refreshInterval = null
    
    const fetchOverview = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/v1/admin/overview', {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          overview.value = data
          lastUpdate.value = Date.now()
        } else {
          console.error('获取系统概览失败')
        }
      } catch (error) {
        console.error('获取系统概览错误:', error)
      } finally {
        loading.value = false
      }
    }
    
    const refreshData = () => {
      fetchOverview()
    }
    
    const goToTenants = () => {
      router.push('/monitoring/tenants')
    }
    
    const goToLogs = () => {
      router.push('/monitoring/logs')
    }
    
    const goToHealth = () => {
      router.push('/monitoring/health')
    }
    
    const logout = () => {
      authStore.clearMonitoringAuth()
      router.push('/monitoring/login')
    }
    
    const formatTime = (timestamp) => {
      if (!timestamp) return '未知'
      return new Date(timestamp * 1000).toLocaleString('zh-CN')
    }
    
    const formatUptime = (uptime) => {
      if (!uptime) return '未知'
      const hours = Math.floor(uptime / 3600)
      const minutes = Math.floor((uptime % 3600) / 60)
      return `${hours}小时${minutes}分钟`
    }
    
    onMounted(() => {
      fetchOverview()
      // 每5分钟自动刷新一次
      refreshInterval = setInterval(fetchOverview, 5 * 60 * 1000)
    })
    
    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })
    
    return {
      loading,
      overview,
      lastUpdate,
      refreshData,
      goToTenants,
      goToLogs,
      goToHealth,
      logout,
      formatTime,
      formatUptime
    }
  }
}
</script>

<style scoped>
.monitoring-dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.dashboard-header h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.last-update {
  color: #666;
  font-size: 14px;
}

.refresh-btn {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.overview-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.2s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.card-icon.tenants { background: #e3f2fd; }
.card-icon.projects { background: #f3e5f5; }
.card-icon.transactions { background: #e8f5e8; }
.card-icon.system { background: #fff3e0; }

.card-content h3 {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.card-change {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.change-label {
  color: #666;
}

.change-value {
  font-weight: 600;
}

.change-value.positive {
  color: #4caf50;
}

.status-healthy {
  color: #4caf50;
}

.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-actions h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #f8f9fa;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  color: #333;
}

.action-btn:hover {
  background: #e9ecef;
  border-color: #667eea;
  transform: translateY(-2px);
}

.action-btn.logout {
  background: #fee;
  color: #d32f2f;
}

.action-btn.logout:hover {
  background: #ffebee;
  border-color: #d32f2f;
}

.action-icon {
  font-size: 24px;
}

@media (max-width: 768px) {
  .monitoring-dashboard {
    padding: 16px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
