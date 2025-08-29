<template>
  <div class="projects-container">
    <div class="page-header">
      <div class="header-left">
        <h1>项目管理</h1>
        <p>管理所有工程项目信息</p>
      </div>
      <div class="header-right">
        <el-button @click="refreshProjects" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="goToNewProject">
          <el-icon><Plus /></el-icon>
          新建项目
        </el-button>
      </div>
    </div>
    
    <!-- 项目统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="8">
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
        
        <el-col :span="8">
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
        
        <el-col :span="8">
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
      </el-row>
        
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
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
        
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">￥{{ formatAmount(stats.totalBudget) }}</div>
                <div class="stat-label">总预算金额</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">￥{{ formatAmount(stats.totalContract) }}</div>
                <div class="stat-label">总合同金额</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 项目列表 -->
    <el-card class="projects-list-card">
      <template #header>
        <div class="card-header">
          <span>项目列表</span>
          <div class="header-actions">
            <span class="sync-status" :class="{ 'syncing': loading }">
              {{ loading ? '同步中...' : '数据已同步' }}
            </span>
            <el-input
              v-model="searchQuery"
              placeholder="搜索项目名称、编号或项目经理"
              style="width: 300px; margin-right: 16px;"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px; margin-right: 16px;">
              <el-option label="全部状态" value="" />
              <el-option label="规划中" value="planning" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="暂停" value="on_hold" />
              <el-option label="已完成" value="completed" />
              <el-option label="延期" value="delayed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-select v-model="progressFilter" placeholder="进度筛选" clearable style="width: 150px; margin-right: 16px;">
              <el-option label="全部进度" value="" />
              <el-option label="0-25%" value="0-25" />
              <el-option label="26-50%" value="26-50" />
              <el-option label="51-75%" value="51-75" />
              <el-option label="76-100%" value="76-100" />
              <el-option label="100%以上" value="100+" />
            </el-select>
            <el-button type="primary" @click="resetFilters" style="margin-left: 8px;">
              重置筛选
            </el-button>
            <el-button type="success" @click="refreshProjects" style="margin-left: 8px;">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="warning" @click="exportToExcel" style="margin-left: 8px;">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 表格容器，支持水平滚动 -->
      <div class="table-container">
        <el-table 
          :data="filteredProjects" 
          style="width: 100%" 
          v-loading="loading" 
          border
          :max-height="600"
          class="projects-table"
        >
          <!-- 项目名称列 -->
          <el-table-column prop="name" label="项目名称" min-width="200" class-name="name-column">
          <template #default="{ row }">
            <div class="project-name-cell">
              <div class="project-name">{{ row.name }}</div>
              <div class="project-code">{{ row.project_code }}</div>
            </div>
          </template>
        </el-table-column>
        
          <!-- 项目状态列 -->
          <el-table-column prop="status" label="项目状态" width="130" class-name="status-column">
          <template #default="{ row }">
            <el-select 
              v-model="row.status"
              size="small" 
              style="width: 100%"
              @change="handleStatusChange(row.id, $event)"
              popper-class="status-select-dropdown"
            >
              <el-option label="规划中" value="planning" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="暂停" value="on_hold" />
              <el-option label="已完成" value="completed" />
              <el-option label="延期" value="delayed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <!-- 状态颜色标识 -->
            <div class="status-indicator" :class="`status-${row.status}`"></div>
          </template>
        </el-table-column>
        
          <!-- 项目经理列 -->
          <el-table-column prop="manager_name" label="项目经理" width="120" class-name="manager-column">
          <template #default="{ row }">
            <span class="manager-name">{{ row.manager_name }}</span>
          </template>
        </el-table-column>
        
          <!-- 预算金额列 -->
          <el-table-column prop="budget" label="预算金额(万元)" width="140" class-name="amount-column">
          <template #default="{ row }">
            <span class="amount">￥{{ formatAmount(row.budget) }}</span>
          </template>
        </el-table-column>
        
          <!-- 合同金额列 -->
          <el-table-column prop="contract_amount" label="合同金额(万元)" width="140" class-name="amount-column">
          <template #default="{ row }">
            <span class="amount">￥{{ formatAmount(row.contract_amount) }}</span>
          </template>
        </el-table-column>
        
          <!-- 预算利润列 -->
          <el-table-column label="预算利润(万元)" width="140" class-name="profit-column">
          <template #default="{ row }">
            <span :class="['profit', getProfitClass(row.budget, row.contract_amount)]">
              ￥{{ formatAmount(calculateProfit(row.budget, row.contract_amount)) }}
            </span>
          </template>
        </el-table-column>
        
          <!-- 实际利润列 -->
          <el-table-column label="实际利润(万元)" width="140" class-name="profit-column">
          <template #default="{ row }">
            <span :class="['profit', getProfitClass(row.actual_expenses || 0, row.contract_amount)]">
              ￥{{ formatAmount(calculateActualProfit(row.actual_expenses || 0, row.contract_amount)) }}
            </span>
          </template>
        </el-table-column>
        
          <!-- 项目进度列 -->
          <el-table-column label="项目进度" width="150" class-name="progress-column">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress 
                :percentage="calculateProgress(row.start_date, row.end_date, row.status)" 
                :color="getProgressColor(row.start_date, row.end_date, row.status)"
                :stroke-width="8"
                :show-text="false"
                :status="getProgressStatus(row.start_date, row.end_date, row.status)"
                class="project-progress"
              />
              <span class="progress-text" :class="getProgressTextClass(row.start_date, row.end_date, row.status)">
                {{ calculateProgress(row.start_date, row.end_date, row.status) }}%
              </span>
            </div>
          </template>
        </el-table-column>
        
          <!-- 开始时间列 -->
          <el-table-column prop="start_date" label="开始时间" width="130" class-name="date-column">
          <template #default="{ row }">
            <span class="date-text">{{ row.start_date }}</span>
          </template>
        </el-table-column>
        
          <!-- 计划结束时间列 -->
          <el-table-column prop="end_date" label="结束时间" width="130" class-name="date-column">
          <template #default="{ row }">
            <span class="date-text">{{ row.end_date }}</span>
          </template>
        </el-table-column>
          <!-- 操作列 - 固定在右侧 -->
          <el-table-column label="操作" width="220" fixed="right" class-name="action-column">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="viewProject(row.id)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button type="warning" size="small" @click="openEditDialog(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="deleteProject(row.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      </div>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalProjects"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 编辑项目弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑项目"
      width="80%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div v-if="editingProject" class="edit-dialog-content">
      <el-form
          ref="editFormRef"
          :model="editForm"
          :rules="editRules"
        label-width="120px"
          class="edit-form"
        >
          <!-- 基本信息 -->
          <div class="form-section">
            <h3 class="section-title">基本信息</h3>
            
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="项目名称" prop="name">
                  <el-input 
                    v-model="editForm.name" 
                    placeholder="请输入项目名称"
                    maxlength="100"
                    show-word-limit
                  />
            </el-form-item>
          </el-col>
              
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="项目编号">
                  <el-input 
                    v-model="editForm.project_code" 
                    disabled
                    placeholder="项目编号不可修改"
                  />
                  <div class="form-hint">项目编号不可修改</div>
            </el-form-item>
          </el-col>
        
              <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="项目类型" prop="project_type">
                  <el-select 
                    v-model="editForm.project_type" 
                    placeholder="请选择项目类型"
                    style="width: 100%;"
                  >
                    <el-option label="市政工程" value="municipal" />
                    <el-option label="装饰工程" value="decoration" />
                    <el-option label="建筑工程" value="construction" />
                    <el-option label="水利水电工程" value="water_conservancy" />
                    <el-option label="安装工程" value="installation" />
                    <el-option label="公路工程" value="highway" />
                    <el-option label="桥梁工程" value="bridge" />
                    <el-option label="隧道工程" value="tunnel" />
                    <el-option label="机电工程" value="mechanical_electrical" />
                    <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="项目状态" prop="status">
                  <el-select 
                    v-model="editForm.status" 
                    placeholder="请选择项目状态"
                    style="width: 100%;"
                  >
                <el-option label="规划中" value="planning" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                    <el-option label="已暂停" value="on_hold" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
              
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="项目优先级" prop="priority">
                  <el-select 
                    v-model="editForm.priority" 
                    placeholder="请选择优先级"
                    style="width: 100%;"
                  >
                    <el-option label="低" value="low" />
                    <el-option label="中" value="medium" />
                    <el-option label="高" value="high" />
                    <el-option label="紧急" value="urgent" />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="项目经理" prop="manager_name">
                  <el-input 
                    v-model="editForm.manager_name" 
                    placeholder="请输入项目经理姓名"
                    maxlength="100"
                  />
            </el-form-item>
          </el-col>
        </el-row>
        
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="开始时间" prop="start_date">
                  <el-date-picker
                    v-model="editForm.start_date"
                    type="date"
                    placeholder="选择开始日期"
                    style="width: 100%;"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="结束时间" prop="end_date">
                  <el-date-picker
                    v-model="editForm.end_date"
                    type="date"
                    placeholder="选择结束日期"
                    style="width: 100%;"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="项目地址" prop="address">
                  <el-input 
                    v-model="editForm.address" 
                    placeholder="请输入项目地址"
                    maxlength="500"
                    show-word-limit
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 财务信息 -->
          <div class="form-section">
            <h3 class="section-title">财务信息</h3>
            
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="预算金额" prop="budget">
                  <el-input-number 
                    v-model="editForm.budget" 
                    :min="0" 
                    :precision="2" 
                    style="width: 100%;"
                    placeholder="请输入预算金额"
                  />
                  <div class="form-hint">单位：元</div>
            </el-form-item>
          </el-col>
              
              <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="合同金额" prop="contract_amount">
                  <el-input-number 
                    v-model="editForm.contract_amount" 
                    :min="0" 
                    :precision="2" 
                    style="width: 100%;"
                    placeholder="请输入合同金额"
                  />
                  <div class="form-hint">单位：元</div>
            </el-form-item>
          </el-col>
              
              
        </el-row>
          </div>

          <!-- 变更原因说明 -->
          <div class="form-section" v-if="budgetChanged || contractChanged">
            <h3 class="section-title">变更原因说明</h3>
            
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8" v-if="budgetChanged">
                <el-form-item label="预算变更原因" prop="budget_change_reason">
                  <el-select 
                    v-model="editForm.budget_change_reason" 
                    placeholder="请选择变更原因"
                    style="width: 100%;"
                    allow-create
                    filterable
                  >
                    <el-option label="工程量变更" value="工程量变更" />
                    <el-option label="材料价格调整" value="材料价格调整" />
                    <el-option label="设计变更" value="设计变更" />
                    <el-option label="工期调整" value="工期调整" />
                    <el-option label="其他" value="其他" />
                  </el-select>
            </el-form-item>
          </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" v-if="contractChanged">
                <el-form-item label="合同变更原因" prop="contract_change_reason">
                  <el-select 
                    v-model="editForm.contract_change_reason" 
                    placeholder="请选择变更原因"
                    style="width: 100%;"
                    allow-create
                    filterable
                  >
                    <el-option label="合同变更" value="合同变更" />
                    <el-option label="工程量变更" value="工程量变更" />
                    <el-option label="价格调整" value="价格调整" />
                    <el-option label="条款修改" value="条款修改" />
                    <el-option label="其他" value="其他" />
                  </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
            <el-row :gutter="24" v-if="budgetChanged || contractChanged">
              <el-col :xs="24">
                <el-form-item label="修改说明" prop="change_description">
                  <el-input 
                    v-model="editForm.change_description" 
                    type="textarea"
                    :rows="3"
                    placeholder="合同变更、工程量变更"
                    maxlength="500"
                    show-word-limit
                  />
                  <div class="form-hint">请详细说明变更原因和影响</div>
        </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 客户信息 -->
          <div class="form-section">
            <h3 class="section-title">客户信息</h3>
            
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="客户名称">
                  <el-input 
                    v-model="editForm.client_name" 
                    placeholder="请输入客户名称"
                    maxlength="100"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="客户联系人">
                  <el-input 
                    v-model="editForm.client_contact" 
                    placeholder="请输入客户联系人"
                    maxlength="50"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8">
                <el-form-item label="客户电话">
                  <el-input 
                    v-model="editForm.client_phone" 
                    placeholder="请输入客户电话"
                    maxlength="20"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 项目描述 -->
          <div class="form-section">
            <h3 class="section-title">项目描述</h3>
            
            <el-form-item label="项目描述">
              <el-input 
                v-model="editForm.description" 
                type="textarea"
                :rows="4"
                placeholder="请输入项目描述..."
                maxlength="500"
                show-word-limit
              />
            </el-form-item>
          </div>

          <!-- 项目标签 -->
          <div class="form-section">
            <h3 class="section-title">项目标签</h3>
            
            <el-form-item label="项目标签">
              <el-select 
                v-model="editForm.tags" 
                multiple 
                filterable 
                allow-create 
                default-first-option
                placeholder="请选择或输入标签"
                style="width: 100%;"
              >
                <el-option label="重点项目" value="重点项目" />
                <el-option label="政府项目" value="政府项目" />
                <el-option label="商业项目" value="商业项目" />
                <el-option label="住宅项目" value="住宅项目" />
                <el-option label="基础设施" value="基础设施" />
              </el-select>
            </el-form-item>
          </div>
      </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeEditDialog">取消</el-button>
          <el-button type="primary" @click="handleSaveProject" :loading="saving">
            保存修改
          </el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Folder, Check, Clock, Warning, Search, View, Edit, Delete, ArrowDown, Money, Document, Refresh, Download } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const progressFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalProjects = ref(0)

