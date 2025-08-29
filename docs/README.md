# 工程项目流水账管理系统

## 项目简介

这是一个基于Python FastAPI + Vue.js + PostgreSQL的工程项目流水账管理系统，支持多租户架构，提供完整的项目管理、财务记录、权限管理等功能。

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL
- **认证**: JWT + bcrypt
- **缓存**: Redis
- **异步任务**: Celery

### 前端
- **框架**: Vue 3 + Composition API
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **构建工具**: Vite
- **样式**: SCSS

## 项目结构

```
工程项目流水账/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   └── utils/          # 工具函数
│   ├── requirements.txt    # Python依赖
│   └── main.py            # 启动文件
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   ├── utils/          # 工具函数
│   │   └── router/         # 路由配置
│   ├── package.json        # Node.js依赖
│   └── vite.config.js      # Vite配置
├── scripts/                # 部署脚本
│   ├── start-backend.sh    # 后端启动脚本
│   ├── start-frontend-improved.sh  # 前端启动脚本
│   └── check-backend-status.sh     # 状态检查脚本
├── docs/                   # 项目文档
└── README.md              # 项目说明
```

## 快速开始

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 使用脚本启动
```bash
# 启动后端
./scripts/start-backend.sh

# 启动前端
./scripts/start-frontend-improved.sh

# 检查后端状态
./scripts/check-backend-status.sh
```

## 主要功能

### 1. 用户认证系统
- ✅ 租户注册
- ✅ 用户登录
- ✅ JWT认证
- ✅ 权限控制

### 2. 项目管理
- ✅ 项目创建/编辑/删除
- ✅ 项目状态管理
- ✅ 里程碑管理
- ✅ 团队成员管理

### 3. 财务管理
- ✅ 收入/支出记录
- ✅ 财务分类管理
- ✅ 财务统计报表
- ✅ 预算管理

### 4. 供应商管理
- ✅ 供应商信息管理
- ✅ 合同管理
- ✅ 付款记录

### 5. 数据可视化
- ✅ 项目进度图表
- ✅ 财务趋势分析
- ✅ 统计仪表盘

## 部署说明

### 服务器要求
- Ubuntu 24.0.0+
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 6+

### 环境变量配置
```bash
# 后端环境变量
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# 前端环境变量
VITE_API_BASE_URL=http://your-server-ip:8000
```

## 开发状态

- ✅ 用户认证系统 - 已完成
- ✅ 项目管理界面 - 已完成
- ✅ 基础架构搭建 - 已完成
- 🔄 财务管理界面 - 开发中
- 🔄 供应商管理界面 - 开发中
- 🔄 数据可视化 - 开发中
- 🔄 响应式设计 - 开发中

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系开发团队。
