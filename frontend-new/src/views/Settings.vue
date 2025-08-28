<template>
  <div class="settings-container">
    <div class="page-header">
      <h1>系统设置</h1>
      <p>管理系统配置和用户偏好</p>
    </div>
    
    <div class="settings-content">
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="基本设置" name="basic">
          <el-form :model="basicSettings" label-width="120px">
            <el-form-item label="系统名称" required>
              <el-input 
                v-model="basicSettings.systemName" 
                placeholder="请输入系统名称"
                maxlength="50"
                show-word-limit
              />
              <div class="form-tip">系统名称将显示在页面左上角</div>
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input 
                v-model="basicSettings.description" 
                type="textarea" 
                :rows="3"
                placeholder="请输入系统描述"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings" :loading="savingBasic">保存设置</el-button>
              <el-button @click="resetBasicSettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="安全设置" name="security">
          <el-form :model="securitySettings" label-width="120px">
            <el-form-item label="会话超时" required>
              <el-input-number 
                v-model="securitySettings.sessionTimeout" 
                :min="15" 
                :max="1440"
                :step="15"
                controls-position="right"
              />
              <span style="margin-left: 8px;">分钟</span>
              <div class="form-tip">设置用户登录后的会话超时时间，超时后需要重新登录</div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings" :loading="savingSecurity">保存设置</el-button>
              <el-button @click="resetSecuritySettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const activeTab = ref('basic')

// 基本设置
const basicSettings = reactive({
  systemName: '工程项目流水账',
  description: '专业的工程项目财务管理系统'
})

// 安全设置
const securitySettings = reactive({
  sessionTimeout: 120
})

// 保存状态
const savingBasic = ref(false)
const savingSecurity = ref(false)

// 原始设置备份（用于重置）
const originalBasicSettings = ref({})
const originalSecuritySettings = ref({})

// 加载系统设置
const loadSettings = async () => {
  try {
    // 从后端API加载系统设置
    const response = await fetch('/api/v1/system', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      if (result.success && result.data) {
        // 更新基本设置
        if (result.data.system) {
          basicSettings.systemName = result.data.system.system_name
          basicSettings.description = result.data.system.description
        }
        
        // 更新安全设置
        if (result.data.security) {
          securitySettings.sessionTimeout = result.data.security.session_timeout
        }
        
        // 同步更新auth store中的系统名称
        authStore.updateSystemName(basicSettings.systemName)
        
        // 更新原始数据备份
        Object.assign(originalBasicSettings.value, { ...basicSettings })
        Object.assign(originalSecuritySettings.value, { ...securitySettings })
        
        console.log('系统设置已从后端加载:', { basicSettings, securitySettings })
      }
    } else {
      console.warn('无法从后端加载系统设置，使用默认值')
      // 如果后端加载失败，使用默认值
      if (authStore.systemName) {
        basicSettings.systemName = authStore.systemName
      }
    }
  } catch (error) {
    console.error('加载系统设置失败:', error)
    // 使用默认值
    if (authStore.systemName) {
      basicSettings.systemName = authStore.systemName
    }
  }
}

// 保存基本设置
const saveBasicSettings = async () => {
  try {
    if (!basicSettings.systemName.trim()) {
      ElMessage.error('系统名称不能为空')
      return
    }
    
    savingBasic.value = true
    
    // 调用后端API保存系统设置
    const response = await fetch('/api/v1/system', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        system_name: basicSettings.systemName.trim(),
        description: basicSettings.description || ''
      })
    })

    if (response.ok) {
      const result = await response.json()
      
      // 保存系统名称到auth store，这样左上角就会显示新的系统名称
      authStore.updateSystemName(basicSettings.systemName)
      
      // 更新原始数据备份
      Object.assign(originalBasicSettings.value, { ...basicSettings })
      
      console.log('基本设置已保存到后端:', basicSettings)
      ElMessage.success(result.message || '基本设置保存成功')
    } else {
      const errorData = await response.json()
      ElMessage.error(errorData.detail || '保存失败，请重试')
    }
    
  } catch (error) {
    console.error('保存基本设置失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    savingBasic.value = false
  }
}

// 保存安全设置
const saveSecuritySettings = async () => {
  try {
    if (!securitySettings.sessionTimeout || securitySettings.sessionTimeout < 15) {
      ElMessage.error('会话超时时间不能少于15分钟')
      return
    }
    
    savingSecurity.value = true
    
    // 调用后端API保存安全设置
    const response = await fetch('/api/v1/security', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        session_timeout: securitySettings.sessionTimeout
      })
    })

    if (response.ok) {
      const result = await response.json()
      
      // 更新原始数据备份
      Object.assign(originalSecuritySettings.value, { ...securitySettings })
      
      console.log('安全设置已保存到后端:', securitySettings)
      ElMessage.success(result.message || '安全设置保存成功')
    } else {
      const errorData = await response.json()
      ElMessage.error(errorData.detail || '保存失败，请重试')
    }
    
  } catch (error) {
    console.error('保存安全设置失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    savingSecurity.value = false
  }
}

// 重置基本设置
const resetBasicSettings = () => {
  Object.assign(basicSettings, { ...originalBasicSettings.value })
  ElMessage.info('基本设置已重置')
}

// 重置安全设置
const resetSecuritySettings = () => {
  Object.assign(securitySettings, { ...originalSecuritySettings.value })
  ElMessage.info('安全设置已重置')
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-container {
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

.settings-content {
  margin-bottom: 30px;
  width: 100%;
}

.el-form {
  max-width: 600px;
  padding: 20px 0;
}

.form-tip {
  color: #999;
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.4;
}

.el-tabs {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.el-tab-pane {
  padding: 20px;
}
</style>
