# 监控系统技术设计文档 (TDD)

## 📋 文档信息
- **文档版本**: v1.0
- **创建日期**: 2025-08-27
- **文档状态**: 草稿
- **负责人**: 技术架构师

## 🏗️ 系统架构设计

### 整体架构
```
前端管理界面 (Vue.js 3 + Element Plus)
    ↓
Nginx 代理 (负载均衡 + 路由)
    ↓
FastAPI 后端服务 (监控 + 租户管理)
    ↓
PostgreSQL 数据库 (监控数据 + 租户数据)
```

### 模块架构
```
监控系统
├── 前端模块
│   ├── 监控仪表盘
│   ├── 租户管理
│   └── 操作日志
├── 后端模块
│   ├── 监控服务
│   ├── 租户管理服务
│   └── 健康检查服务
└── 数据模块
    ├── 监控数据表
    ├── 操作日志表
    └── 统计缓存表
```

## 🗄️ 数据库设计

### 1. 监控数据表 (monitoring_data)
```sql
CREATE TABLE monitoring_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    service_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    response_time INTEGER,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. 操作日志表 (admin_operation_logs)
```sql
CREATE TABLE admin_operation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID REFERENCES users(id),
    operation_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id UUID,
    operation_details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. 系统统计表 (system_statistics)
```sql
CREATE TABLE system_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    stat_date DATE NOT NULL,
    stat_type VARCHAR(50) NOT NULL,
    stat_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔌 API 接口设计

### 1. 监控相关接口
- `GET /api/v1/admin/health` - 系统健康检查
- `GET /api/v1/admin/monitoring` - 获取监控数据
- `GET /api/v1/admin/statistics/overview` - 系统统计概览

### 2. 租户管理接口
- `GET /api/v1/admin/tenants` - 获取租户列表
- `PUT /api/v1/admin/tenants/{tenant_id}/reset-password` - 重置密码
- `PUT /api/v1/admin/tenants/{tenant_id}/status` - 更新状态

### 3. 统计信息接口
- `GET /api/v1/admin/statistics/tenant-activity` - 租户活跃度统计

## 🎨 前端设计

### 1. 页面结构
- 主布局：左侧导航 + 主内容区
- 监控仪表盘：服务状态卡片 + 统计信息
- 租户管理：搜索筛选 + 租户列表 + 操作按钮

### 2. 状态管理
- 监控状态管理 (Pinia Store)
- 租户管理状态 (Pinia Store)
- 实时数据更新

## 🔒 安全设计

### 1. 权限控制
- 只有super_admin角色可访问
- 操作审计日志
- 数据隔离

### 2. 操作审计
- 记录所有管理员操作
- IP地址和用户代理记录
- 操作详情存储

## 📊 性能优化

### 1. 数据缓存
- Redis缓存统计数据
- 异步数据采集
- 数据库查询优化

### 2. 异步处理
- 并发健康检查
- 异步日志记录
- 非阻塞操作

## 🚀 部署配置

### 1. Docker配置
- Python 3.11基础镜像
- 依赖安装
- 端口暴露

### 2. Nginx配置
- 监控系统路由
- API代理转发
- 负载均衡

## 🧪 测试策略

### 1. 单元测试
- 服务层测试
- 数据层测试
- 工具函数测试

### 2. 集成测试
- API接口测试
- 数据库集成测试
- 前端组件测试

## 📋 开发检查清单

### 第一阶段：基础监控
- [ ] 创建监控数据表
- [ ] 实现健康检查服务
- [ ] 开发监控API接口
- [ ] 创建监控仪表盘页面

### 第二阶段：租户管理
- [ ] 创建操作日志表
- [ ] 实现租户管理API
- [ ] 开发租户管理页面
- [ ] 实现密码重置功能

### 第三阶段：完善功能
- [ ] 实现活跃度分析
- [ ] 添加数据导出功能
- [ ] 完善操作日志
- [ ] 系统测试和优化

---

**文档版本历史**
| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2025-08-27 | 初始版本 | 技术架构师 |
