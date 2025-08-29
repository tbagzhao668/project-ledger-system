<template>
  <div class="reports-container">
    <div class="page-header">
      <h1>财务统计</h1>
      <p>财务数据可视化分析和报表</p>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon income">💰</div>
              <div class="stat-info">
                <div class="stat-number income">¥{{ formatNumber(statistics.total_income) }}</div>
                <div class="stat-label">总收入</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon expense">💸</div>
              <div class="stat-info">
                <div class="stat-number expense">¥{{ formatNumber(statistics.total_expense) }}</div>
                <div class="stat-label">总支出</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon profit">📈</div>
              <div class="stat-info">
                <div class="stat-number profit">¥{{ formatNumber(statistics.net_profit) }}</div>
                <div class="stat-label">净利润</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon count">📊</div>
              <div class="stat-info">
                <div class="stat-number count">{{ statistics.total_transactions }}</div>
                <div class="stat-label">交易笔数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-section">
      <!-- 第一行：收支对比和分类分布 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>收支对比分析</span>
                <el-select v-model="incomeExpensePeriod" size="small" style="width: 120px;">
                  <el-option label="本月" value="month" />
                  <el-option label="本季度" value="quarter" />
                  <el-option label="本年" value="year" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="incomeExpenseOption" />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>支出分类分布</span>
                <el-select v-model="categoryPeriod" size="small" style="width: 120px;">
                  <el-option label="本月" value="month" />
                  <el-option label="本季度" value="quarter" />
                  <el-option label="本年" value="year" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="categoryDistributionOption" />
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 第二行：月度趋势和供应商分析 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="16">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>月度收支趋势</span>
                <el-date-picker
                  v-model="trendDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  size="small"
                  style="width: 280px;"
                  @change="loadTrendData"
                />
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="monthlyTrendOption" />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>供应商交易排行</span>
                <el-select v-model="supplierPeriod" size="small" style="width: 120px;">
                  <el-option label="本月" value="month" />
                  <el-option label="本季度" value="quarter" />
                  <el-option label="本年" value="year" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="supplierRankingOption" />
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 第三行：项目财务分析和详细数据表格 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>项目财务分析</span>
                <el-select v-model="projectPeriod" size="small" style="width: 120px;">
                  <el-option label="本月" value="month" />
                  <el-option label="本季度" value="quarter" />
                  <el-option label="本年" value="year" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="projectAnalysisOption" />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>支付方式分析</span>
                <el-select v-model="paymentPeriod" size="small" style="width: 120px;">
                  <el-option label="本月" value="month" />
                  <el-option label="本季度" value="quarter" />
                  <el-option label="本年" value="year" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="paymentMethodOption" />
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 第四行：详细数据表格 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="table-container">
            <template #header>
              <div class="card-header">
                <span>财务数据明细</span>
              </div>
            </template>
            
            <el-table :data="tableData" style="width: 100%" v-loading="loading">
              <el-table-column prop="transaction_date" label="交易日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.transaction_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="type" label="交易类型" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.type === 'income' ? 'success' : 'danger'">
                    {{ scope.row.type === 'income' ? '收入' : '支出' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="category_name" label="交易分类" width="120" />
              <el-table-column prop="amount" label="金额" width="120">
                <template #default="scope">
                  <span :class="scope.row.type === 'income' ? 'income-amount' : 'expense-amount'">
                    ¥{{ formatNumber(scope.row.amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="project_name" label="关联项目" width="150" />
              <el-table-column prop="supplier_name" label="关联供应商" width="150" />
              <el-table-column prop="payment_method" label="支付方式" width="120">
                <template #default="scope">
                  {{ getPaymentMethodText(scope.row.payment_method) }}
                </template>
              </el-table-column>
              <el-table-column prop="description" label="交易描述" />
            </el-table>
            
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="pagination.page"
                v-model:page-size="pagination.size"
                :page-sizes="[10, 20, 50, 100]"
                :total="pagination.total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

// 预定义颜色数组，确保图表颜色丰富且区分明显
const chartColors = [
  '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
  '#36CBCB', '#FF9C6E', '#9B59B6', '#E74C3C', '#3498DB',
  '#2ECC71', '#F1C40F', '#E67E22', '#95A5A6', '#34495E',
  '#1ABC9C', '#F39C12', '#D35400', '#BDC3C7', '#2C3E50',
  '#8E44AD', '#16A085', '#27AE60', '#2980B9', '#C0392B',
  '#F7DC6F', '#D7BDE2', '#A9CCE3', '#F8C471', '#82E0AA'
]

// 获取分类分布图表的颜色 - 确保每个分类都有不同颜色
const getCategoryColors = (dataLength) => {
  const colors = []
  for (let i = 0; i < dataLength; i++) {
    colors.push(chartColors[i % chartColors.length])
  }
  return colors
}

// 获取供应商排行图表的颜色 - 确保每个供应商都有不同颜色
const getSupplierColors = (dataLength) => {
  const colors = []
  for (let i = 0; i < dataLength; i++) {
    colors.push(chartColors[i % chartColors.length])
  }
  return colors
}

// 获取支付方式图表的颜色 - 确保每种支付方式都有不同颜色
const getPaymentMethodColors = (dataLength) => {
  const colors = []
  for (let i = 0; i < dataLength; i++) {
    colors.push(chartColors[i % chartColors.length])
  }
  return colors
}

// 响应式数据
const loading = ref(false)
const incomeExpensePeriod = ref('month')
const categoryPeriod = ref('month')
const supplierPeriod = ref('month')
const projectPeriod = ref('month')
const paymentPeriod = ref('month')
const trendDateRange = ref([])
const tableDateRange = ref([])

// 统计数据
const statistics = reactive({
  total_income: 0,
  total_expense: 0,
  net_profit: 0,
  total_transactions: 0
})

// 图表数据
const chartData = reactive({
  income_expense: { income: 0, expense: 0, net: 0 },
  category_distribution: [],
  monthly_trend: [],
  supplier_ranking: [],
  project_analysis: [],
  payment_method_analysis: []
})

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 表格数据
const tableData = ref([])

// 图表配置
const incomeExpenseOption = computed(() => {
  const income = chartData.income_expense.income || 0
  const expense = chartData.income_expense.expense || 0
  
  return {
    title: {
      text: '收支对比',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: income, name: '收入', itemStyle: { color: '#67c23a' } },
          { value: expense, name: '支出', itemStyle: { color: '#f56c6c' } }
        ]
      }
    ]
  }
})

const categoryDistributionOption = computed(() => {
  const data = chartData.category_distribution || []
  
  return {
    title: {
      text: '支出分类分布',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      type: 'scroll'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: data.length > 0 ? data.map((item, index) => ({
          name: item.name,
          value: item.value,
          itemStyle: { 
            color: getCategoryColors(data.length)[index],
            borderColor: '#fff',
            borderWidth: 2
          }
        })) : [{ name: '暂无数据', value: 1, itemStyle: { color: '#909399' } }],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
          formatter: '{b}: ¥{c}'
        }
      }
    ]
  }
})