// 统计数据
const stats = ref({
  totalProjects: 0,
  completedProjects: 0,
  ongoingProjects: 0,
  delayedProjects: 0,
  totalBudget: 0,
  totalContract: 0
})

// 项目列表
const projects = ref([])

// 编辑弹窗相关
const editDialogVisible = ref(false)
const editingProject = ref(null)
const editFormRef = ref(null)
const saving = ref(false)

// 编辑表单数据
const editForm = reactive({
  name: '',
  project_code: '',
  description: '',
  project_type: '',
  priority: '',
  status: '',
  start_date: '',
  end_date: '',
  budget: null,
  contract_amount: null,
  actual_expenses: null,
  address: '',
  manager_name: '',
  client_name: '',
  client_contact: '',
  client_phone: '',
  tags: [],
  // 变更原因相关
  budget_change_reason: '',
  contract_change_reason: '',
  change_description: ''
})

// 编辑表单验证规则
const editRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度在2-100个字符', trigger: 'blur' }
  ],
  project_type: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择项目优先级', trigger: 'change' }
  ],
  manager_name: [
    { required: true, message: '请输入项目经理姓名', trigger: 'blur' },
    { min: 2, max: 100, message: '项目经理姓名长度在2-100个字符', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ],
  budget: [
    { required: true, message: '请输入预算金额', trigger: 'blur' },
    { type: 'number', min: 0, message: '预算金额必须大于0', trigger: 'blur' }
  ],
  contract_amount: [
    { required: true, message: '请输入合同金额', trigger: 'blur' },
    { type: 'number', min: 0, message: '合同金额必须大于0', trigger: 'blur' }
  ],
  change_description: [
    { required: true, message: '请输入修改说明', trigger: 'blur' }
  ]
}



