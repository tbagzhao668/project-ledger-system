<template>
  <div class="monitoring-logs">
    <MonitoringNav />
    
    <div class="page-header">
      <h1>操作日志</h1>
      <div class="header-actions">
        <button @click="exportLogs" :disabled="loading" class="export-btn">
          <span v-if="loading">导出中...</span>
          <span v-else>导出日志</span>
        </button>
        <button @click="refreshData" :disabled="loading" class="refresh-btn">
          <span v-if="loading">刷新中...</span>
          <span v-else>刷新</span>
        </button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索操作类型或目标..."
          @input="handleSearch"
          class="search-input"
        />
        <button @click="handleSearch" class="search-btn">搜索</button>
      </div>
      
      <div class="filter-options">
        <select v-model="operationTypeFilter" @change="handleFilter" class="filter-select">
          <option value="">全部操作类型</option>
          <option value="monitoring_login">监控系统登录</option>
          <option value="update_tenant_status">更新租户状态</option>
          <option value="reset_tenant_password">重置租户密码</option>
          <option value="view_tenant">查看租户详情</option>
        </select>
        
        <select v-model="targetTypeFilter" @change="handleFilter" class="filter-select">
          <option value="">全部目标类型</option>
          <option value="tenant">租户</option>
          <option value="system">系统</option>
          <option value="user">用户</option>
        </select>
        
        <select v-model="sortBy" @change="handleSort" class="filter-select">
          <option value="created_at">操作时间</option>
          <option value="operation_type">操作类型</option>
          <option value="target_type">目标类型</option>
        </select>
      </div>
    </div>

    <!-- 日志统计 -->
    <div class="logs-stats">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ totalLogs }}</div>
          <div class="stat-label">总日志数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">👤</div>
        <div class="stat-content">
          <div class="stat-value">{{ uniqueAdmins }}</div>
          <div class="stat-label">活跃管理员</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🕒</div>
        <div class="stat-content">
          <div class="stat-value">{{ todayLogs }}</div>
          <div class="stat-label">今日操作</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-value">{{ errorLogs }}</div>
          <div class="stat-label">异常操作</div>
        </div>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="logs-table">
      <div class="table-header">
        <div class="table-row header-row">
          <div class="col-time">操作时间</div>
          <div class="col-admin">管理员</div>
          <div class="col-operation">操作类型</div>
          <div class="col-target">目标对象</div>
          <div class="col-details">操作详情</div>
          <div class="col-location">操作位置</div>
        </div>
      </div>
      
      <div class="table-body">
        <div v-if="loading" class="loading-row">
          <div class="loading-spinner">加载中...</div>
        </div>
        
        <div v-else-if="logs.length === 0" class="empty-row">
          <div class="empty-message">暂无操作日志</div>
        </div>
        
        <div v-else class="table-row" v-for="log in logs" :key="log.id">
          <div class="col-time">
            <div class="time">{{ formatTime(log.created_at) }}</div>
            <div class="date">{{ formatDate(log.created_at) }}</div>
          </div>
          
          <div class="col-admin">
            <div class="admin-id">ID: {{ log.admin_user_id.slice(0, 8) }}...</div>
            <div class="admin-role">超级管理员</div>
          </div>
          
          <div class="col-operation">
            <span :class="['operation-badge', getOperationTypeClass(log.operation_type)]">
              {{ getOperationTypeText(log.operation_type) }}
            </span>
          </div>
          
          <div class="col-target">
            <div class="target-type">{{ getTargetTypeText(log.target_type) }}</div>
            <div v-if="log.target_id" class="target-id">
              ID: {{ log.target_id.slice(0, 8) }}...
            </div>
          </div>
          
          <div class="col-details">
            <div class="details-preview">
              {{ getDetailsPreview(log.operation_details) }}
            </div>
            <button @click="viewDetails(log)" class="view-details-btn">查看详情</button>
          </div>
          
          <div class="col-location">
            <div class="ip-address">{{ log.ip_address || '未知' }}</div>
            <div class="user-agent">{{ truncateUserAgent(log.user_agent) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        @click="changePage(currentPage - 1)" 
        :disabled="currentPage <= 1"
        class="page-btn"
      >
        上一页
      </button>
      
      <div class="page-numbers">
        <span v-for="page in visiblePages" :key="page" 
              :class="['page-number', { active: page === currentPage }]"
              @click="changePage(page)">
          {{ page }}
        </span>
      </div>
      
      <button 
        @click="changePage(currentPage + 1)" 
        :disabled="currentPage >= totalPages"
        class="page-btn"
      >
        下一页
      </button>
    </div>

    <!-- 日志详情模态框 -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>操作日志详情</h3>
          <button @click="closeDetailsModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body" v-if="selectedLog">
          <div class="log-details">
            <div class="detail-group">
              <label>操作时间:</label>
              <span>{{ formatFullTime(selectedLog.created_at) }}</span>
            </div>
            
            <div class="detail-group">
              <label>管理员ID:</label>
              <span>{{ selectedLog.admin_user_id }}</span>
            </div>
            
            <div class="detail-group">
              <label>操作类型:</label>
              <span :class="['operation-badge', getOperationTypeClass(selectedLog.operation_type)]">
                {{ getOperationTypeText(selectedLog.operation_type) }}
              </span>
            </div>
            
            <div class="detail-group">
              <label>目标类型:</label>
              <span>{{ getTargetTypeText(selectedLog.target_type) }}</span>
            </div>
            
            <div class="detail-group" v-if="selectedLog.target_id">
              <label>目标ID:</label>
              <span>{{ selectedLog.target_id }}</span>
            </div>
            
            <div class="detail-group">
              <label>IP地址:</label>
              <span>{{ selectedLog.ip_address || '未知' }}</span>
            </div>
            
            <div class="detail-group">
              <label>用户代理:</label>
              <span class="user-agent-full">{{ selectedLog.user_agent || '未知' }}</span>
            </div>
            
            <div class="detail-group" v-if="selectedLog.operation_details">
              <label>操作详情:</label>
              <div class="operation-details">
                <pre>{{ JSON.stringify(selectedLog.operation_details, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import MonitoringNav from '@/components/MonitoringNav.vue'

export default {
  name: 'MonitoringLogs',
  components: {
    MonitoringNav
  },
  setup() {
    const authStore = useAuthStore()
    
    // 状态管理
    const loading = ref(false)
    const logs = ref([])
    const currentPage = ref(1)
    const pageSize = ref(50)
    const totalPages = ref(1)
    const totalLogs = ref(0)
    
    // 搜索和筛选
    const searchQuery = ref('')
    const operationTypeFilter = ref('')
    const targetTypeFilter = ref('')
    const sortBy = ref('created_at')
    
    // 模态框状态
    const showDetailsModal = ref(false)
    const selectedLog = ref(null)
    
    // 统计数据
    const uniqueAdmins = ref(0)
    const todayLogs = ref(0)
    const errorLogs = ref(0)
    
    // 获取操作日志
    const fetchLogs = async () => {
      try {
        loading.value = true
        
        const params = new URLSearchParams({
          page: currentPage.value,
          size: pageSize.value
        })
        
        if (searchQuery.value) {
          params.append('search', searchQuery.value)
        }
        if (operationTypeFilter.value) {
          params.append('operation_type', operationTypeFilter.value)
        }
        if (targetTypeFilter.value) {
          params.append('target_type', targetTypeFilter.value)
        }
        if (sortBy.value) {
          params.append('sort_by', sortBy.value)
        }
        
        const response = await fetch(`/api/v1/admin/admin-logs?${params}`, {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          logs.value = data || []
          
          // 计算统计数据
          calculateStats()
        } else {
          console.error('获取操作日志失败')
        }
      } catch (error) {
        console.error('获取操作日志错误:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 计算统计数据
    const calculateStats = () => {
      totalLogs.value = logs.value.length
      
      // 计算唯一管理员数量
      const adminIds = new Set(logs.value.map(log => log.admin_user_id))
      uniqueAdmins.value = adminIds.size
      
      // 计算今日日志数量
      const today = new Date().toDateString()
      todayLogs.value = logs.value.filter(log => {
        return new Date(log.created_at).toDateString() === today
      }).length
      
      // 计算异常操作数量（这里可以根据实际需求定义异常操作）
      errorLogs.value = logs.value.filter(log => {
        return log.operation_type.includes('error') || log.operation_type.includes('fail')
      }).length
    }
    
    // 搜索处理
    const handleSearch = () => {
      currentPage.value = 1
      fetchLogs()
    }
    
    // 筛选处理
    const handleFilter = () => {
      currentPage.value = 1
      fetchLogs()
    }
    
    // 排序处理
    const handleSort = () => {
      currentPage.value = 1
      fetchLogs()
    }
    
    // 分页处理
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        fetchLogs()
      }
    }
    
    // 查看日志详情
    const viewDetails = (log) => {
      selectedLog.value = log
      showDetailsModal.value = true
    }
    
    // 关闭详情模态框
    const closeDetailsModal = () => {
      showDetailsModal.value = false
      selectedLog.value = null
    }
    
    // 刷新数据
    const refreshData = () => {
      fetchLogs()
    }
    
    // 导出日志
    const exportLogs = async () => {
      try {
        loading.value = true
        
        const response = await fetch('/api/v1/admin/admin-logs/export', {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `操作日志_${new Date().toISOString().split('T')[0]}.csv`
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
        } else {
          alert('导出失败')
        }
      } catch (error) {
        console.error('导出日志失败:', error)
        alert('导出失败')
      } finally {
        loading.value = false
      }
    }
    
    // 工具函数
    const formatTime = (dateString) => {
      if (!dateString) return '未知'
      return new Date(dateString).toLocaleTimeString('zh-CN')
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      return new Date(dateString).toLocaleDateString('zh-CN')
    }
    
    const formatFullTime = (dateString) => {
      if (!dateString) return '未知'
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    const getOperationTypeText = (type) => {
      const typeMap = {
        'monitoring_login': '监控系统登录',
        'update_tenant_status': '更新租户状态',
        'reset_tenant_password': '重置租户密码',
        'view_tenant': '查看租户详情',
        'tenant_login': '租户登录',
        'tenant_logout': '租户登出'
      }
      return typeMap[type] || type
    }
    
    const getOperationTypeClass = (type) => {
      if (type.includes('login')) return 'login'
      if (type.includes('update') || type.includes('reset')) return 'modify'
      if (type.includes('view')) return 'view'
      return 'default'
    }
    
    const getTargetTypeText = (type) => {
      const typeMap = {
        'tenant': '租户',
        'system': '系统',
        'user': '用户'
      }
      return typeMap[type] || type
    }
    
    const getDetailsPreview = (details) => {
      if (!details) return '无详细信息'
      
      try {
        if (typeof details === 'string') {
          return details.length > 50 ? details.substring(0, 50) + '...' : details
        }
        
        const detailsStr = JSON.stringify(details)
        return detailsStr.length > 50 ? detailsStr.substring(0, 50) + '...' : detailsStr
      } catch {
        return '详细信息解析失败'
      }
    }
    
    const truncateUserAgent = (userAgent) => {
      if (!userAgent) return '未知'
      return userAgent.length > 30 ? userAgent.substring(0, 30) + '...' : userAgent
    }
    
    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })
    
    onMounted(() => {
      fetchLogs()
    })
    
    return {
      // 状态
      loading,
      logs,
      currentPage,
      totalPages,
      totalLogs,
      searchQuery,
      operationTypeFilter,
      targetTypeFilter,
      sortBy,
      showDetailsModal,
      selectedLog,
      uniqueAdmins,
      todayLogs,
      errorLogs,
      
      // 方法
      fetchLogs,
      handleSearch,
      handleFilter,
      handleSort,
      changePage,
      viewDetails,
      closeDetailsModal,
      refreshData,
      exportLogs,
      
      // 工具函数
      formatTime,
      formatDate,
      formatFullTime,
      getOperationTypeText,
      getOperationTypeClass,
      getTargetTypeText,
      getDetailsPreview,
      truncateUserAgent,
      visiblePages
    }
  }
}
</script>

<style scoped>
.monitoring-logs {
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

.export-btn, .refresh-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.export-btn {
  background: #28a745;
  color: white;
}

.export-btn:hover:not(:disabled) {
  background: #218838;
}

.refresh-btn {
  background: #667eea;
  color: white;
}

.refresh-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.export-btn:disabled, .refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.search-btn {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.search-btn:hover {
  background: #218838;
}

.filter-options {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.logs-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 32px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.logs-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 24px;
}

.table-header {
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.table-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1.5fr 1fr 2fr 1.5fr;
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

.admin-id {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.admin-role {
  font-size: 12px;
  color: #28a745;
  background: #d4edda;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
}

.operation-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  display: inline-block;
  min-width: 80px;
}

.operation-badge.login {
  background: #d4edda;
  color: #155724;
}

.operation-badge.modify {
  background: #fff3cd;
  color: #856404;
}

.operation-badge.view {
  background: #d1ecf1;
  color: #0c5460;
}

.operation-badge.default {
  background: #e2e3e5;
  color: #383d41;
}

.target-type {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.target-id {
  font-size: 12px;
  color: #666;
}

.details-preview {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  line-height: 1.4;
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

.ip-address {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.user-agent {
  font-size: 11px;
  color: #666;
  line-height: 1.3;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  border-radius: 6px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #f8f9fa;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 8px;
}

.page-number {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  border-radius: 6px;
  cursor: pointer;
  min-width: 40px;
  text-align: center;
}

.page-number:hover {
  background: #f8f9fa;
}

.page-number.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
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
  max-width: 700px;
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

.log-details {
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

.operation-details {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}

.operation-details pre {
  margin: 0;
  font-size: 12px;
  color: #495057;
  white-space: pre-wrap;
  word-break: break-word;
}

.user-agent-full {
  word-break: break-all;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .monitoring-logs {
    padding: 16px;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .logs-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .header-row {
    display: none;
  }
  
  .col-time, .col-admin, .col-operation, .col-target, .col-details, .col-location {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .col-time::before { content: "操作时间: "; font-weight: 600; }
  .col-admin::before { content: "管理员: "; font-weight: 600; }
  .col-operation::before { content: "操作类型: "; font-weight: 600; }
  .col-target::before { content: "目标对象: "; font-weight: 600; }
  .col-details::before { content: "操作详情: "; font-weight: 600; }
  .col-location::before { content: "操作位置: "; font-weight: 600; }
}
</style>
