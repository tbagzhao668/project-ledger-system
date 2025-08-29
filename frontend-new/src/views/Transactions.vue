<template>
  <div class="transactions-container">
    <div class="transactions-header">
      <h1>财务记录</h1>
      <div class="header-actions">
        <el-button @click="exportToExcel" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新增财务记录
        </el-button>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="transactions-filters">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="24" :md="12" :lg="6" :xl="6">
          <el-input
            v-model="filters.search"
            placeholder="搜索交易描述、标签或备注"
            prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="4" :xl="4">
          <el-select
            v-model="filters.type"
            placeholder="交易类型"
            clearable
            @change="handleSearch"
          >
            <el-option label="收入" value="income" />
            <el-option label="支出" value="expense" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="4" :xl="4">
          <el-select
            v-model="filters.category_id"
            placeholder="交易分类"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="4" :xl="4">
          <el-select
            v-model="filters.project_id"
            placeholder="关联项目"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="24" :md="12" :lg="6" :xl="6">
          <el-date-picker
            v-model="filters.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleSearch"
            style="width: 100%"
          />
        </el-col>
        <el-col :xs="24" :sm="24" :md="24" :lg="4" :xl="4">
          <el-button @click="resetFilters" style="width: 100%">重置筛选</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 统计信息 -->
    <div class="transactions-stats" v-if="statistics">
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
              <div class="stat-icon net">📊</div>
              <div class="stat-info">
                <div class="stat-number" :class="statistics.net_amount >= 0 ? 'income' : 'expense'">
                  {{ statistics.net_amount >= 0 ? '+' : '' }}¥{{ formatNumber(statistics.net_amount) }}
                </div>
                <div class="stat-label">净额</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon count">📋</div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.total_transactions }}</div>
                <div class="stat-label">交易总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 交易列表 -->
    <div class="transactions-table">
      <el-table
        :data="transactions"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="transaction_date" label="交易日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.transaction_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="交易描述" min-width="150" max-width="200" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'" size="small">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.category_name" size="small">{{ row.category_name }}</el-tag>
            <span v-else class="no-category">未分类</span>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="150">
          <template #default="{ row }">
            <span :class="row.type === 'income' ? 'income-amount' : 'expense-amount'">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ formatNumber(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="关联项目" width="140" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.project_name">{{ row.project_name }}</span>
            <span v-else class="no-project">未关联项目</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="supplier_name" label="关联供应商" width="140" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.supplier_name">{{ row.supplier_name }}</span>
            <span v-else class="no-supplier">未关联供应商</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            <span v-if="row.payment_method">{{ getPaymentMethodText(row.payment_method) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="140">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              @click="viewTransaction(row)"
            >
              查看
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteTransaction(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 分页 -->
    <div class="transactions-pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 新增/编辑交易对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      @close="resetForm"
    >
      <el-form
        ref="transactionFormRef"
        :model="transactionForm"
        :rules="transactionRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="交易日期" prop="transaction_date">
              <el-date-picker
                v-model="transactionForm.transaction_date"
                type="date"
                placeholder="选择交易日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交易类型" prop="type">
              <el-radio-group v-model="transactionForm.type">
                <el-radio label="income">收入</el-radio>
                <el-radio label="expense">支出</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关联项目" prop="project_id">
              <el-select 
                v-model="transactionForm.project_id" 
                placeholder="选择关联项目（可选）"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="关联供应商" prop="supplier_id">
              <el-select 
                v-model="transactionForm.supplier_id" 
                placeholder="选择关联供应商（可选）"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="supplier in suppliers"
                  :key="supplier.id"
                  :label="supplier.name"
                  :value="supplier.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交易分类" prop="category_id">
              <el-select 
                v-model="transactionForm.category_id" 
                placeholder="选择交易分类（可选）"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="交易金额" prop="amount">
              <el-input-number
                v-model="transactionForm.amount"
                :min="0"
                :precision="2"
                placeholder="请输入交易金额"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="货币类型" prop="currency">
              <el-select v-model="transactionForm.currency" style="width: 100%">
                <el-option label="人民币 (CNY)" value="CNY" />
                <el-option label="美元 (USD)" value="USD" />
                <el-option label="欧元 (EUR)" value="EUR" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="支付方式" prop="payment_method">
              <el-select
                v-model="transactionForm.payment_method"
                placeholder="请选择支付方式"
                clearable
                style="width: 100%"
              >
                <el-option label="现金" value="cash" />
                <el-option label="银行转账" value="bank_transfer" />
                <el-option label="支付宝" value="alipay" />
                <el-option label="微信支付" value="wechat_pay" />
                <el-option label="支票" value="check" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="汇率" prop="exchange_rate">
              <el-input-number
                v-model="transactionForm.exchange_rate"
                :min="0.000001"
                :precision="6"
                placeholder="汇率"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="交易描述" prop="description">
          <el-input
            v-model="transactionForm.description"
            placeholder="请输入交易描述"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="transactionForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in commonTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="transactionForm.notes"
            placeholder="请输入备注信息"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTransaction" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 查看交易详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="交易详情"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="viewingTransaction" class="transaction-detail">
        <!-- 按照创建表单的格式显示所有字段 -->
        <el-form label-width="120px" class="detail-form">
          <!-- 第一行：交易日期、交易类型 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="交易日期">
                <span class="detail-value">{{ formatDate(viewingTransaction.transaction_date) }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="交易类型">
                <el-tag :type="viewingTransaction.type === 'income' ? 'success' : 'danger'" size="small">
                  {{ viewingTransaction.type === 'income' ? '收入' : '支出' }}
                </el-tag>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第二行：关联项目、关联供应商 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="关联项目">
                <span class="detail-value" v-if="viewingTransaction.project_name">{{ viewingTransaction.project_name }}</span>
                <span class="detail-value no-data" v-else>未关联项目</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="关联供应商">
                <span class="detail-value" v-if="viewingTransaction.supplier_name">{{ viewingTransaction.supplier_name }}</span>
                <span class="detail-value no-data" v-else>未关联供应商</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第三行：交易分类、交易金额 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="交易分类">
                <span class="detail-value" v-if="viewingTransaction.category_name">{{ viewingTransaction.category_name }}</span>
                <span class="detail-value no-data" v-else>未分类</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="交易金额">
                <span class="detail-value amount-display" :class="viewingTransaction.type === 'income' ? 'income-amount' : 'expense-amount'">
                  {{ viewingTransaction.type === 'income' ? '+' : '-' }}¥{{ formatNumber(viewingTransaction.amount) }}
                </span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第四行：货币类型、支付方式 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="货币类型">
                <span class="detail-value">{{ viewingTransaction.currency || 'CNY' }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="支付方式">
                <span class="detail-value" v-if="viewingTransaction.payment_method">{{ getPaymentMethodText(viewingTransaction.payment_method) }}</span>
                <span class="detail-value no-data" v-else>未设置</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第五行：汇率、交易状态 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="汇率">
                <span class="detail-value">{{ viewingTransaction.exchange_rate || '1.000000' }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="交易状态">
                <el-tag :type="getStatusType(viewingTransaction.status)" size="small">
                  {{ getStatusText(viewingTransaction.status) }}
                </el-tag>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第六行：交易描述 -->
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="交易描述">
                <span class="detail-value description-content" v-if="viewingTransaction.description">{{ viewingTransaction.description }}</span>
                <span class="detail-value no-data" v-else>无描述</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第七行：标签 -->
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="标签">
                <div class="detail-value tags-content" v-if="viewingTransaction.tags && viewingTransaction.tags.length > 0">
                  <el-tag 
                    v-for="tag in viewingTransaction.tags" 
                    :key="tag" 
                    size="small" 
                    style="margin-right: 8px; margin-bottom: 8px;"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
                <span class="detail-value no-data" v-else>无标签</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第八行：备注 -->
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="备注">
                <span class="detail-value notes-content" v-if="viewingTransaction.notes">{{ viewingTransaction.notes }}</span>
                <span class="detail-value no-data" v-else>无备注</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第九行：其他信息 -->
          <el-row :gutter="20" v-if="viewingTransaction.attachment_url || viewingTransaction.reference_number || viewingTransaction.approved_by || viewingTransaction.approved_at">
            <el-col :span="12" v-if="viewingTransaction.attachment_url">
              <el-form-item label="附件链接">
                <span class="detail-value attachment-link">
                  <a :href="viewingTransaction.attachment_url" target="_blank">{{ viewingTransaction.attachment_url }}</a>
                </span>
              </el-form-item>
            </el-col>
            <el-col :span="12" v-if="viewingTransaction.reference_number">
              <el-form-item label="参考编号">
                <span class="detail-value">{{ viewingTransaction.reference_number }}</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" v-if="viewingTransaction.approved_by || viewingTransaction.approved_at">
            <el-col :span="12" v-if="viewingTransaction.approved_by">
              <el-form-item label="审批人">
                <span class="detail-value">{{ viewingTransaction.approved_by }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12" v-if="viewingTransaction.approved_at">
              <el-form-item label="审批时间">
                <span class="detail-value">{{ formatDateTime(viewingTransaction.approved_at) }}</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 第十行：系统信息 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="创建时间">
                <span class="detail-value">{{ formatDateTime(viewingTransaction.created_at) }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12" v-if="viewingTransaction.updated_at">
              <el-form-item label="更新时间">
                <span class="detail-value">{{ formatDateTime(viewingTransaction.updated_at) }}</span>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="viewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const currentTransaction = ref(null)
const viewingTransaction = ref(null)
const transactionFormRef = ref()

const transactions = ref([])
const projects = ref([])
const categories = ref([])
const suppliers = ref([])
const statistics = ref(null)

// 分页
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 筛选条件
const filters = reactive({
  search: '',
  type: '',
  category_id: '',
  project_id: '',
  date_range: []
})

// 表单数据
const transactionForm = reactive({
  transaction_date: '',
  type: 'expense',
  project_id: '',
  category_id: '',
  amount: null,
  currency: 'CNY',
  exchange_rate: 1.0,
  description: '',
  tags: [],
  payment_method: '',
  notes: '',
  supplier_id: '' // 新增供应商ID
})

// 表单验证规则
const transactionRules = {
  transaction_date: [
    { required: true, message: '请选择交易日期', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择交易类型', trigger: 'change' }
  ],
  project_id: [
    { required: true, message: '请选择关联项目', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入交易金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入交易描述', trigger: 'blur' },
    { min: 1, max: 500, message: '描述长度在1到500个字符', trigger: 'blur' }
  ]
}

// 常用标签
const commonTags = [
  '材料费', '人工费', '设备费', '管理费', '差旅费', '办公费',
  '工程款', '预付款', '进度款', '质保金', '其他'
]

// 计算属性
const dialogTitle = computed(() => {
  return isEdit.value ? '编辑财务记录' : '新增财务记录'
})

// 格式化函数
const formatNumber = (num) => {
  if (!num && num !== 0) return '0.00'
  return new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2 }).format(num)
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN')
}

const getPaymentMethodText = (method) => {
  const methodMap = {
    'cash': '现金',
    'bank_transfer': '银行转账',
    'alipay': '支付宝',
    'wechat_pay': '微信支付',
    'check': '支票',
    'other': '其他'
  }
  return methodMap[method] || method
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'confirmed': '已确认',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    'draft': 'info',
    'confirmed': 'success',
    'cancelled': 'danger'
  }
  return typeMap[status] || 'info'
}

// 方法
const showCreateDialog = () => {
  isEdit.value = false
  currentTransaction.value = null
  resetForm()
  dialogVisible.value = true
}

const editTransaction = (transaction) => {
  isEdit.value = true
  currentTransaction.value = transaction
  fillFormData(transaction)
  dialogVisible.value = true
}

const fillFormData = (transaction) => {
  Object.assign(transactionForm, {
    transaction_date: transaction.transaction_date,
    type: transaction.type,
    project_id: transaction.project_id,
    category_id: transaction.category_id,
    amount: transaction.amount,
    currency: transaction.currency || 'CNY',
    exchange_rate: transaction.exchange_rate || 1.0,
    description: transaction.description,
    tags: transaction.tags || [],
    payment_method: transaction.payment_method || '',
    notes: transaction.notes || '',
    supplier_id: transaction.supplier_id || '' // 填充供应商ID
  })
}

const viewTransaction = (transaction) => {
  viewingTransaction.value = transaction
  viewDialogVisible.value = true
}

const deleteTransaction = async (transaction) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条财务记录"${transaction.description}"吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
    
    const response = await fetch(`/api/v1/transactions/${transaction.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '删除失败')
    }
    
    ElMessage.success('删除成功')
    await loadTransactions()
  } catch (error) {
    if (error.message === '用户取消') return
    console.error('删除财务记录失败:', error)
    ElMessage.error(`删除失败: ${error.message}`)
  }
}

const submitTransaction = async () => {
  try {
    console.log('开始提交财务记录...')
    await transactionFormRef.value.validate()
    
    submitting.value = true
    
    const submitData = {
      project_id: transactionForm.project_id,
      type: transactionForm.type,
      category_id: transactionForm.category_id,
      amount: transactionForm.amount,
      currency: transactionForm.currency,
      exchange_rate: transactionForm.exchange_rate,
      description: transactionForm.description,
      tags: transactionForm.tags,
      payment_method: transactionForm.payment_method,
      notes: transactionForm.notes,
      transaction_date: transactionForm.transaction_date,
      supplier_id: transactionForm.supplier_id // 提交供应商ID
    }
    
    let response
    if (isEdit.value) {
      // 编辑模式
      response = await fetch(`/api/v1/transactions/${currentTransaction.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(submitData)
      })
    } else {
      // 新增模式
      response = await fetch('/api/v1/transactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(submitData)
      })
    }
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '操作失败')
    }
    
    console.log('财务记录提交成功')
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    await loadTransactions()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  transactionFormRef.value?.resetFields()
  Object.assign(transactionForm, {
    transaction_date: '',
    type: 'expense',
    project_id: '',
    category_id: '',
    amount: null,
    currency: 'CNY',
    exchange_rate: 1.0,
    description: '',
    tags: [],
    payment_method: '',
    notes: '',
    supplier_id: '' // 重置供应商ID
  })
}

const handleSearch = () => {
  pagination.page = 1
  loadTransactions()
}

const resetFilters = () => {
  Object.assign(filters, {
    search: '',
    type: '',
    category_id: '',
    project_id: '',
    date_range: []
  })
  pagination.page = 1
  loadTransactions()
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  loadTransactions()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadTransactions()
}

// 加载数据
const loadTransactions = async () => {
  try {
    console.log('开始加载财务记录...')
    loading.value = true
    
    // 构建查询参数
    const params = new URLSearchParams({
      skip: ((pagination.page - 1) * pagination.per_page).toString(),
      limit: pagination.per_page.toString()
    })
    
    if (filters.search) params.append('search', filters.search)
    if (filters.type) params.append('type', filters.type)
    if (filters.category_id) params.append('category_id', filters.category_id)
    if (filters.project_id) params.append('project_id', filters.project_id)
    if (filters.date_range && filters.date_range.length === 2) {
      params.append('start_date', filters.date_range[0])
      params.append('end_date', filters.date_range[1])
    }
    
    const response = await fetch(`/api/v1/transactions?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    // API直接返回交易记录列表，不是分页对象
    if (Array.isArray(data)) {
      transactions.value = data
      pagination.total = data.length
      
      // 计算统计信息
      const totalIncome = data
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
      
      const totalExpense = data
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
      
      statistics.value = {
        total_transactions: data.length,
        total_income: totalIncome,
        total_expense: totalExpense,
        net_amount: totalIncome - totalExpense
      }
    } else {
      // 如果API返回的是分页对象，使用原来的逻辑
      transactions.value = data.transactions || []
      pagination.total = data.total || 0
      
      statistics.value = {
        total_transactions: data.total || 0,
        total_income: data.total_income || 0,
        total_expense: data.total_expense || 0,
        net_amount: data.net_amount || 0
      }
    }
  } catch (error) {
    console.error('加载财务记录失败:', error)
    ElMessage.error('加载财务记录失败')
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  try {
    const response = await fetch('/api/v1/projects', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    projects.value = data
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  }
}

const loadCategories = async () => {
  try {
    const response = await fetch('/api/v1/categories', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    categories.value = data
  } catch (error) {
    console.error('加载分类列表失败:', error)
    ElMessage.error('加载分类列表失败')
  }
}

const loadSuppliers = async () => {
  try {
    const response = await fetch('/api/v1/suppliers', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    suppliers.value = data
  } catch (error) {
    console.error('加载供应商列表失败:', error)
    ElMessage.error('加载供应商列表失败')
  }
}

// 导出Excel
const exporting = ref(false)
const exportToExcel = async () => {
  try {
    exporting.value = true
    
    // 如果没有数据，先加载数据
    if (transactions.value.length === 0) {
      await loadTransactions()
    }
    
    // 准备导出数据
    const exportData = transactions.value.map(transaction => ({
      '交易日期': formatDate(transaction.transaction_date),
      '交易描述': transaction.description,
      '类型': transaction.type === 'income' ? '收入' : '支出',
      '分类': transaction.category_name || '未分类',
      '金额': transaction.amount,
      '关联项目': transaction.project_name || '未关联项目',
      '支付方式': transaction.payment_method ? getPaymentMethodText(transaction.payment_method) : '-',
      '关联供应商': transaction.supplier_name || '未关联供应商' // 添加供应商信息
    }))
    
    // 如果没有数据，提示用户
    if (exportData.length === 0) {
      ElMessage.warning('没有数据可导出')
      return
    }
    
    // 尝试使用后端API导出
    try {
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.per_page.toString()
      })
      if (filters.search) params.append('search', filters.search)
      if (filters.type) params.append('type', filters.type)
      if (filters.category_id) params.append('category_id', filters.category_id)
      if (filters.project_id) params.append('project_id', filters.project_id)
      if (filters.date_range && filters.date_range.length === 2) {
        params.append('date_from', filters.date_range[0])
        params.append('date_to', filters.date_range[1])
      }

      const response = await fetch(`/api/v1/transactions/export?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `财务记录_${new Date().toISOString().slice(0, 10)}.xlsx`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        ElMessage.success('导出成功')
        return
      }
    } catch (error) {
      console.log('后端导出API不可用，使用前端导出')
    }
    
    // 前端导出（使用CSV格式，兼容性更好）
    const csvContent = generateCSV(exportData)
    downloadCSV(csvContent, `财务记录_${new Date().toISOString().slice(0, 10)}.csv`)
    ElMessage.success('导出成功')
    
  } catch (error) {
    console.error('导出财务记录失败:', error)
    ElMessage.error(`导出失败: ${error.message}`)
  } finally {
    exporting.value = false
  }
}

// 生成CSV内容
const generateCSV = (data) => {
  if (data.length === 0) return ''
  
  const headers = Object.keys(data[0])
  const csvRows = []
  
  // 添加表头
  csvRows.push(headers.join(','))
  
  // 添加数据行
  for (const row of data) {
    const values = headers.map(header => {
      const value = row[header]
      // 如果值包含逗号、引号或换行符，需要用引号包围并转义
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        return `"${value.replace(/"/g, '""')}"`
      }
      return value
    })
    csvRows.push(values.join(','))
  }
  
  return csvRows.join('\n')
}

// 下载CSV文件
const downloadCSV = (csvContent, filename) => {
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

onMounted(() => {
  loadTransactions()
  loadProjects()
  loadCategories()
  loadSuppliers()
})
</script>

<style scoped>
.transactions-container {
  padding: 20px;
}

.transactions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.transactions-header h1 {
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.transactions-filters {
  margin-bottom: 20px;
}

.transactions-stats {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  font-size: 48px;
  margin-right: 20px;
}

.stat-icon.income {
  color: #67c23a;
}

.stat-icon.expense {
  color: #f56c6c;
}

.stat-icon.net {
  color: #409eff;
}

.stat-icon.count {
  color: #909399;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-number.income {
  color: #67c23a;
}

.stat-number.expense {
  color: #f56c6c;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.transactions-table {
  margin-bottom: 20px;
}

.transactions-pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.income-amount {
  color: #67c23a;
  font-weight: bold;
}

.expense-amount {
  color: #f56c6c;
  font-weight: bold;
}

.no-project, .no-category, .no-supplier {
  color: #999;
  font-style: italic;
}

/* 查看详情样式 */
.transaction-detail {
  padding: 20px 0;
}

/* 新的详情表单样式 */
.detail-form {
  background: #fff;
  border-radius: 8px;
}

.detail-form .el-form-item {
  margin-bottom: 20px;
}

.detail-form .el-form-item__label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.detail-value {
  color: #303133;
  line-height: 1.5;
  font-size: 14px;
  display: inline-block;
  min-height: 20px;
}

.detail-value.no-data {
  color: #999;
  font-style: italic;
}

/* 保留原有样式以兼容 */
.detail-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.section-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

.detail-row {
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}

.detail-item label {
  font-weight: 600;
  color: #606266;
  min-width: 120px; /* Adjusted for better alignment */
  margin-right: 15px;
  line-height: 1.5;
}

.detail-item span {
  color: #303133;
  line-height: 1.5;
  flex: 1;
}

.amount-display {
  font-weight: bold;
  font-size: 16px;
}

.income-amount {
  color: #67c23a;
}

.expense-amount {
  color: #f56c6c;
}

.description-content, .notes-content {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  margin-top: 8px;
  line-height: 1.6;
  color: #303133;
}

.tags-content {
  margin-top: 8px;
}

.no-data {
  color: #999;
  font-style: italic;
}

.attachment-link {
  color: #409eff;
  text-decoration: none;
}

.attachment-link:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .transactions-container {
    padding: 16px;
  }
  
  .transactions-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .transactions-header h1 {
    font-size: 20px;
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .stat-card {
    height: 80px;
  }
  
  .stat-icon {
    font-size: 36px;
    margin-right: 16px;
  }
  
  .stat-number {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .transactions-container {
    padding: 12px;
  }
  
  .transactions-header h1 {
    font-size: 18px;
  }
  
  .stat-card {
    height: 70px;
  }
  
  .stat-icon {
    font-size: 32px;
    margin-right: 12px;
  }
  
  .stat-number {
    font-size: 18px;
  }
}
</style>
