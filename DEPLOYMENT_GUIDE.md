# 工程项目流水账管理系统 - 部署指南

## 🎯 项目概述

工程项目流水账管理系统是一个基于FastAPI + Vue.js的现代化Web应用，提供完整的工程项目财务管理功能。

## 🏗️ 系统架构

- **前端**: Vue.js 3 + Vite
- **后端**: FastAPI + Python 3.12
- **数据库**: PostgreSQL 16
- **缓存**: Redis
- **Web服务器**: Nginx + HTTPS
- **部署**: Systemd服务管理

## 📁 项目结构

```
project-fince/
├── backend/                 # 后端Python代码
│   ├── app/                # FastAPI应用
│   ├── venv/               # Python虚拟环境
│   └── requirements.txt    # Python依赖
├── frontend-new/           # 前端Vue.js代码
│   ├── src/                # 源代码
│   ├── dist/               # 构建输出
│   └── package.json        # Node.js依赖
├── backups/                # 数据库备份
├── logs/                   # 日志文件
├── nginx/                  # Nginx配置
├── deploy.sh               # 主部署脚本
├── quick_deploy.sh         # 快速部署脚本
├── start-all-services.sh   # 服务启动脚本
├── generate_ssl_cert.sh    # SSL证书生成脚本
├── init_database.sql       # 数据库初始化脚本
├── database_initial.sql.gz # 初始数据库导出
└── nginx-site.conf         # Nginx站点配置
```

## 🚀 快速部署

### 方法1: 一键快速部署（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd project-fince

# 执行快速部署
chmod +x quick_deploy.sh
./quick_deploy.sh
```

### 方法2: 分步部署

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

## 🔧 脚本使用说明

### deploy.sh - 主部署脚本

```bash
# 查看帮助
./deploy.sh help

# 首次部署
./deploy.sh first-deploy

# 快速部署
./deploy.sh quick-deploy

# 修复数据库结构
./deploy.sh fix-schema

# 检测API错误
./deploy.sh detect-api-errors

# 导出数据库
./deploy.sh export-db

# 导入数据库
./deploy.sh import-db

# 备份数据库
./deploy.sh backup-db

# 健康检查
./deploy.sh health

# 查看状态
./deploy.sh status
```

### quick_deploy.sh - 快速部署脚本

用于快速部署到新环境，包含所有必要的步骤。

### start-all-services.sh - 服务启动脚本

启动所有系统服务：PostgreSQL、Redis、后端API、Nginx。

### generate_ssl_cert.sh - SSL证书生成脚本

生成自签名SSL证书，用于HTTPS访问。

## 🗄️ 数据库管理

### 数据库结构

- **tenants**: 租户信息
- **users**: 用户管理
- **projects**: 项目管理
- **categories**: 分类管理
- **suppliers**: 供应商管理
- **transactions**: 交易记录

### 数据库操作

```bash
# 导出数据库（包含结构和数据）
./deploy.sh export-db

# 导入数据库
./deploy.sh import-db

# 备份数据库（仅数据）
./deploy.sh backup-db

# 修复数据库结构
./deploy.sh fix-schema
```

## 🌐 访问地址

- **前端应用**: https://localhost
- **后端API**: https://localhost/api/v1
- **健康检查**: https://localhost/health

## 🔒 SSL证书

系统使用自签名SSL证书，浏览器会显示安全警告（正常现象）。

如需使用受信任的证书：
1. 购买或申请SSL证书
2. 将证书文件放置到 `/etc/nginx/ssl/`
3. 更新 `nginx-site.conf` 中的证书路径

## 📊 服务管理

### 查看服务状态

```bash
# 后端API服务
sudo systemctl status fince-backend.service

# Nginx服务
sudo systemctl status nginx

# PostgreSQL服务
sudo systemctl status postgresql

# Redis服务
sudo systemctl status redis-server
```

### 重启服务

```bash
# 重启后端
sudo systemctl restart fince-backend.service

# 重启Nginx
sudo systemctl restart nginx

# 重启所有服务
./start-all-services.sh
```

### 查看日志

```bash
# 后端日志
sudo journalctl -u fince-backend.service -f

# Nginx访问日志
sudo tail -f /var/log/nginx/fince-project.access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/fince-project.error.log
```

## 🚨 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep :8000
   
   # 停止冲突进程
   sudo pkill -f uvicorn
   ```

2. **数据库连接失败**
   ```bash
   # 检查PostgreSQL状态
   sudo systemctl status postgresql
   
   # 检查数据库用户
   sudo -u postgres psql -c "\du"
   ```

3. **Nginx配置错误**
   ```bash
   # 测试配置
   sudo nginx -t
   
   # 重新加载配置
   sudo systemctl reload nginx
   ```

4. **SSL证书问题**
   ```bash
   # 重新生成证书
   sudo ./generate_ssl_cert.sh
   
   # 重启Nginx
   sudo systemctl restart nginx
   ```

## 📝 更新日志

- **v1.0.0** (2025-08-29): 初始版本发布
  - 完整的工程项目管理系统
  - 支持HTTPS访问
  - 自动化部署脚本
  - 数据库导入导出功能

## 🤝 技术支持

如遇到问题，请检查：
1. 系统日志
2. 服务状态
3. 配置文件
4. 网络连接

---

**注意**: 此系统仅供学习和测试使用，生产环境请做好安全配置。