// 计算属性
const filteredProjects = computed(() => {
  let filtered = projects.value
  
  // 文本搜索：项目名称、编号或项目经理
  if (searchQuery.value) {
    filtered = filtered.filter(project => 
      project.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      project.project_code.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      project.manager_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  
  // 状态筛选
  if (statusFilter.value) {
    filtered = filtered.filter(project => project.status === statusFilter.value)
  }
  
  // 进度筛选
  if (progressFilter.value) {
    filtered = filtered.filter(project => {
      const progress = calculateProgress(project.start_date, project.end_date, project.status)
      switch (progressFilter.value) {
        case '0-25':
          return progress >= 0 && progress <= 25
        case '26-50':
          return progress >= 26 && progress <= 50
        case '51-75':
          return progress >= 51 && progress <= 75
        case '76-100':
          return progress >= 76 && progress <= 100
        case '100+':
          return progress > 100
        default:
          return true
      }
    })
  }
  
  return filtered
})

// 方法
const getProjectTypeText = (type) => {
  return type || '未设置'
}

const getStatusType = (status) => {
  const statusMap = {
    'planning': 'info',
    'in_progress': 'primary',
    'on_hold': 'warning',
    'completed': 'success',
    'delayed': 'danger',
    'cancelled': 'danger'
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

// 格式化金额为"万"为单位
const formatAmount = (num) => {
  if (!num) return '0万'
  const wan = num / 10000
  if (wan === Math.floor(wan)) {
    return `${wan}万`
  } else {
    return `${wan.toFixed(1)}万`
  }
}

const viewProject = (id) => {
  router.push(`/projects/${id}`)
}

// 打开编辑弹窗
const openEditDialog = (row) => {
  editingProject.value = row
  fillEditForm(row)
  editDialogVisible.value = true
}

// 填充编辑表单
const fillEditForm = (projectData) => {
  editForm.name = projectData.name || ''
  editForm.project_code = projectData.project_code || ''
  editForm.description = projectData.description || ''
  editForm.project_type = projectData.project_type || ''
  editForm.priority = projectData.priority || ''
  editForm.status = projectData.status || ''
  editForm.start_date = projectData.start_date || ''
  editForm.end_date = projectData.end_date || ''
  editForm.budget = projectData.budget || null
  editForm.contract_amount = projectData.contract_amount || null
  editForm.address = projectData.address || ''
  editForm.manager_name = projectData.manager_name || ''
  editForm.client_name = projectData.client_name || ''
  editForm.client_contact = projectData.client_contact || ''
  editForm.client_phone = projectData.client_phone || ''
  editForm.tags = projectData.tags || []
  
  // 清空变更原因
  editForm.budget_change_reason = ''
  editForm.contract_change_reason = ''
  editForm.change_description = ''
}

// 关闭编辑弹窗
const closeEditDialog = () => {
  editDialogVisible.value = false
  editingProject.value = null
  editFormRef.value?.resetFields()
}

// 计算属性：检测预算是否变更
const budgetChanged = computed(() => {
  if (!editingProject.value) return false
  return editForm.budget !== editingProject.value.budget
})

// 计算属性：检测合同金额是否变更
const contractChanged = computed(() => {
  if (!editingProject.value) return false
  return editForm.contract_amount !== editingProject.value.contract_amount
})

// 保存项目修改
const handleSaveProject = async () => {
  try {
    // 验证表单
    await editFormRef.value?.validate()
    
    // 检查是否有变更
    const hasChanges = budgetChanged.value || contractChanged.value || 
                      editForm.name !== editingProject.value.name ||
                      editForm.description !== editingProject.value.description ||
                      editForm.project_type !== editingProject.value.project_type ||
                      editForm.priority !== editingProject.value.priority ||
                      editForm.status !== editingProject.value.status ||
                      editForm.start_date !== editingProject.value.start_date ||
                      editForm.end_date !== editingProject.value.end_date ||
                      editForm.address !== editingProject.value.address ||
                      editForm.manager_name !== editingProject.value.manager_name ||
                      editForm.client_name !== editingProject.value.client_name ||
                      editForm.client_contact !== editingProject.value.client_contact ||
                      editForm.client_phone !== editingProject.value.client_phone ||
                      JSON.stringify(editForm.tags) !== JSON.stringify(editingProject.value.tags || [])
    
    if (!hasChanges) {
      ElMessage.info('没有检测到任何变更')
      return
    }
    
    // 检查变更原因和修改说明
    if (budgetChanged.value && !editForm.budget_change_reason) {
      ElMessage.warning('请填写预算变更原因')
      return
    }
    
    if (contractChanged.value && !editForm.contract_change_reason) {
      ElMessage.warning('请填写合同变更原因')
      return
    }
    
    if ((budgetChanged.value || contractChanged.value) && !editForm.change_description) {
      ElMessage.warning('请填写修改说明')
      return
    }
    
    saving.value = true
    
    // 准备提交数据
    const submitData = {
      name: editForm.name,
      description: editForm.description,
      project_type: editForm.project_type,
      priority: editForm.priority,
      status: editForm.status,
      start_date: editForm.start_date,
      end_date: editForm.end_date,
      budget: editForm.budget,
      contract_amount: editForm.contract_amount,
      address: editForm.address,
      manager_name: editForm.manager_name,
      client_name: editForm.client_name,
      client_contact: editForm.client_contact,
      client_phone: editForm.client_phone,
      tags: editForm.tags
    }
    
    // 只有当有变更时才添加变更原因字段
    if (budgetChanged.value || contractChanged.value) {
      submitData.budget_change_reason = editForm.budget_change_reason
      submitData.contract_change_reason = editForm.contract_change_reason
      submitData.change_description = editForm.change_description
    }
    
    // 准备提交修改数据
    
    // 调用API更新项目
    const response = await fetch(`/api/v1/projects/${editingProject.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(submitData)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    ElMessage.success('项目修改保存成功！')
    
    // 关闭弹窗
    closeEditDialog()
    
    // 重新加载项目列表
    loadProjects()
    
  } catch (error) {
    console.error('保存项目修改失败:', error)
    
    if (error.message && error.message.includes('HTTP error')) {
      const status = error.message.match(/status: (\d+)/)?.[1]
      if (status === '400') {
        ElMessage.error('保存失败：请检查表单数据')
      } else if (status === '401') {
        ElMessage.error('保存失败：请重新登录')
      } else if (status === '403') {
        ElMessage.error('保存失败：权限不足')
      } else {
        ElMessage.error('保存失败，请检查网络连接')
      }
    } else {
      ElMessage.error(`保存失败: ${error.message || '未知错误'}`)
    }
  } finally {
    saving.value = false
  }
}

const deleteProject = async (id) => {
  try {
    // 获取项目信息用于确认对话框
    const project = projects.value.find(p => p.id === id)
    if (!project) {
      ElMessage.error('项目不存在')
      return
    }
    
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要删除项目"${project.name}"吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
    
    // 开始删除项目
    
    // 调用删除API
    const response = await fetch(`/api/v1/projects/${id}`, {
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
    
    // 重新加载项目列表
    await loadProjects()
    
  } catch (error) {
    console.error('删除项目失败:', error)
    
    if (error.message === '用户取消') {
      // 用户取消删除，不显示错误消息
      return
    }
    
    // 显示错误消息
    ElMessage.error(`删除项目失败: ${error.message}`)
  }
}

// 处理状态变更（显示确认对话框）
const handleStatusChange = async (id, newStatus) => {
  const project = projects.value.find(p => p.id === id)
  if (!project) return
  
  const oldStatus = project.status
  const oldStatusText = getStatusText(oldStatus)
  const newStatusText = getStatusText(newStatus)
  
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要将项目"${project.name}"的状态从"${oldStatusText}"更改为"${newStatusText}"吗？`,
      '确认状态更改',
      {
        confirmButtonText: '确定更改',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
    
    // 用户确认，更新状态
    await updateProjectStatus(id, newStatus)
    
  } catch (error) {
    // 用户取消，恢复原状态
    project.status = oldStatus
  }
}

// 更新项目状态
const updateProjectStatus = async (id, newStatus) => {
  try {
    // 调用API更新项目状态到数据库
    const response = await fetch(`/api/v1/projects/${id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ status: newStatus })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success('项目状态更新成功')
      
      // 更新本地项目状态
      const project = projects.value.find(p => p.id === id)
      if (project) {
        project.status = newStatus
        
        // 如果进度超过100%，提示用户但允许手动更改状态
        const progress = calculateProgress(project.start_date, project.end_date, newStatus)
        if (progress > 100 && newStatus !== 'completed') {
          ElMessage.warning(`项目进度已超过100%（当前进度：${progress}%），建议设置为延期状态，但您已手动设置为"${getStatusText(newStatus)}"`)
        }
      }
      
      // 重新计算统计数据
      updateStats()
      
    } else {
      throw new Error(result.message || '更新失败')
    }
    
  } catch (error) {
    console.error('更新项目状态失败:', error)
    ElMessage.error(`更新项目状态失败: ${error.message}`)
    
    // 更新失败时，恢复到原始状态
    const project = projects.value.find(p => p.id === id)
    if (project) {
      // 重新加载项目数据以恢复原始状态
      await loadProjects()
    }
  }
}

// 计算预算利润
const calculateProfit = (budget, contractAmount) => {
  if (!budget || !contractAmount) return 0
  return contractAmount - budget
}

// 计算实际利润
const calculateActualProfit = (actualExpenses, contractAmount) => {
  if (!actualExpenses || !contractAmount) return 0
  return contractAmount - actualExpenses
}

// 获取利润样式类
const getProfitClass = (budget, contractAmount) => {
  const profit = calculateProfit(budget, contractAmount)
  if (profit > 0) return 'profit-positive'
  if (profit < 0) return 'profit-negative'
  return 'profit-zero'
}

// 计算项目进度
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

// 获取进度条颜色
const getProgressColor = (startDate, endDate, status) => {
  if (status === 'completed') return '#67c23a'
  
  const progress = calculateProgress(startDate, endDate, status)
  if (progress >= 100) return '#f56c6c' // 红色表示延期
  if (progress >= 80) return '#e6a23c' // 橙色表示接近完成
  if (progress >= 50) return '#409eff' // 蓝色表示进行中
  return '#909399' // 灰色表示刚开始
}

// 获取进度条状态
const getProgressStatus = (startDate, endDate, status) => {
  if (status === 'completed') return 'success'
  
  const progress = calculateProgress(startDate, endDate, status)
  if (progress >= 100) return 'exception' // 延期状态
  if (progress >= 80) return 'warning' // 接近完成
  return 'normal' // 正常进行
}

// 获取进度文字样式类
const getProgressTextClass = (startDate, endDate, status) => {
  if (status === 'completed') return 'progress-completed'
  
  const progress = calculateProgress(startDate, endDate, status)
  if (progress >= 100) return 'progress-delayed' // 延期状态
  if (progress >= 80) return 'progress-warning' // 接近完成
  return 'progress-normal' // 正常进行
}





const goToNewProject = () => {
  router.push('/projects/new')
}



const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadProjects()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadProjects()
}

// 重置所有筛选条件
const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  progressFilter.value = ''
  currentPage.value = 1
}



// 更新统计数据
const updateStats = () => {
  stats.value = {
    totalProjects: projects.value.length,
    completedProjects: projects.value.filter(p => p.status === 'completed').length,
    ongoingProjects: projects.value.filter(p => p.status === 'in_progress').length,
    delayedProjects: projects.value.filter(p => p.status === 'delayed').length,
    totalBudget: projects.value.reduce((sum, p) => sum + (p.budget || 0), 0),
    totalContract: projects.value.reduce((sum, p) => sum + (p.contract_amount || 0), 0)
  }
}

// 加载数据
const loadProjects = async () => {
  try {
    loading.value = true
    
    // 调用API从数据库获取项目列表
    const response = await fetch('/api/v1/projects', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    // 后端API直接返回项目数组，不需要检查success字段
    if (Array.isArray(result)) {
      // 从API接收到的项目数据
      projects.value = result
      totalProjects.value = projects.value.length
      
      // 检查项目进度，为超过100%的项目自动设置为延期状态
      projects.value.forEach(project => {
        if (project.status !== 'completed') {
          const progress = calculateProgress(project.start_date, project.end_date, project.status)
          if (progress > 100) {
            project.status = 'delayed'
          }
        }
      })
      
      // 数据字段映射：将后端字段名映射到前端期望的字段名
      projects.value.forEach(project => {
        // 映射字段名
        project.project_code = project.code || project.project_code
        project.end_date = project.end_date || project.planned_end_date
        
        // 确保所有必需字段都存在
        project.contract_amount = project.contract_amount || 0
        project.actual_expenses = project.actual_expenses || 0
        project.description = project.description || project.notes || ''
      })
      
      // 计算统计数据
      updateStats()
      
    } else {
      throw new Error('API返回格式错误')
    }
    
  } catch (error) {
    console.error('加载项目数据失败:', error)
    ElMessage.error(`加载项目数据失败: ${error.message}`)
    
    // 如果API调用失败，使用模拟数据作为备用
    console.log('使用模拟数据作为备用')
    projects.value = [
      {
        id: '1',
        project_code: 'PRJ001',
        name: '市政道路改造工程',
        manager_name: '张三',
        status: 'in_progress',
        budget: 5000000,
        contract_amount: 4800000,
        actual_expenses: 3200000,
        start_date: '2024-01-15',
        end_date: '2024-12-31',
        description: '城市主干道改造升级项目'
      },
      {
        id: '2',
        project_code: 'PRJ002',
        name: '商业大厦装修项目',
        manager_name: '李四',
        status: 'planning',
        budget: 2000000,
        contract_amount: 1800000,
        actual_expenses: 0,
        start_date: '2024-03-01',
        end_date: '2024-08-31',
        description: '商业综合体内部装修工程'
      },
      {
        id: '3',
        project_code: 'PRJ003',
        name: '水利枢纽工程',
        manager_name: '王五',
        status: 'completed',
        budget: 8000000,
        contract_amount: 8200000,
        actual_expenses: 7800000,
        start_date: '2023-06-01',
        end_date: '2024-05-31',
        description: '大型水利枢纽建设工程'
      },
      {
        id: '4',
        project_code: 'PRJ004',
        name: '高速公路扩建',
        manager_name: '赵六',
        status: 'delayed',
        budget: 15000000,
        contract_amount: 14800000,
        actual_expenses: 12500000,
        start_date: '2023-09-01',
        end_date: '2024-08-31',
        description: '高速公路双向四车道扩建工程'
      },
      {
        id: '5',
        project_code: 'PRJ005',
        name: '地铁站建设工程',
        manager_name: '钱七',
        status: 'on_hold',
        budget: 12000000,
        contract_amount: 11800000,
        actual_expenses: 8500000,
        start_date: '2024-02-01',
        end_date: '2025-01-31',
        description: '城市地铁站建设及配套设施工程'
      },
      {
        id: '6',
        project_code: 'PRJ006',
        name: '工业园区基础设施',
        manager_name: '孙八',
        status: 'cancelled',
        budget: 8000000,
        contract_amount: 0,
        actual_expenses: 0,
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        description: '工业园区道路、水电等基础设施建设项目'
      }
    ]
    
    totalProjects.value = projects.value.length
    updateStats()
  } finally {
    loading.value = false
  }
}

// 刷新项目列表
const refreshProjects = async () => {
  try {
    loading.value = true
    ElMessage.info('正在刷新项目列表...')
    
    // 重新加载项目数据
    await loadProjects()
    
    // 检查是否有项目状态被自动调整为延期
    const autoDelayedProjects = projects.value.filter(project => {
      if (project.status === 'delayed') {
        const progress = calculateProgress(project.start_date, project.end_date, 'delayed')
        return progress > 100
      }
      return false
    })
    
    if (autoDelayedProjects.length > 0) {
      ElMessage.info(`检测到 ${autoDelayedProjects.length} 个项目进度超过100%，已自动设置为延期状态`)
    }
    
    ElMessage.success('项目列表刷新成功')
  } catch (error) {
    console.error('刷新项目列表失败:', error)
    ElMessage.error('刷新项目列表失败')
  } finally {
    loading.value = false
  }
}

// 导出为Excel
const exportToExcel = () => {
  try {
    // 准备导出数据（排除操作列）
    const exportData = filteredProjects.value.map(project => ({
      '项目名称': project.name,
      '项目编号': project.project_code,
      '项目状态': getStatusText(project.status),
      '项目经理': project.manager_name,
      '预算金额(万元)': (project.budget / 10000).toFixed(1),
      '合同金额(万元)': (project.contract_amount / 10000).toFixed(1),
      '预算利润(万元)': ((project.contract_amount - project.budget) / 10000).toFixed(1),
      '实际利润(万元)': ((project.contract_amount - (project.actual_expenses || 0)) / 10000).toFixed(1),
      '项目进度(%)': calculateProgress(project.start_date, project.end_date, project.status).toFixed(1),
      '项目开始时间': project.start_date,
      '项目计划结束时间': project.end_date,
      '项目类型': project.project_type,
      '项目描述': project.description
    }))
    
    // 创建工作簿
    const worksheet = XLSX.utils.json_to_sheet(exportData)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '项目列表')
    
    // 设置列宽
    const columnWidths = [
      { wch: 20 }, // 项目名称
      { wch: 15 }, // 项目编号
      { wch: 12 }, // 项目状态
      { wch: 12 }, // 项目经理
      { wch: 15 }, // 预算金额
      { wch: 15 }, // 合同金额
      { wch: 15 }, // 预算利润
      { wch: 15 }, // 实际利润
      { wch: 12 }, // 项目进度
      { wch: 15 }, // 开始时间
      { wch: 15 }, // 结束时间
      { wch: 12 }, // 项目类型
      { wch: 30 }  // 项目描述
    ]
    worksheet['!cols'] = columnWidths
    
    // 生成文件名
    const now = new Date()
    const timestamp = now.getFullYear() + 
                     String(now.getMonth() + 1).padStart(2, '0') + 
                     String(now.getDate()).padStart(2, '0') + '_' +
                     String(now.getHours()).padStart(2, '0') + 
                     String(now.getMinutes()).padStart(2, '0')
    const fileName = `项目列表_${timestamp}.xlsx`
    
    // 下载文件
    XLSX.writeFile(workbook, fileName)
    
    ElMessage.success('项目列表导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  }
}



// 定时刷新间隔（毫秒）
const REFRESH_INTERVAL = 60000 // 1分钟

// 定时器引用
let refreshTimer = null

// 生命周期
onMounted(() => {
  loadProjects()
  
  // 启动定时刷新
  startAutoRefresh()
})

onUnmounted(() => {
  // 清理定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})

// 启动自动刷新
const startAutoRefresh = () => {
  refreshTimer = setInterval(async () => {
    // 只在页面可见时刷新
    if (!document.hidden) {
      await loadProjects()
      
      // 同时更新统计数据
      updateStats()
    }
  }, REFRESH_INTERVAL)
}
</script>

<style scoped>
.projects-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left h1 {
  color: #333;
  margin-bottom: 10px;
}

.header-left p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.stats-section {
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
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.projects-list-card {
  margin-bottom: 30px;
}

/* 表格容器样式 - 支持水平滚动 */
.table-container {
  overflow-x: auto;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.projects-table {
  min-width: 1340px; /* 确保表格有足够的最小宽度，包含新增的实际利润列 */
}

/* 表格滚动条样式 */
.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
}

.sync-status {
  font-size: 12px;
  color: #67c23a;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #f0f9ff;
  border: 1px solid #e1f3d8;
  margin-right: 16px;
}

.sync-status.syncing {
  color: #e6a23c;
  background-color: #fdf6ec;
  border-color: #f5dab1;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  text-align: right;
}

/* 表格整体样式 */
:deep(.el-table) {
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #303133;
  font-weight: 600;
  font-size: 14px;
  padding: 10px 8px;
}

:deep(.el-table td) {
  padding: 10px 8px;
}

/* 表格单元格通用样式 - 防止换行 */
.name-column,
.status-column,
.manager-column,
.amount-column,
.profit-column,
.progress-column,
.date-column {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 响应式表格样式 */
@media (max-width: 1200px) {
  :deep(.el-table) {
    font-size: 13px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 8px 6px;
  }
}

@media (max-width: 768px) {
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 6px 4px;
  }
  
  .project-name {
    font-size: 13px;
  }
  
  .project-code {
    font-size: 11px;
  }
  
  .amount,
  .profit {
    font-size: 12px;
  }
  
  .progress-text {
    font-size: 11px;
  }
}

/* 项目名称单元格样式 */
.project-name-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.project-name {
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.project-code {
  font-size: 12px;
  color: #909399;
  font-family: 'Courier New', monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 项目经理样式 */
.manager-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #303133;
  font-weight: 500;
}

/* 金额样式 - 简洁版 */
.amount {
  font-family: 'Courier New', monospace;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

/* 利润样式 - 简洁版 */
.profit {
  font-family: 'Courier New', monospace;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.profit-positive {
  color: #67c23a;
}

.profit-negative {
  color: #f56c6c;
}

.profit-zero {
  color: #909399;
}

/* 状态选项样式 */
.status-option {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-option.planning {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.status-option.in-progress {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-option.completed {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-option.delayed {
  background-color: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.status-option.on-hold {
  background-color: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.status-option.cancelled {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

/* 状态选择器下拉框样式 */
:deep(.status-select-dropdown) {
  z-index: 9999 !important;
}

:deep(.status-select-dropdown .el-select-dropdown__item) {
  padding: 8px 12px;
}

:deep(.status-select-dropdown .el-select-dropdown__item:hover) {
  background-color: #f5f7fa;
}

/* 确认对话框样式优化 */
:deep(.el-popconfirm) {
  z-index: 10000 !important;
}

:deep(.el-popconfirm__main) {
  z-index: 10001 !important;
}

/* 状态颜色标识 */
.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 4px;
  display: inline-block;
}

.status-planning {
  background-color: #1890ff;
}

.status-in_progress {
  background-color: #52c41a;
}

.status-on_hold {
  background-color: #fa8c16;
}

.status-completed {
  background-color: #52c41a;
}

.status-delayed {
  background-color: #f5222d;
}

.status-cancelled {
  background-color: #8c8c8c;
}

/* 进度条样式 - 简洁版 */
.progress-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  min-width: 0;
}

.project-progress {
  width: 100%;
}

.progress-text {
  font-size: 12px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progress-completed {
  color: #67c23a;
}

.progress-delayed {
  color: #f56c6c;
}

.progress-warning {
  color: #e6a23c;
}

.progress-normal {
  color: #409eff;
}

/* 日期样式 */
.date-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #606266;
  font-size: 12px;
}

/* 操作按钮样式 */
.action-column {
  min-width: 220px;
  position: sticky;
  right: 0;
  background: #fff;
  z-index: 10;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  justify-content: flex-start;
  align-items: center;
  min-width: 180px;
}

.action-buttons .el-button {
  margin: 0;
  padding: 6px 10px;
  font-size: 12px;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .action-buttons .el-button {
    padding: 4px 8px;
    font-size: 11px;
  }
  
  .action-buttons .el-button .el-icon {
    margin-right: 3px;
  }
  
  /* 调整表格列宽度 */
  .projects-table {
    min-width: 1000px;
  }
  
  .stats-section .el-col {
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .projects-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 20px;
  }
  
  .page-header h1 {
    font-size: 20px;
    margin-bottom: 8px;
  }
  
  .page-header p {
    font-size: 14px;
  }
  
  .stats-section {
    margin-bottom: 20px;
  }
  
  .stats-section .el-col {
    margin-bottom: 16px;
  }
  
  .stats-section .el-row {
    margin-bottom: 0;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }
  
  .header-actions .el-input,
  .header-actions .el-select {
    width: 100% !important;
    margin-right: 0 !important;
  }
  
  .header-actions .el-button {
    width: 100%;
  }
  
  /* 移动端表格优化 */
  .table-container {
    margin: 0 -16px;
    border-radius: 0;
  }
  
  .projects-table {
    min-width: 900px;
    font-size: 12px;
  }
  
  /* 移动端按钮样式优化 */
  .action-column {
    min-width: 180px;
  }
  
  .action-buttons {
    gap: 4px;
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-buttons .el-button {
    padding: 6px 8px;
    font-size: 11px;
    width: 100%;
    margin-bottom: 4px;
  }
  
  .action-buttons .el-button:last-child {
    margin-bottom: 0;
  }
  
  .action-buttons .el-button .el-icon {
    margin-right: 4px;
  }
  
  /* 移动端统计卡片优化 */
  .stat-card {
    height: 100px;
    margin-bottom: 16px;
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
}

@media (max-width: 480px) {
  .projects-container {
    padding: 12px;
  }
  
  .page-header h1 {
    font-size: 18px;
  }
  
  .page-header p {
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
  
  .projects-table {
    min-width: 800px;
    font-size: 11px;
  }
  
  .action-buttons .el-button {
    padding: 4px 6px;
    font-size: 10px;
  }
}

/* iPhone 安全区域适配 */
@supports (padding: max(0px)) {
  .projects-container {
    padding-left: max(12px, env(safe-area-inset-left));
    padding-right: max(12px, env(safe-area-inset-right));
  }
  
  .table-container {
    margin-left: max(-16px, calc(-1 * env(safe-area-inset-left)));
    margin-right: max(-16px, calc(-1 * env(safe-area-inset-right)));
  }
}

/* 编辑弹窗样式 */
.edit-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 30px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.dialog-footer {
  text-align: right;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}



@media (max-width: 480px) {
  .projects-container {
    padding: 12px;
  }
  
  .page-header h1 {
    font-size: 20px;
  }
  
  .page-header p {
    font-size: 14px;
  }
  
  .stat-card {
    height: 100px;
  }
  
  .stat-icon {
    font-size: 36px;
    margin-right: 16px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .stat-label {
    font-size: 12px;
  }
}
</style>
