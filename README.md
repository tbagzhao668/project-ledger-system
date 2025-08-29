# 工程项目流水账管理系统

一个基于FastAPI + Vue.js的现代化工程项目财务管理系统。

## 🚀 快速开始

### 一键部署（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd project-fince

# 执行快速部署
chmod +x quick_deploy.sh
./quick_deploy.sh
```

### 分步部署

```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install -y postgresql postgresql-contrib redis-server nginx curl wget git

# 2. 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 3. 生成SSL证书
sudo ./generate_ssl_cert.sh

# 4. 初始化数据库
sudo -u postgres psql -f init_database.sql

# 5. 部署应用
./deploy.sh first-deploy

# 6. 启动服务
./start-all-services.sh
```

## 📁 项目结构

```
project-fince/
├── backend/                 # 后端Python代码
├── frontend-new/           # 前端Vue.js代码
├── backups/                # 数据库备份
├── logs/                   # 日志文件
├── nginx/                  # Nginx配置
├── deploy.sh               # 主部署脚本
├── quick_deploy.sh         # 快速部署脚本
├── start-all-services.sh   # 服务启动脚本
├── generate_ssl_cert.sh    # SSL证书生成脚本
├── init_database.sql       # 数据库初始化脚本
├── database_initial.sql.gz # 初始数据库导出
├── nginx-site.conf         # Nginx站点配置
├── fince-backend.service   # 后端系统服务文件
├── DEPLOYMENT_GUIDE.md     # 完整部署指南
└── 数据库迁移指南.md        # 数据库迁移说明
```

## 🔧 脚本说明

### 核心脚本

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `deploy.sh` | 主部署脚本 | 完整的系统部署和管理 |
| `quick_deploy.sh` | 快速部署脚本 | 新环境一键部署 |
| `start-all-services.sh` | 服务启动脚本 | 启动所有系统服务 |
| `generate_ssl_cert.sh` | SSL证书生成 | 生成HTTPS证书 |

### 数据库脚本

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `init_database.sql` | 数据库初始化 | 新环境数据库创建 |
| `database_initial.sql.gz` | 初始数据库 | 包含基础表结构和数据 |

### 配置文件

| 文件 | 用途 | 说明 |
|------|------|------|
| `nginx-site.conf` | Nginx配置 | HTTPS站点配置 |
| `fince-backend.service` | 系统服务 | 后端API服务管理 |

## 🌐 访问地址

- **前端应用**: https://localhost
- **后端API**: https://localhost/api/v1
- **健康检查**: https://localhost/health

## 📊 系统架构

- **前端**: Vue.js 3 + Vite
- **后端**: FastAPI + Python 3.12
- **数据库**: PostgreSQL 16
- **缓存**: Redis
- **Web服务器**: Nginx + HTTPS
- **部署**: Systemd服务管理

## 🗄️ 数据库管理

### 主要表结构

- **tenants**: 租户信息管理
- **users**: 用户管理
- **projects**: 工程项目管理
- **categories**: 分类管理
- **suppliers**: 供应商管理
- **transactions**: 交易记录管理

### 数据库操作

```bash
# 导出数据库
./deploy.sh export-db

# 导入数据库
./deploy.sh import-db

# 备份数据库
./deploy.sh backup-db

# 修复数据库结构
./deploy.sh fix-schema
```

## 📚 详细文档

- [完整部署指南](DEPLOYMENT_GUIDE.md) - 详细的部署说明
- [数据库迁移指南](数据库迁移指南.md) - 数据库迁移和备份说明

## 🔒 安全说明

- 系统使用自签名SSL证书
- 生产环境请使用受信任的CA证书
- 默认数据库密码为 `postgres`，生产环境请修改

## 🚨 故障排除

### 常见问题

1. **端口冲突**: 使用 `sudo pkill -f uvicorn` 停止冲突进程
2. **数据库连接失败**: 检查PostgreSQL服务状态
3. **Nginx配置错误**: 使用 `sudo nginx -t` 测试配置
4. **SSL证书问题**: 重新运行 `sudo ./generate_ssl_cert.sh`

### 日志查看

```bash
# 后端日志
sudo journalctl -u fince-backend.service -f

# Nginx日志
sudo tail -f /var/log/nginx/fince-project.access.log
sudo tail -f /var/log/nginx/fince-project.error.log
```

## 🤝 技术支持

如遇到问题，请检查：
1. 系统日志
2. 服务状态
3. 配置文件
4. 网络连接

## 📝 更新日志

- **v1.0.0** (2025-08-29): 初始版本发布
  - 完整的工程项目管理系统
  - 支持HTTPS访问
  - 自动化部署脚本
  - 数据库导入导出功能

---

**注意**: 此系统仅供学习和测试使用，生产环境请做好安全配置。
