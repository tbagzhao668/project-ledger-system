#!/bin/bash

# 快速部署脚本
# 用于快速部署工程项目流水账管理系统

echo "=== 工程项目流水账管理系统 - 快速部署脚本 ==="

# 检查是否以root权限运行
if [[ $EUID -eq 0 ]]; then
   echo "❌ 请不要以root权限运行此脚本"
   exit 1
fi

# 项目目录
PROJECT_DIR="/home/dev/project-fince"

# 检查项目目录
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

echo "📁 项目目录: $PROJECT_DIR"

# 1. 安装系统依赖
echo ""
echo "1️⃣ 安装系统依赖..."
sudo apt update
sudo apt install -y postgresql postgresql-contrib redis-server nginx curl wget git

# 2. 安装Node.js
echo ""
echo "2️⃣ 安装Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "✅ Node.js 已安装: $(node --version)"
fi

# 3. 启动PostgreSQL
echo ""
echo "3️⃣ 启动PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 4. 创建数据库用户和数据库
echo ""
echo "4️⃣ 创建数据库..."
sudo -u postgres createuser --interactive --pwprompt fince_app_project
sudo -u postgres createdb -O fince_app_project fince_project_prod

# 5. 初始化数据库结构
echo ""
echo "5️⃣ 初始化数据库结构..."
if [[ -f "init_database.sql" ]]; then
    sudo -u postgres psql -f init_database.sql
    echo "✅ 数据库结构初始化完成"
else
    echo "⚠️  数据库初始化脚本不存在，使用deploy.sh fix-schema"
    ./deploy.sh fix-schema
fi

# 6. 部署后端
echo ""
echo "6️⃣ 部署后端..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# 7. 部署前端
echo ""
echo "7️⃣ 部署前端..."
cd frontend-new
npm install
npm run build
cd ..

# 8. 生成SSL证书
echo ""
echo "8️⃣ 生成SSL证书..."
sudo ./generate_ssl_cert.sh

# 9. 配置Nginx
echo ""
echo "9️⃣ 配置Nginx..."
sudo cp nginx-site.conf /etc/nginx/sites-available/fince-project
sudo ln -sf /etc/nginx/sites-available/fince-project /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 10. 启动所有服务
echo ""
echo "🔟 启动所有服务..."
./start-all-services.sh

echo ""
echo "🎉 快速部署完成！"
echo "📱 访问地址："
echo "   前端应用: https://localhost"
echo "   后端API:  https://localhost/api/v1"
echo "   健康检查: https://localhost/health"
echo ""
echo "🔧 管理命令："
echo "   启动服务: ./start-all-services.sh"
echo "   查看状态: ./deploy.sh status"
echo "   健康检查: ./deploy.sh health"
