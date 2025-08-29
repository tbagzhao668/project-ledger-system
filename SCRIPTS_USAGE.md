# 脚本使用总结

## 📋 脚本总览

本项目包含多个脚本文件，每个脚本都有特定的用途。以下是所有脚本的详细说明和使用方法。

## 🚀 部署脚本

### 1. `deploy.sh` - 主部署脚本

**用途**: 完整的系统部署和管理脚本

**主要功能**:
- 首次部署 (`first-deploy`)
- 快速部署 (`quick-deploy`)
- 数据库管理 (导出、导入、备份、修复)
- 服务管理 (启动、停止、重启)
- 健康检查和状态监控

**使用方法**:
```bash
# 查看帮助
./deploy.sh help

# 首次部署
./deploy.sh first-deploy

# 快速部署
./deploy.sh quick-deploy

# 数据库操作
./deploy.sh export-db      # 导出数据库
./deploy.sh import-db      # 导入数据库
./deploy.sh backup-db      # 备份数据库
./deploy.sh fix-schema     # 修复数据库结构

# 服务管理
./deploy.sh start          # 启动服务
./deploy.sh stop           # 停止服务
./deploy.sh restart        # 重启服务
./deploy.sh status         # 查看状态
./deploy.sh health         # 健康检查
```

### 2. `quick_deploy.sh` - 快速部署脚本

**用途**: 新环境的一键快速部署

**特点**:
- 自动安装系统依赖
- 自动配置数据库
- 自动生成SSL证书
- 自动部署前后端
- 自动配置Nginx

**使用方法**:
```bash
chmod +x quick_deploy.sh
./quick_deploy.sh
```

**适用场景**:
- 新服务器部署
- 开发环境搭建
- 测试环境部署

### 3. `start-all-services.sh` - 服务启动脚本

**用途**: 启动所有系统服务

**启动的服务**:
- PostgreSQL 数据库
- Redis 缓存
- 后端API服务
- Nginx Web服务器

**使用方法**:
```bash
chmod +x start-all-services.sh
./start-all-services.sh
```

**适用场景**:
- 系统重启后启动服务
- 服务异常后重新启动
- 日常服务管理

## 🔐 安全脚本

### 4. `generate_ssl_cert.sh` - SSL证书生成脚本

**用途**: 生成自签名SSL证书

**功能**:
- 自动创建SSL目录
- 生成RSA密钥对
- 设置正确的文件权限
- 显示证书信息

**使用方法**:
```bash
sudo ./generate_ssl_cert.sh
```

**注意事项**:
- 需要root权限运行
- 生成的是自签名证书
- 浏览器会显示安全警告（正常现象）

## 🗄️ 数据库脚本

### 5. `init_database.sql` - 数据库初始化脚本

**用途**: 创建完整的数据库结构

**包含内容**:
- 6个核心表 (tenants, users, projects, categories, suppliers, transactions)
- 完整的字段定义
- 索引和约束
- 初始数据
- 用户权限设置

**使用方法**:
```bash
sudo -u postgres psql -f init_database.sql
```

**适用场景**:
- 新数据库初始化
- 数据库结构重建
- 开发环境搭建

### 6. `database_initial.sql.gz` - 初始数据库导出

**用途**: 包含基础表结构和数据的数据库导出文件

**特点**:
- 压缩格式，节省空间
- 包含完整的数据库状态
- 可用于快速恢复

**使用方法**:
```bash
# 解压并导入
gunzip -c database_initial.sql.gz | sudo -u postgres psql
```

## ⚙️ 配置文件

### 7. `nginx-site.conf` - Nginx站点配置

**用途**: Nginx服务器配置

**配置内容**:
- HTTPS支持 (443端口)
- HTTP重定向到HTTPS
- 前端静态文件服务
- 后端API代理
- SSL安全配置
- 日志配置

**使用方法**:
```bash
sudo cp nginx-site.conf /etc/nginx/sites-available/fince-project
sudo ln -sf /etc/nginx/sites-available/fince-project /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. `fince-backend.service` - 系统服务文件

**用途**: 后端API服务的systemd配置

**配置内容**:
- 服务描述和依赖
- 启动命令和参数
- 自动重启策略
- 用户权限设置

**使用方法**:
```bash
sudo cp fince-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fince-backend.service
sudo systemctl start fince-backend.service
```

## 📚 文档文件

### 9. `DEPLOYMENT_GUIDE.md` - 完整部署指南

**用途**: 详细的部署说明文档

**内容**:
- 系统架构说明
- 分步部署指南
- 脚本使用说明
- 故障排除指南
- 最佳实践建议

### 10. `README.md` - 项目说明文档

**用途**: 项目概述和快速开始指南

**内容**:
- 项目介绍
- 快速部署方法
- 脚本说明表格
- 访问地址
- 技术支持信息

## 🔄 脚本执行顺序

### 新环境部署流程

```bash
# 1. 克隆项目
git clone <repository-url>
cd project-fince

# 2. 快速部署（推荐）
chmod +x quick_deploy.sh
./quick_deploy.sh

# 3. 启动服务
./start-all-services.sh
```

### 现有环境更新流程

```bash
# 1. 更新代码
git pull origin master

# 2. 重新部署
./deploy.sh quick-deploy

# 3. 重启服务
./deploy.sh restart
```

### 数据库迁移流程

```bash
# 1. 导出当前数据库
./deploy.sh export-db

# 2. 迁移到新环境
./deploy.sh import-db

# 3. 验证数据
./deploy.sh health
```

## 🚨 故障排除

### 常见问题及解决方案

1. **脚本权限问题**
   ```bash
   chmod +x *.sh
   ```

2. **SSL证书问题**
   ```bash
   sudo ./generate_ssl_cert.sh
   sudo systemctl restart nginx
   ```

3. **数据库连接问题**
   ```bash
   sudo systemctl status postgresql
   ./deploy.sh fix-schema
   ```

4. **服务启动失败**
   ```bash
   ./deploy.sh status
   sudo journalctl -u fince-backend.service -f
   ```

## 💡 最佳实践

1. **首次部署**: 使用 `quick_deploy.sh`
2. **日常管理**: 使用 `deploy.sh` 的各种命令
3. **服务启动**: 使用 `start-all-services.sh`
4. **数据库备份**: 定期使用 `./deploy.sh backup-db`
5. **SSL证书**: 每年更新一次证书

## 📞 技术支持

如遇到问题，请按以下顺序检查：

1. 查看脚本帮助: `./deploy.sh help`
2. 检查服务状态: `./deploy.sh status`
3. 执行健康检查: `./deploy.sh health`
4. 查看系统日志
5. 参考部署指南文档

---

**注意**: 所有脚本都经过测试，但建议在生产环境使用前先在测试环境验证。
