# 基准数据库说明文档

## 📋 概述

`BASE_DATABASE_FULL.sql.gz` 是工程项目流水账管理系统的基准数据库文件，包含了完整的数据库结构和初始数据。

## 🗄️ 数据库信息

- **数据库名称**: `fince_project_prod`
- **导出时间**: 2025年8月29日 21:54:10 +07
- **PostgreSQL版本**: 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
- **字符编码**: UTF8
- **语言环境**: zh_CN.UTF-8

## 📊 包含的表结构

1. **categories** - 项目分类表
2. **projects** - 项目信息表
3. **suppliers** - 供应商表
4. **tenants** - 租户表
5. **transactions** - 交易记录表
6. **users** - 用户表

## 🔧 使用方法

### 方法1: 使用 deploy.sh 脚本导入（推荐）

```bash
# 将基准数据库文件复制到正确位置
cp backups/BASE_DATABASE_FULL.sql.gz backups/database_export_$(date +%Y%m%d_%H%M%S).sql.gz

# 使用 deploy.sh 导入
./deploy.sh import-db
```

### 方法2: 手动导入

```bash
# 解压并导入
gunzip -c backups/BASE_DATABASE_FULL.sql.gz | sudo -u postgres psql

# 或者导入到指定数据库
gunzip -c backups/BASE_DATABASE_FULL.sql.gz | sudo -u postgres psql -d 目标数据库名
```

## 📱 默认用户信息

导入后，系统包含以下默认用户：

- **管理员用户**:
  - 邮箱: `admin@example.com`
  - 密码: `admin123`
  - 角色: `admin`

## ⚠️ 注意事项

1. **备份现有数据**: 导入前请备份现有数据库
2. **数据库名称**: 默认创建名为 `fince_project_prod` 的数据库
3. **权限要求**: 需要 PostgreSQL 超级用户权限
4. **版本兼容**: 建议使用 PostgreSQL 16.x 版本

## 🔄 重新部署流程

1. **准备环境**: 确保 PostgreSQL 服务运行正常
2. **导入基准数据库**: 使用上述方法之一导入数据库
3. **启动后端服务**: `sudo systemctl start fince-backend.service`
4. **启动前端服务**: 确保 Nginx 配置正确
5. **验证系统**: 访问前端页面和API接口

## 📁 文件位置

- **基准数据库**: `backups/BASE_DATABASE_FULL.sql.gz`
- **说明文档**: `backups/README_BASE_DATABASE.md`
- **部署脚本**: `deploy.sh`

## 🆘 故障排除

如果导入过程中遇到问题：

1. **检查 PostgreSQL 服务状态**: `sudo systemctl status postgresql`
2. **检查用户权限**: 确保有足够的数据库权限
3. **查看错误日志**: 检查 PostgreSQL 和系统日志
4. **使用 deploy.sh 脚本**: 脚本包含完整的错误处理逻辑

## 📞 技术支持

如有问题，请参考：
- `deploy.sh` 脚本的帮助信息
- 项目根目录的 `README.md` 文档
- 系统日志文件
