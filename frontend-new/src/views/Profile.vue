<template>
  <div class="profile-container">
    <div class="page-header">
      <h1>个人资料</h1>
      <p>管理您的个人信息（仅限非登录相关信息）</p>
    </div>
    
    <div class="profile-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="profile-card">
            <div class="avatar-section">
              <el-avatar :size="120" :src="userProfile.avatar">
                {{ userProfile.name.charAt(0).toUpperCase() }}
              </el-avatar>
              <el-button type="primary" style="margin-top: 16px;">更换头像</el-button>
            </div>
            
            <div class="user-info">
              <h3>{{ userProfile.name }}</h3>
              <p>{{ userProfile.role }}</p>
              <p>{{ userProfile.email }}</p>
              <p class="note">邮箱作为登录账号，不可修改</p>
            </div>
          </el-card>
          
          <!-- 企业信息卡片 -->
          <el-card class="profile-card company-card">
            <template #header>
              <span>企业信息</span>
            </template>
            
            <div class="company-info">
              <div class="company-item">
                <label>企业名称：</label>
                <span>{{ companyInfo.name || '未设置' }}</span>
              </div>
              <div class="company-item">
                <label>行业类型：</label>
                <span>{{ getIndustryTypeText(companyInfo.industry_type) }}</span>
              </div>
              <div class="company-item">
                <label>企业规模：</label>
                <span>{{ getCompanySizeText(companyInfo.company_size) }}</span>
              </div>
              <div class="company-item">
                <label>注册时间：</label>
                <span>{{ formatDate(companyInfo.created_at) }}</span>
              </div>
              
              <el-button 
                type="primary" 
                size="small" 
                @click="showCompanyEditDialog = true"
                style="margin-top: 16px; width: 100%;"
              >
                编辑企业信息
              </el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <el-card class="profile-card">
            <template #header>
              <span>基本信息</span>
            </template>
            
            <el-form :model="userProfile" label-width="100px">
              <el-form-item label="姓名">
                <el-input v-model="userProfile.name" />
              </el-form-item>
              
              <el-form-item label="邮箱">
                <el-input v-model="userProfile.email" disabled />
                <span class="disabled-note">邮箱作为登录账号，不可修改</span>
              </el-form-item>
              
              <el-form-item label="手机号">
                <el-input v-model="userProfile.phone" />
              </el-form-item>
              
              <el-form-item label="职位">
                <el-input v-model="userProfile.position" />
              </el-form-item>
              
              <el-form-item label="部门">
                <el-input v-model="userProfile.department" />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveProfile" :loading="saving">保存修改</el-button>
                <el-button @click="resetProfile">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
          
          <!-- 修改密码卡片 -->
          <el-card class="profile-card" style="margin-top: 20px;">
            <template #header>
              <span>修改密码</span>
            </template>
            
            <el-form :model="passwordForm" label-width="100px">
              <el-form-item label="当前密码">
                <el-input 
                  v-model="passwordForm.oldPassword" 
                  type="password" 
                  show-password
                  placeholder="请输入当前密码"
                />
              </el-form-item>
              
              <el-form-item label="新密码">
                <el-input 
                  v-model="passwordForm.newPassword" 
                  type="password" 
                  show-password
                  placeholder="请输入新密码（至少6位）"
                />
              </el-form-item>
              
              <el-form-item label="确认新密码">
                <el-input 
                  v-model="passwordForm.confirmPassword" 
                  type="password" 
                  show-password
                  placeholder="请再次输入新密码"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="warning" @click="changePassword" :loading="changingPassword">修改密码</el-button>
                <el-button @click="resetPasswordForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 编辑企业信息对话框 -->
    <el-dialog
      v-model="showCompanyEditDialog"
      title="编辑企业信息"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="companyForm" label-width="100px">
        <el-form-item label="企业名称" required>
          <el-input v-model="companyForm.name" placeholder="请输入企业名称" />
        </el-form-item>
        
        <el-form-item label="行业类型" required>
          <el-select v-model="companyForm.industry_type" placeholder="请选择行业类型" style="width: 100%;">
            <el-option label="施工单位" value="construction" />
            <el-option label="开发商" value="developer" />
            <el-option label="监理单位" value="supervisor" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="企业规模" required>
          <el-select v-model="companyForm.company_size" placeholder="请选择企业规模" style="width: 100%;">
            <el-option label="小型企业(1-50人)" value="small" />
            <el-option label="中型企业(51-200人)" value="medium" />
            <el-option label="大型企业(201-1000人)" value="large" />
            <el-option label="超大型企业(1000+人)" value="enterprise" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCompanyEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveCompanyInfo" :loading="savingCompany">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 响应式数据
