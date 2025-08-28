<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>仪表盘</h1>
      <p>欢迎回来，{{ username }}</p>
    </div>
    
    <!-- 核心统计数据 -->
    <div class="dashboard-stats">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="8" :md="6" :lg="6" :xl="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Folder /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.totalProjects }}</div>
                <div class="stat-label">项目总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="12" :sm="8" :md="6" :lg="6" :xl="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.completedProjects }}</div>
                <div class="stat-label">已完工项目</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="12" :sm="8" :md="6" :lg="6" :xl="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.ongoingProjects }}</div>
                <div class="stat-label">进行中项目</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="12" :sm="8" :md="6" :lg="6" :xl="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.delayedProjects }}</div>
                <div class="stat-label">延期项目</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12">
          <el-card class="stat-card budget-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number budget-amount">¥{{ formatNumber(stats.totalBudget) }}</div>
                <div class="stat-label">总预算</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12">
          <el-card class="stat-card contract-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number contract-amount">¥{{ formatNumber(stats.totalContractAmount) }}</div>
                <div class="stat-label">总合同金额</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 财务数据 -->
    <div class="financial-stats">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
          <el-card class="financial-card">
            <div class="financial-content">
              <div class="financial-icon income">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number income-amount">¥{{ formatNumber(stats.totalIncome) }}</div>
                <div class="stat-label">总收入</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
          <el-card class="financial-card">
            <div class="financial-content">
              <div class="financial-icon expense">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number expense-amount">¥{{ formatNumber(stats.totalExpense) }}</div>
                <div class="stat-label">总支出</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
          <el-card class="financial-card">
            <div class="financial-content">
              <div class="financial-icon profit">
                <el-icon><Wallet /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number" :class="getProfitClass(stats.netProfit)">
                  ¥{{ formatNumber(stats.netProfit) }}
                </div>
                <div class="stat-label">净利润</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
          <el-card class="financial-card">
            <div class="financial-content">
              <div class="financial-icon">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.totalTransactions }}</div>
                <div class="stat-label">交易笔数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 图表和详细数据 -->
    <div class="dashboard-content">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>项目状态分布</span>
                <el-button type="text" size="small" @click="refreshChartData">刷新</el-button>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="projectStatusOption" />
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>月度项目趋势</span>
                <el-select v-model="trendPeriod" size="small" style="width: 120px;" @change="loadChartData">
                  <el-option label="近6个月" value="6" />
                  <el-option label="近12个月" value="12" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="monthlyTrendOption" />
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>项目类型分布</span>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="projectTypeOption" />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>项目进度分布</span>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="projectProgressOption" />
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="recent-projects-card">
            <template #header>
              <div class="card-header">
                <span>最近项目</span>
                <el-button type="text" size="small" @click="viewAllProjects">查看全部</el-button>
              </div>
            </template>
            
            <el-table :data="recentProjects" style="width: 100%" v-loading="loading">
              <el-table-column prop="name" label="项目名称" min-width="200" />
              <el-table-column prop="project_type" label="项目类型" width="120">
                <template #default="scope">
                  {{ getProjectTypeText(scope.row.project_type) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)" size="small">
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="budget" label="预算" width="120">
                <template #default="scope">
                  ¥{{ formatNumber(scope.row.budget) }}
                </template>
              </el-table-column>
              <el-table-column prop="progress" label="进度" width="120">
                <template #default="scope">
                  <el-progress :percentage="scope.row.progress || 0" :color="getProgressColor(scope.row.progress)" />
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="scope">
                  <el-button type="text" size="small" @click="viewProject(scope.row.id)">查看</el-button>
                </template>
              </el-table-column>
              
              <!-- 空状态显示 -->
              <template #empty>
                <div class="empty-projects">
                  <el-empty description="暂无项目数据" :image-size="80">
                    <el-button type="primary" @click="viewAllProjects">查看所有项目</el-button>
                  </el-empty>
                </div>
              </template>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Folder, Check, Clock, Warning, TrendCharts, Money, 
  Document, Wallet, DataAnalysis 
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()
const loading = ref(false)
const trendPeriod = ref('6')

// 响应式数据
const stats = reactive({
  totalProjects: 0,
  completedProjects: 0,
  ongoingProjects: 0,
  delayedProjects: 0,
  totalBudget: 0,
  totalContractAmount: 0,
  totalIncome: 0,
  totalExpense: 0,
  netProfit: 0,
  totalTransactions: 0
})

const chartData = reactive({
  projectStatus: [],
  monthlyTrend: [],
  projectTypes: [],
  projectProgress: []
})

const recentProjects = ref([])

// 用户名
const username = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.name || '用户'
})

