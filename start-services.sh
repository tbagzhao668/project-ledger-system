#!/bin/bash

# 工程项目流水账管理系统 - 服务启动脚本
# 适用于本地部署（非Docker）

echo "=== 工程项目流水账管理系统 - 服务启动脚本 ==="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查服务状态函数
check_service() {
    local service_name=$1
    if systemctl is-active --quiet $service_name; then
        echo -e "${GREEN}✓ $service_name 正在运行${NC}"
        return 0
    else
        echo -e "${RED}✗ $service_name 未运行${NC}"
        return 1
    fi
}

# 启动服务函数
start_service() {
    local service_name=$1
    local display_name=$2
    
    echo -n "正在启动 $display_name... "
    if sudo systemctl start $service_name; then
        echo -e "${GREEN}成功${NC}"
    else
        echo -e "${RED}失败${NC}"
        return 1
    fi
}

# 1. 启动PostgreSQL
echo -e "\n${YELLOW}1. 启动PostgreSQL数据库${NC}"
start_service postgresql "PostgreSQL数据库"

# 2. 启动Redis
echo -e "\n${YELLOW}2. 启动Redis缓存服务${NC}"
start_service redis-server "Redis缓存服务"

# 3. 检查数据库连接
echo -e "\n${YELLOW}3. 检查数据库连接${NC}"
if sudo -u postgres psql -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 数据库连接正常${NC}"
else
    echo -e "${RED}✗ 数据库连接失败${NC}"
    exit 1
fi

# 4. 启动后端服务
echo -e "\n${YELLOW}4. 启动后端API服务${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "安装依赖包..."
pip install -r requirements.txt > /dev/null 2>&1

echo "运行数据库迁移..."
alembic stamp head > /dev/null 2>&1

echo "启动后端服务..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/uvicorn.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > logs/backend.pid
echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"

# 5. 启动Celery工作进程
echo -e "\n${YELLOW}5. 启动Celery异步任务工作进程${NC}"
nohup celery -A app.core.celery_app worker --loglevel=info > logs/celery.log 2>&1 &
CELERY_PID=$!
echo $CELERY_PID > logs/celery.pid
echo -e "${GREEN}✓ Celery工作进程已启动 (PID: $CELERY_PID)${NC}"

# 6. 启动Nginx
echo -e "\n${YELLOW}6. 启动Nginx Web服务器${NC}"
start_service nginx "Nginx Web服务器"

# 7. 等待服务启动
echo -e "\n${YELLOW}7. 等待服务启动完成...${NC}"
sleep 5

# 8. 检查服务状态
echo -e "\n${YELLOW}8. 检查服务状态${NC}"
check_service postgresql
check_service redis-server
check_service nginx

# 检查后端服务
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端API服务正常${NC}"
else
    echo -e "${RED}✗ 后端API服务异常${NC}"
fi

# 检查前端服务
if curl -s http://localhost/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端Web服务正常${NC}"
else
    echo -e "${RED}✗ 前端Web服务异常${NC}"
fi

# 9. 显示访问信息
echo -e "\n${GREEN}=== 服务启动完成 ===${NC}"
echo -e "${YELLOW}前端访问地址:${NC} http://localhost"
echo -e "${YELLOW}后端API地址:${NC} http://localhost:8000"
echo -e "${YELLOW}API文档地址:${NC} http://localhost:8000/docs"
echo -e "${YELLOW}健康检查:${NC} http://localhost/health"
echo -e "\n${YELLOW}进程PID文件:${NC}"
echo "  后端服务: logs/backend.pid"
echo "  Celery: logs/celery.pid"
echo -e "\n${YELLOW}日志文件:${NC}"
echo "  后端服务: logs/uvicorn.log"
echo "  Celery: logs/celery.log"
echo "  Nginx: /var/log/nginx/"

cd ..
