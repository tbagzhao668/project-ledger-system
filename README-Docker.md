# 工程项目流水账系统 - Docker部署指南

## 🎯 项目概述

本项目已完全Docker化，支持生产环境部署，包含HTTPS访问和完整的服务编排。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (443)   │    │   Frontend      │    │   Backend API   │
│   HTTPS代理     │◄──►│   Vue.js        │◄──►│   FastAPI       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis         │    │   Celery        │
│   数据库        │    │   缓存          │    │   异步任务      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 域名（用于HTTPS证书）
- 80和443端口开放

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd 工程项目流水账
```

### 3. 配置域名

编辑 `nginx/conf.d/default.conf` 文件，将 `yourdomain.com` 替换为您的实际域名。

### 4. 获取SSL证书

```bash
./setup-ssl.sh yourdomain.com admin@yourdomain.com
```

### 5. 部署系统

```bash
./deploy.sh
```

## 📋 服务配置

### 数据库配置

- **用户**: `gcxm_admin`
- **密码**: `ADS@gcxm#@%`
- **数据库**: `project_ledger`
- **端口**: `5432` (仅本地访问)

### Redis配置

- **密码**: `ADS@gcxm#@%`
- **端口**: `6379` (仅本地访问)

### 应用配置

- **后端API**: 容器内8000端口
- **前端**: 容器内80端口
- **Nginx**: 80和443端口（公网访问）

## 🔧 环境变量

主要环境变量在 `env.production` 文件中配置：

```bash
# 数据库连接
DATABASE_URL=postgresql+asyncpg://gcxm_admin:ADS%40gcxm%23%40%25@postgres:5432/project_ledger

# Redis连接
REDIS_URL=redis://:ADS%40gcxm%23%40%25@redis:6379/0

# 应用配置
ENVIRONMENT=production
DEBUG=false
```

## 📁 目录结构

```
工程项目流水账/
├── docker-compose.prod.yml    # 生产环境编排文件
├── backend/
│   ├── Dockerfile.prod        # 后端生产镜像
│   └── ...
├── frontend-new/
│   ├── Dockerfile.prod        # 前端生产镜像
│   └── ...
├── nginx/
│   ├── nginx.conf             # 主配置
│   ├── conf.d/                # 站点配置
│   ├── ssl/                   # SSL证书
│   └── logs/                  # 日志文件
├── deploy.sh                  # 部署脚本
├── setup-ssl.sh              # SSL证书配置
├── renew-ssl.sh              # 证书续期
└── env.production            # 环境变量
```

## 🛠️ 管理命令

### 启动服务

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 停止服务

```bash
docker-compose -f docker-compose.prod.yml down
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 重启服务

```bash
docker-compose -f docker-compose.prod.yml restart [服务名]
```

### 更新服务

```bash
# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 仅更新特定服务
docker-compose -f docker-compose.prod.yml up -d --build backend
```

## 🔐 SSL证书管理

### 自动续期

设置cron任务，每60天自动续期：

```bash
# 编辑crontab
crontab -e

# 添加以下行（替换为实际路径）
0 0 1 */2 * /path/to/your/project/renew-ssl.sh
```

### 手动续期

```bash
./renew-ssl.sh
```

## 📊 监控和日志

### 健康检查

- **前端**: `https://yourdomain.com/health`
- **后端**: `https://yourdomain.com/api/health`
- **数据库**: 容器内健康检查
- **Redis**: 容器内健康检查

### 日志位置

- **Nginx**: `nginx/logs/`
- **应用**: `logs/`
- **容器**: `docker-compose -f docker-compose.prod.yml logs`

## 🔒 安全配置

### 网络安全

- 数据库和Redis仅限本地访问
- 所有外部流量通过Nginx代理
- 启用HSTS安全头
- 配置CORS策略

### 文件权限

```bash
chmod 755 uploads logs
chmod 700 nginx/ssl
```

## 🚨 故障排除

### 常见问题

1. **端口冲突**: 检查80和443端口是否被占用
2. **证书问题**: 确保域名解析正确，80端口开放
3. **数据库连接**: 检查容器网络和数据库状态
4. **权限问题**: 确保目录权限正确设置

### 调试命令

```bash
# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 检查网络
docker network ls
docker network inspect project_ledger_project_ledger_network

# 进入容器调试
docker-compose -f docker-compose.prod.yml exec backend bash
```

## 📈 性能优化

### 生产环境建议

- 使用多worker进程（已配置4个）
- 启用Gzip压缩
- 配置静态资源缓存
- 使用连接池
- 监控资源使用

### 扩展配置

```yaml
# 在docker-compose.prod.yml中添加
deploy:
  replicas: 3  # 扩展后端服务
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

## 📞 技术支持

如遇到问题，请检查：

1. Docker和Docker Compose版本
2. 系统资源使用情况
3. 网络和防火墙配置
4. 日志文件内容

---

**注意**: 生产环境部署前，请务必：
- 修改默认密码和密钥
- 配置备份策略
- 设置监控告警
- 测试故障恢复流程
