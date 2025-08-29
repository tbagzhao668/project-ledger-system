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

# 检查数据库状态
./check_database.sh
```

### 数据库检查脚本

#### 1. `check_database.sh` - 综合数据库检查脚本

**用途**: 一键检查数据库状态、结构和性能

**功能**:
- 检查PostgreSQL服务状态
- 验证数据库连接和用户权限
- 检查表结构和字段数量
- 测试数据库性能
- 提供详细的检查报告

**使用方法**:
```bash
chmod +x check_database.sh
./check_database.sh
```

#### 2. `check_database_structure.py` - 数据库结构检查脚本

**用途**: 详细检查数据库表结构和字段完整性

**功能**:
- 验证必需表是否存在
- 检查字段数量和类型
- 识别缺失和多余的字段
- 提供字段详细信息

**使用方法**:
```bash
cd backend
source venv/bin/activate
cd ..
python3 check_database_structure.py
```

#### 3. `test_database_connection.py` - 数据库连接测试脚本

**用途**: 测试数据库连接、权限和基本功能

**功能**:
- 测试不同用户的连接
- 验证用户权限配置
- 测试基本数据库操作
- 检查事务处理能力

**使用方法**:
```bash
cd backend
source venv/bin/activate
cd ..
python3 test_database_connection.py
```

#### 4. `test_database_performance.py` - 数据库性能测试脚本

**用途**: 评估数据库查询性能和并发处理能力

**功能**:
- 测试简单和复杂查询性能
- 评估插入操作性能
- 测试并发连接能力
- 分析数据库大小和统计信息
- 提供性能优化建议

**使用方法**:
```bash
cd backend
source venv/bin/activate
cd ..
python3 test_database_performance.py
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
   
   # 使用数据库检查脚本诊断
   ./check_database.sh
   python3 test_database_connection.py
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

5. **数据库结构问题**
   ```bash
   # 检查数据库结构
   ./check_database.sh
   
   # 详细检查表结构
   python3 check_database_structure.py
   
   # 修复数据库结构
   ./deploy.sh fix-schema
   ```

6. **数据库性能问题**
   ```bash
   # 测试数据库性能
   python3 test_database_performance.py
   
   # 检查数据库大小和统计
   sudo -u postgres psql -d fince_project_prod -c "SELECT pg_size_pretty(pg_database_size(current_database()));"
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
