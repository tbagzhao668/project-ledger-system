<template>
  <div class="monitoring-tenants">
    <MonitoringNav />
    
    <div class="page-header">
      <h1>租户管理</h1>
      <div class="header-actions">
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
          placeholder="搜索租户名称或邮箱..."
          @input="handleSearch"
          class="search-input"
        />
        <button @click="handleSearch" class="search-btn">搜索</button>
      </div>
      
      <div class="filter-options">
        <select v-model="statusFilter" @change="handleFilter" class="filter-select">
          <option value="">全部状态</option>
          <option value="active">活跃</option>
          <option value="disabled">禁用</option>
        </select>
        
        <select v-model="sortBy" @change="handleSort" class="filter-select">
          <option value="created_at">创建时间</option>
          <option value="name">名称</option>
          <option value="last_login_at">最后登录</option>
        </select>
      </div>
    </div>

    <!-- 租户列表 -->
    <div class="tenants-table">
      <div class="table-header">
        <div class="table-row header-row">
          <div class="col-name">租户名称</div>
          <div class="col-email">邮箱</div>
          <div class="col-status">状态</div>
          <div class="col-stats">统计信息</div>
          <div class="col-activity">活跃度</div>
          <div class="col-actions">操作</div>
        </div>
      </div>
      
      <div class="table-body">
        <div v-if="loading" class="loading-row">
          <div class="loading-spinner">加载中...</div>
        </div>
        
        <div v-else-if="tenants.length === 0" class="empty-row">
          <div class="empty-message">暂无租户数据</div>
        </div>
        
        <div v-else class="table-row" v-for="tenant in tenants" :key="tenant.id">
          <div class="col-name">
            <div class="tenant-name">{{ tenant.name }}</div>
            <div class="tenant-id">ID: {{ tenant.id.slice(0, 8) }}...</div>
          </div>
          
          <div class="col-email">
            <div class="email">{{ tenant.email }}</div>
            <div class="created-at">创建于: {{ formatDate(tenant.created_at) }}</div>
          </div>
          
          <div class="col-status">
            <span :class="['status-badge', tenant.status]">
              {{ getStatusText(tenant.status) }}
            </span>
          </div>
          
          <div class="col-stats">
            <div class="stat-item">
              <span class="stat-label">用户:</span>
              <span class="stat-value">{{ tenant.users_count }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">项目:</span>
              <span class="stat-value">{{ tenant.projects_count }}</span>
            </div>
          </div>
          
          <div class="col-activity">
            <div class="last-login">
              {{ formatLastLogin(tenant.last_login_at) }}
            </div>
          </div>
          
          <div class="col-actions">
            <button @click="viewTenant(tenant)" class="action-btn view">
              查看
            </button>
            <button 
              @click="handleToggleStatus(tenant)" 
              :class="['action-btn', tenant.status === 'active' ? 'disable' : 'enable']"
            >
              {{ tenant.status === 'active' ? '禁用' : '启用' }}
            </button>
            <button @click="resetPassword(tenant)" class="action-btn reset">
              重置密码
            </button>
            <button 
              @click="deleteTenant(tenant)" 
              class="action-btn delete"
              :disabled="tenant.name === '监控系统'"
              :title="tenant.name === '监控系统' ? '不能删除监控系统租户' : '删除租户'"
            >
              删除
            </button>
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

    <!-- 租户详情模态框 -->
    <div v-if="showTenantModal" class="modal-overlay" @click="closeTenantModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>租户详情</h3>
          <button @click="closeTenantModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body" v-if="selectedTenant">
          <div class="tenant-info">
            <div class="info-group">
              <label>租户名称:</label>
              <span>{{ selectedTenant.name }}</span>
            </div>
            <div class="info-group">
              <label>邮箱:</label>
              <span>{{ selectedTenant.email }}</span>
            </div>
            <div class="info-group">
              <label>状态:</label>
              <span :class="['status-badge', selectedTenant.status]">
                {{ getStatusText(selectedTenant.status) }}
              </span>
            </div>
            <div class="info-group">
              <label>创建时间:</label>
              <span>{{ formatDate(selectedTenant.created_at) }}</span>
            </div>
            <div class="info-group">
              <label>最后登录:</label>
              <span>{{ formatLastLogin(selectedTenant.last_login_at) }}</span>
            </div>
          </div>
          
          <div class="tenant-users" v-if="selectedTenant.users">
            <h4>用户列表</h4>
            <div class="user-list">
              <div v-for="user in selectedTenant.users" :key="user.id" class="user-item">
                <div class="user-info">
                  <span class="user-email">{{ user.email }}</span>
                  <span :class="['user-role', user.role]">{{ user.role }}</span>
                  <span :class="['user-status', user.is_active ? 'active' : 'inactive']">
                    {{ user.is_active ? '活跃' : '禁用' }}
                  </span>
                </div>
                <div class="user-activity">
                  最后登录: {{ formatLastLogin(user.last_login_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作确认模态框 -->
    <div v-if="showConfirmModal" class="modal-overlay" @click="closeConfirmModal">
      <div class="modal-content confirm-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ confirmAction.title }}</h3>
        </div>
        
        <div class="modal-body">
          <p>{{ confirmAction.message }}</p>
          <div v-if="confirmAction.requiresReason" class="reason-input">
            <label>操作原因:</label>
            <textarea v-model="confirmAction.reason" placeholder="请输入操作原因..." rows="3"></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeConfirmModal" class="btn btn-cancel">取消</button>
          <button @click="executeAction" class="btn btn-confirm">确认</button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header">
          <h3>⚠️ 确认删除租户</h3>
          <button @click="closeDeleteModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="delete-warning">
            <p><strong>此操作不可逆！</strong></p>
            <p>您即将删除租户 <strong>{{ tenantToDelete?.name }}</strong></p>
            <p>删除后将永久丢失以下数据：</p>
            <ul>
              <li>所有用户账号 ({{ tenantToDelete?.users_count || 0 }} 个)</li>
              <li>所有项目数据 ({{ tenantToDelete?.projects_count || 0 }} 个)</li>
              <li>所有财务记录 ({{ tenantToDelete?.transactions_count || 0 }} 条)</li>
              <li>所有分类和供应商信息</li>
            </ul>
          </div>
          
          <div class="confirmation-input">
            <label for="delete-confirm">
              请输入租户名称 <strong>{{ tenantToDelete?.name }}</strong> 以确认删除：
            </label>
            <input
              id="delete-confirm"
              v-model="deleteConfirmation"
              type="text"
              placeholder="请输入租户名称"
              class="confirm-input"
            />
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn btn-cancel">
            取消
          </button>
          <button 
            @click="confirmDeleteTenant" 
            :disabled="deleteConfirmation !== tenantToDelete?.name || deleting"
            class="btn btn-confirm"
          >
            <span v-if="deleting">删除中...</span>
            <span v-else>确认删除</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import MonitoringNav from '@/components/MonitoringNav.vue'

export default {
  name: 'MonitoringTenants',
  components: {
    MonitoringNav
  },
  setup() {
    const authStore = useAuthStore()
    
    // 状态管理
    const loading = ref(false)
    const tenants = ref([])
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalPages = ref(1)
    const totalCount = ref(0)
    
    // 搜索和筛选
    const searchQuery = ref('')
    const statusFilter = ref('')
    const sortBy = ref('created_at')
    
    // 模态框状态
    const showTenantModal = ref(false)
    const showConfirmModal = ref(false)
    const selectedTenant = ref(null)
    const confirmAction = ref({})
    
    // 删除相关状态
    const showDeleteModal = ref(false)
    const tenantToDelete = ref(null)
    const deleteConfirmation = ref('')
    const deleting = ref(false)
    
    // 获取租户列表
    const fetchTenants = async () => {
      try {
        console.log('🔄 开始获取租户列表...')
        loading.value = true
        
        const params = new URLSearchParams({
          page: currentPage.value,
          size: pageSize.value
        })
        
        if (searchQuery.value) {
          params.append('search', searchQuery.value)
        }
        if (statusFilter.value) {
          params.append('status', statusFilter.value)
        }
        if (sortBy.value) {
          params.append('sort_by', sortBy.value)
        }
        
        const response = await fetch(`/api/v1/admin/tenants?${params}`, {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          console.log('📋 获取到租户数据:', data.tenants?.length || 0, '个租户')
          console.log('   租户数据:', data.tenants)
          
          tenants.value = data.tenants || []
          totalCount.value = data.pagination?.total || 0
          totalPages.value = data.pagination?.pages || 1
          
          console.log('✅ 租户列表更新完成')
          console.log('   当前tenants.value:', tenants.value)
          
          // 检查按钮是否正确渲染
          setTimeout(() => {
            const actionButtons = document.querySelectorAll('.action-btn')
            console.log(`🔍 渲染后找到 ${actionButtons.length} 个操作按钮`)
            
            // 检查启用/禁用按钮的状态
            tenants.value.forEach((tenant, tenantIndex) => {
              const enableDisableBtn = actionButtons[tenantIndex * 4 + 1] // 第二个按钮是启用/禁用按钮
              if (enableDisableBtn) {
                const expectedText = tenant.status === 'active' ? '禁用' : '启用'
                const actualText = enableDisableBtn.textContent.trim()
                console.log(`   租户 ${tenant.name}: 状态=${tenant.status}, 按钮文字="${actualText}", 期望="${expectedText}"`)
                
                if (actualText !== expectedText) {
                  console.log(`   ⚠️ 按钮文字不匹配!`)
                }
              }
            })
          }, 100)
        } else {
          console.error('获取租户列表失败:', response.status)
        }
      } catch (error) {
        console.error('获取租户列表错误:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 搜索处理
    const handleSearch = () => {
      currentPage.value = 1
      fetchTenants()
    }
    
    // 筛选处理
    const handleFilter = () => {
      currentPage.value = 1
      fetchTenants()
    }
    
    // 排序处理
    const handleSort = () => {
      currentPage.value = 1
      fetchTenants()
    }
    
    // 分页处理
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        fetchTenants()
      }
    }
    
    // 查看租户详情
    const viewTenant = async (tenant) => {
      try {
        const response = await fetch(`/api/v1/admin/tenants/${tenant.id}`, {
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          selectedTenant.value = data
          showTenantModal.value = true
        }
      } catch (error) {
        console.error('获取租户详情失败:', error)
      }
    }
    
    // 处理切换租户状态按钮点击
    const handleToggleStatus = (tenant) => {
      toggleTenantStatus(tenant)
    }
    
    // 切换租户状态
    const toggleTenantStatus = (tenant) => {
      const newStatus = tenant.status === 'active' ? 'disabled' : 'active'
      const action = newStatus === 'active' ? '启用' : '禁用'
      
      confirmAction.value = {
        type: 'toggle_status',
        title: `${action}租户`,
        message: `确定要${action}租户 "${tenant.name}" 吗？`,
        requiresReason: true,
        reason: '',
        tenant: tenant,
        newStatus: newStatus
      }
      
      showConfirmModal.value = true
    }
    
    // 重置密码
    const resetPassword = (tenant) => {
      confirmAction.value = {
        type: 'reset_password',
        title: '重置密码',
        message: `确定要重置租户 "${tenant.name}" 的密码吗？新密码将显示在结果中。`,
        requiresReason: false,
        tenant: tenant
      }
      
      showConfirmModal.value = true
    }
    
    // 执行确认操作
    const executeAction = async () => {
      try {
        if (confirmAction.value.type === 'toggle_status') {
          await updateTenantStatus()
        } else if (confirmAction.value.type === 'reset_password') {
          await resetTenantPassword()
        }
        
        closeConfirmModal()
        // 注意：fetchTenants() 已在各个操作函数中调用，这里不需要重复调用
      } catch (error) {
        console.error('❌ 执行操作失败:', error)
      }
    }
    
    // 更新租户状态
    const updateTenantStatus = async () => {
      const { tenant, newStatus, reason } = confirmAction.value
      
      console.log(`🔄 开始更新租户状态: ${tenant.name} -> ${newStatus}`)
      
      // 构建查询参数
      const params = new URLSearchParams({
        status: newStatus,
        reason: reason || ''
      })
      
      const response = await fetch(`/api/v1/admin/tenants/${tenant.id}/status?${params}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authStore.monitoringToken}`
        }
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '更新租户状态失败')
      }
      
      // 显示成功消息
      const result = await response.json()
      console.log('✅ 状态更新成功:', result)
      alert(`租户状态更新成功！\n\n租户: ${result.tenant_name}\n旧状态: ${result.old_status}\n新状态: ${result.new_status}\n原因: ${result.reason}`)
      
      // 刷新租户列表以更新状态显示
      console.log('🔄 开始刷新租户列表...')
      await fetchTenants()
      console.log('✅ 租户列表刷新完成')
      
      // 验证状态是否真的更新了
      console.log('🔍 验证状态更新...')
      const updatedTenant = tenants.value.find(t => t.id === tenant.id)
      if (updatedTenant) {
        console.log(`   租户 ${updatedTenant.name} 当前状态: ${updatedTenant.status}`)
        console.log(`   期望状态: ${newStatus}`)
        if (updatedTenant.status === newStatus) {
          console.log('✅ 状态验证成功!')
        } else {
          console.log('❌ 状态验证失败!')
        }
      }
    }
    
    // 重置租户密码
    const resetTenantPassword = async () => {
      const { tenant } = confirmAction.value
      
      const response = await fetch(`/api/v1/admin/tenants/${tenant.id}/reset-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.monitoringToken}`
        }
      })
      
      if (!response.ok) {
        throw new Error('重置密码失败')
      }
      
      const result = await response.json()
      alert(`密码重置成功！新密码: ${result.new_password}`)
      
      // 刷新租户列表
      await fetchTenants()
    }
    
    // 关闭模态框
    const closeTenantModal = () => {
      showTenantModal.value = false
      selectedTenant.value = null
    }
    
    const closeConfirmModal = () => {
      showConfirmModal.value = false
      confirmAction.value = {}
    }
    
    // 删除租户相关函数
    const deleteTenant = (tenant) => {
      tenantToDelete.value = tenant
      deleteConfirmation.value = ''
      showDeleteModal.value = true
    }
    
    const closeDeleteModal = () => {
      showDeleteModal.value = false
      tenantToDelete.value = null
      deleteConfirmation.value = ''
    }
    
    const confirmDeleteTenant = async () => {
      if (deleteConfirmation.value !== tenantToDelete.value?.name) {
        alert('请输入正确的租户名称以确认删除')
        return
      }
      
      try {
        deleting.value = true
        
        const response = await fetch(`/api/v1/admin/tenants/${tenantToDelete.value.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${authStore.monitoringToken}`
          }
        })
        
        if (response.ok) {
          const result = await response.json()
          alert(`租户删除成功！\n\n删除的租户: ${result.deleted_tenant.name}\n删除的数据:\n- 用户: ${result.deleted_tenant.users_count} 个\n- 项目: ${result.deleted_tenant.projects_count} 个\n- 财务记录: ${result.deleted_tenant.transactions_count} 条\n\n⚠️ 此操作不可逆，所有数据已被永久删除！`)
          
          // 关闭模态框并刷新数据
          closeDeleteModal()
          fetchTenants()
        } else {
          const error = await response.json()
          throw new Error(error.detail || '删除租户失败')
        }
      } catch (error) {
        alert(`删除租户失败: ${error.message}`)
      } finally {
        deleting.value = false
      }
    }
    
    // 刷新数据
    const refreshData = () => {
      fetchTenants()
    }
    
    // 工具函数
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    const formatLastLogin = (dateString) => {
      if (!dateString) return '从未登录'
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    const getStatusText = (status) => {
      const statusMap = {
        'active': '活跃',
        'disabled': '禁用'
      }
      return statusMap[status] || status
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
      console.log('🚀 MonitoringTenants组件已挂载')
      console.log('   组件状态:', {
        loading: loading.value,
        tenantsCount: tenants.value.length,
        showConfirmModal: showConfirmModal.value,
        showTenantModal: showTenantModal.value
      })
      
      fetchTenants()
      
      // 测试按钮事件绑定
      console.log('🔍 测试按钮事件绑定...')
      setTimeout(() => {
        const buttons = document.querySelectorAll('.action-btn')
        console.log(`   找到 ${buttons.length} 个操作按钮`)
        buttons.forEach((btn, index) => {
          console.log(`   按钮 ${index}:`, btn.textContent, btn.className)
        })
      }, 2000)
    })
    
    return {
      // 状态
      loading,
      tenants,
      currentPage,
      totalPages,
      totalCount,
      searchQuery,
      statusFilter,
      sortBy,
      showTenantModal,
      showConfirmModal,
      selectedTenant,
      confirmAction,
      showDeleteModal,
      tenantToDelete,
      deleteConfirmation,
      deleting,
      
      // 方法
      fetchTenants,
      handleSearch,
      handleFilter,
      handleSort,
      changePage,
      viewTenant,
      handleToggleStatus,
      toggleTenantStatus,
      resetPassword,
      deleteTenant,
      confirmDeleteTenant,
      closeDeleteModal,
      executeAction,
      closeTenantModal,
      closeConfirmModal,
      refreshData,
      
      // 工具函数
      formatDate,
      formatLastLogin,
      getStatusText,
      visiblePages
    }
  }
}
</script>

<style scoped>
.monitoring-tenants {
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

.tenants-table {
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
  grid-template-columns: 2fr 2fr 1fr 1.5fr 1.5fr 2fr;
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

.tenant-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.tenant-id {
  font-size: 12px;
  color: #999;
}

.email {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.created-at {
  font-size: 12px;
  color: #666;
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

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.disabled {
  background: #f8d7da;
  color: #721c24;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 12px;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: 600;
  color: #333;
}

.last-login {
  font-size: 12px;
  color: #666;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 8px;
  margin-bottom: 4px;
}

.action-btn.view {
  background: #17a2b8;
  color: white;
}

.action-btn.enable {
  background: #28a745;
  color: white;
}

.action-btn.disable {
  background: #dc3545;
  color: white;
}

.action-btn.reset {
  background: #ffc107;
  color: #212529;
}

.action-btn:hover {
  opacity: 0.8;
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
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.confirm-modal {
  max-width: 500px;
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

.tenant-info {
  margin-bottom: 24px;
}

.info-group {
  display: flex;
  margin-bottom: 12px;
}

.info-group label {
  width: 100px;
  font-weight: 600;
  color: #666;
}

.info-group span {
  color: #333;
}

.tenant-users h4 {
  margin: 0 0 16px 0;
  color: #333;
}

.user-item {
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 8px;
}

.user-info {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.user-email {
  font-weight: 500;
  color: #333;
}

.user-role {
  padding: 2px 8px;
  background: #e9ecef;
  color: #495057;
  border-radius: 12px;
  font-size: 12px;
}

.user-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.user-status.active {
  background: #d4edda;
  color: #155724;
}

.user-status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.user-activity {
  font-size: 12px;
  color: #666;
}

.reason-input {
  margin-top: 16px;
}

.reason-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.reason-input textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-cancel {
  background: #6c757d;
  color: white;
}

.btn-confirm {
  background: #dc3545;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}

@media (max-width: 768px) {
  .monitoring-tenants {
    padding: 16px;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .header-row {
    display: none;
  }
  
  .col-name, .col-email, .col-status, .col-stats, .col-activity, .col-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .col-name::before { content: "租户名称: "; font-weight: 600; }
  .col-email::before { content: "邮箱: "; font-weight: 600; }
  .col-status::before { content: "状态: "; font-weight: 600; }
  .col-stats::before { content: "统计: "; font-weight: 600; }
  .col-activity::before { content: "活跃度: "; font-weight: 600; }
  .col-actions::before { content: "操作: "; font-weight: 600; }
}
</style>
