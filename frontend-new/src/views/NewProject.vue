<template>
  <div class="new-project-page">
    <!-- 页面标题 -->
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <div class="title-section">
          <el-button @click="goBack" icon="ArrowLeft" text>返回</el-button>
          <h1 class="page-title">新建项目</h1>
        </div>
        <div class="header-actions">
          <el-button @click="resetForm" :disabled="!hasChanges">重置</el-button>
          <el-button type="primary" @click="handleCreateProject" :loading="creating" :disabled="!hasChanges">
            创建项目
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 项目表单 -->
    <el-card class="form-card" shadow="never">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
        class="project-form"
      >
        <!-- 基础信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Document /></el-icon>
            基础信息
          </h3>
          
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目名称" prop="name" required>
                <el-input 
                  v-model="form.name" 
                  placeholder="请输入项目名称"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目编号" prop="project_code" required>
                <div class="code-input-group">
                  <el-input 
                    v-model="form.project_code" 
                    placeholder="自动生成"
                    maxlength="50"
                    readonly
                    class="readonly-input"
                  />
                  <el-button 
                    @click="regenerateProjectCode" 
                    type="info" 
                    size="small"
                    class="regenerate-btn"
                  >
                    重新生成
                  </el-button>
                </div>
                <div class="form-hint">系统自动生成，不可修改</div>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目类型" prop="project_type" required>
                <el-select v-model="form.project_type" placeholder="请选择项目类型" style="width: 100%;">
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
              <el-form-item label="项目状态" prop="status" required>
                <el-select v-model="form.status" placeholder="请选择项目状态" style="width: 100%;">
                  <el-option label="规划中" value="planning" />
                  <el-option label="进行中" value="in_progress" />
                  <el-option label="暂停" value="on_hold" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已取消" value="cancelled" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目优先级" prop="priority">
                <el-select v-model="form.priority" placeholder="请选择优先级" style="width: 100%;">
                  <el-option label="低" value="low" />
                  <el-option label="中" value="medium" />
                  <el-option label="高" value="high" />
                  <el-option label="紧急" value="urgent" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目经理" prop="manager_name" required>
                <el-input 
                  v-model="form.manager_name" 
                  placeholder="请输入项目经理姓名"
                  maxlength="100"
                />
              </el-form-item>
            </el-col>
            

          </el-row>
        </div>

        <!-- 时间管理 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Clock /></el-icon>
            时间管理
          </h3>
          
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="开始日期" prop="start_date" required>
                <el-date-picker 
                  v-model="form.start_date" 
                  type="date" 
                  placeholder="选择开始日期" 
                  style="width: 100%;"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="计划结束日期" prop="end_date" required>
                <el-date-picker 
                  v-model="form.end_date" 
                  type="date" 
                  placeholder="选择结束日期" 
                  style="width: 100%;"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="预计工期(天)">
                <el-input-number 
                  v-model="form.estimated_duration" 
                  :min="1" 
                  :max="3650"
                  style="width: 100%;"
                  placeholder="自动计算"
                  readonly
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 财务信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Money /></el-icon>
            财务信息
          </h3>
          
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目预算" prop="budget">
                <el-input-number 
                  v-model="form.budget" 
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
                  v-model="form.contract_amount" 
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

        <!-- 位置和联系信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Location /></el-icon>
            位置和联系信息
          </h3>
          
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目地址" prop="address">
                <el-input 
                  v-model="form.address" 
                  placeholder="请输入项目地址"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="甲方名称">
                <el-input 
                  v-model="form.client_name" 
                  placeholder="请输入甲方名称"
                  maxlength="100"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="甲方联系人">
                <el-input 
                  v-model="form.client_contact" 
                  placeholder="请输入甲方联系人"
                  maxlength="50"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="甲方联系电话">
                <el-input 
                  v-model="form.client_phone" 
                  placeholder="请输入甲方联系电话"
                  maxlength="20"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目标签">
                <el-select 
                  v-model="form.tags" 
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
            </el-col>
          </el-row>
        </div>

        <!-- 项目描述 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Document /></el-icon>
            项目描述
          </h3>
          
          <el-form-item label="项目描述" prop="description">
            <el-input 
              v-model="form.description" 
              type="textarea" 
              :rows="4" 
              placeholder="请详细描述项目内容、目标、技术要求等"
              maxlength="1000"
              show-word-limit
            />
          </el-form-item>
        </div>


      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, 
  Document, 
  Clock, 
  Money, 
  Location 
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const formRef = ref()
const creating = ref(false)

// 表单数据
const form = reactive({
  name: '',
  project_code: '',
  project_type: '',
  status: 'planning',
  priority: 'medium',
  manager_name: '',
  start_date: '',
  end_date: '',
  estimated_duration: 0,
  budget: null,
  contract_amount: null,
  address: '',
  client_name: '',
  client_contact: '',
  client_phone: '',
  tags: [],
  description: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度在2-100个字符', trigger: 'blur' }
  ],
  project_code: [
    { required: true, message: '请输入项目编号', trigger: 'blur' },
    { min: 2, max: 50, message: '项目编号长度在2-50个字符', trigger: 'blur' }
  ],
  project_type: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
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
  contract_amount: [
    { required: true, message: '请输入合同金额', trigger: 'blur' },
    { type: 'number', min: 0, message: '合同金额必须大于0', trigger: 'blur' }
  ]
}

