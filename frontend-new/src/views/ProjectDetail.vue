<template>
  <div class="project-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" type="text" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回项目列表
        </el-button>
        <h1>项目详情</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="goToEdit">
          <el-icon><Edit /></el-icon>
          编辑项目
        </el-button>
        <el-button type="danger" @click="deleteProject" :loading="deleting" :disabled="deleting">
          <el-icon><Delete /></el-icon>
          {{ deleting ? '删除中...' : '删除项目' }}
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 项目详情内容 -->
    <div v-else-if="project" class="project-content">
      <!-- 基本信息卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <div class="header-actions">
              <span class="sync-status" :class="{ 'syncing': loading }">
                {{ loading ? '同步中...' : '数据已同步' }}
              </span>
              <el-button type="text" @click="refreshData" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>
        
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :md="8">
            <div class="info-item">
              <label>项目名称:</label>
              <span>{{ project.name }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="info-item">
              <label>项目编号:</label>
              <span>{{ project.project_code }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="info-item">
              <label>项目类型:</label>
              <span>{{ getProjectTypeText(project.project_type) }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="info-item">
              <label>项目状态:</label>
              <el-tag :type="getStatusType(project.status)" size="large">
                {{ getStatusText(project.status) }}
              </el-tag>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="info-item">
              <label>项目经理:</label>
              <span>{{ project.manager_name }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="info-item">
              <label>创建时间:</label>
              <span>{{ formatDate(project.created_at) }}</span>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 财务信息卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>财务信息</span>
          </div>
        </template>
        
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :md="6">
            <div class="financial-item">
              <div class="financial-label">预算金额</div>
              <div class="financial-value budget">￥{{ formatAmount(project.budget) }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="financial-item">
              <div class="financial-label">合同金额</div>
              <div class="financial-value contract">￥{{ formatAmount(project.contract_amount) }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="financial-item">
              <div class="financial-label">实际支出</div>
              <div class="financial-value expenses">￥{{ formatAmount(project.actual_expenses || 0) }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="financial-item">
              <div class="financial-label">预算利润</div>
              <div class="financial-value" :class="getProfitClass(project.budget, project.contract_amount)">
                ￥{{ formatAmount(calculateProfit(project.budget, project.contract_amount)) }}
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="financial-item">
              <div class="financial-label">实际利润</div>
              <div class="financial-value" :class="getProfitClass(project.actual_expenses || 0, project.contract_amount)">
                ￥{{ formatAmount(calculateActualProfit(project.actual_expenses || 0, project.contract_amount)) }}
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="financial-item">
              <div class="financial-label">利润率</div>
              <div class="financial-value" :class="getProfitClass(project.budget, project.contract_amount)">
                {{ calculateProfitRate(project.budget, project.contract_amount) }}%
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 时间信息卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>时间信息</span>
          </div>
        </template>
        
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :md="8">
            <div class="time-item">
              <div class="time-label">项目开始时间</div>
              <div class="time-value">{{ formatDate(project.start_date) }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="time-item">
              <div class="time-label">项目计划结束时间</div>
              <div class="time-value">{{ formatDate(project.planned_end_date || project.end_date) }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="time-item">
              <div class="time-label">项目进度</div>
              <div class="progress-display">
                <el-progress 
                  :percentage="calculateProgress(project.start_date, project.planned_end_date || project.end_date, project.status)" 
                  :color="getProgressColor(project.start_date, project.planned_end_date || project.end_date, project.status)"
                  :stroke-width="12"
                  :show-text="false"
                  :status="getProgressStatus(project.start_date, project.planned_end_date || project.end_date, project.status)"
                />
                <span class="progress-text">
                  {{ calculateProgress(project.start_date, project.planned_end_date || project.end_date, project.status) }}%
                </span>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 项目描述卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>项目描述</span>
          </div>
        </template>
        
        <div class="description-content">
          {{ project.description || '暂无项目描述' }}
        </div>
      </el-card>

      <!-- 项目变更记录卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>项目变更记录</span>
            <el-button type="text" @click="loadChangeLogs" :loading="changeLogsLoading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        
        <div v-if="changeLogsLoading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="changeLogs.length === 0" class="empty-logs">
          <el-empty description="暂无变更记录" />
        </div>
        
        <div v-else class="change-records-list">
          <div v-for="log in changeLogs" :key="log.id" class="change-record-item">
            <div class="record-header">
              <div class="record-time">
                <strong>日期：</strong>{{ formatDateTime(log.created_at) }}
              </div>
              <div class="record-user">
                <strong>用户：</strong>{{ getCurrentUserName() }}
              </div>
            </div>
            <div class="record-content">
              <div class="record-title">
                <strong>变更内容：</strong>
              </div>
              <div class="record-details">
                {{ log.change_record || '项目信息已更新' }}
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 项目统计卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>项目统计</span>
          </div>
        </template>
        
        <el-row :gutter="24">
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ getDaysRemaining(project.start_date, project.planned_end_date || project.end_date) }}</div>
                <div class="stat-label">剩余天数</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ getBudgetUtilization(project.budget, project.actual_expenses) }}%</div>
                <div class="stat-label">预算使用率</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ getCostEfficiency(project.contract_amount, project.actual_expenses) }}%</div>
                <div class="stat-label">成本效率</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ getCompletionRate(project.start_date, project.planned_end_date || project.end_date, project.status) }}%</div>
                <div class="stat-label">完成率</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 项目不存在提示 -->
    <div v-else class="not-found">
      <el-empty description="项目不存在或已被删除">
        <el-button type="primary" @click="goBack">返回项目列表</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Delete, Clock, TrendCharts, Money, Check, Refresh } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const deleting = ref(false)