const monthlyTrendOption = computed(() => {
  const data = chartData.monthly_trend || []
  
  return {
    title: {
      text: '月度收支趋势',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['收入', '支出', '净利润'],
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
      boundaryGap: false,
      data: data.length > 0 ? data.map(item => item.label) : ['暂无数据']
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        stack: 'Total',
        data: data.length > 0 ? data.map(item => item.income) : [0],
        itemStyle: { color: '#67c23a' },
        smooth: true
      },
      {
        name: '支出',
        type: 'line',
        stack: 'Total',
        data: data.length > 0 ? data.map(item => item.expense) : [0],
        itemStyle: { color: '#f56c6c' },
        smooth: true
      },
      {
        name: '净利润',
        type: 'line',
        stack: 'Total',
        data: data.length > 0 ? data.map(item => item.net) : [0],
        itemStyle: { color: '#409eff' },
        smooth: true
      }
    ]
  }
})

const supplierRankingOption = computed(() => {
  const data = chartData.supplier_ranking || []
  
  return {
    title: {
      text: '供应商交易排行',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function(params) {
        const data = params[0]
        return `${data.name}<br/>交易金额: ¥${formatNumber(data.value)}<br/>交易次数: ${data.data.count || 0}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    yAxis: {
      type: 'category',
      data: data.length > 0 ? data.map(item => item.name) : ['暂无数据']
    },
    series: [
      {
        name: '交易金额',
        type: 'bar',
        data: data.length > 0 ? data.map((item, index) => ({
          value: item.value,
          count: item.count,
          itemStyle: { 
            color: getSupplierColors(data.length)[index],
            borderRadius: [0, 4, 4, 0]
          }
        })) : [0],
        barWidth: '60%',
        label: {
          show: true,
          position: 'right',
          formatter: '¥{c}'
        }
      }
    ]
  }
})

const projectAnalysisOption = computed(() => {
  const data = chartData.project_analysis || []
  
  return {
    title: {
      text: '项目财务分析',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['预算', '实际支出', '利润'],
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
      data: data.length > 0 ? data.map(item => item.name) : ['暂无数据']
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '预算',
        type: 'bar',
        data: data.length > 0 ? data.map(item => item.budget) : [0],
        itemStyle: { color: '#e6a23c' }
      },
      {
        name: '实际支出',
        type: 'bar',
        data: data.length > 0 ? data.map(item => item.actual_expense) : [0],
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: '利润',
        type: 'bar',
        data: data.length > 0 ? data.map(item => item.profit) : [0],
        itemStyle: { color: '#67c23a' }
      }
    ]
  }
})

const paymentMethodOption = computed(() => {
  const data = chartData.payment_method_analysis || []
  
  return {
    title: {
      text: '支付方式分析',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      type: 'scroll'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: data.length > 0 ? data.map((item, index) => ({
          name: getPaymentMethodText(item.name),
          value: item.value,
          itemStyle: { 
            color: getPaymentMethodColors(data.length)[index],
            borderColor: '#fff',
            borderWidth: 2
          }
        })) : [{ name: '暂无数据', value: 1, itemStyle: { color: '#909399' } }],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
          formatter: '{b}: ¥{c}'
        }
      }
    ]
  }
})

// 方法
const loadStatistics = async () => {
  try {
    loading.value = true
    
    // 调用基础统计API
    const response = await fetch('/api/v1/transactions/statistics/overview', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    // 更新统计数据
    statistics.total_income = data.total_income || 0
    statistics.total_expense = data.total_expense || 0
    statistics.net_profit = data.net_amount || 0
    statistics.total_transactions = data.total_transactions || 0
    
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

const loadChartData = async (period = 'month') => {
  try {
    loading.value = true
    console.log('开始加载图表数据，周期:', period)
    
    // 构建查询参数
    const params = new URLSearchParams({
      period: period
    })
    
    if (trendDateRange.value && trendDateRange.value.length === 2) {
      // 格式化日期为 YYYY-MM-DD 格式
      const formatDate = (date) => {
        const d = new Date(date)
        const year = d.getFullYear()
        const month = String(d.getMonth() + 1).padStart(2, '0')
        const day = String(d.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
      }
      
      const dateFrom = formatDate(trendDateRange.value[0])
      const dateTo = formatDate(trendDateRange.value[1])
      
      params.append('date_from', dateFrom)
      params.append('date_to', dateTo)
      
      console.log('格式化后的日期范围:', { dateFrom, dateTo })
    }
    
    console.log('请求参数:', params.toString())
    
    // 调用图表统计API
    const response = await fetch(`/api/v1/transactions/statistics/charts?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('API响应错误:', response.status, errorText)
      throw new Error(`HTTP error! status: ${response.status}, detail: ${errorText}`)
    }
    
    const data = await response.json()
    console.log('图表数据响应:', data)
    
    // 更新图表数据
    updateChartOptions(data)
    
  } catch (error) {
    console.error('加载图表数据失败:', error)
    ElMessage.error('加载图表数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const updateChartOptions = (data) => {
  console.log('开始更新图表选项:', data)
  
  // 更新收支对比图表
  if (data.income_expense) {
    console.log('更新收支对比数据:', data.income_expense)
    chartData.income_expense = data.income_expense
  }
  
  // 更新分类分布图表
  if (data.category_distribution) {
    console.log('更新分类分布数据:', data.category_distribution)
    chartData.category_distribution = data.category_distribution
  }
  
  // 更新月度趋势图表
  if (data.monthly_trend) {
    console.log('更新月度趋势数据:', data.monthly_trend)
    chartData.monthly_trend = data.monthly_trend
  }
  
  // 更新供应商排行图表
  if (data.supplier_ranking) {
    console.log('更新供应商排行数据:', data.supplier_ranking)
    chartData.supplier_ranking = data.supplier_ranking
  }
  
  // 更新项目分析图表
  if (data.project_analysis) {
    console.log('更新项目分析数据:', data.project_analysis)
    chartData.project_analysis = data.project_analysis
  }
  
  // 更新支付方式图表
  if (data.payment_method_analysis) {
    console.log('更新支付方式数据:', data.payment_method_analysis)
    chartData.payment_method_analysis = data.payment_method_analysis
  }
  
  console.log('图表数据更新完成，当前chartData:', chartData)
}

const loadTrendData = async () => {
  if (trendDateRange.value && trendDateRange.value.length === 2) {
    await loadChartData(incomeExpensePeriod.value)
  }
}

const loadTableData = async () => {
  try {
    loading.value = true
    
    // 构建查询参数
    const params = new URLSearchParams({
      skip: ((pagination.page - 1) * pagination.per_page).toString(),
      limit: pagination.per_page.toString()
    })
    
    if (tableDateRange.value && tableDateRange.value.length === 2) {
      params.append('date_from', tableDateRange.value[0])
      params.append('date_to', tableDateRange.value[1])
    }
    
    // 调用表格统计API
    const response = await fetch(`/api/v1/transactions/statistics/table?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    // 更新表格数据
    tableData.value = data.data || []
    pagination.total = data.total || 0
    
  } catch (error) {
    console.error('加载表格数据失败:', error)
    ElMessage.error('加载表格数据失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  loadTableData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadTableData()
}

const exportToExcel = () => {
  ElMessage.success('导出功能开发中...')
}

const formatNumber = (num) => {
  return new Intl.NumberFormat('zh-CN').format(num)
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

const getPaymentMethodText = (method) => {
  const methods = {
    'cash': '现金',
    'bank_transfer': '银行转账',
    'alipay': '支付宝',
    'wechat_pay': '微信支付',
    'check': '支票',
    'other': '其他'
  }
  return methods[method] || method
}

// 监听时间筛选变化
const watchPeriodChanges = () => {
  // 监听收支对比周期变化
  watch(incomeExpensePeriod, () => {
    loadChartData(incomeExpensePeriod.value)
  })
  
  // 监听分类周期变化
  watch(categoryPeriod, () => {
    loadChartData(categoryPeriod.value)
  })
  
  // 监听供应商周期变化
  watch(supplierPeriod, () => {
    loadChartData(supplierPeriod.value)
  })
  
  // 监听项目周期变化
  watch(projectPeriod, () => {
    loadChartData(projectPeriod.value)
  })
  
  // 监听支付方式周期变化
  watch(paymentPeriod, () => {
    loadChartData(paymentPeriod.value)
  })
}

// 生命周期
onMounted(async () => {
  await loadStatistics()
  await loadChartData()
  await loadTableData()
  watchPeriodChanges()
})
</script>

<style scoped>
.reports-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 28px;
  font-weight: bold;
}

.page-header p {
  color: #666;
  font-size: 16px;
}

/* 统计卡片样式 */
.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  height: 120px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 20px;
}

.stat-icon {
  font-size: 48px;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.income {
  color: #67c23a;
}

.expense {
  color: #f56c6c;
}

.profit {
  color: #409eff;
}

.count {
  color: #e6a23c;
}

/* 图表区域样式 */
.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #333;
  font-size: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.chart-container {
  height: 400px;
  padding: 20px;
}

.chart {
  height: 100%;
  width: 100%;
}

/* 表格样式 */
.table-container {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.income-amount {
  color: #67c23a;
  font-weight: bold;
}

.expense-amount {
  color: #f56c6c;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .chart-container {
    height: 300px;
  }
}

@media (max-width: 768px) {
  .reports-container {
    padding: 16px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .stat-card {
    height: 100px;
    margin-bottom: 16px;
  }
  
  .stat-icon {
    font-size: 36px;
    margin-right: 16px;
  }
  
  .stat-number {
    font-size: 20px;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>
