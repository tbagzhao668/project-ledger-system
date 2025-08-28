#!/bin/bash

echo "🚀 开始部署项目新功能..."

# 设置变量
SERVER_IP="192.168.1.215"
SERVER_USER="dev"
SERVER_PASS="123"
PROJECT_DIR="/home/dev/project"

echo "📡 连接到服务器 $SERVER_IP..."

# 连接到服务器并执行部署命令
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'

cd /home/dev/project

echo "🔄 停止后端服务..."
pkill -f "uvicorn app.main:app" || true

echo "📦 更新代码..."
git pull origin main || true

echo "🗄️ 运行数据库迁移..."
cd backend
python scripts/create_project_tables.py

echo "🚀 启动后端服务..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

echo "⏳ 等待服务启动..."
sleep 5

echo "🔍 检查服务状态..."
curl -s http://localhost:8000/docs | head -5

echo "✅ 部署完成！"

EOF

echo "🎉 项目新功能部署完成！"
echo "📋 新增功能："
echo "   - 项目里程碑管理（增删改查）"
echo "   - 项目团队成员管理（增删改查）"
echo "   - 项目变更记录追踪"
echo "   - 完整的项目详情页面"
echo ""
echo "🌐 访问地址：http://$SERVER_IP:8000/docs"
