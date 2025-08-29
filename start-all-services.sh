#!/bin/bash

echo "=== 工程项目流水账管理系统 - 启动所有服务 ==="

# 启动PostgreSQL
echo "1. 启动PostgreSQL数据库..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 启动Redis
echo "2. 启动Redis缓存服务..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 启动后端API服务
echo "3. 启动后端API服务..."
sudo systemctl start fince-backend.service
sudo systemctl enable fince-backend.service

# 启动Nginx
echo "4. 启动Nginx Web服务器..."
sudo systemctl start nginx
sudo systemctl enable nginx

# 等待服务启动
echo "5. 等待服务启动..."
sleep 5

# 检查服务状态
echo "6. 检查服务状态..."
echo "PostgreSQL状态: $(sudo systemctl is-active postgresql)"
echo "Redis状态: $(sudo systemctl is-active redis-server)"
echo "后端API状态: $(sudo systemctl is-active fince-backend.service)"
echo "Nginx状态: $(sudo systemctl is-active nginx)"

# 测试服务
echo "7. 测试服务..."
echo "后端健康检查: $(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' || echo '失败')"
echo "前端页面: $(curl -k -s https://localhost/ | grep -o '<title>[^<]*</title>' || echo '失败')"

echo ""
echo "🎉 所有服务启动完成！"
echo "📱 访问地址："
echo "   前端应用: https://localhost"
echo "   后端API:  https://localhost/api/v1"
echo "   健康检查: https://localhost/health"
echo ""
echo "🔧 管理命令："
echo "   查看状态: sudo systemctl status fince-backend.service"
echo "   重启后端: sudo systemctl restart fince-backend.service"
echo "   查看日志: sudo journalctl -u fince-backend.service -f"
