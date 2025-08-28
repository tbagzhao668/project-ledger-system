#!/bin/bash

# 工程项目流水账管理系统 - 服务停止脚本
# 适用于本地部署（非Docker）

echo "=== 工程项目流水账管理系统 - 服务停止脚本 ==="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 停止服务函数
stop_service() {
    local service_name=$1
    local display_name=$2
    
    echo -n "正在停止 $display_name... "
    if sudo systemctl stop $service_name; then
        echo -e "${GREEN}成功${NC}"
    else
        echo -e "${YELLOW}服务可能已经停止${NC}"
    fi
}

# 1. 停止Nginx
echo -e "\n${YELLOW}1. 停止Nginx Web服务器${NC}"
stop_service nginx "Nginx Web服务器"

# 2. 停止后端服务
echo -e "\n${YELLOW}2. 停止后端API服务${NC}"
cd backend
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "正在停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "强制停止后端服务..."
            kill -9 $BACKEND_PID
        fi
        echo -e "${GREEN}✓ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}后端服务进程不存在${NC}"
    fi
    rm -f logs/backend.pid
else
    echo -e "${YELLOW}后端服务PID文件不存在${NC}"
fi

# 3. 停止Celery工作进程
echo -e "\n${YELLOW}3. 停止Celery异步任务工作进程${NC}"
if [ -f "logs/celery.pid" ]; then
    CELERY_PID=$(cat logs/celery.pid)
    if kill -0 $CELERY_PID 2>/dev/null; then
        echo "正在停止Celery工作进程 (PID: $CELERY_PID)..."
        kill $CELERY_PID
        sleep 2
        if kill -0 $CELERY_PID 2>/dev/null; then
            echo "强制停止Celery工作进程..."
            kill -9 $CELERY_PID
        fi
        echo -e "${GREEN}✓ Celery工作进程已停止${NC}"
    else
        echo -e "${YELLOW}Celery工作进程不存在${NC}"
    fi
    rm -f logs/celery.pid
else
    echo -e "${YELLOW}Celery工作进程PID文件不存在${NC}"
fi

# 4. 停止Redis
echo -e "\n${YELLOW}4. 停止Redis缓存服务${NC}"
stop_service redis-server "Redis缓存服务"

# 5. 停止PostgreSQL
echo -e "\n${YELLOW}5. 停止PostgreSQL数据库${NC}"
stop_service postgresql "PostgreSQL数据库"

# 6. 检查进程是否完全停止
echo -e "\n${YELLOW}6. 检查进程状态${NC}"
sleep 2

# 检查是否还有相关进程在运行
REMAINING_PROCESSES=$(ps aux | grep -E "(uvicorn|celery|gunicorn)" | grep -v grep | wc -l)
if [ $REMAINING_PROCESSES -eq 0 ]; then
    echo -e "${GREEN}✓ 所有应用进程已停止${NC}"
else
    echo -e "${YELLOW}还有 $REMAINING_PROCESSES 个进程在运行${NC}"
    ps aux | grep -E "(uvicorn|celery|gunicorn)" | grep -v grep
fi

# 7. 显示停止完成信息
echo -e "\n${GREEN}=== 服务停止完成 ===${NC}"
echo -e "${YELLOW}注意:${NC}"
echo "  - 数据库数据已保存"
echo "  - 下次启动时使用 ./start-services.sh"
echo "  - 查看日志: tail -f logs/*.log"

cd ..
