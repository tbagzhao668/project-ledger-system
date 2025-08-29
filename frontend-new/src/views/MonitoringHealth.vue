<template>
  <div class="monitoring-health">
    <MonitoringNav />
    
    <div class="page-header">
      <h1>系统健康检查</h1>
      <div class="header-actions">
        <button @click="runHealthCheck" :disabled="checking" class="check-btn">
          <span v-if="checking">检查中...</span>
          <span v-else>立即检查</span>
        </button>
        <button @click="refreshData" :disabled="loading" class="refresh-btn">
          <span v-if="loading">刷新中...</span>
          <span v-else>刷新</span>
        </button>
      </div>
    </div>

    <!-- 整体健康状态 -->
    <div class="overall-health">
      <div class="health-status-card" :class="overallStatus">
        <div class="status-icon">
          <span v-if="overallStatus === 'healthy'">✅</span>
          <span v-else-if="overallStatus === 'warning'">⚠️</span>
          <span v-else>❌</span>
        </div>
        <div class="status-content">
          <h2>整体健康状态</h2>
          <div class="status-text">{{ getOverallStatusText() }}</div>
          <div class="last-check">最后检查: {{ formatTime(lastCheckTime) }}</div>
        </div>
      </div>
      
      <!-- 健康检查类型选择 -->
      <div class="health-check-types">
        <button 
          @click="runBasicHealthCheck" 
          :class="['check-type-btn', { active: currentCheckType === 'basic' }]"
          :disabled="checking"
        >
          基础检查
        </button>
        <button 
          @click="runApiEndpointsCheck" 
          :class="['check-type-btn', { active: currentCheckType === 'api' }]"
          :disabled="checking"
        >
          API端点检查
        </button>
        <button 
          @click="runDetailedHealthCheck" 
          :class="['check-type-btn', { active: currentCheckType === 'detailed' }]"
          :disabled="checking"
        >
          详细检查
        </button>
      </div>
    </div>

    <!-- 服务健康状态 -->
    <div class="services-health">
      <h2>服务健康状态</h2>
      <div class="services-grid">
        <div 
          v-for="service in services" 
          :key="service.name"
          :class="['service-card', getServiceStatusClass(service.status)]"
        >
          <div class="service-header">
            <div class="service-icon">
              <span v-if="service.status === 'healthy'">✅</span>
              <span v-else-if="service.status === 'warning'">⚠️</span>
              <span v-else>❌</span>
            </div>
            <div class="service-name">{{ getServiceName(service.name) }}</div>
            <div class="service-status">{{ getServiceStatusText(service.status) }}</div>
          </div>
          
          <div class="service-details">
            <div class="detail-item">
              <span class="detail-label">响应时间:</span>
              <span class="detail-value">{{ service.response_time || 0 }}ms</span>
            </div>
            
            <div class="detail-item">
              <span class="detail-label">最后检查:</span>
              <span class="detail-value">{{ formatTime(service.last_check) }}</span>
            </div>
            
            <div v-if="service.error_message" class="detail-item error">
              <span class="detail-label">错误信息:</span>
              <span class="detail-value">{{ service.error_message }}</span>
            </div>
          </div>
          
          <div class="service-actions">
            <button @click="checkService(service.name)" class="service-check-btn">
              检查
            </button>
            <button @click="viewServiceDetails(service)" class="service-details-btn">
              详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- API端点健康状态 -->
    <div v-if="apiEndpoints.length > 0" class="api-endpoints-health">
      <h2>API端点健康状态</h2>
      <div class="api-endpoints-summary">
        <div class="summary-card">
          <div class="summary-number">{{ apiEndpoints.length }}</div>
          <div class="summary-label">总端点</div>
        </div>
        <div class="summary-card healthy">
          <div class="summary-number">{{ healthyEndpointsCount }}</div>
          <div class="summary-label">健康端点</div>
        </div>
        <div class="summary-card unhealthy">
          <div class="summary-number">{{ unhealthyEndpointsCount }}</div>
          <div class="summary-label">异常端点</div>
        </div>
      </div>
      
      <div class="api-endpoints-grid">
        <div 
          v-for="endpoint in apiEndpoints" 
          :key="`${endpoint.path}-${endpoint.method}`"
          :class="['endpoint-card', getEndpointStatusClass(endpoint.status)]"
        >
          <div class="endpoint-header">
            <div class="endpoint-icon">
              <span v-if="endpoint.status === 'healthy'">✅</span>
              <span v-else-if="endpoint.status === 'requires_auth'">🔐</span>
              <span v-else-if="endpoint.status === 'not_found'">❓</span>
              <span v-else>❌</span>
            </div>
            <div class="endpoint-info">
              <div class="endpoint-name">{{ endpoint.endpoint }}</div>
              <div class="endpoint-path">{{ endpoint.path }}</div>
              <div class="endpoint-method">{{ endpoint.method }}</div>
            </div>
            <div class="endpoint-status">{{ getEndpointStatusText(endpoint.status) }}</div>
          </div>
          
          <div class="endpoint-details">
            <div class="detail-item">
              <span class="detail-label">状态码:</span>
              <span class="detail-value">{{ endpoint.status_code }}</span>
            </div>
            
            <div class="detail-item">
              <span class="detail-label">响应时间:</span>
              <span class="detail-value">{{ endpoint.response_time || 0 }}ms</span>
            </div>
            
            <div class="detail-item">
              <span class="detail-label">最后检查:</span>
              <span class="detail-value">{{ formatTime(endpoint.last_check) }}</span>
            </div>
            
            <div v-if="endpoint.error" class="detail-item error">
              <span class="detail-label">错误信息:</span>
              <span class="detail-value">{{ endpoint.error }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统资源状态 -->
    <div v-if="systemResources" class="system-resources">
      <h2>系统资源状态</h2>
      <div class="resources-grid">
        <div class="resource-card">
          <div class="resource-icon">🖥️</div>
          <div class="resource-info">
            <div class="resource-name">CPU使用率</div>
            <div class="resource-value">{{ systemResources.cpu_percent }}%</div>
            <div class="resource-bar">
              <div class="resource-bar-fill" :style="{ width: systemResources.cpu_percent + '%' }"></div>
            </div>
          </div>
        </div>
        
        <div class="resource-card">
          <div class="resource-icon">💾</div>
          <div class="resource-info">
            <div class="resource-name">内存使用率</div>
            <div class="resource-value">{{ systemResources.memory_percent }}%</div>
            <div class="resource-bar">
              <div class="resource-bar-fill" :style="{ width: systemResources.memory_percent + '%' }"></div>
            </div>
          </div>
        </div>
        
        <div class="resource-card">
          <div class="resource-icon">💿</div>
          <div class="resource-info">
            <div class="resource-name">磁盘使用率</div>
            <div class="resource-value">{{ systemResources.disk_percent }}%</div>
            <div class="resource-bar">
              <div class="resource-bar-fill" :style="{ width: systemResources.disk_percent + '%' }"></div>
            </div>
          </div>
        </div>
        
        <div class="resource-card">
          <div class="resource-icon">🌐</div>
          <div class="resource-info">
            <div class="resource-name">网络连接</div>
            <div class="resource-value">{{ systemResources.network_connections }}</div>
          </div>
        </div>
        
        <div class="resource-card">
          <div class="resource-icon">⚙️</div>
          <div class="resource-info">
            <div class="resource-name">进程数量</div>
            <div class="resource-value">{{ systemResources.process_count }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史健康检查记录 -->
    <div class="health-history">
      <h2>健康检查历史</h2>
      <div class="history-filters">
        <select v-model="historyFilter" @change="filterHistory" class="filter-select">
          <option value="">全部状态</option>
          <option value="healthy">健康</option>
          <option value="warning">警告</option>
          <option value="unhealthy">异常</option>
        </select>
        
        <select v-model="historySort" @change="sortHistory" class="filter-select">
          <option value="created_at">检查时间</option>
          <option value="status">状态</option>
          <option value="response_time">响应时间</option>
        </select>
      </div>
      
      <div class="history-table">
        <div class="table-header">
          <div class="table-row header-row">
            <div class="col-time">检查时间</div>
            <div class="col-service">服务名称</div>
            <div class="col-status">状态</div>
            <div class="col-response">响应时间</div>
            <div class="col-details">详细信息</div>
          </div>
        </div>
        
        <div class="table-body">
          <div v-if="loading" class="loading-row">
            <div class="loading-spinner">加载中...</div>
          </div>
          
          <div v-else-if="healthHistory.length === 0" class="empty-row">
            <div class="empty-message">暂无健康检查记录</div>
          </div>
          
          <div v-else class="table-row" v-for="record in healthHistory" :key="record.id">
            <div class="col-time">
              <div class="time">{{ formatTime(record.created_at) }}</div>
              <div class="date">{{ formatDate(record.created_at) }}</div>
            </div>
            
            <div class="col-service">
              <div class="service-name">{{ getServiceName(record.service_name) }}</div>
            </div>
            
            <div class="col-status">
              <span :class="['status-badge', getServiceStatusClass(record.status)]">
                {{ getServiceStatusText(record.status) }}
              </span>
            </div>
            
            <div class="col-response">
              <div class="response-time">{{ record.response_time || 0 }}ms</div>
            </div>
            
            <div class="col-details">
              <div v-if="record.error_details" class="error-details">
                {{ record.error_details }}
              </div>
              <div v-else-if="record.check_details" class="check-details">
                <button @click="viewCheckDetails(record)" class="view-details-btn">
                  查看详情
                </button>
              </div>
              <div v-else class="no-details">
                无详细信息
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 服务详情模态框 -->
    <div v-if="showServiceModal" class="modal-overlay" @click="closeServiceModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>服务详情</h3>
          <button @click="closeServiceModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body" v-if="selectedService">
          <div class="service-details-full">
            <div class="detail-group">
              <label>服务名称:</label>
              <span>{{ getServiceName(selectedService.name) }}</span>
            </div>
            
            <div class="detail-group">
              <label>当前状态:</label>
              <span :class="['status-badge', getServiceStatusClass(selectedService.status)]">
                {{ getServiceStatusText(selectedService.status) }}
              </span>
            </div>
            
            <div class="detail-group">
              <label>响应时间:</label>
              <span>{{ selectedService.response_time || 0 }}ms</span>
            </div>
            
            <div class="detail-group">
              <label>最后检查:</label>
              <span>{{ formatTime(selectedService.last_check) }}</span>
            </div>
            
            <div v-if="selectedService.error_message" class="detail-group">
              <label>错误信息:</label>
              <span class="error-message">{{ selectedService.error_message }}</span>
            </div>
            
            <div v-if="selectedService.check_details" class="detail-group">
              <label>检查详情:</label>
              <div class="check-details-full">
                <pre>{{ JSON.stringify(selectedService.check_details, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 检查详情模态框 -->
    <div v-if="showCheckModal" class="modal-overlay" @click="closeCheckModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>检查详情</h3>
          <button @click="closeCheckModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body" v-if="selectedCheck">
          <div class="check-details-full">
            <div class="detail-group">
              <label>检查时间:</label>
              <span>{{ formatFullTime(selectedCheck.created_at) }}</span>
            </div>
            
            <div class="detail-group">
              <label>服务名称:</label>
              <span>{{ getServiceName(selectedCheck.service_name) }}</span>
            </div>
            
            <div class="detail-group">
              <label>检查状态:</label>
              <span :class="['status-badge', getServiceStatusClass(selectedCheck.status)]">
                {{ getServiceStatusText(selectedCheck.status) }}
              </span>
            </div>
            
            <div class="detail-group">
              <label>响应时间:</label>
              <span>{{ selectedCheck.response_time || 0 }}ms</span>
            </div>
            
            <div v-if="selectedCheck.error_details" class="detail-group">
              <label>错误详情:</label>
              <span class="error-details">{{ selectedCheck.error_details }}</span>
            </div>
            
            <div v-if="selectedCheck.check_details" class="detail-group">
              <label>检查详情:</label>
              <div class="check-details-content">
                <pre>{{ JSON.stringify(selectedCheck.check_details, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import MonitoringNav from '@/components/MonitoringNav.vue'

export default {
  name: 'MonitoringHealth',
  components: {
    MonitoringNav
  },
  setup() {
    const authStore = useAuthStore()
    
    // 状态管理
    const loading = ref(false)
    const checking = ref(false)
    const services = ref([])
    const healthHistory = ref([])
    const overallStatus = ref('unknown')
    const lastCheckTime = ref(null)
    
    // 新增状态
    const currentCheckType = ref('basic')
    const apiEndpoints = ref([])
    const systemResources = ref(null)
    
    // 筛选和排序
    const historyFilter = ref('')
    const historySort = ref('created_at')
    
    // 模态框状态
    const showServiceModal = ref(false)
    const showCheckModal = ref(false)
    const selectedService = ref(null)
    const selectedCheck = ref(null)
    
    // 自动检查定时器
    let autoCheckTimer = null

    // 计算属性
    const healthyEndpointsCount = computed(() => {
      return apiEndpoints.value.filter(ep => 
        ep.status === 'healthy' || ep.status === 'requires_auth'
      ).length
    })

    const unhealthyEndpointsCount = computed(() => {
      return apiEndpoints.value.filter(ep => 
        ep.status === 'unhealthy' || ep.status === 'error' || ep.status === 'not_found'
      ).length
    })
    
    // 运行基础健康检查
    const runBasicHealthCheck = async () => {
      try {
        checking.value = true
        currentCheckType.value = 'basic'
        
        const response = await fetch('/api/v1/admin/health', {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          updateHealthStatus(data)
          await fetchHealthHistory()
        } else {
          console.error('基础健康检查失败')
        }
      } catch (error) {
        console.error('基础健康检查错误:', error)
      } finally {
        checking.value = false
      }
    }

    // 运行API端点健康检查
    const runApiEndpointsCheck = async () => {
      try {
        checking.value = true
        currentCheckType.value = 'api'
        
        const response = await fetch('/api/v1/admin/health/api-endpoints', {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          updateApiEndpointsStatus(data)
        } else {
          console.error('API端点健康检查失败')
        }
      } catch (error) {
        console.error('API端点健康检查错误:', error)
      } finally {
        checking.value = false
      }
    }

    // 运行详细健康检查
    const runDetailedHealthCheck = async () => {
      try {
        checking.value = true
        currentCheckType.value = 'detailed'
        
        const response = await fetch('/api/v1/admin/health/detailed', {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          updateDetailedHealthStatus(data)
        } else {
          console.error('详细健康检查失败')
        }
      } catch (error) {
        console.error('详细健康检查错误:', error)
      } finally {
        checking.value = false
      }
    }

    // 运行健康检查（兼容旧版本）
    const runHealthCheck = async () => {
      await runBasicHealthCheck()
    }
    
    // 更新健康状态
    const updateHealthStatus = (data) => {
      overallStatus.value = data.status
      lastCheckTime.value = data.timestamp
      
      if (data.services) {
        services.value = Object.entries(data.services).map(([name, service]) => ({
          name,
          ...service
        }))
      }
    }

    // 更新API端点状态
    const updateApiEndpointsStatus = (data) => {
      overallStatus.value = data.status
      lastCheckTime.value = data.timestamp
      apiEndpoints.value = data.endpoints || []
    }

    // 更新详细健康状态
    const updateDetailedHealthStatus = (data) => {
      overallStatus.value = data.status
      lastCheckTime.value = data.timestamp
      
      if (data.basic_health && data.basic_health.services) {
        services.value = Object.entries(data.basic_health.services).map(([name, service]) => ({
          name,
          ...service
        }))
      }
      
      if (data.api_endpoints) {
        apiEndpoints.value = data.api_endpoints.endpoints || []
      }
      
      if (data.system_resources) {
        systemResources.value = data.system_resources
      }
    }
    
    // 获取健康检查历史
    const fetchHealthHistory = async () => {
      try {
        loading.value = true
        
        const response = await fetch('/api/v1/admin/monitoring?service_name=system_overall', {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          healthHistory.value = data || []
        } else {
          console.error('获取健康检查历史失败')
        }
      } catch (error) {
        console.error('获取健康检查历史错误:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 检查特定服务
    const checkService = async (serviceName) => {
      try {
        const response = await fetch('/api/v1/admin/health', {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          updateHealthStatus(data)
        }
      } catch (error) {
        console.error('检查服务失败:', error)
      }
    }
    
    // 查看服务详情
    const viewServiceDetails = (service) => {
      selectedService.value = service
      showServiceModal.value = true
    }
    
    // 查看检查详情
    const viewCheckDetails = (check) => {
      selectedCheck.value = check
      showCheckModal.value = true
    }
    
    // 关闭模态框
    const closeServiceModal = () => {
      showServiceModal.value = false
      selectedService.value = null
    }
    
    const closeCheckModal = () => {
      showCheckModal.value = false
      selectedCheck.value = null
    }
    
    // 刷新数据
    const refreshData = () => {
      fetchHealthHistory()
    }
    
    // 筛选历史记录
    const filterHistory = () => {
      // 这里可以实现筛选逻辑
    }
    
    // 排序历史记录
    const sortHistory = () => {
      // 这里可以实现排序逻辑
    }
    
    // 工具函数
    const getOverallStatusText = () => {
      const statusMap = {
        'healthy': '系统运行正常',
        'warning': '系统存在警告',
        'unhealthy': '系统运行异常',
        'unknown': '状态未知'
      }
      return statusMap[overallStatus.value] || '状态未知'
    }
    
    const getServiceName = (name) => {
      const nameMap = {
        'database': '数据库服务',
        'api': 'API服务',
        'frontend': '前端服务',
        'redis': 'Redis缓存',
        'system_overall': '系统整体'
      }
      return nameMap[name] || name
    }
    
    const getServiceStatusText = (status) => {
      const statusMap = {
        'healthy': '健康',
        'warning': '警告',
        'unhealthy': '异常'
      }
      return statusMap[status] || status
    }
    
    const getServiceStatusClass = (status) => {
      return status || 'unknown'
    }

    const getEndpointStatusClass = (status) => {
      const statusMap = {
        'healthy': 'healthy',
        'requires_auth': 'healthy',
        'not_found': 'warning',
        'unhealthy': 'unhealthy',
        'error': 'unhealthy'
      }
      return statusMap[status] || 'unknown'
    }

    const getEndpointStatusText = (status) => {
      const statusMap = {
        'healthy': '健康',
        'requires_auth': '需要认证',
        'not_found': '未找到',
        'unhealthy': '异常',
        'error': '错误'
      }
      return statusMap[status] || status
    }
    
    const formatTime = (timestamp) => {
      if (!timestamp) return '未知'
      return new Date(timestamp * 1000).toLocaleTimeString('zh-CN')
    }
    
    const formatDate = (timestamp) => {
      if (!timestamp) return '未知'
      return new Date(timestamp * 1000).toLocaleDateString('zh-CN')
    }
    
    const formatFullTime = (timestamp) => {
      if (!timestamp) return '未知'
      return new Date(timestamp * 1000).toLocaleString('zh-CN')
    }
    
    onMounted(() => {
      runHealthCheck()
      // 每5分钟自动检查一次
      autoCheckTimer = setInterval(runHealthCheck, 5 * 60 * 1000)
    })
    
    onUnmounted(() => {
      if (autoCheckTimer) {
        clearInterval(autoCheckTimer)
      }
    })
    
    return {
      // 状态
      loading,
      checking,
      services,
      healthHistory,
      overallStatus,
      lastCheckTime,
      historyFilter,
      historySort,
      showServiceModal,
      showCheckModal,
      selectedService,
      selectedCheck,
      currentCheckType,
      apiEndpoints,
      systemResources,
      healthyEndpointsCount,
      unhealthyEndpointsCount,
      
      // 方法
      runHealthCheck,
      runBasicHealthCheck,
      runApiEndpointsCheck,
      runDetailedHealthCheck,
      updateHealthStatus,
      updateApiEndpointsStatus,
      updateDetailedHealthStatus,
      fetchHealthHistory,
      checkService,
      viewServiceDetails,
      viewCheckDetails,
      closeServiceModal,
      closeCheckModal,
      refreshData,
      filterHistory,
      sortHistory,
      
      // 工具函数
      getOverallStatusText,
      getServiceName,
      getServiceStatusText,
      getServiceStatusClass,
      getEndpointStatusClass,
      getEndpointStatusText,
      formatTime,
      formatDate,
      formatFullTime
    }
  }
}
</script>

<style scoped>
.monitoring-health {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.check-btn, .refresh-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.check-btn {
  background: #28a745;
  color: white;
}

.check-btn:hover:not(:disabled) {
  background: #218838;
}

.refresh-btn {
  background: #667eea;
  color: white;
}

.refresh-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.check-btn:disabled, .refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.overall-health {
  margin-bottom: 32px;
}

.health-check-types {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.check-type-btn {
  padding: 10px 20px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  background: white;
  color: #666;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.check-type-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.check-type-btn.active {
  border-color: #667eea;
  background: #667eea;
  color: white;
}

.check-type-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.health-status-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 24px;
}

.health-status-card.healthy {
  border-left: 6px solid #28a745;
}

.health-status-card.warning {
  border-left: 6px solid #ffc107;
}

.health-status-card.unhealthy {
  border-left: 6px solid #dc3545;
}

.status-icon {
  font-size: 48px;
}

.status-content h2 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 20px;
}

.status-text {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.health-status-card.healthy .status-text {
  color: #28a745;
}

.health-status-card.warning .status-text {
  color: #ffc107;
}

.health-status-card.unhealthy .status-text {
  color: #dc3545;
}

.last-check {
  font-size: 14px;
  color: #666;
}

.services-health {
  margin-bottom: 32px;
}

.services-health h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.service-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ddd;
}

.service-card.healthy {
  border-left-color: #28a745;
}

.service-card.warning {
  border-left-color: #ffc107;
}

.service-card.unhealthy {
  border-left-color: #dc3545;
}

.service-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.service-icon {
  font-size: 24px;
}

.service-name {
  flex: 1;
  font-weight: 600;
  color: #333;
}

.service-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.service-card.healthy .service-status {
  background: #d4edda;
  color: #155724;
}

.service-card.warning .service-status {
  background: #fff3cd;
  color: #856404;
}

.service-card.unhealthy .service-status {
  background: #f8d7da;
  color: #721c24;
}

.service-details {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-label {
  color: #666;
}

.detail-value {
  font-weight: 500;
  color: #333;
}

.detail-item.error .detail-value {
  color: #dc3545;
}

.service-actions {
  display: flex;
  gap: 8px;
}

.service-check-btn, .service-details-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.service-check-btn {
  background: #17a2b8;
  color: white;
}

.service-details-btn {
  background: #6c757d;
  color: white;
}

.service-check-btn:hover, .service-details-btn:hover {
  opacity: 0.8;
}

.health-history {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.health-history h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.history-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.history-table {
  overflow-x: auto;
}

.table-header {
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.table-row {
  display: grid;
  grid-template-columns: 1.5fr 1.5fr 1fr 1fr 2fr;
  gap: 16px;
  padding: 16px;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.header-row {
  font-weight: 600;
  color: #666;
  font-size: 14px;
}

.loading-row, .empty-row {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: #666;
}

.loading-spinner {
  color: #667eea;
}

.time {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.date {
  font-size: 12px;
  color: #666;
}

.service-name {
  font-weight: 500;
  color: #333;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  display: inline-block;
  min-width: 60px;
}

.status-badge.healthy {
  background: #d4edda;
  color: #155724;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.status-badge.unhealthy {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.unknown {
  background: #e2e3e5;
  color: #383d41;
}

.response-time {
  font-weight: 500;
  color: #333;
}

.error-details {
  font-size: 12px;
  color: #dc3545;
  line-height: 1.4;
}

.check-details {
  font-size: 12px;
  color: #666;
}

.view-details-btn {
  padding: 4px 8px;
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
}

.view-details-btn:hover {
  background: #138496;
}

.no-details {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 24px;
}

.service-details-full, .check-details-full {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-group {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.detail-group label {
  width: 100px;
  font-weight: 600;
  color: #666;
  flex-shrink: 0;
}

.detail-group span {
  color: #333;
  flex: 1;
}

.error-message {
  color: #dc3545;
  word-break: break-all;
}

.check-details-content, .check-details-full {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}

.check-details-content pre, .check-details-full pre {
  margin: 0;
  font-size: 12px;
  color: #495057;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 768px) {
  .monitoring-health {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .header-row {
    display: none;
  }
  
  .col-time, .col-service, .col-status, .col-response, .col-details {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .col-time::before { content: "检查时间: "; font-weight: 600; }
  .col-service::before { content: "服务名称: "; font-weight: 600; }
  .col-status::before { content: "状态: "; font-weight: 600; }
  .col-response::before { content: "响应时间: "; font-weight: 600; }
  .col-details::before { content: "详细信息: "; font-weight: 600; }
}

/* API端点健康状态样式 */
.api-endpoints-health {
  margin-bottom: 32px;
}

.api-endpoints-health h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.api-endpoints-summary {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.summary-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  flex: 1;
}

.summary-card.healthy {
  border-left: 4px solid #28a745;
}

.summary-card.unhealthy {
  border-left: 4px solid #dc3545;
}

.summary-number {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.summary-label {
  font-size: 14px;
  color: #666;
}

.api-endpoints-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.endpoint-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ddd;
}

.endpoint-card.healthy {
  border-left-color: #28a745;
}

.endpoint-card.warning {
  border-left-color: #ffc107;
}

.endpoint-card.unhealthy {
  border-left-color: #dc3545;
}

.endpoint-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.endpoint-icon {
  font-size: 24px;
}

.endpoint-info {
  flex: 1;
}

.endpoint-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.endpoint-path {
  font-size: 12px;
  color: #666;
  font-family: monospace;
  margin-bottom: 2px;
}

.endpoint-method {
  font-size: 11px;
  color: #999;
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

.endpoint-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.endpoint-card.healthy .endpoint-status {
  background: #d4edda;
  color: #155724;
}

.endpoint-card.warning .endpoint-status {
  background: #fff3cd;
  color: #856404;
}

.endpoint-card.unhealthy .endpoint-status {
  background: #f8d7da;
  color: #721c24;
}

/* 系统资源状态样式 */
.system-resources {
  margin-bottom: 32px;
}

.system-resources h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.resource-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.resource-icon {
  font-size: 32px;
}

.resource-info {
  flex: 1;
}

.resource-name {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.resource-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.resource-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.resource-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  transition: width 0.3s ease;
}

.resource-card:nth-child(1) .resource-bar-fill {
  background: linear-gradient(90deg, #007bff, #0056b3);
}

.resource-card:nth-child(2) .resource-bar-fill {
  background: linear-gradient(90deg, #6f42c1, #5a32a3);
}

.resource-card:nth-child(3) .resource-bar-fill {
  background: linear-gradient(90deg, #fd7e14, #e55a00);
}
</style>