const saving = ref(false)
const changingPassword = ref(false)
const savingCompany = ref(false) // 新增：企业信息保存状态

// 获取auth store
const authStore = useAuthStore()

// 用户资料数据
const userProfile = reactive({
  name: '',
  email: '',
  phone: '',
  position: '',
  department: '',
  role: '',
  avatar: ''
})

// 企业信息数据
const companyInfo = reactive({
  name: '',
  industry_type: '',
  company_size: '',
  created_at: ''
})

// 修改密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 企业信息编辑表单
const companyForm = reactive({
  name: '',
  industry_type: '',
  company_size: ''
})

// 原始数据备份（用于重置）
const originalProfile = ref({})

// 对话框控制
const showCompanyEditDialog = ref(false)

// 监听对话框显示状态，同步数据到编辑表单
watch(showCompanyEditDialog, (newVal) => {
  if (newVal) {
    // 当对话框打开时，同步当前企业信息到编辑表单
    companyForm.name = companyInfo.name
    companyForm.industry_type = companyInfo.industry_type
    companyForm.company_size = companyInfo.company_size
  }
})

// 保存个人资料
const saveProfile = async () => {
  try {
    saving.value = true
    
    // 调用API保存个人资料
    const response = await fetch('/api/v1/auth/me', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        name: userProfile.name,
        phone: userProfile.phone,
        position: userProfile.position,
        department: userProfile.department
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      ElMessage.success(result.message || '个人资料保存成功')
      
      // 同步更新auth store中的用户信息
      console.log('更新前auth store用户名:', authStore.username)
      console.log('要更新的用户信息:', userProfile.name)
      
      authStore.updateUserInfo({
        name: userProfile.name,
        profile: {
          name: userProfile.name,
          phone: userProfile.phone,
          position: userProfile.position,
          department: userProfile.department
        }
      })
      
      console.log('更新后auth store用户名:', authStore.username)
      console.log('auth store用户对象:', authStore.user)
      
      // 更新原始数据备份
      Object.assign(originalProfile.value, { ...userProfile })
      
      // 重新加载用户资料
      await loadProfile()
    } else {
      const errorData = await response.json()
      ElMessage.error(errorData.detail || '保存失败，请重试')
    }
    
  } catch (error) {
    console.error('保存个人资料失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

// 修改密码
const changePassword = async () => {
  try {
    // 验证表单
    if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
      ElMessage.error('请填写完整的密码信息')
      return
    }
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      ElMessage.error('新密码和确认密码不一致')
      return
    }
    
    if (passwordForm.newPassword.length < 6) {
      ElMessage.error('新密码长度不能少于6位')
      return
    }
    
    if (passwordForm.oldPassword === passwordForm.newPassword) {
      ElMessage.error('新密码不能与当前密码相同')
      return
    }
    
    changingPassword.value = true
    
    // 调用API修改密码
    const response = await fetch('/api/v1/auth/me/password', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        old_password: passwordForm.oldPassword,
        new_password: passwordForm.newPassword,
        confirm_password: passwordForm.confirmPassword
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      ElMessage.success(result.message || '密码修改成功')
      
      // 清空密码表单
      resetPasswordForm()
      
      // 提示用户重新登录
      ElMessage.warning('密码已修改，建议您重新登录以确保安全')
    } else {
      const errorData = await response.json()
      ElMessage.error(errorData.detail || '密码修改失败，请重试')
    }
    
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败，请重试')
  } finally {
    changingPassword.value = false
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

// 重置个人资料
const resetProfile = () => {
  Object.assign(userProfile, { ...originalProfile.value })
  ElMessage.info('已重置为上次保存的数据')
}

// 加载个人资料
const loadProfile = async () => {
  try {
    // 调用API获取个人资料
    const response = await fetch('/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (response.ok) {
      const userData = await response.json()
      
      // 更新用户资料
      userProfile.name = userData.profile?.name || userData.username || ''
      userProfile.email = userData.email || ''
      userProfile.phone = userData.profile?.phone || ''
      userProfile.position = userData.profile?.position || ''
      userProfile.department = userData.profile?.department || ''
      userProfile.role = userData.role || ''
      userProfile.avatar = userData.profile?.avatar || ''
      
      // 备份原始数据
      Object.assign(originalProfile.value, { ...userProfile })
      
    } else {
      ElMessage.error('加载个人资料失败')
    }
    
  } catch (error) {
    console.error('加载个人资料失败:', error)
    ElMessage.error('加载个人资料失败')
  }
}

// 加载企业信息
const loadCompanyInfo = async () => {
  try {
    const response = await fetch('/api/v1/auth/tenant', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      if (result.success && result.data) {
        const companyData = result.data
        
        // 使用Object.assign确保响应式更新
        Object.assign(companyInfo, {
          name: companyData.name || '',
          industry_type: companyData.settings?.industry_type || '',
          company_size: companyData.settings?.company_size || '',
          created_at: companyData.created_at || ''
        })
        
        // 同步更新编辑表单
        Object.assign(companyForm, {
          name: companyData.name || '',
          industry_type: companyData.settings?.industry_type || '',
          company_size: companyData.settings?.company_size || ''
        })
        
        console.log('企业信息已加载:', companyInfo)
        console.log('编辑表单已同步:', companyForm)
      }
    } else {
      ElMessage.error('加载企业信息失败')
    }
  } catch (error) {
    console.error('加载企业信息失败:', error)
    ElMessage.error('加载企业信息失败')
  }
}

// 保存企业信息
const saveCompanyInfo = async () => {
  try {
    savingCompany.value = true
    const response = await fetch('/api/v1/auth/tenant', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        name: companyForm.name,
        industry_type: companyForm.industry_type,
        company_size: companyForm.company_size
      })
    })

    if (response.ok) {
      const result = await response.json()
      ElMessage.success(result.message || '企业信息保存成功')
      
      // 立即更新本地数据，确保界面实时反映
      companyInfo.name = companyForm.name
      companyInfo.industry_type = companyForm.industry_type
      companyInfo.company_size = companyForm.company_size
      
      console.log('企业信息已更新:', companyInfo)
      
      showCompanyEditDialog.value = false
      
      // 不再重新加载，保持用户看到的更新结果
      // await loadCompanyInfo()
    } else {
      const errorData = await response.json()
      ElMessage.error(errorData.detail || '保存企业信息失败，请重试')
    }
  } catch (error) {
    console.error('保存企业信息失败:', error)
    ElMessage.error('保存企业信息失败，请重试')
  } finally {
    savingCompany.value = false
  }
}

