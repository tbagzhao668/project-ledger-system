<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h2>注册新账户</h2>
        <p>创建您的工程项目管理系统账户</p>
      </div>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="company_name">
          <el-input
            v-model="registerForm.company_name"
            placeholder="请输入企业名称"
            prefix-icon="OfficeBuilding"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="admin_name">
          <el-input
            v-model="registerForm.admin_name"
            placeholder="请输入管理员姓名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="admin_email">
          <el-input
            v-model="registerForm.admin_email"
            placeholder="请输入管理员邮箱"
            prefix-icon="Message"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="admin_phone">
          <el-input
            v-model="registerForm.admin_phone"
            placeholder="请输入管理员电话"
            prefix-icon="Phone"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="industry_type">
          <el-select
            v-model="registerForm.industry_type"
            placeholder="请选择行业类型"
            size="large"
          >
            <el-option label="施工单位" value="contractor" />
            <el-option label="开发商" value="developer" />
            <el-option label="监理单位" value="supervisor" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item prop="company_size">
          <el-select
            v-model="registerForm.company_size"
            placeholder="请选择企业规模"
            size="large"
          >
            <el-option label="小型企业(1-50人)" value="small" />
            <el-option label="中型企业(51-200人)" value="medium" />
            <el-option label="大型企业(201-1000人)" value="large" />
            <el-option label="超大型企业(1000+人)" value="enterprise" />
          </el-select>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item prop="confirm_password">
          <el-input
            v-model="registerForm.confirm_password"
            type="password"
            placeholder="请确认密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="register-button"
            :loading="loading"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-footer">
        <p>已有账户？ <router-link to="/login">立即登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'

const router = useRouter()

// 表单引用
const registerFormRef = ref()

// 注册状态
const loading = ref(false)

// 注册表单数据
const registerForm = reactive({
  company_name: '',
  admin_name: '',
  admin_email: '',
  admin_phone: '',
  industry_type: 'contractor',
  company_size: 'small',
  password: '',
  confirm_password: ''
})

// 表单验证规则
const registerRules = {
  company_name: [
    { required: true, message: '请输入企业名称', trigger: 'blur' },
    { min: 2, max: 100, message: '企业名称长度在2-100个字符', trigger: 'blur' }
  ],
  admin_name: [
    { required: true, message: '请输入管理员姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在2-50个字符', trigger: 'blur' }
  ],
  admin_email: [
    { required: true, message: '请输入管理员邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  admin_phone: [
    { required: true, message: '请输入管理员电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  industry_type: [
    { required: true, message: '请选择行业类型', trigger: 'change' }
  ],
  company_size: [
    { required: true, message: '请选择企业规模', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在6-50个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 处理注册
const handleRegister = async () => {
  try {
    // 表单验证
    await registerFormRef.value.validate()
    
    loading.value = true
    
    // 调用真实的注册API
    const response = await authApi.register({
      company_name: registerForm.company_name,
      admin_name: registerForm.admin_name,
      admin_email: registerForm.admin_email,
      admin_phone: registerForm.admin_phone,
      industry_type: registerForm.industry_type,
      company_size: registerForm.company_size,
      password: registerForm.password,
      confirm_password: registerForm.confirm_password
    })
    
    if (response.success) {
      ElMessage.success(response.message || '注册成功！')
      
      // 注册成功后跳转到登录页
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      ElMessage.error(response.detail || '注册失败')
    }
    
  } catch (error) {
    console.error('注册错误:', error)
    ElMessage.error(error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  color: #333;
  margin-bottom: 10px;
  font-size: 24px;
}

.register-header p {
  color: #666;
  font-size: 14px;
}

.register-form {
  margin-bottom: 20px;
}

.register-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-footer a {
  color: #409eff;
  text-decoration: none;
}

.register-footer a:hover {
  text-decoration: underline;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .register-box {
    width: 90% !important;
    margin: 0 20px;
  }
}
</style>