// 计算属性
const hasChanges = computed(() => {
  return Object.values(form).some(value => {
    if (Array.isArray(value)) {
      return value.length > 0
    }
    return value !== '' && value !== null && value !== 0
  })
})

// 监听日期变化，自动计算工期
watch([() => form.start_date, () => form.end_date], ([startDate, endDate]) => {
  if (startDate && endDate) {
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffTime = Math.abs(end - start)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    form.estimated_duration = diffDays
  }
})

// 方法
const goBack = () => {
  if (hasChanges.value) {
    ElMessageBox.confirm(
      '表单已修改，确定要离开吗？',
      '确认离开',
      {
        confirmButtonText: '确定离开',
        cancelButtonText: '继续编辑',
        type: 'warning'
      }
    ).then(() => {
      router.push('/projects')
    }).catch(() => {
      // 用户取消，继续编辑
    })
  } else {
    router.push('/projects')
  }
}

const resetForm = () => {
  ElMessageBox.confirm(
    '确定要重置所有表单数据吗？',
    '确认重置',
    {
      confirmButtonText: '确定重置',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    formRef.value?.resetFields()
    Object.keys(form).forEach(key => {
      if (Array.isArray(form[key])) {
        form[key] = []
      } else if (typeof form[key] === 'number') {
        form[key] = 0
      } else {
        form[key] = ''
      }
    })
    form.status = 'planning'
    form.priority = 'medium'
    form.estimated_duration = 0
    
    // 重新生成项目编号
    generateUniqueProjectCode()
    
    ElMessage.success('表单已重置')
  }).catch(() => {
    // 用户取消
  })
}

const handleCreateProject = async () => {
  try {
    await formRef.value?.validate()
    
    creating.value = true
    
    // 准备提交数据
    const submitData = {
      name: form.name,
      project_code: form.project_code,
      project_type: form.project_type,
      status: form.status,
      priority: form.priority,
      manager_name: form.manager_name,
      start_date: form.start_date,
      end_date: form.end_date,
      budget: form.budget,
      contract_amount: form.contract_amount,
      address: form.address,
      client_name: form.client_name,
      client_contact: form.client_contact,
      client_phone: form.client_phone,
      tags: form.tags,
      description: form.description
    }
    
    console.log('DEBUG: 准备提交的数据:', submitData)
    
    // 调用API创建项目
    const response = await fetch('/api/v1/projects', {
      method: 'POST',
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
    
    ElMessage.success('项目创建成功！')
    
    // 跳转到项目列表页面
    router.push('/projects')
    
  } catch (error) {
    console.error('创建项目失败:', error)
    
    // 处理HTTP错误
    if (error.message && error.message.includes('HTTP error')) {
      const status = error.message.match(/status: (\d+)/)?.[1]
      if (status === '400') {
        ElMessage.error('创建项目失败：请检查表单数据，确保所有必填字段都已填写')
      } else if (status === '401') {
        ElMessage.error('创建项目失败：请重新登录')
      } else if (status === '403') {
        ElMessage.error('创建项目失败：权限不足')
      } else {
        ElMessage.error('创建项目失败，请检查网络连接')
      }
    } else {
      // 处理其他错误
      ElMessage.error(`创建项目失败: ${error.message || '未知错误'}`)
    }
  } finally {
    creating.value = false
  }
}

// 生成唯一项目编号
const generateUniqueProjectCode = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  const milliseconds = String(now.getMilliseconds()).padStart(3, '0')
  
  // 生成6位随机数，包含字母和数字
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let randomStr = ''
  for (let i = 0; i < 6; i++) {
    randomStr += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  
  // 格式：PRJ-YYYYMMDD-HHMMSS-MMM-XXXXXX
  // 例如：PRJ-20241201-143052-123-ABC123
  form.project_code = `PRJ-${year}${month}${day}-${hours}${minutes}${seconds}-${milliseconds}-${randomStr}`
}

// 重新生成项目编号
const regenerateProjectCode = () => {
  ElMessageBox.confirm(
    '确定要重新生成项目编号吗？',
    '确认重新生成',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    generateUniqueProjectCode()
    ElMessage.success('项目编号已重新生成')
  }).catch(() => {
    // 用户取消
  })
}

// 页面加载时生成默认项目编号
onMounted(() => {
  generateUniqueProjectCode()
})
</script>

<style scoped>
.new-project-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 20px;
  border-radius: 8px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.form-card {
  border-radius: 8px;
}

.project-form {
  padding: 20px 0;
}

.form-section {
  margin-bottom: 40px;
  padding: 24px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.section-title {
  margin: 0 0 24px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title .el-icon {
  color: #409eff;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.code-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.readonly-input {
  flex: 1;
}

.readonly-input :deep(.el-input__inner) {
  background-color: #f5f7fa;
  color: #606266;
  cursor: not-allowed;
}

.regenerate-btn {
  flex-shrink: 0;
  white-space: nowrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .new-project-page {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .form-section {
    padding: 16px;
    margin-bottom: 24px;
  }
  
  .section-title {
    font-size: 16px;
    margin-bottom: 16px;
  }
}

@media (max-width: 480px) {
  .new-project-page {
    padding: 12px;
  }
  
  .form-section {
    padding: 12px;
  }
  
  .page-title {
    font-size: 20px;
  }
}
</style>
