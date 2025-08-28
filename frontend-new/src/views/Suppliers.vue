<template>
  <div class="suppliers-page">
    <div class="page-header">
      <h1>供应商管理</h1>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        新增供应商
      </el-button>
    </div>

    <div class="page-content">
      <el-card>
        <div class="table-container">
          <el-table :data="suppliers" style="width: 100%" v-loading="loading" class="suppliers-table">
            <el-table-column prop="name" label="供应商名称" min-width="150" />
            <el-table-column prop="contact_person" label="联系人" min-width="100" />
            <el-table-column prop="phone" label="联系电话" min-width="120" />
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column prop="credit_rating" label="信用等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getCreditRatingType(row.credit_rating)">
                  {{ getCreditRatingText(row.credit_rating) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="transaction_count" label="交易次数" width="100" />
            <el-table-column prop="total_amount" label="累计金额" width="120">
              <template #default="{ row }">
                ¥{{ formatNumber(row.total_amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '活跃' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <div class="action-buttons">
                  <el-button size="small" @click="editSupplier(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteSupplier(row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 新增/编辑供应商对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingSupplier ? '编辑供应商' : '新增供应商'"
      width="600px"
    >
      <el-form :model="supplierForm" :rules="rules" ref="supplierFormRef" label-width="100px">
        <el-form-item label="供应商名称" prop="name">
          <el-input v-model="supplierForm.name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="供应商编码" prop="code">
          <el-input v-model="supplierForm.code" placeholder="请输入供应商编码（可选）" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="supplierForm.contact_person" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="supplierForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="supplierForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input
            v-model="supplierForm.address"
            type="textarea"
            :rows="2"
            placeholder="请输入地址"
          />
        </el-form-item>
        <el-form-item label="经营范围" prop="business_scope">
          <el-input
            v-model="supplierForm.business_scope"
            type="textarea"
            :rows="2"
            placeholder="请输入经营范围（可选）"
          />
        </el-form-item>
        <el-form-item label="资质证书" prop="qualification">
          <el-input
            v-model="supplierForm.qualification"
            type="textarea"
            :rows="2"
            placeholder="请输入资质证书（可选）"
          />
        </el-form-item>
        <el-form-item label="信用等级" prop="credit_rating">
          <el-select v-model="supplierForm.credit_rating" placeholder="请选择信用等级" style="width: 100%">
            <el-option label="优秀" value="excellent" />
            <el-option label="良好" value="good" />
            <el-option label="一般" value="fair" />
            <el-option label="较差" value="poor" />
            <el-option label="未知" value="unknown" />
          </el-select>
        </el-form-item>
        <el-form-item label="付款条件" prop="payment_terms">
          <el-input v-model="supplierForm.payment_terms" placeholder="请输入付款条件" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="supplierForm.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="supplierForm.is_active"
            active-text="活跃"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="saveSupplier">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const showAddDialog = ref(false)
const editingSupplier = ref(null)
const supplierFormRef = ref()

const suppliers = ref([])

// 表单数据
const supplierForm = reactive({
  name: '',
  code: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  business_scope: '',
  qualification: '',
  credit_rating: '',
  payment_terms: '',
  notes: '',
  is_active: true
})

const rules = {
  name: [
    { required: true, message: '请输入供应商名称', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 编辑供应商
const editSupplier = (supplier) => {
  editingSupplier.value = supplier
  Object.assign(supplierForm, {
    name: supplier.name,
    code: supplier.code,
    contact_person: supplier.contact_person,
    phone: supplier.phone,
    email: supplier.email,
    address: supplier.address,
    business_scope: supplier.business_scope,
    qualification: supplier.qualification,
    credit_rating: supplier.credit_rating,
    payment_terms: supplier.payment_terms,
    notes: supplier.notes,
    is_active: supplier.is_active
  })
  showAddDialog.value = true
}

// 删除供应商
const deleteSupplier = async (supplier) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除供应商"${supplier.name}"吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
    
    const response = await fetch(`/api/v1/suppliers/${supplier.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      let errorMessage = '删除失败'
      
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(err => {
            if (typeof err === 'object' && err.msg) {
              return err.msg
            } else if (typeof err === 'string') {
              return err
            } else {
              return JSON.stringify(err)
            }
          }).join(', ')
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else {
          errorMessage = JSON.stringify(errorData.detail)
        }
      }
      
      throw new Error(errorMessage)
    }
    
    ElMessage.success('删除成功')
    await loadSuppliers()
  } catch (error) {
    if (error.message === '用户取消') return
    console.error('删除供应商失败:', error)
    ElMessage.error(`删除失败: ${error.message}`)
  }
}

// 保存供应商
const saveSupplier = async () => {
  try {
    await supplierFormRef.value.validate()
    
    // 构建提交数据，过滤空值
    const submitData = {}
    
    // 必填字段
    submitData.name = supplierForm.name
    
    // 可选字段 - 只添加非空值
    if (supplierForm.code && supplierForm.code.trim()) {
      submitData.code = supplierForm.code.trim()
    }
    if (supplierForm.contact_person && supplierForm.contact_person.trim()) {
      submitData.contact_person = supplierForm.contact_person.trim()
    }
    if (supplierForm.phone && supplierForm.phone.trim()) {
      submitData.phone = supplierForm.phone.trim()
    }
    if (supplierForm.email && supplierForm.email.trim()) {
      // 简单的邮箱格式验证
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (emailRegex.test(supplierForm.email.trim())) {
        submitData.email = supplierForm.email.trim()
      }
    }
    if (supplierForm.address && supplierForm.address.trim()) {
      submitData.address = supplierForm.address.trim()
    }
    if (supplierForm.business_scope && supplierForm.business_scope.trim()) {
      submitData.business_scope = supplierForm.business_scope.trim()
    }
    if (supplierForm.qualification && supplierForm.qualification.trim()) {
      submitData.qualification = supplierForm.qualification.trim()
    }
    if (supplierForm.credit_rating && supplierForm.credit_rating.trim()) {
      // 信用等级必须是有效的枚举值
      const validCreditRatings = ['excellent', 'good', 'fair', 'poor', 'unknown']
      if (validCreditRatings.includes(supplierForm.credit_rating.trim())) {
        submitData.credit_rating = supplierForm.credit_rating.trim()
      }
    }
    if (supplierForm.payment_terms && supplierForm.payment_terms.trim()) {
      submitData.payment_terms = supplierForm.payment_terms.trim()
    }
    if (supplierForm.notes && supplierForm.notes.trim()) {
      submitData.notes = supplierForm.notes.trim()
    }
    
    // 布尔字段
    submitData.is_active = supplierForm.is_active
    
    let response
    if (editingSupplier.value) {
      // 编辑模式
      response = await fetch(`/api/v1/suppliers/${editingSupplier.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(submitData)
      })
    } else {
      // 新增模式
      response = await fetch('/api/v1/suppliers', {
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
      let errorMessage = '操作失败'
      
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          // 处理验证错误数组
          errorMessage = errorData.detail.map(err => {
            if (typeof err === 'object' && err.msg) {
              return err.msg
            } else if (typeof err === 'string') {
              return err
            } else {
              return JSON.stringify(err)
            }
          }).join(', ')
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else {
          errorMessage = JSON.stringify(errorData.detail)
        }
      }
      
      throw new Error(errorMessage)
    }
    
    ElMessage.success(editingSupplier.value ? '更新成功' : '创建成功')
    showAddDialog.value = false
    await loadSuppliers()
    resetForm()
  } catch (error) {
    console.error('保存供应商失败:', error)
    ElMessage.error(error.message || '操作失败')
  }
}

// 重置表单
const resetForm = () => {
  editingSupplier.value = null
  Object.assign(supplierForm, {
    name: '',
    code: '',
    contact_person: '',
    phone: '',
    email: '',
    address: '',
    business_scope: '',
    qualification: '',
    credit_rating: '',
    payment_terms: '',
    notes: '',
    is_active: true
  })
  supplierFormRef.value?.resetFields()
}

// 加载供应商数据
const loadSuppliers = async () => {
  try {
    loading.value = true
    
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
  } finally {
    loading.value = false
  }
}

// 格式化数字
const formatNumber = (value) => {
  if (!value) return '0.00'
  const num = parseFloat(value)
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 获取信用等级文本
const getCreditRatingText = (rating) => {
  const ratingMap = {
    'excellent': '优秀',
    'good': '良好',
    'fair': '一般',
    'poor': '较差',
    'unknown': '未知'
  }
  return ratingMap[rating] || '未知'
}

// 获取信用等级标签类型
const getCreditRatingType = (rating) => {
  const typeMap = {
    'excellent': 'success',
    'good': 'success',
    'fair': 'warning',
    'poor': 'danger',
    'unknown': 'info'
  }
  return typeMap[rating] || 'info'
}

onMounted(() => {
  loadSuppliers()
})
</script>

<style scoped>
.suppliers-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.page-content {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 表格容器样式 */
.table-container {
  overflow-x: auto;
  border-radius: 4px;
}

.suppliers-table {
  min-width: 1200px;
}

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  justify-content: flex-start;
  align-items: center;
  min-width: 160px;
}

.action-buttons .el-button {
  margin: 0;
  padding: 6px 10px;
  font-size: 12px;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .suppliers-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .page-header h1 {
    font-size: 20px;
  }
  
  .page-header .el-button {
    width: 100%;
  }
  
  /* 移动端表格优化 */
  .table-container {
    margin: 0 -16px;
    border-radius: 0;
  }
  
  .suppliers-table {
    min-width: 900px;
    font-size: 12px;
  }
  
  /* 移动端按钮样式优化 */
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
}

@media (max-width: 480px) {
  .suppliers-page {
    padding: 12px;
  }
  
  .page-header h1 {
    font-size: 18px;
  }
  
  .suppliers-table {
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
  .suppliers-page {
    padding-left: max(12px, env(safe-area-inset-left));
    padding-right: max(12px, env(safe-area-inset-right));
  }
  
  .table-container {
    margin-left: max(-16px, calc(-1 * env(safe-area-inset-left)));
    margin-right: max(-16px, calc(-1 * env(safe-area-inset-right)));
  }
}
</style>
