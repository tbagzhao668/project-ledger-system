# 🏗️ 工程项目流水账管理系统

> 专业的多租户工程项目财务管理SaaS系统

[![CI/CD](https://github.com/您的用户名/project-ledger-system/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/您的用户名/project-ledger-system/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/vue.js-3.x-green.svg)](https://vuejs.org/)

## ✨ 功能特性

- 🏢 **多租户架构** - 支持多个企业独立使用
- 📊 **项目管理** - 完整的项目生命周期管理
- 💰 **财务管理** - 收入、支出、预算、利润跟踪
- 👥 **用户管理** - 角色权限、团队协作
- 📈 **报表分析** - 数据可视化、趋势分析
- 🔒 **安全可靠** - JWT认证、数据隔离、审计日志
- 📱 **响应式设计** - 支持PC和移动设备

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+

### 安装部署

1. **克隆仓库**
```bash
git clone https://github.com/您的用户名/project-ledger-system.git
cd project-ledger-system
```

2. **后端设置**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **数据库设置**
```bash
# 创建数据库
createdb project_ledger

# 运行迁移
alembic upgrade head
```

4. **前端设置**
```bash
cd frontend-new
npm install
npm run build
```

5. **启动服务**
```bash
# 后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端 (生产环境使用Nginx)
cd frontend-new
npm run dev
```

## 📁 项目结构

```
project-ledger-system/
├── backend/                 # 后端API服务
│   ├── app/                # 应用代码
│   ├── alembic/           # 数据库迁移
│   └── requirements.txt    # Python依赖
├── frontend-new/           # 前端Vue.js应用
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── package.json       # Node.js依赖
├── docs/                  # 项目文档
├── scripts/               # 部署和工具脚本
└── .github/               # GitHub配置
```

## 🔧 技术栈

### 后端
- **FastAPI** - 现代、快速的Web框架
- **PostgreSQL** - 关系型数据库
- **Redis** - 缓存和会话存储
- **SQLAlchemy** - ORM框架
- **Alembic** - 数据库迁移
- **JWT** - 身份认证

### 前端
- **Vue.js 3** - 渐进式JavaScript框架
- **Vite** - 构建工具
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端
- **Pinia** - 状态管理

### 部署
- **Docker** - 容器化部署
- **Nginx** - Web服务器和反向代理
- **GitHub Actions** - CI/CD自动化

## 📊 API文档

- **开发环境**: http://localhost:8000/docs
- **生产环境**: https://your-domain.com/docs
- **OpenAPI规范**: http://localhost:8000/openapi.json

## 🧪 测试

```bash
# 后端测试
cd backend
pytest tests/ -v

# 前端测试
cd frontend-new
npm run test
```

## 📦 部署

### Docker部署
```bash
docker-compose up -d
```

### 手动部署
```bash
# 使用部署脚本
./scripts/deploy.sh
```

## 🔒 安全

- JWT令牌认证
- 密码哈希加密
- SQL注入防护
- XSS防护
- CSRF防护
- 数据隔离

## 📈 监控

- 系统健康检查
- 性能监控
- 错误日志
- 用户行为分析

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

- 📧 邮箱: support@project-ledger.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/您的用户名/project-ledger-system/issues)
- 📖 文档: [项目Wiki](https://github.com/您的用户名/project-ledger-system/wiki)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**
