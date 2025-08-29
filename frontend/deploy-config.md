# 前端部署配置指南

## 🌍 多环境部署方案

### 方案1: 自动检测（推荐）
系统会自动根据访问域名检测环境和API地址：

```javascript
// 访问地址: http://192.168.1.215:3000
// API地址会自动设置为: http://192.168.1.215:8000

// 访问地址: http://localhost:3000  
// API地址会自动设置为: http://localhost:8000

// 访问地址: http://myserver.com:3000
// API地址会自动设置为: http://myserver.com:8000
```

### 方案2: 环境变量配置

#### 开发环境 (.env.development)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=工程项目流水账管理系统 (开发)
VITE_NODE_ENV=development
VITE_APP_DEBUG=true
```

#### 测试环境 (.env.testing) 
```bash
VITE_API_BASE_URL=http://test-server:8000
VITE_APP_TITLE=工程项目流水账管理系统 (测试)
VITE_NODE_ENV=testing
VITE_APP_DEBUG=true
```

#### 生产环境 (.env.production)
```bash
VITE_API_BASE_URL=http://your-production-server:8000
VITE_APP_TITLE=工程项目流水账管理系统
VITE_NODE_ENV=production
VITE_APP_DEBUG=false
```

## 🚀 快速部署步骤

### 1. 服务器迁移部署

```bash
# 1. 在新服务器上创建项目目录
mkdir -p /home/dev/project
cd /home/dev/project

# 2. 上传代码包
scp frontend.tar.gz user@new-server:/home/dev/project/

# 3. 解压代码
tar -xzf frontend.tar.gz

# 4. 安装依赖
cd frontend
npm install

# 5. 启动服务（自动检测模式）
npm run dev
# 访问: http://new-server-ip:3000
# API会自动指向: http://new-server-ip:8000
```

### 2. 自定义API地址部署

如果后端API在不同服务器上：

```bash
# 创建环境文件
cat > .env.local << EOF
VITE_API_BASE_URL=http://api-server-ip:8000
EOF

# 启动服务
npm run dev
```

### 3. Docker部署

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY . .

RUN npm install
RUN npm run build

# 使用nginx提供静态文件
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

# 自定义nginx配置支持前端路由
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://backend:8000
    depends_on:
      - backend
      
  backend:
    # 后端配置...
    ports:
      - "8000:8000"
```

## ⚙️ 配置优先级

系统按以下优先级读取配置：

1. **环境变量** (最高优先级)
2. **.env.local** (本地覆盖)
3. **.env.[mode]** (环境特定)
4. **.env** (默认配置)
5. **自动检测** (最低优先级)

## 🔧 高级配置

### 反向代理配置

如果使用Nginx反向代理：

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://backend-server:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

此时前端配置：
```bash
VITE_API_BASE_URL=/api  # 使用相对路径
```

### 多域名部署

```javascript
// config/domains.js
const domainConfigs = {
  'project.company.com': {
    apiUrl: 'https://api.company.com',
    title: '公司项目管理系统'
  },
  'demo.project.com': {
    apiUrl: 'https://demo-api.project.com', 
    title: '项目管理系统演示版'
  }
}

export default domainConfigs[window.location.hostname] || {}
```

## 📋 部署检查清单

### 部署前检查
- [ ] 确认目标服务器IP和端口
- [ ] 检查后端API服务状态
- [ ] 准备环境配置文件
- [ ] 检查防火墙端口开放

### 部署后验证
- [ ] 前端页面正常加载
- [ ] API请求正常响应
- [ ] 功能操作正常
- [ ] 不同设备访问正常

## 🐛 常见问题

### Q: API请求失败 "ERR_CONNECTION_REFUSED"
**A**: 检查后端服务是否启动，端口是否正确

### Q: 页面空白或加载失败
**A**: 检查静态文件路径配置和nginx配置

### Q: 跨域问题
**A**: 配置后端CORS或使用nginx代理

### Q: 环境变量不生效
**A**: 确保变量名以VITE_开头，重新构建项目

## 📞 技术支持

如遇到部署问题，请提供：
1. 服务器环境信息
2. 错误日志
3. 网络配置
4. 浏览器控制台错误

---

**当前配置**: 自动检测模式 + 192.168.1.215:8000
**迁移建议**: 使用自动检测模式，无需修改代码即可适配新环境
