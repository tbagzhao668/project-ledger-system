#!/bin/bash

# 数据库密码重置脚本
# 专门用于重置数据库用户密码为配置文件中的值：Fince_project_5%8*6^9(3#0)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="工程项目流水账管理系统"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/logs/reset_password.log"

# 数据库配置（从deploy.sh保持一致）
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="fince_project_prod"
DB_USER="fince_app_project"
DB_PASSWORD="Fince_project_5%8*6^9(3#0)"

# 日志函数
log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[$timestamp]${NC} $message" | tee -a "$LOG_FILE"
}

warn() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${YELLOW}[$timestamp] WARNING:${NC} $message" | tee -a "$LOG_FILE"
}

error() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${RED}[$timestamp] ERROR:${NC} $message" | tee -a "$LOG_FILE"
}

success() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${GREEN}[$timestamp] SUCCESS:${NC} $message" | tee -a "$LOG_FILE"
}

# 检查PostgreSQL服务状态
check_postgresql() {
    log "🔍 检查PostgreSQL服务状态..."
    
    if ! systemctl is-active --quiet postgresql; then
        error "PostgreSQL服务未运行，正在启动..."
        sudo systemctl start postgresql
        sleep 3
        
        if ! systemctl is-active --quiet postgresql; then
            error "PostgreSQL启动失败"
            return 1
        fi
    fi
    
    success "PostgreSQL服务运行正常"
    return 0
}

# 重置数据库用户密码
reset_db_password() {
    log "🔐 重置数据库用户密码..."
    
    # 检查用户是否存在
    if ! sudo -u postgres psql -c "\du $DB_USER" > /dev/null 2>&1; then
        warn "数据库用户 $DB_USER 不存在，正在创建..."
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB CREATEROLE;"
        success "数据库用户 $DB_USER 创建成功"
    else
        log "数据库用户 $DB_USER 已存在，正在重置密码..."
        sudo -u postgres psql -c "ALTER ROLE $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        success "数据库用户 $DB_USER 密码重置成功"
    fi
    
    # 验证密码是否正确
    log "🔍 验证数据库连接..."
    if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
        success "数据库连接验证成功"
    else
        error "数据库连接验证失败"
        return 1
    fi
    
    return 0
}

# 重置应用用户密码（可选）
reset_app_user_password() {
    log "👤 重置应用用户密码（可选功能）..."
    
    # 检查数据库是否存在
    if ! sudo -u postgres psql -l | grep -q "^[[:space:]]*$DB_NAME[[:space:]]"; then
        warn "数据库 $DB_NAME 不存在，跳过应用用户密码重置"
        return 0
    fi
    
    # 检查users表是否存在
    if ! sudo -u postgres psql -d "$DB_NAME" -c "\dt users" > /dev/null 2>&1; then
        warn "users表不存在，跳过应用用户密码重置"
        return 0
    fi
    
    log "💡 应用用户密码重置功能已跳过（主要功能是重置数据库用户密码）"
    return 0
}

# 测试数据库连接
test_database_connection() {
    log "🧪 测试数据库连接..."
    
    # 测试应用用户连接
    if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM users;" > /dev/null 2>&1; then
        success "应用用户数据库连接测试成功"
    else
        error "应用用户数据库连接测试失败"
        return 1
    fi
    
    # 测试后端API连接
    log "🔍 测试后端API连接..."
    if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
        success "后端API连接测试成功"
    else
        warn "后端API连接测试失败，可能需要重启服务"
    fi
    
    return 0
}

# 重启后端服务
restart_backend_service() {
    log "🔄 重启后端服务..."
    
    if systemctl is-active --quiet fince-backend.service; then
        sudo systemctl restart fince-backend.service
        sleep 3
        
        if systemctl is-active --quiet fince-backend.service; then
            success "后端服务重启成功"
        else
            error "后端服务重启失败"
            return 1
        fi
    else
        warn "后端服务未运行，正在启动..."
        sudo systemctl start fince-backend.service
        sleep 3
        
        if systemctl is-active --quiet fince-backend.service; then
            success "后端服务启动成功"
        else
            error "后端服务启动失败"
            return 1
        fi
    fi
    
    return 0
}

# 显示帮助信息
show_help() {
    cat << EOF
$PROJECT_NAME - 数据库密码重置脚本

用法: $0 [选项]

选项:
    --help, -h          显示此帮助信息
    --test             测试数据库连接
    --restart          重启后端服务

示例:
    $0                   # 重置数据库用户密码
    $0 --test           # 测试数据库连接
    $0 --restart        # 重启后端服务

注意:
- 此脚本专门用于重置数据库用户密码为配置文件中的值
- 数据库用户: fince_app_project
- 数据库密码: Fince_project_5%8*6^9(3#0)
- 此密码与 deploy.sh 中的配置保持一致
EOF
}

# 主函数
main() {
    local test_connection=false
    local restart_service=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --test)
                test_connection=true
                shift
                ;;
            --restart)
                restart_service=true
                shift
                ;;
            *)
                error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定选项，默认执行数据库密码重置
    if [[ "$test_connection" == false && "$restart_service" == false ]]; then
        test_connection=true
        restart_service=true
    fi
    
    # 创建日志目录
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log "🚀 开始执行数据库密码重置..."
    log "项目目录: $PROJECT_DIR"
    
    # 检查PostgreSQL服务
    if ! check_postgresql; then
        exit 1
    fi
    
    # 重置数据库用户密码（主要功能）
    log "🔐 开始重置数据库用户密码..."
    if ! reset_db_password; then
        error "数据库用户密码重置失败"
        exit 1
    fi
    
    # 重置应用用户密码（可选功能）
    reset_app_user_password
    
    # 测试数据库连接
    if [[ "$test_connection" == true ]]; then
        if ! test_database_connection; then
            error "数据库连接测试失败"
            exit 1
        fi
    fi
    
    # 重启后端服务
    if [[ "$restart_service" == true ]]; then
        if ! restart_backend_service; then
            error "后端服务重启失败"
            exit 1
        fi
    fi
    
    success "🎉 数据库密码重置完成！"
    log "📱 数据库连接信息:"
    log "   数据库用户: $DB_USER"
    log "   数据库密码: $DB_PASSWORD"
    log "   数据库名称: $DB_NAME"
    log "   数据库主机: $DB_HOST:$DB_PORT"
    
    exit 0
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
