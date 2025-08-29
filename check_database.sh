#!/bin/bash

# 数据库检查脚本
# 用于快速检查数据库状态、结构和性能

echo "=== 数据库检查脚本 ==="

# 检查PostgreSQL服务状态
echo "1️⃣ 检查PostgreSQL服务状态..."
if systemctl is-active --quiet postgresql; then
    echo "   ✅ PostgreSQL服务正在运行"
    echo "   📊 服务状态: $(systemctl is-active postgresql)"
else
    echo "   ❌ PostgreSQL服务未运行"
    echo "   💡 启动服务: sudo systemctl start postgresql"
    exit 1
fi

# 检查数据库连接
echo ""
echo "2️⃣ 检查数据库连接..."
if sudo -u postgres psql -c "SELECT version();" >/dev/null 2>&1; then
    echo "   ✅ postgres用户连接正常"
else
    echo "   ❌ postgres用户连接失败"
    exit 1
fi

# 检查数据库是否存在
echo ""
echo "3️⃣ 检查数据库是否存在..."
if sudo -u postgres psql -l | grep -q "fince_project_prod"; then
    echo "   ✅ 数据库 fince_project_prod 存在"
else
    echo "   ❌ 数据库 fince_project_prod 不存在"
    echo "   💡 创建数据库: sudo -u postgres createdb -O fince_app_project fince_project_prod"
    exit 1
fi

# 检查数据库用户
echo ""
echo "4️⃣ 检查数据库用户..."
if sudo -u postgres psql -c "\du" | grep -q "fince_app_project"; then
    echo "   ✅ 用户 fince_app_project 存在"
else
    echo "   ❌ 用户 fince_app_project 不存在"
    echo "   💡 创建用户: sudo -u postgres createuser --interactive --pwprompt fince_app_project"
    exit 1
fi

# 检查表结构
echo ""
echo "5️⃣ 检查数据库表结构..."
cd /home/dev/project-fince

if [[ -f "check_database_structure.py" ]]; then
    echo "   🔍 运行Python结构检查脚本..."
    cd backend
    source venv/bin/activate
    cd ..
    python3 check_database_structure.py
else
    echo "   ⚠️  Python检查脚本不存在，使用SQL检查..."
    
    # 使用SQL检查表结构
    tables=("tenants" "users" "projects" "categories" "suppliers" "transactions")
    for table in "${tables[@]}"; do
        if sudo -u postgres psql -d fince_project_prod -c "\dt $table" 2>/dev/null | grep -q "$table"; then
            echo "   ✅ 表 $table 存在"
            
            # 检查字段数量
            field_count=$(sudo -u postgres psql -d fince_project_prod -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '$table';" 2>/dev/null | tail -1 | tr -d ' ')
            echo "      📊 字段数量: $field_count"
        else
            echo "   ❌ 表 $table 不存在"
        fi
    done
fi

# 检查数据库性能
echo ""
echo "6️⃣ 检查数据库性能..."
if [[ -f "test_database_performance.py" ]]; then
    echo "   🔍 运行性能测试脚本..."
    cd backend
    source venv/bin/activate
    cd ..
    python3 test_database_performance.py
else
    echo "   ⚠️  性能测试脚本不存在，跳过性能检查"
fi

# 检查数据库大小
echo ""
echo "7️⃣ 检查数据库大小..."
db_size=$(sudo -u postgres psql -d fince_project_prod -c "SELECT pg_size_pretty(pg_database_size(current_database()));" 2>/dev/null | tail -1 | tr -d ' ')
echo "   📊 数据库大小: $db_size"

# 检查表记录数量
echo ""
echo "8️⃣ 检查表记录数量..."
tables=("tenants" "users" "projects" "categories" "suppliers" "transactions")
for table in "${tables[@]}"; do
    if sudo -u postgres psql -d fince_project_prod -c "\dt $table" 2>/dev/null | grep -q "$table"; then
        record_count=$(sudo -u postgres psql -d fince_project_prod -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tail -1 | tr -d ' ')
        echo "   📊 表 $table: $record_count 条记录"
    fi
done

# 检查数据库连接测试
echo ""
echo "9️⃣ 检查数据库连接测试..."
if [[ -f "test_database_connection.py" ]]; then
    echo "   🔍 运行连接测试脚本..."
    cd backend
    source venv/bin/activate
    cd ..
    python3 test_database_connection.py
else
    echo "   ⚠️  连接测试脚本不存在，跳过连接测试"
fi

echo ""
echo "🎉 数据库检查完成！"
echo ""
echo "💡 如果发现问题，可以使用以下命令修复："
echo "   - 修复数据库结构: ./deploy.sh fix-schema"
echo "   - 重新初始化数据库: sudo -u postgres psql -f init_database.sql"
echo "   - 重启PostgreSQL: sudo systemctl restart postgresql"
