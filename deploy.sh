#!/bin/bash

# 工程项目流水账系统 - 一键部署脚本
# 版本: 1.0.1
# 作者: 系统管理员

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="工程项目流水账系统"
PROJECT_DIR="/home/dev/工程项目流水账"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend-new"
FRONTEND_DIST_DIR="$PROJECT_DIR/frontend/dist"
DB_NAME="project_ledger"
DB_USER="project_ledger"
DB_PASSWORD="project_ledger_123"
BACKEND_PORT="8000"
NGINX_CONFIG="/etc/nginx/nginx.conf"
NGINX_SITE_CONFIG="/etc/nginx/sites-enabled/default"

# 日志文件
LOG_FILE="$PROJECT_DIR/deploy.log"
BACKUP_DIR="$PROJECT_DIR/backups"

# 创建必要的目录
mkdir -p "$BACKUP_DIR"
mkdir -p "$FRONTEND_DIST_DIR"

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] 错误: $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%M:%S')] 警告: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%M:%S')] 信息: $1${NC}" | tee -a "$LOG_FILE"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统依赖
check_dependencies() {
    log "检查系统依赖..."
    
    local missing_deps=()
    
    # 检查必要的命令
    local commands=("node" "npm" "python3" "pip3" "git" "sudo")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "缺少必要的系统依赖: ${missing_deps[*]}"
        error "请先安装这些依赖后再运行部署脚本"
        exit 1
    fi
    
    log "系统依赖检查完成"
}

# 停止所有服务
stop_services() {
    log "停止所有服务..."
    
    # 停止后端服务
    if pgrep -f "uvicorn.*$BACKEND_PORT" > /dev/null; then
        log "停止后端服务 (端口: $BACKEND_PORT)..."
        sudo pkill -f "uvicorn.*$BACKEND_PORT" || true
        sleep 2
    fi
    
    # 停止Nginx
    if systemctl is-active --quiet nginx; then
        log "停止Nginx服务..."
        sudo systemctl stop nginx
    fi
    
    # 停止PostgreSQL
    if systemctl is-active --quiet postgresql; then
        log "停止PostgreSQL服务..."
        sudo systemctl stop postgresql
    fi
    
    log "所有服务已停止"
}

# 启动所有服务
start_services() {
    log "启动所有服务..."
    
    # 启动PostgreSQL
    if ! systemctl is-active --quiet postgresql; then
        log "启动PostgreSQL服务..."
        sudo systemctl start postgresql
        sleep 3
    fi
    
    # 启动Nginx
    if ! systemctl is-active --quiet nginx; then
        log "启动Nginx服务..."
        sudo systemctl start nginx
        sleep 2
    fi
    
    # 启动后端服务
    log "启动后端服务..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload > "$PROJECT_DIR/backend.log" 2>&1 &
    sleep 3
    
    # 检查服务状态
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null; then
        log "后端服务启动成功"
    else
        error "后端服务启动失败"
        exit 1
    fi
    
    if systemctl is-active --quiet nginx; then
        log "Nginx服务启动成功"
    else
        error "Nginx服务启动失败"
        exit 1
    fi
    
    log "所有服务启动完成"
}

# 安装系统依赖
install_system_dependencies() {
    log "安装系统依赖..."
    
    # 更新包列表
    sudo apt update
    
    # 安装必要的系统包
    local packages=(
        "python3"
        "python3-pip"
        "python3-venv"
        "postgresql"
        "postgresql-contrib"
        "nginx"
        "curl"
        "git"
        "build-essential"
        "libpq-dev"
        "python3-dev"
    )
    
    for package in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            log "安装 $package..."
            sudo apt install -y "$package"
        else
            log "$package 已安装"
        fi
    done
    
    log "系统依赖安装完成"
}

# 安装Node.js和npm
install_nodejs() {
    log "检查Node.js安装..."
    
    if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
        log "安装Node.js和npm..."
        
        # 下载并安装Node.js
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
        
        # 验证安装
        if command -v node &> /dev/null && command -v npm &> /dev/null; then
            log "Node.js $(node --version) 和 npm $(npm --version) 安装成功"
        else
            error "Node.js安装失败"
            exit 1
        fi
    else
        log "Node.js $(node --version) 和 npm $(npm --version) 已安装"
    fi
}