const project = ref(null)
const changeLogs = ref([])
const changeLogsLoading = ref(false)

// 定时刷新间隔（毫秒）
const REFRESH_INTERVAL = 30000 // 30秒

// 定时器引用
let refreshTimer = null

// 生命周期
onMounted(() => {
  loadProjectDetail()
  loadChangeLogs()
  
  // 启动定时刷新
  startAutoRefresh()
  
  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  // 清理定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  
  // 移除事件监听器
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

// 启动自动刷新
const startAutoRefresh = () => {
  refreshTimer = setInterval(async () => {
          // 只在页面可见时刷新
      if (!document.hidden) {
        await loadProjectDetail()
        await loadChangeLogs()
      }
  }, REFRESH_INTERVAL)
}

// 监听路由变化，当从编辑页面返回时刷新数据
onMounted(() => {
  // 监听路由变化
  const unwatch = router.beforeEach((to, from, next) => {
    // 如果从编辑页面返回到详情页面，立即刷新数据
    if (to.name === 'ProjectDetail' && from.name === 'EditProject') {
      nextTick(() => {
        loadProjectDetail()
        loadChangeLogs()
      })
    }
    next()
  })
  
  // 组件卸载时取消监听
  onUnmounted(() => {
    unwatch()
  })
})

const handleVisibilityChange = async () => {
  if (!document.hidden) {
    await loadProjectDetail()
    await loadChangeLogs()
  }
}

// 加载项目详情
const loadProjectDetail = async () => {
  try {
    loading.value = true
    const projectId = route.params.id
    
    // 加载项目详情
    
    // 调用API获取项目详情
    const response = await fetch(`/api/v1/projects/${projectId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      if (response.status === 404) {
        ElMessage.error('项目不存在或已删除')
        project.value = null
        return
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const projectData = await response.json()
    
    project.value = projectData
    
    // 项目数据加载完成
    
  } catch (error) {
    console.error('加载项目详情失败:', error)
    ElMessage.error('加载项目详情失败')
    project.value = null
  } finally {
    loading.value = false
  }
}

// 加载项目变更日志
const loadChangeLogs = async () => {
  try {
    changeLogsLoading.value = true
    const projectId = route.params.id
    
    // 加载项目变更日志
    
    const response = await fetch(`/api/v1/projects/${projectId}/change-logs`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      if (response.status === 404) {
        console.log('项目变更日志API不存在，跳过加载')
        changeLogs.value = []
        return
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const logsData = await response.json()
    
    changeLogs.value = logsData
    
  } catch (error) {
    console.error('加载项目变更日志失败:', error)
    changeLogs.value = []
  } finally {
    changeLogsLoading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
      // 手动刷新项目数据
  await loadProjectDetail()
  await loadChangeLogs()
  
  // 检查数据一致性
  checkDataConsistency()
}

    // 数据一致性检查（生产环境可移除）

// 返回项目列表
const goBack = () => {
  router.push('/projects')
}

// 跳转到编辑页面
const goToEdit = () => {
  router.push(`/projects/${project.value.id}/edit`)
}

// 删除项目
const deleteProject = async () => {
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要删除项目"${project.value.name}"吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
    
    // 显示删除中状态
    deleting.value = true
    
    // 开始删除项目
    console.log('DEBUG: 项目状态:', project.value.status)
    
    // 调用删除API
    const response = await fetch(`/api/v1/projects/${project.value.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      let errorMessage = `删除失败，状态码: ${response.status}`
      
      try {
        const errorData = await response.json()
        if (errorData.detail) {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        }
      } catch (parseError) {
        console.warn('无法解析错误响应:', parseError)
      }
      
      if (response.status === 404) {
        throw new Error('项目不存在或已被删除')
      } else if (response.status === 403) {
        throw new Error('没有权限删除此项目')
      } else if (response.status === 422) {
        throw new Error(`数据验证失败: ${errorMessage}`)
      } else {
        throw new Error(errorMessage)
      }
    }
    
    // 项目删除成功
    
    // 显示成功消息
    ElMessage.success('项目删除成功')
    
    // 返回项目列表页面
    goBack()
    
  } catch (error) {
    console.error('删除项目失败:', error)
    
    if (error.message === '用户取消') {
      // 用户取消删除，不显示错误消息
      return
    }
    
    // 显示错误消息
    ElMessage.error(`删除项目失败: ${error.message}`)
  } finally {
    deleting.value = false
  }
}

// 工具方法
const getStatusType = (status) => {
  const statusMap = {
    'planning': 'info',
    'in_progress': 'primary',
    'on_hold': 'warning',
    'completed': 'success',
    'delayed': 'danger',
    'cancelled': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'planning': '规划中',
    'in_progress': '进行中',
    'on_hold': '暂停',
    'completed': '已完成',
    'delayed': '延期',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const getProjectTypeText = (projectType) => {
  const typeMap = {
    'construction': '建筑工程',
    'decoration': '装饰工程',
    'municipal': '市政工程',
    'electrical': '电气工程',
    'mechanical': '机械工程',
    'industrial': '工业工程',
    'residential': '住宅工程',
    'commercial': '商业工程',
    'infrastructure': '基础设施工程',
    'renovation': '改造工程',
    'maintenance': '维护工程',
    'other': '其他工程'
  }
  return typeMap[projectType] || projectType || '未设置'
}

const formatAmount = (num) => {
  if (!num) return '0万'
  const wan = num / 10000
  if (wan === Math.floor(wan)) {
    return `${wan}万`
  } else {
    return `${wan.toFixed(1)}万`
  }
}

const calculateProfit = (budget, contractAmount) => {
  if (!budget || !contractAmount) return 0
  return contractAmount - budget
}

const calculateActualProfit = (actualExpenses, contractAmount) => {
  if (!actualExpenses || !contractAmount) return 0
  return contractAmount - actualExpenses
}

const getProfitClass = (budget, contractAmount) => {
  const profit = contractAmount - budget
  if (profit > 0) return 'profit-positive'
  if (profit < 0) return 'profit-negative'
  return 'profit-zero'
}

const calculateProfitRate = (budget, contractAmount) => {
  if (!budget || !contractAmount) return 0
  return ((contractAmount - budget) / budget * 100).toFixed(1)
}

const calculateProgress = (startDate, endDate, status) => {
  if (!startDate || !endDate) return 0
  if (status === 'completed') return 100
  
  const start = new Date(startDate)
  const end = new Date(endDate)
  const now = new Date()
  
  if (now < start) return 0
  if (now > end) return Math.min(120, Math.round(((now - start) / (end - start)) * 100))
  
  return Math.round(((now - start) / (end - start)) * 100)
}

const getProgressColor = (startDate, endDate, status) => {
  if (status === 'completed') return '#67c23a'
  
  const progress = calculateProgress(startDate, endDate, status)
  if (progress >= 100) return '#f56c6c'
  if (progress >= 80) return '#e6a23c'
  if (progress >= 50) return '#409eff'
  return '#909399'
}

const getProgressStatus = (startDate, endDate, status) => {
  if (status === 'completed') return 'success'
  
  const progress = calculateProgress(startDate, endDate, status)
  if (progress >= 100) return 'exception'
  if (progress >= 80) return 'warning'
  return 'normal'
}

const formatDate = (date) => {
  if (!date) return '未设置'
  
  try {
    const dateObj = new Date(date)
    if (isNaN(dateObj.getTime())) {
      console.warn('无效的日期格式:', date)
      return '日期格式错误'
    }
    return dateObj.toLocaleDateString('zh-CN')
  } catch (error) {
    console.error('格式化日期时出错:', error)
    return '日期格式错误'
  }
}

const formatDateTime = (date) => {
  if (!date) return '未设置'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getCurrentUserName = () => {
  // 从localStorage获取当前用户名，如果没有则显示默认值
  return localStorage.getItem('username') || '系统用户'
}

const getDaysRemaining = (startDate, endDate) => {
  if (!startDate || !endDate) return 0
  const end = new Date(endDate)
  const now = new Date()
  const diff = end - now
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

const getBudgetUtilization = (budget, actualExpenses) => {
  if (!budget || !actualExpenses) return 0
  return Math.min(100, Math.round((actualExpenses / budget) * 100))
}

const getCostEfficiency = (contractAmount, actualExpenses) => {
  if (!contractAmount || !actualExpenses) return 0
  return Math.min(100, Math.round((actualExpenses / contractAmount) * 100))
}

const getCompletionRate = (startDate, endDate, status) => {
  if (status === 'completed') return 100
  return calculateProgress(startDate, endDate, status)
}

// 获取变更类型颜色
const getChangeTypeColor = (changeType) => {
  const colorMap = {
    'create': 'success',
    'update': 'warning',
    'delete': 'danger',
    'status_change': 'info',
    'budget_change': 'warning',
    'schedule_change': 'info'
  }
  return colorMap[changeType] || 'info'
}

// 获取变更类型文本
const getChangeTypeText = (changeType) => {
  const textMap = {
    'create': '创建',
    'update': '更新',
    'delete': '删除',
    'status_change': '状态变更',
    'budget_change': '预算变更',
    'schedule_change': '进度变更'
  }
  return textMap[changeType] || changeType
}
</script>

<style scoped>
.project-detail-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-button {
  font-size: 16px;
  color: #409eff;
}

.back-button:hover {
  color: #66b1ff;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.loading-container {
  padding: 40px;
}

.project-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card {
  margin-bottom: 0;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.info-item {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.info-item span {
  color: #303133;
  font-size: 16px;
}

.financial-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
  margin-bottom: 16px;
}

.financial-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.financial-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.financial-value.budget {
  color: #409eff;
}

.financial-value.contract {
  color: #67c23a;
}

.financial-value.expenses {
  color: #e6a23c;
}

.financial-value.profit-positive {
  color: #67c23a;
}

.financial-value.profit-negative {
  color: #f56c6c;
}

.financial-value.profit-zero {
  color: #909399;
}

.time-item {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.time-value {
  color: #303133;
  font-size: 16px;
}

.progress-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-text {
  font-size: 14px;
  color: #606266;
  min-width: 40px;
}

.description-content {
  color: #303133;
  font-size: 16px;
  line-height: 1.6;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  min-height: 80px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.stat-icon {
  font-size: 32px;
  color: #409eff;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.not-found {
  text-align: center;
  padding: 60px 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .project-detail-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: stretch;
  }
  
  .header-actions .el-button {
    flex: 1;
  }
  
  .info-card {
    margin-bottom: 16px;
  }
  
  .financial-item {
    padding: 16px;
  }
  
  .financial-value {
    font-size: 18px;
  }
  
  .stat-item {
    padding: 16px;
  }
  
  .stat-icon {
    font-size: 28px;
    margin-right: 12px;
  }
  
  .stat-number {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .project-detail-container {
    padding: 12px;
  }
  
  .page-header h1 {
    font-size: 20px;
  }
  
  .financial-item {
    padding: 12px;
  }
  
  .financial-value {
    font-size: 16px;
  }
  
  .stat-item {
    padding: 12px;
  }
  
  .stat-icon {
    font-size: 24px;
    margin-right: 8px;
  }
  
  .stat-number {
    font-size: 18px;
  }
}

/* iPhone 安全区域适配 */
@supports (padding: max(0px)) {
  .project-detail-container {
    padding-left: max(20px, env(safe-area-inset-left));
    padding-right: max(20px, env(safe-area-inset-right));
  }
}

/* 变更记录样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sync-status {
  font-size: 12px;
  color: #67c23a;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #f0f9ff;
  border: 1px solid #e1f3d8;
}

.sync-status.syncing {
  color: #e6a23c;
  background-color: #fdf6ec;
  border-color: #f5dab1;
}

.change-records-list {
  max-height: 400px;
  overflow-y: auto;
}

.change-record-item {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 16px;
  background: #fafafa;
}

.change-record-item:last-child {
  margin-bottom: 0;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.record-time {
  color: #303133;
  font-size: 14px;
}

.record-user {
  color: #409eff;
  font-size: 14px;
}

.record-content {
  font-size: 14px;
  line-height: 1.8;
}

.record-title {
  margin-bottom: 12px;
  color: #303133;
  font-weight: 600;
}

.record-details {
  color: #606266;
  white-space: pre-line;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.empty-logs {
  padding: 40px 20px;
}
</style>