// 图表配置
const projectStatusOption = computed(() => {
  const data = chartData.projectStatus || []
  
  return {
    title: {
      text: '项目状态分布',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}个 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: data.length > 0 ? data : [{ name: '暂无数据', value: 1, itemStyle: { color: '#909399' } }],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

const monthlyTrendOption = computed(() => {
  const data = chartData.monthlyTrend || []
  
  return {
    title: {
      text: '月度项目趋势',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['项目数量', '预算金额'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.length > 0 ? data.map(item => item.month) : ['暂无数据']
    },
    yAxis: [
      {
        type: 'value',
        name: '项目数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '预算金额',
        position: 'right',
        axisLabel: {
          formatter: '¥{value}'
        }
      }
    ],
    series: [
      {
        name: '项目数量',
        type: 'line',
        data: data.length > 0 ? data.map(item => item.projects) : [0],
        itemStyle: { color: '#409eff' },
        smooth: true
      },
      {
        name: '预算金额',
        type: 'bar',
        yAxisIndex: 1,
        data: data.length > 0 ? data.map(item => item.budget) : [0],
        itemStyle: { color: '#67c23a' }
      }
    ]
  }
})

const projectTypeOption = computed(() => {
  const data = chartData.projectTypes || []
  
  return {
    title: {
      text: '项目类型分布',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}个 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: data.length > 0 ? data : [{ name: '暂无数据', value: 1, itemStyle: { color: '#909399' } }],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

const projectProgressOption = computed(() => {
  const data = chartData.projectProgress || []
  
  return {
    title: {
      text: '项目进度分布',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.length > 0 ? data.map(item => item.range) : ['暂无数据']
    },
    yAxis: {
      type: 'value',
      name: '项目数量'
    },
    series: [
      {
        name: '项目数量',
        type: 'bar',
        data: data.length > 0 ? data.map(item => item.count) : [0],
        itemStyle: { color: '#409eff' }
      }
    ]
  }
})

// 方法
const getStatusText = (status) => {
  const statusMap = {
    'planning': '规划中',
    'in_progress': '进行中',
    'on_hold': '暂停',
    'completed': '已完成',
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

const getStatusType = (status) => {
  const typeMap = {
    'planning': 'info',
    'in_progress': 'primary',
    'on_hold': 'warning',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return typeMap[status] || 'info'
}

const getProgressColor = (progress) => {
  if (progress >= 80) return '#67c23a'
  if (progress >= 50) return '#e6a23c'
  if (progress >= 20) return '#f56c6c'
  return '#909399'
}

const getProfitClass = (profit) => {
  if (profit >= 0) return 'profit-positive'
  return 'profit-negative'
}

const formatNumber = (num) => {
  if (!num) return '0.00'
  
  const number = Number(num)
  
  // 对于超大数额，使用更紧凑的显示方式
  if (number >= 100000000) {
    // 大于等于1亿，显示为"X.XX亿"
    return (number / 100000000).toFixed(2) + '亿'
  } else if (number >= 10000) {
    // 大于等于1万，显示为"X.XX万"
    return (number / 10000).toFixed(2) + '万'
  } else {
    // 小于1万，使用标准格式
    return number.toLocaleString('zh-CN', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const viewProject = (projectId) => {
  router.push(`/projects/${projectId}`)
}

const viewAllProjects = () => {
  router.push('/projects')
}

const refreshChartData = () => {
  loadChartData()
}

// 加载仪表板数据
const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // 调用项目统计API
    const projectsResponse = await fetch('/api/v1/projects/statistics', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (projectsResponse.ok) {
      const projectsData = await projectsResponse.json()
      
      // 更新项目统计数据
      stats.totalProjects = projectsData.total_projects || 0
      stats.completedProjects = projectsData.completed_projects || 0
      stats.ongoingProjects = projectsData.ongoing_projects || 0
      stats.delayedProjects = projectsData.delayed_projects || 0
      stats.totalBudget = projectsData.total_budget || 0
      stats.totalContractAmount = projectsData.total_contract_amount || 0
    }
    
    // 调用财务统计API
    const financeResponse = await fetch('/api/v1/transactions/statistics/overview', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (financeResponse.ok) {
      const financeData = await financeResponse.json()
      
      // 更新财务统计数据
      stats.totalIncome = financeData.total_income || 0
      stats.totalExpense = financeData.total_expense || 0
      stats.netProfit = financeData.net_amount || 0
      stats.totalTransactions = financeData.total_transactions || 0
    }
    
    // 加载最近项目
    const recentResponse = await fetch('/api/v1/projects/?skip=0&limit=10', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (recentResponse.ok) {
      const recentData = await recentResponse.json()
      console.log('最近项目API响应:', recentData)
      recentProjects.value = recentData.projects || []
      console.log('最近项目数据已设置:', recentProjects.value)
    } else {
      console.error('加载最近项目失败:', recentResponse.status, recentResponse.statusText)
    }
    
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
    ElMessage.error('加载仪表板数据失败')
  } finally {
    loading.value = false
  }
}

// 加载图表数据
const loadChartData = async () => {
  try {
    loading.value = true
    
    // 调用项目状态分布API
    const statusResponse = await fetch('/api/v1/projects/statistics/status', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (statusResponse.ok) {
      const statusData = await statusResponse.json()
      chartData.projectStatus = statusData.status_distribution || []
    }
    
    // 调用月度趋势API
    const trendResponse = await fetch(`/api/v1/projects/statistics/trend?months=${trendPeriod.value}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (trendResponse.ok) {
      const trendData = await trendResponse.json()
      chartData.monthlyTrend = trendData.monthly_trend || []
    }
    
    // 调用项目类型分布API
    const typeResponse = await fetch('/api/v1/projects/statistics/types', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (typeResponse.ok) {
      const typeData = await typeResponse.json()
      chartData.projectTypes = typeData.type_distribution || []
    }
    
    // 调用项目进度分布API
    const progressResponse = await fetch('/api/v1/projects/statistics/progress', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (progressResponse.ok) {
      const progressData = await progressResponse.json()
      chartData.projectProgress = progressData.progress_distribution || []
    }
    
  } catch (error) {
    console.error('加载图表数据失败:', error)
    ElMessage.error('加载图表数据失败')
  } finally {
    loading.value = false
  }
}

// 监听趋势周期变化
watch(trendPeriod, () => {
  loadChartData()
})

// 生命周期
onMounted(async () => {
  await loadDashboardData()
  await loadChartData()
})
</script>

<style scoped>
.dashboard-container {
  /* 移除padding，因为现在在布局组件中显示 */
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  color: #333;
  margin-bottom: 10px;
}

.dashboard-header p {
  color: #666;
  font-size: 16px;
}

.dashboard-stats {
  margin-bottom: 30px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  font-size: 48px;
  color: #409eff;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
  word-break: break-all;
  line-height: 1.2;
}

/* 大数额专用样式 */
.budget-card .stat-number,
.contract-card .stat-number {
  font-size: 20px;
  line-height: 1.3;
  word-break: break-word;
  hyphens: auto;
}

/* 超长数字的响应式处理 */
@media (max-width: 1200px) {
  .budget-card .stat-number,
  .contract-card .stat-number {
    font-size: 18px;
  }
}

@media (max-width: 992px) {
  .budget-card .stat-number,
  .contract-card .stat-number {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .budget-card .stat-number,
  .contract-card .stat-number {
    font-size: 14px;
  }
  
  .budget-card,
  .contract-card {
    height: auto;
    min-height: 100px;
  }
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.financial-stats {
  margin-bottom: 30px;
}

.financial-card {
  height: 120px;
}

.financial-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.financial-icon {
  font-size: 48px;
  color: #67c23a;
  margin-right: 20px;
}

.financial-icon.income {
  color: #409eff; /* 收入图标颜色 */
}

.financial-icon.expense {
  color: #f56c6c; /* 支出图标颜色 */
}

.financial-icon.profit {
  color: #67c23a; /* 利润图标颜色 */
}

.financial-info {
  flex: 1;
}

.financial-number {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.financial-number.profit-positive {
  color: #67c23a;
}

.financial-number.profit-negative {
  color: #f56c6c;
}

.financial-label {
  color: #666;
  font-size: 14px;
}

.dashboard-content {
  margin-bottom: 30px;
}

.chart-card {
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #333;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart {
  width: 100%;
  height: 100%;
}

.recent-projects-card {
  height: 400px;
}

.recent-projects {
  height: 300px;
  overflow-y: auto;
}

.empty-projects {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.project-list {
  padding: 0;
}

.project-item {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.project-item:hover {
  background-color: #f5f7fa;
}

.project-item:last-child {
  border-bottom: none;
}

.project-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.project-name {
  font-weight: 500;
  color: #333;
}

.project-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.project-type {
  background-color: #f0f0f0;
  padding: 2px 8px;
  border-radius: 10px;
}

.project-budget {
  color: #409eff;
  font-weight: 500;
}

/* 移动端响应式优化 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .dashboard-header {
    margin-bottom: 20px;
  }
  
  .dashboard-header h1 {
    font-size: 20px;
    margin-bottom: 8px;
  }
  
  .dashboard-header p {
    font-size: 14px;
  }
  
  .dashboard-stats .el-col {
    margin-bottom: 16px;
  }
  
  .dashboard-stats .el-row {
    margin-bottom: 0;
  }
  
  .stat-card {
    height: 100px;
  }
  
  .stat-icon {
    font-size: 32px;
    margin-right: 16px;
  }
  
  .stat-number {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .financial-stats .el-col {
    margin-bottom: 16px;
  }
  
  .financial-stats .el-row {
    margin-bottom: 0;
  }
  
  .chart-card {
    height: 300px;
    margin-bottom: 16px;
  }
  
  .chart-container {
    height: 200px;
  }
  
  .recent-projects-card {
    height: 300px;
  }
  
  .recent-projects {
    height: 200px;
  }
}

@media (max-width: 480px) {
  .dashboard-container {
    padding: 12px;
  }
  
  .dashboard-header h1 {
    font-size: 18px;
  }
  
  .dashboard-header p {
    font-size: 13px;
  }
  
  .stat-card {
    height: 90px;
  }
  
  .stat-icon {
    font-size: 28px;
    margin-right: 12px;
  }
  
  .stat-number {
    font-size: 18px;
  }
  
  .stat-label {
    font-size: 11px;
  }
  
  .chart-card {
    height: 250px;
  }
  
  .chart-container {
    height: 150px;
  }
  
  .recent-projects-card {
    height: 250px;
  }
  
  .recent-projects {
    height: 150px;
  }
}

/* iPhone 安全区域适配 */
@supports (padding: max(0px)) {
  .dashboard-container {
    padding-left: max(12px, env(safe-area-inset-left));
    padding-right: max(12px, env(safe-area-inset-right));
  }
}
</style>