// 格式化日期
const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 获取行业类型文本
const getIndustryTypeText = (value) => {
  switch (value) {
    case 'contractor':
      return '施工单位'
    case 'construction':
      return '施工单位'
    case 'developer':
      return '开发商'
    case 'supervisor':
      return '监理单位'
    case 'other':
      return '其他'
    default:
      return '未设置'
  }
}

// 获取企业规模文本
const getCompanySizeText = (value) => {
  switch (value) {
    case 'small':
      return '小型企业(1-50人)'
    case 'medium':
      return '中型企业(51-200人)'
    case 'large':
      return '大型企业(201-1000人)'
    case 'enterprise':
      return '超大型企业(1000+人)'
    default:
      return '未设置'
  }
}

// 生命周期
onMounted(() => {
  loadProfile()
  loadCompanyInfo()
})
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
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
  font-weight: 600;
}

.page-header p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.profile-content {
  margin-bottom: 30px;
  width: 100%;
}

.profile-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.avatar-section {
  text-align: center;
  padding: 20px 0;
}

.user-info {
  text-align: center;
  margin-top: 20px;
}

.user-info h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.user-info p {
  margin: 4px 0;
  color: #666;
  font-size: 14px;
}

.user-info .note {
  color: #999;
  font-size: 12px;
  font-style: italic;
}

.disabled-note {
  color: #999;
  font-size: 12px;
  margin-left: 8px;
}

.el-form {
  max-width: 100%;
}

.company-card .el-card__header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  padding: 12px 20px;
}

.company-card .el-card__header span {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.company-card .el-card__body {
  padding: 20px;
}

.company-info {
  display: flex;
  flex-direction: column;
}

.company-item {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.company-item label {
  font-weight: 600;
  color: #333;
  margin-right: 10px;
  font-size: 14px;
  min-width: 80px;
}

.company-item span {
  color: #666;
  font-size: 14px;
  flex: 1;
}

.el-dialog__header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.el-dialog__body {
  padding: 20px;
}

.el-dialog__footer {
  background-color: #f5f7fa;
  border-top: 1px solid #ebeef5;
  padding: 10px 20px;
}

.dialog-footer .el-button {
  width: 100%;
}
</style>
