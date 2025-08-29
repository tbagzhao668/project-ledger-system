# 用户管理API测试方案

## 🎯 测试目标
验证用户管理API的完整功能，包括CRUD操作、权限控制、数据验证等。

## 📋 测试环境
- **API服务器**: http://192.168.10.38:8000
- **API文档**: http://192.168.10.38:8000/docs
- **测试工具**: Postman、curl、或PowerShell Invoke-WebRequest

---

## 🚀 测试步骤

### 第1步：创建测试租户和管理员

#### 1.1 注册租户
```bash
# PowerShell
$registerData = @{
    company_name = "测试建筑公司"
    industry_type = "construction"
    company_size = "small"
    admin_name = "张三"
    admin_email = "admin@test.com"
    admin_phone = "13800138000"
    password = "123456"
    confirm_password = "123456"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/auth/register" `
    -Method POST `
    -Body $registerData `
    -ContentType "application/json" `
    -UseBasicParsing
```

**预期结果**: 
- 状态码: 200
- 返回: 注册成功信息，包含租户ID和域名

#### 1.2 管理员登录获取Token
```bash
# PowerShell
$loginData = @{
    email = "admin@test.com"
    password = "123456"
    remember_me = $false
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/auth/login" `
    -Method POST `
    -Body $loginData `
    -ContentType "application/json" `
    -UseBasicParsing

$tokenData = $loginResponse.Content | ConvertFrom-Json
$accessToken = $tokenData.access_token
Write-Host "Access Token: $accessToken"
```

**预期结果**:
- 状态码: 200
- 返回: JWT令牌和用户信息

---

### 第2步：测试用户管理功能

