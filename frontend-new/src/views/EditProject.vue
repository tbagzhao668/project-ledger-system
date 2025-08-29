<template>
  <div class="edit-project-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" type="text" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回项目列表
        </el-button>
        <h1>编辑项目</h1>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" @click="handleSaveProject" :loading="saving">
          <el-icon><Check /></el-icon>
          保存修改
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 编辑表单 -->
    <div v-else-if="project" class="edit-form-container">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="edit-form"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Folder /></el-icon>
            基本信息
          </h3>
          
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目名称" prop="name">
                <el-input 
                  v-model="form.name" 
                  placeholder="请输入项目名称"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目编号">
                <el-input 
                  v-model="form.project_code" 
                  disabled
                  placeholder="项目编号不可修改"
                />
                <div class="form-hint">项目编号不可修改</div>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目类型" prop="project_type">
                <el-select 
                  v-model="form.project_type" 
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
                  v-model="form.status" 
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
                  v-model="form.priority" 
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
                  v-model="form.manager_name" 
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
                  v-model="form.start_date"
                  type="date"
                  placeholder="选择开始日期"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="结束时间" prop="end_date">
                <el-date-picker
                  v-model="form.end_date"
                  type="date"
                  placeholder="选择结束日期"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目地址" prop="address">
                <el-input 
                  v-model="form.address" 
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
          <h3 class="section-title">
            <el-icon><Money /></el-icon>
            财务信息
          </h3>
          
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="预算金额" prop="budget">
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

                  <!-- 变更原因说明 -->
          <div class="form-section" v-if="budgetChanged || contractChanged">
            <h3 class="section-title">
              <el-icon><Edit /></el-icon>
              变更原因说明
            </h3>
            
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8" v-if="budgetChanged">
                <el-form-item label="预算变更原因" prop="budget_change_reason">
                  <el-select 
                    v-model="form.budget_change_reason" 
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
                    v-model="form.contract_change_reason" 
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
                    v-model="form.change_description" 
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
          <h3 class="section-title">
            <el-icon><User /></el-icon>
            客户信息
          </h3>
          
          <el-row :gutter="24">
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
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="甲方电话">
                <el-input 
                  v-model="form.client_phone" 
                  placeholder="请输入甲方电话"
                  maxlength="20"
                />
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
          
          <el-form-item label="项目描述">
            <el-input 
              v-model="form.description" 
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
          <h3 class="section-title">
            <el-icon><Collection /></el-icon>
            项目标签
          </h3>
          
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
        </div>
      </el-form>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Check, Folder, Money, Edit, User, Document, Collection } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const saving = ref(false)
const project = ref(null)
const formRef = ref(null)

// 表单数据
const form = reactive({
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

// 原始数据（用于比较变更）
const originalData = ref({})

// 表单验证规则
const rules = {
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

// 计算属性：检测预算是否变更
const budgetChanged = computed(() => {
  return form.budget !== originalData.value.budget
})

// 计算属性：检测合同金额是否变更
const contractChanged = computed(() => {
  return form.contract_amount !== originalData.value.contract_amount
})

// 生命周期
onMounted(() => {
  loadProjectDetail()
})

// 加载项目详情
const loadProjectDetail = async () => {
  try {
    loading.value = true
    const projectId = route.params.id
    
    // 加载项目详情
    
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
    
    // 填充表单数据
    fillFormData(projectData)
    
    // 保存原始数据用于比较
    originalData.value = { ...projectData }
    
  } catch (error) {
    console.error('加载项目详情失败:', error)
    ElMessage.error('加载项目详情失败')
    project.value = null
  } finally {
    loading.value = false
  }
}

// 填充表单数据
const fillFormData = (projectData) => {
  form.name = projectData.name || ''
  form.project_code = projectData.project_code || ''
  form.description = projectData.description || ''
  form.project_type = projectData.project_type || ''
  form.priority = projectData.priority || ''
  form.status = projectData.status || ''
  form.start_date = projectData.start_date || ''
  form.end_date = projectData.planned_end_date || projectData.end_date || ''
  form.budget = projectData.budget || null
  form.contract_amount = projectData.contract_amount || null
  form.address = projectData.address || ''
  form.manager_name = projectData.manager_name || ''
  form.client_name = projectData.client_name || ''
  form.client_contact = projectData.client_contact || ''
  form.client_phone = projectData.client_phone || ''
  form.tags = projectData.tags || []
  
  // 清空变更原因
  form.budget_change_reason = ''
  form.contract_change_reason = ''
  form.change_description = ''
  
  // 表单数据填充完成
}

// 保存项目修改
const handleSaveProject = async () => {
  try {
    // 验证表单
    await formRef.value?.validate()
    
    // 检查是否有变更
    if (!hasChanges.value) {
      ElMessage.info('没有检测到任何变更')
      return
    }
    
    // 检查变更原因和修改说明
    if (budgetChanged.value && !form.budget_change_reason) {
      ElMessage.warning('请填写预算变更原因')
      return
    }
    
    if (contractChanged.value && !form.contract_change_reason) {
      ElMessage.warning('请填写合同变更原因')
      return
    }
    
    if ((budgetChanged.value || contractChanged.value) && !form.change_description) {
      ElMessage.warning('请填写修改说明')
      return
    }
    
    saving.value = true
    
    // 准备提交数据
    const submitData = {
      name: form.name,
      description: form.description,
      project_type: form.project_type,
      priority: form.priority,
      status: form.status,
      start_date: form.start_date ? new Date(form.start_date).toISOString().split('T')[0] : form.start_date,
      end_date: form.end_date ? new Date(form.end_date).toISOString().split('T')[0] : form.end_date,
      budget: form.budget,
      contract_amount: form.contract_amount,
      address: form.address,
      manager_name: form.manager_name,
      client_name: form.client_name,
      client_contact: form.client_contact,
      client_phone: form.client_phone,
      tags: form.tags
    }
    
    // 只有当有变更时才添加变更原因字段
    if (budgetChanged.value || contractChanged.value) {
      submitData.budget_change_reason = form.budget_change_reason
      submitData.contract_change_reason = form.contract_change_reason
      submitData.change_description = form.change_description
    }
    
    // 准备提交修改数据
    
    // 调用API更新项目
    const response = await fetch(`/api/v1/projects/${project.value.id}`, {
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
    
    // 跳转到项目详情页面
    router.push(`/projects/${project.value.id}`)
    
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

// 计算属性：检测是否有变更
const hasChanges = computed(() => {
  return Object.keys(form).some(key => {
    if (key.includes('change_')) return false // 跳过变更原因字段
    if (Array.isArray(form[key])) {
      return JSON.stringify(form[key]) !== JSON.stringify(originalData.value[key] || [])
    }
    return form[key] !== originalData.value[key]
  })
})

// 返回项目列表
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
</script>

<style scoped>
.edit-project-container {
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

.edit-form-container {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 40px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.section-title .el-icon {
  color: #409eff;
  font-size: 20px;
}

.edit-form {
  max-width: 100%;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.not-found {
  text-align: center;
  padding: 60px 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .edit-project-container {
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
  
  .edit-form-container {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .edit-project-container {
    padding: 12px;
  }
  
  .page-header h1 {
    font-size: 20px;
  }
  
  .edit-form-container {
    padding: 16px;
  }
}
</style>
