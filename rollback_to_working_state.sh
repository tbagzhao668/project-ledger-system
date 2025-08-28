#!/bin/bash

# 🎉 快速回滚到工作状态脚本
# 备份时间: 2025-08-28

echo "🔄 开始回滚到系统完全修复状态..."

# 检查Git状态
if [ -d ".git" ]; then
    echo "📋 检测到Git仓库，使用Git回滚..."
    
    # 查看当前状态
    echo "当前Git状态:"
    git status --short
    
    # 查看提交历史
    echo -e "\n📜 最近的提交历史:"
    git log --oneline -5
    
    # 回滚到备份点
    echo -e "\n🔄 回滚到备份点: 9ac38d4"
    git reset --hard 9ac38d4
    
    if [ $? -eq 0 ]; then
        echo "✅ Git回滚成功！"
    else
        echo "❌ Git回滚失败！"
        exit 1
    fi
else
    echo "⚠️ 未检测到Git仓库，使用手动回滚..."
    echo "请参考 SYSTEM_BACKUP_README.md 进行手动恢复"
    exit 1
fi

# 重启服务
echo -e "\n🚀 重启服务..."

# 停止后端服务
echo "停止后端服务..."
pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 2

# 启动后端服务
echo "启动后端服务..."
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/uvicorn.log 2>&1 &
cd ..

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 测试服务状态
echo -e "\n🧪 测试服务状态..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务启动成功！"
else
    echo "❌ 后端服务启动失败！"
    echo "请检查日志: backend/logs/uvicorn.log"
fi

# 重启Nginx
echo -e "\n🌐 重启Nginx..."
sudo systemctl restart nginx

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx重启成功！"
else
    echo "❌ Nginx重启失败！"
    echo "请检查状态: sudo systemctl status nginx"
fi

echo -e "\n🎉 回滚完成！"
echo "📋 系统状态: 已回滚到 2025-08-28 的完全修复状态"
echo "🔗 前端地址: https://192.168.4.130"
echo "🔗 后端地址: http://localhost:8000"
echo "📖 详细说明: 查看 SYSTEM_BACKUP_README.md"
echo "🧪 测试命令: curl http://localhost:8000/health"