# 安装数据库
install_database() {
    log "安装和配置PostgreSQL数据库..."
    
    # 检查PostgreSQL是否已安装
    if ! command -v psql &> /dev/null; then
        error "PostgreSQL未安装，请先运行: ./deploy.sh install-deps"
        exit 1
    fi
    
    # 启动PostgreSQL服务
    if ! systemctl is-active --quiet postgresql; then
        sudo systemctl start postgresql
        sleep 3
    fi
    
    # 创建数据库用户和数据库
    log "创建数据库用户和数据库..."
    
    sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || {
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        log "数据库用户 $DB_USER 创建成功"
    }
    
    sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || {
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        log "数据库 $DB_NAME 创建成功"
    }
    
    # 授予权限
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    sudo -u postgres psql -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    
    log "数据库安装和配置完成"
}

# 安装后端依赖
install_backend_dependencies() {
    log "安装后端依赖..."
    
    cd "$BACKEND_DIR"
    
    # 创建虚拟环境
    if [[ ! -d "venv" ]]; then
        log "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [[ -f "requirements.txt" ]]; then
        log "安装Python依赖..."
        pip install -r requirements.txt
    else
        log "安装基础Python依赖..."
        pip install fastapi uvicorn sqlalchemy asyncpg redis celery python-multipart python-jose[cryptography] passlib[bcrypt] alembic
    fi
    
    log "后端依赖安装完成"
}

# 安装前端依赖
install_frontend_dependencies() {
    log "安装前端依赖..."
    
    cd "$FRONTEND_DIR"
    
    # 安装npm依赖
    if [[ -f "package.json" ]]; then
        log "安装Node.js依赖..."
        npm install
    else
        error "前端目录中未找到package.json文件"
        exit 1
    fi
    
    log "前端依赖安装完成"
}

# 数据库迁移
run_database_migrations() {
    log "运行数据库迁移..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 检查alembic配置
    if [[ ! -f "alembic.ini" ]]; then
        log "初始化Alembic..."
        alembic init alembic
    fi
    
    # 运行迁移
    log "执行数据库迁移..."
    alembic upgrade head
    
    log "数据库迁移完成"
}

