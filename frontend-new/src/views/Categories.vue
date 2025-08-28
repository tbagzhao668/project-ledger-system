<template>
  <div class="categories-page">
    <div class="page-header">
      <h1>分类管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddCategory">
          <el-icon><Plus /></el-icon>
          新增分类
        </el-button>
        <el-button @click="initializeSystemCategories" :loading="initializing">
          <el-icon><Refresh /></el-icon>
          初始化系统分类
        </el-button>
      </div>
    </div>

    <div class="page-content">
      <!-- 首次使用提醒 -->
      <el-alert
        v-if="showFirstTimeAlert"
        title="欢迎使用分类管理！"
        type="info"
        :closable="false"
        show-icon
        class="first-time-alert"
      >
        <template #default>
          <p>检测到您是第一次使用分类管理功能，建议先点击右上角的"初始化系统分类"按钮来创建常用的默认分类。</p>
          <p>系统预设分类包括：工程款收入、材料费、人工费、机械费等常用分类，可以大大提高后续财务记录的效率。</p>
        </template>
      </el-alert>

      <!-- 空状态提示 -->
      <el-empty
        v-if="!loading && categories.length === 0"
        description="暂无分类数据"
        class="empty-state"
      >
        <template #extra>
          <el-button type="primary" @click="initializeSystemCategories" :loading="initializing">
            <el-icon><Refresh /></el-icon>
            初始化系统分类
          </el-button>
        </template>
      </el-empty>

      <el-card v-if="categories.length > 0">
        <el-table :data="categories" style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="340" />
          <el-table-column prop="name" label="分类名称" />
          <el-table-column prop="icon" label="图标" width="80">
            <template #default="{ row }">
              <span v-if="row.icon" style="font-size: 20px;">{{ row.icon }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="color" label="颜色" width="100">
            <template #default="{ row }">
              <div v-if="row.color" class="color-preview" :style="{ backgroundColor: row.color }"></div>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="parent_name" label="父分类" width="120">
            <template #default="{ row }">
              <span v-if="row.parent_name">{{ row.parent_name }}</span>
              <el-tag v-else size="small" type="info">顶级分类</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="transaction_count" label="交易数量" width="100">
            <template #default="{ row }">
              <el-tag :type="row.transaction_count > 0 ? 'success' : 'info'" size="small">
                {{ row.transaction_count }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_system" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_system ? 'warning' : 'primary'" size="small">
                {{ row.is_system ? '系统' : '自定义' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                {{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="editCategory(row)" :disabled="row.is_system">编辑</el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteCategory(row)"
                :disabled="row.is_system || row.transaction_count > 0"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 新增/编辑分类对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingCategory ? '编辑分类' : '新增分类'"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form :model="categoryForm" :rules="rules" ref="categoryFormRef" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="父分类" prop="parent_id">
          <el-select v-model="categoryForm.parent_id" placeholder="请选择父分类" style="width: 100%" clearable>
            <el-option label="顶级分类" :value="null" />
            <el-option 
              v-for="cat in parentCategories" 
              :key="cat.id" 
              :label="cat.name" 
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="categoryForm.icon" placeholder="请输入图标（emoji或文字）" />
        </el-form-item>
        <el-form-item label="颜色" prop="color">
          <el-color-picker v-model="categoryForm.color" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="categoryForm.sort_order" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="saveCategory" :loading="saving">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const initializing = ref(false)
const showAddDialog = ref(false)
const editingCategory = ref(null)
const categoryFormRef = ref()

const categories = ref([])
const parentCategories = ref([])

// 智能提醒相关
const showFirstTimeAlert = ref(false)
const hasInitializedBefore = ref(false)

const categoryForm = reactive({
  name: '',
  parent_id: null,
  icon: '',
  color: '#409eff',
  sort_order: 0
})

const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 100, message: '分类名称长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

// 格式化日期时间
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '-'
  try {
    const date = new Date(dateTimeStr)
    return date.toLocaleString('zh-CN')
  } catch (error) {
    return dateTimeStr
  }
}

// 处理新增分类
const handleAddCategory = () => {
  // 检查是否建议先初始化系统分类
  if (categories.value.length === 0) {
    ElMessageBox.confirm(
      '检测到您还没有任何分类数据，建议先初始化系统分类来获得常用的默认分类。',
      '提示',
      {
        confirmButtonText: '先初始化系统分类',
        cancelButtonText: '继续新增自定义分类',
        type: 'info'
      }
    ).then(() => {
      // 用户选择先初始化系统分类
      initializeSystemCategories()
    }).catch(() => {
      // 用户选择继续新增自定义分类
      showAddDialog.value = true
    })
  } else {
    showAddDialog.value = true
  }
}

// 检查首次使用状态
const checkFirstTimeUsage = () => {
  // 检查本地存储中是否已经初始化过
  const hasInitialized = localStorage.getItem('categories_initialized')
  
  if (!hasInitialized && categories.value.length === 0) {
    // 第一次使用且没有分类数据，显示提醒
    showFirstTimeAlert.value = true
  } else if (hasInitialized && categories.value.length === 0) {
    // 之前初始化过但当前没有分类数据，可能是被删除了
    showFirstTimeAlert.value = false
  } else if (categories.value.length > 0) {
    // 有分类数据，隐藏提醒
    showFirstTimeAlert.value = false
  }
}

// 加载分类列表
const loadCategories = async () => {
  try {
    loading.value = true
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
    
    // 过滤出可以作为父分类的分类（排除当前编辑的分类）
    parentCategories.value = data.filter(cat => 
      cat.is_active && (!editingCategory.value || cat.id !== editingCategory.value.id)
    )
    
    // 检查是否需要显示首次使用提醒
    checkFirstTimeUsage()
  } catch (error) {
    console.error('加载分类列表失败:', error)
    ElMessage.error('加载分类列表失败')
  } finally {
    loading.value = false
  }
}

// 初始化系统分类
const initializeSystemCategories = async () => {
  try {
    initializing.value = true
    const response = await fetch('/api/v1/categories/initialize', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '初始化失败')
    }
    
    const result = await response.json()
    ElMessage.success(`系统分类初始化完成，创建了 ${result.created_count} 个分类`)
    
    // 设置本地存储标记，表示已经初始化过
    localStorage.setItem('categories_initialized', 'true')
    
    await loadCategories()
  } catch (error) {
    console.error('初始化系统分类失败:', error)
    ElMessage.error(`初始化系统分类失败: ${error.message}`)
  } finally {
    initializing.value = false
  }
}

// 编辑分类
const editCategory = (category) => {
  editingCategory.value = category
  Object.assign(categoryForm, {
    name: category.name,
    parent_id: category.parent_id,
    icon: category.icon || '',
    color: category.color || '#409eff',
    sort_order: category.sort_order || 0
  })
  showAddDialog.value = true
}

// 删除分类
const deleteCategory = async (category) => {
  try {
    if (category.is_system) {
      ElMessage.warning('系统分类不能删除')
      return
    }
    
    if (category.transaction_count > 0) {
      ElMessage.warning('该分类下还有交易记录，无法删除')
      return
    }
    
    await ElMessageBox.confirm(
      `确定要删除分类"${category.name}"吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
    
    const response = await fetch(`/api/v1/categories/${category.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '删除失败')
    }
    
    const result = await response.json()
    if (result.deactivated) {
      ElMessage.success('分类已停用（因为存在关联的交易记录）')
    } else {
      ElMessage.success('分类删除成功')
    }
    
    await loadCategories()
  } catch (error) {
    if (error.message === '用户取消') return
    console.error('删除分类失败:', error)
    ElMessage.error(`删除分类失败: ${error.message}`)
  }
}

// 保存分类
const saveCategory = async () => {
  try {
    await categoryFormRef.value.validate()
    saving.value = true
    
    const submitData = {
      name: categoryForm.name,
      parent_id: categoryForm.parent_id,
      icon: categoryForm.icon || null,
      color: categoryForm.color,
      sort_order: categoryForm.sort_order
    }
    
    let response
    if (editingCategory.value) {
      // 编辑模式
      response = await fetch(`/api/v1/categories/${editingCategory.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(submitData)
      })
    } else {
      // 新增模式
      response = await fetch('/api/v1/categories', {
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
      throw new Error(errorData.detail || '保存失败')
    }
    
    ElMessage.success(editingCategory.value ? '更新成功' : '添加成功')
    showAddDialog.value = false
    resetForm()
    await loadCategories()
  } catch (error) {
    console.error('保存分类失败:', error)
    ElMessage.error(`保存分类失败: ${error.message}`)
  } finally {
    saving.value = false
  }
}

// 重置表单
const resetForm = () => {
  editingCategory.value = null
  Object.assign(categoryForm, {
    name: '',
    parent_id: null,
    icon: '',
    color: '#409eff',
    sort_order: 0
  })
  categoryFormRef.value?.resetFields()
}

// 监听对话框关闭
const handleDialogClose = () => {
  resetForm()
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.categories-page {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.page-content {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.first-time-alert {
  margin-bottom: 20px;
}

.first-time-alert p {
  margin: 8px 0;
  line-height: 1.6;
}

.empty-state {
  margin: 40px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .categories-page {
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
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .categories-page {
    padding: 12px;
  }
  
  .page-header h1 {
    font-size: 18px;
  }
}
</style>
