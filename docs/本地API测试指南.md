# 本地用户管理API测试指南

## 🎯 目标
由于远程服务器网络连接不稳定，我们创建本地测试环境来验证用户管理API功能。

## 🚀 快速本地启动

### 1. 设置本地数据库
```bash
# 使用Docker启动本地PostgreSQL
docker run --name local-postgres -e POSTGRES_PASSWORD=123456 -e POSTGRES_DB=project_ledger -p 5432:5432 -d postgres:15

# 使用Docker启动本地Redis
docker run --name local-redis -p 6379:6379 -d redis:7
```

### 2. 修改配置
编辑 `backend/app/config.py`，添加本地配置：
```python
# 本地测试配置
DATABASE_URL: str = "postgresql+asyncpg://postgres:123456@localhost:5432/project_ledger"
DATABASE_URL_SYNC: str = "postgresql://postgres:123456@localhost:5432/project_ledger"
REDIS_URL: str = "redis://localhost:6379/0"
```

### 3. 启动本地API服务器
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# 或 source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 完整API测试流程

### 测试1: 健康检查
```bash
curl http://localhost:8000/health
```

### 测试2: 查看API文档
访问: http://localhost:8000/docs

### 测试3: 注册租户
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "测试建筑公司",
       "industry_type": "construction",
       "company_size": "small",
       "admin_name": "张三",
       "admin_email": "admin@test.com",
       "admin_phone": "13800138000",
       "password": "123456",
       "confirm_password": "123456"
     }'
```

### 测试4: 管理员登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@test.com",
       "password": "123456"
     }'
```

**保存返回的access_token，后续请求需要使用**

### 测试5: 获取当前用户信息
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/users/me
```

### 测试6: 创建新用户
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "李四",
       "email": "lisi@test.com",
       "password": "123456",
       "role": "finance",
       "permissions": ["transaction_read", "transaction_create"],
       "profile": {
         "name": "李四",
         "phone": "13800138001",
         "department": "财务部",
         "position": "会计"
       },
       "is_active": true
     }'
```

### 测试7: 获取用户列表
```bash
# 基本列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/users/"

# 带搜索
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/users/?search=李四&page=1&per_page=10"

# 按角色筛选
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/users/?role=finance"
```

### 测试8: 获取用户统计
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/users/statistics
```

### 测试9: 更新用户信息
```bash
# 先获取用户ID，然后更新
curl -X PUT "http://localhost:8000/api/v1/users/USER_ID" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "李四-更新",
       "role": "manager",
       "permissions": ["user_read", "transaction_read", "project_read"]
     }'
```

### 测试10: 更新用户资料
```bash
curl -X PUT "http://localhost:8000/api/v1/users/me/profile" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "张三-系统管理员",
       "phone": "13800138000",
       "department": "IT部",
       "position": "系统管理员",
       "bio": "负责系统维护和用户管理"
     }'
```

### 测试11: 权限测试
```bash
# 创建普通用户
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "王五",
       "email": "wangwu@test.com",
       "password": "123456",
       "role": "viewer",
       "permissions": ["transaction_read"],
       "is_active": true
     }'

# 普通用户登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "wangwu@test.com",
       "password": "123456"
     }'

# 用普通用户token尝试创建用户（应该失败）
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Authorization: Bearer NORMAL_USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "测试用户",
       "email": "test@test.com",
       "password": "123456",
       "role": "viewer"
     }'
```

### 测试12: 错误处理测试
```bash
# 重复邮箱测试
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "重复用户",
       "email": "lisi@test.com",
       "password": "123456",
       "role": "viewer"
     }'

# 无效数据测试
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "测试用户",
       "email": "invalid@test.com",
       "password": "123",
       "role": "viewer"
     }'

# 不存在用户测试
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/users/00000000-0000-0000-0000-000000000000"
```

## 📊 预期测试结果

### 成功的测试应该返回：
- **健康检查**: 200状态码，服务信息
- **注册**: 200状态码，成功信息
- **登录**: 200状态码，JWT令牌
- **用户信息**: 200状态码，用户详情
- **创建用户**: 200状态码，新用户信息
- **用户列表**: 200状态码，分页用户列表
- **统计信息**: 200状态码，统计数据

### 错误测试应该返回：
- **权限不足**: 403状态码
- **重复数据**: 400状态码
- **无效数据**: 422状态码
- **资源不存在**: 404状态码

## 🔧 问题排查

### 1. 数据库连接问题
```bash
# 检查PostgreSQL是否运行
docker ps | grep postgres

# 检查数据库连接
psql postgresql://postgres:123456@localhost:5432/project_ledger -c "SELECT 1;"
```

### 2. 模型关系问题
如果遇到SQLAlchemy关系错误，检查：
- `User.created_transactions` 和 `User.approved_transactions` 关系
- `Transaction.created_by_user` 和 `Transaction.approved_by_user` 关系

### 3. 权限问题
确保用户有正确的权限：
- `user_create`, `user_read`, `user_update`, `user_delete`
- `statistics_view`

## 📈 性能测试

### 批量用户创建测试
```bash
# 创建多个用户来测试分页和搜索性能
for i in {1..50}; do
  curl -X POST "http://localhost:8000/api/v1/users/" \
       -H "Authorization: Bearer YOUR_TOKEN" \
       -H "Content-Type: application/json" \
       -d "{
         \"username\": \"用户$i\",
         \"email\": \"user$i@test.com\",
         \"password\": \"123456\",
         \"role\": \"viewer\"
       }" &
done
wait
```

### 分页性能测试
```bash
# 测试大量数据的分页性能
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/users/?page=1&per_page=20"
```

## 🎉 测试完成

完成所有测试后，您将验证：
1. ✅ 用户管理API的所有功能正常
2. ✅ 权限控制系统工作正常
3. ✅ 数据验证和错误处理正确
4. ✅ 性能满足要求

这样就可以确认用户管理API已经完全开发完成并可以投入使用！