#### 2.1 获取当前用户信息
```bash
# PowerShell
$headers = @{
    "Authorization" = "Bearer $accessToken"
}

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/me" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 当前登录用户的详细信息

#### 2.2 创建新用户
```bash
# PowerShell
$newUserData = @{
    username = "李四"
    email = "lisi@test.com"
    password = "123456"
    role = "finance"
    permissions = @("transaction_read", "transaction_create")
    profile = @{
        name = "李四"
        phone = "13800138001"
        department = "财务部"
        position = "会计"
    }
    is_active = $true
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/" `
    -Method POST `
    -Body $newUserData `
    -ContentType "application/json" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 新创建用户的信息

#### 2.3 获取用户列表
```bash
# PowerShell
# 基本列表
Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/" `
    -Headers $headers `
    -UseBasicParsing

# 带搜索的列表
Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/?search=李四&page=1&per_page=10" `
    -Headers $headers `
    -UseBasicParsing

# 按角色筛选
Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/?role=finance" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 分页的用户列表，包含总数和页面信息

#### 2.4 获取用户统计信息
```bash
# PowerShell
Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/statistics" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 用户统计数据（总数、激活数、角色分布等）

#### 2.5 更新用户信息
```bash
# PowerShell (假设新用户ID为 user_id)
$updateData = @{
    username = "李四-更新"
    role = "manager"
    permissions = @("user_read", "transaction_read", "transaction_create", "project_read")
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/$userId" `
    -Method PUT `
    -Body $updateData `
    -ContentType "application/json" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 更新后的用户信息

#### 2.6 更新用户密码
```bash
# PowerShell
$passwordData = @{
    current_password = "123456"
    new_password = "newpassword123"
    confirm_password = "newpassword123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/$userId/password" `
    -Method PUT `
    -Body $passwordData `
    -ContentType "application/json" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 密码更新成功信息

#### 2.7 更新用户资料
```bash
# PowerShell
$profileData = @{
    name = "李四-财务经理"
    phone = "13800138002"
    department = "财务部"
    position = "财务经理"
    bio = "负责公司财务管理和项目成本控制"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/me/profile" `
    -Method PUT `
    -Body $profileData `
    -ContentType "application/json" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 更新后的用户信息

#### 2.8 停用用户
```bash
# PowerShell
Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/$userId/deactivate" `
    -Method POST `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 用户停用成功信息

#### 2.9 激活用户
```bash
# PowerShell
Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/$userId/activate" `
    -Method POST `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 200
- 返回: 用户激活成功信息

---

### 第3步：权限测试

#### 3.1 创建普通用户并测试权限
```bash
# 创建一个没有用户管理权限的普通用户
$normalUserData = @{
    username = "王五"
    email = "wangwu@test.com"
    password = "123456"
    role = "viewer"
    permissions = @("transaction_read")
    is_active = $true
} | ConvertTo-Json

# 用管理员身份创建
Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/" `
    -Method POST `
    -Body $normalUserData `
    -ContentType "application/json" `
    -Headers $headers `
    -UseBasicParsing
```

#### 3.2 普通用户登录
```bash
$normalLoginData = @{
    email = "wangwu@test.com"
    password = "123456"
} | ConvertTo-Json

$normalLoginResponse = Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/auth/login" `
    -Method POST `
    -Body $normalLoginData `
    -ContentType "application/json" `
    -UseBasicParsing

$normalToken = ($normalLoginResponse.Content | ConvertFrom-Json).access_token
```

#### 3.3 测试权限限制
```bash
# 普通用户尝试创建用户（应该失败）
$normalHeaders = @{
    "Authorization" = "Bearer $normalToken"
}

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/" `
    -Method POST `
    -Body $newUserData `
    -ContentType "application/json" `
    -Headers $normalHeaders `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 403
- 返回: 权限不足错误

---

### 第4步：错误处理测试

#### 4.1 测试重复邮箱
```bash
# 尝试创建相同邮箱的用户
$duplicateUserData = @{
    username = "重复用户"
    email = "lisi@test.com"  # 已存在的邮箱
    password = "123456"
    role = "viewer"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/" `
    -Method POST `
    -Body $duplicateUserData `
    -ContentType "application/json" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 400
- 返回: 邮箱已存在错误

#### 4.2 测试无效数据
```bash
# 密码太短
$invalidUserData = @{
    username = "测试用户"
    email = "invalid@test.com"
    password = "123"  # 太短
    role = "viewer"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/" `
    -Method POST `
    -Body $invalidUserData `
    -ContentType "application/json" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 422
- 返回: 数据验证错误

#### 4.3 测试不存在的用户
```bash
# 获取不存在的用户
$fakeUserId = "00000000-0000-0000-0000-000000000000"
Invoke-WebRequest -Uri "http://192.168.10.38:8000/api/v1/users/$fakeUserId" `
    -Headers $headers `
    -UseBasicParsing
```

**预期结果**:
- 状态码: 404
- 返回: 用户不存在错误

---

## 📊 测试检查清单

### 功能测试 ✅
- [ ] 用户创建
- [ ] 用户列表获取（分页、搜索、筛选）
- [ ] 用户信息获取
- [ ] 用户信息更新
- [ ] 密码更新
- [ ] 用户资料更新
- [ ] 用户激活/停用
- [ ] 用户统计信息

### 安全测试 ✅
- [ ] JWT认证验证
- [ ] 权限控制验证
- [ ] 多租户隔离验证
- [ ] 密码加密验证

### 错误处理测试 ✅
- [ ] 重复数据处理
- [ ] 无效数据验证
- [ ] 资源不存在处理
- [ ] 权限不足处理

### 性能测试 ✅
- [ ] 列表分页性能
- [ ] 搜索查询性能
- [ ] 并发请求处理

---

## 🐛 常见问题排查

### 1. 认证失败
- 检查JWT令牌是否正确
- 检查令牌是否过期
- 检查Authorization头格式

### 2. 权限不足
- 检查用户角色和权限配置
- 检查API端点所需权限

### 3. 数据验证错误
- 检查请求体格式
- 检查必填字段
- 检查数据类型和长度限制

### 4. 服务器错误
- 检查API服务器日志
- 检查数据库连接
- 检查网络连接

---

## 📈 测试报告模板

```
用户管理API测试报告
===============

测试日期: [日期]
测试环境: [环境信息]
测试人员: [姓名]

测试结果汇总:
- 功能测试: [通过数]/[总数]
- 安全测试: [通过数]/[总数]  
- 错误处理: [通过数]/[总数]
- 性能测试: [通过数]/[总数]

详细测试结果:
[具体测试结果和问题记录]

建议和改进:
[测试建议和发现的问题]
```

---

## 🔧 下一步测试建议

1. **完成用户管理API测试**
2. **继续项目管理API开发和测试**
3. **开发财务记录API**
4. **集成测试各模块API**
5. **开始前端界面开发**
