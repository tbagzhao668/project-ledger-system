#!/bin/bash

# 🔍 系统状态检查脚本
# 检查时间: 2025-08-28

echo "🔍 开始检查系统状态..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_service() {
    local service_name=$1
    local check_command=$2
    local description=$3
    
    echo -n "🔍 检查 ${description}... "
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 正常${NC}"
        return 0
    else
        echo -e "${RED}❌ 异常${NC}"
        return 1
    fi
}

# 检查后端服务
echo -e "\n${BLUE}=== 后端服务检查 ===${NC}"
check_service "Backend" "curl -s http://localhost:8000/health" "后端API服务"

# 检查数据库连接
echo -e "\n${BLUE}=== 数据库检查 ===${NC}"
check_service "Database" "PGPASSWORD=123456 psql -h localhost -U postgres -d project_ledger -c 'SELECT 1;'" "PostgreSQL数据库"

# 检查Nginx服务
echo -e "\n${BLUE}=== Web服务检查 ===${NC}"
check_service "Nginx" "systemctl is-active --quiet nginx" "Nginx服务"
check_service "Nginx Port" "netstat -tlnp | grep :443" "HTTPS端口(443)"

# 检查前端可访问性
echo -e "\n${BLUE}=== 前端服务检查 ===${NC}"
check_service "Frontend HTTPS" "curl -s -k https://192.168.4.130 > /dev/null" "前端HTTPS访问"

# 检查关键API
echo -e "\n${BLUE}=== API功能检查 ===${NC}"

# 获取登录令牌
echo "🔐 测试登录API..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/login \
    -H "Content-Type: application/json" \
    -d '{"email":"888@888.com","password":"888888"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "   ${GREEN}✅ 登录API正常${NC}"
    
    # 提取令牌
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    # 测试其他API
    echo "🧪 测试业务API..."
    
    check_service "Projects API" "curl -s -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/v1/projects > /dev/null" "项目列表API"
    check_service "Statistics API" "curl -s -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/v1/projects/statistics > /dev/null" "项目统计API"
    check_service "Categories API" "curl -s -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/v1/categories > /dev/null" "分类列表API"
    check_service "Suppliers API" "curl -s -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/v1/suppliers > /dev/null" "供应商列表API"
    
else
    echo -e "   ${RED}❌ 登录API异常${NC}"
    echo "   响应: $LOGIN_RESPONSE"
fi

# 检查Git状态
echo -e "\n${BLUE}=== 代码版本检查 ===${NC}"
if [ -d ".git" ]; then
    echo "📋 Git仓库状态:"
    git status --short
    
    echo -e "\n📜 最近提交:"
    git log --oneline -3
    
    # 检查是否在备份点
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    if [ "$CURRENT_COMMIT" = "9ac38d4" ]; then
        echo -e "\n${GREEN}✅ 当前在备份点: 9ac38d4${NC}"
    else
        echo -e "\n${YELLOW}⚠️ 当前不在备份点，当前提交: $CURRENT_COMMIT${NC}"
        echo "   备份点: 9ac38d4"
    fi
else
    echo -e "${RED}❌ 未检测到Git仓库${NC}"
fi

# 检查关键文件
echo -e "\n${BLUE}=== 关键文件检查 ===${NC}"
key_files=(
    "backend/app/api/v1/router.py"
    "backend/app/api/v1/projects.py"
    "SYSTEM_BACKUP_README.md"
    "rollback_to_working_state.sh"
)

for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅ $file${NC}"
    else
        echo -e "   ${RED}❌ $file (缺失)${NC}"
    fi
done

# 总结
echo -e "\n${BLUE}=== 检查总结 ===${NC}"
echo "📅 检查时间: $(date)"
echo "🔗 前端地址: https://192.168.4.130"
echo "🔗 后端地址: http://localhost:8000"
echo "📖 备份说明: SYSTEM_BACKUP_README.md"
echo "🔄 回滚脚本: ./rollback_to_working_state.sh"
echo "🗄️ 数据库备份: ./backup_database.sh"

echo -e "\n🎯 系统状态检查完成！"