# 数据库备份
backup_database() {
    log "创建数据库备份..."
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/db_backup_$timestamp.sql"
    
    # 创建备份
    sudo -u postgres pg_dump "$DB_NAME" > "$backup_file"
    
    if [[ $? -eq 0 ]]; then
        log "数据库备份创建成功: $backup_file"
        
        # 压缩备份文件
        gzip "$backup_file"
        log "备份文件已压缩: $backup_file.gz"
        
        # 清理旧备份（保留最近10个）
        local backup_count=$(ls -1 "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | wc -l)
        if [[ $backup_count -gt 10 ]]; then
            log "清理旧备份文件..."
            ls -t "$BACKUP_DIR"/db_backup_*.sql.gz | tail -n +11 | xargs rm -f
        fi
    else
        error "数据库备份创建失败"
        exit 1
    fi
}

# 构建前端
build_frontend() {
    log "构建前端应用..."
    
    cd "$FRONTEND_DIR"
    
    # 检查依赖
    if [[ ! -d "node_modules" ]]; then
        log "前端依赖未安装，正在安装..."
        npm install
    fi
    
    # 构建生产版本
    log "执行前端构建..."
    npm run build
    
    if [[ $? -eq 0 ]]; then
        log "前端构建成功"
        
        # 复制到生产目录
        log "部署前端到生产目录..."
        sudo rm -rf "$FRONTEND_DIST_DIR"/*
        sudo cp -r dist/* "$FRONTEND_DIST_DIR/"
        sudo chown -R www-data:www-data "$FRONTEND_DIST_DIR"
        
        log "前端部署完成"
    else
        error "前端构建失败"
        exit 1
    fi
}

# 配置Nginx
configure_nginx() {
    log "配置Nginx..."
    
    # 检查Nginx配置
    if [[ ! -f "$NGINX_CONFIG" ]]; then
        error "Nginx配置文件不存在: $NGINX_CONFIG"
        exit 1
    fi
    
    # 测试Nginx配置
    if sudo nginx -t; then
        log "Nginx配置测试通过"
        
        # 重新加载Nginx
        sudo systemctl reload nginx
        log "Nginx配置已重新加载"
    else
        error "Nginx配置测试失败"
        exit 1
    fi
}

# 健康检查
health_check() {
    log "执行系统健康检查..."
    
    local checks_passed=0
    local total_checks=4
    
    # 检查后端服务
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null; then
        log "✅ 后端服务正常"
        ((checks_passed++))
    else
        error "❌ 后端服务异常"
    fi
    
    # 检查Nginx服务
    if systemctl is-active --quiet nginx; then
        log "✅ Nginx服务正常"
        ((checks_passed++))
    else
        error "❌ Nginx服务异常"
    fi
    
    # 检查PostgreSQL服务
    if systemctl is-active --quiet postgresql; then
        log "✅ PostgreSQL服务正常"
        ((checks_passed++))
    else
        error "❌ PostgreSQL服务异常"
    fi
    
    # 检查前端文件
    if [[ -f "$FRONTEND_DIST_DIR/index.html" ]]; then
        log "✅ 前端文件正常"
        ((checks_passed++))
    else
        error "❌ 前端文件异常"
    fi
    
    if [[ $checks_passed -eq $total_checks ]]; then
        log "🎉 所有健康检查通过！系统运行正常"
    else
        warn "⚠️  部分健康检查失败，请检查系统状态"
    fi
    
    return $((total_checks - checks_passed))
}

# 显示帮助信息
show_help() {
    cat << EOF
$PROJECT_NAME - 一键部署脚本

用法: $0 [命令]

命令:
    install-deps      安装系统依赖（首次部署）
    install-db        安装和配置数据库
    install-backend   安装后端依赖
    install-frontend  安装前端依赖
    migrate           运行数据库迁移
    backup            创建数据库备份
    build             构建前端应用
    deploy            完整部署（包含构建和重启）
    restart           重启所有服务
    stop              停止所有服务
    start             启动所有服务
    status            检查服务状态
    health            执行健康检查
    help              显示此帮助信息

示例:
    $0 install-deps    # 首次部署，安装系统依赖
    $0 deploy          # 完整部署
    $0 restart         # 重启服务
    $0 health          # 健康检查

注意: 首次部署请按顺序执行 install-deps -> install-db -> install-backend -> install-frontend -> migrate -> deploy
EOF
}

# 主函数
main() {
    local command="${1:-help}"
    
    # 记录开始时间
    local start_time=$(date +%s)
    
    log "开始执行命令: $command"
    log "项目目录: $PROJECT_DIR"
    
    case "$command" in
        "install-deps")
            check_root
            check_dependencies
            install_system_dependencies
            install_nodejs
            log "系统依赖安装完成"
            ;;
        "install-db")
            install_database
            ;;
        "install-backend")
            install_backend_dependencies
            ;;
        "install-frontend")
            install_frontend_dependencies
            ;;
        "migrate")
            run_database_migrations
            ;;
        "backup")
            backup_database
            ;;
        "build")
            build_frontend
            ;;
        "deploy")
            backup_database
            build_frontend
            configure_nginx
            restart_services
            health_check
            ;;
        "restart")
            stop_services
            start_services
            health_check
            ;;
        "stop")
            stop_services
            ;;
        "start")
            start_services
            ;;
        "status")
            log "检查服务状态..."
            systemctl status nginx postgresql --no-pager -l
            ;;
        "health")
            health_check
            ;;
        "help"|*)
            show_help
            ;;
    esac
    
    # 记录结束时间
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "命令执行完成，耗时: ${duration}秒"
}

# 重启服务函数
restart_services() {
    log "重启所有服务..."
    stop_services
    sleep 2
    start_services
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
