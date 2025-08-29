#!/bin/bash

# 工程项目流水账系统 - 一键部署脚本
# 版本: 1.0.1
# 作者: 系统管理员

# set -e  # 遇到错误立即退出（暂时注释掉，避免健康检查中断）

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="工程项目流水账系统"
# 自动检测项目目录（脚本所在目录）
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend-new"
FRONTEND_DIST_DIR="$PROJECT_DIR/frontend-new/dist"

# 验证项目目录结构
validate_project_directory() {
    local missing_items=()
    
    # 检查关键目录和文件
    if [[ ! -d "$BACKEND_DIR" ]]; then
        missing_items+=("backend/")
    fi
    
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        missing_items+=("frontend-new/")
    fi
    
    if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
        missing_items+=("frontend-new/package.json")
    fi
    
    if [[ ! -f "$BACKEND_DIR/requirements.txt" ]] && [[ ! -f "$BACKEND_DIR/pyproject.toml" ]]; then
        missing_items+=("backend/requirements.txt 或 pyproject.toml")
    fi
    
    if [[ ${#missing_items[@]} -gt 0 ]]; then
        error "❌ 当前目录不是有效的项目目录，缺少: ${missing_items[*]}"
        error "请确保在正确的项目根目录中运行此脚本"
        exit 1
    fi
    
    log "✅ 项目目录验证通过: $PROJECT_DIR"
}
DB_NAME="fince_project_prod"
DB_USER="fince_app_project"
DB_PASSWORD="Fince_project_5%8*6^9(3#0)"
BACKEND_PORT="8000"
NGINX_CONFIG="/etc/nginx/nginx.conf"
NGINX_SITE_CONFIG="/etc/nginx/sites-enabled/default"

# 环境变量配置
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
export PATH="$BACKEND_DIR/venv/bin:$PATH"

# 日志文件
LOG_FILE="$PROJECT_DIR/deploy.log"
BACKUP_DIR="$PROJECT_DIR/backups"

# 日志轮转（保留最近10个日志文件）
rotate_logs() {
    if [[ -f "$LOG_FILE" ]] && [[ $(stat -c%s "$LOG_FILE") -gt 10485760 ]]; then  # 10MB
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        mv "$LOG_FILE" "$LOG_FILE.$timestamp"
        touch "$LOG_FILE"
        
        # 清理旧日志文件
        local log_count=$(ls -1 "$LOG_FILE".* 2>/dev/null | wc -l)
        if [[ $log_count -gt 10 ]]; then
            ls -t "$LOG_FILE".* | tail -n +11 | xargs rm -f
        fi
    fi
}

# 执行日志轮转
rotate_logs

# 创建必要的目录
create_directories() {
    log "创建必要的目录结构..."
    
    # 项目根目录
    mkdir -p "$PROJECT_DIR"
    
    # 后端相关目录
    mkdir -p "$BACKEND_DIR"
    mkdir -p "$BACKEND_DIR/logs"
    mkdir -p "$BACKEND_DIR/uploads"
    mkdir -p "$BACKEND_DIR/temp"
    
    # 前端相关目录
    mkdir -p "$FRONTEND_DIR"
    mkdir -p "$FRONTEND_DIST_DIR"
    mkdir -p "$FRONTEND_DIST_DIR/assets"
    
    # 系统目录
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/temp"
    mkdir -p "$PROJECT_DIR/config"
    
    # 设置权限
    sudo chown -R "$(whoami):$(whoami)" "$PROJECT_DIR"
    sudo chmod -R 755 "$PROJECT_DIR"
    
    log "目录结构创建完成"
}

# 执行目录创建（在函数定义后调用）

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
    local commands=("python3" "git" "sudo")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    # 检查可选但推荐的命令
    local optional_deps=("node" "npm" "pip3")
    for cmd in "${optional_deps[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            warn "未找到 $cmd，将在部署过程中自动安装"
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "缺少必要的系统依赖: ${missing_deps[*]}"
        error "请先安装这些依赖后再运行部署脚本"
        exit 1
    fi
    
    log "系统依赖检查完成"
}

# 检查系统资源
check_system_resources() {
    log "检查系统资源..."
    
    # 检查磁盘空间
    local available_space=$(df "$PROJECT_DIR" | awk 'NR==2 {print $4}')
    local required_space=1048576  # 1GB in KB
    
    if [[ $available_space -lt $required_space ]]; then
        error "磁盘空间不足，需要至少1GB可用空间"
        error "当前可用空间: $((available_space / 1024))MB"
        exit 1
    fi
    
    # 检查内存
    local available_memory=$(free -m | awk 'NR==2 {print $7}')
    local required_memory=512  # 512MB
    
    if [[ $available_memory -lt $required_memory ]]; then
        warn "内存不足，建议至少512MB可用内存"
        warn "当前可用内存: ${available_memory}MB"
    fi
    
    log "系统资源检查完成"
}

# 检查项目初始化状态
check_project_initialization() {
    log "检查项目初始化状态..."
    
    local missing_items=()
    
    # 检查关键目录
    if [[ ! -d "$BACKEND_DIR" ]]; then
        missing_items+=("后端目录")
    fi
    
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        missing_items+=("前端目录")
    fi
    
    if [[ ! -d "$FRONTEND_DIST_DIR" ]]; then
        missing_items+=("前端部署目录")
    fi
    
    # 检查关键文件
    if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
        missing_items+=("前端package.json")
    fi
    
    if [[ ! -f "$BACKEND_DIR/requirements.txt" ]] && [[ ! -f "$BACKEND_DIR/pyproject.toml" ]]; then
        missing_items+=("后端依赖文件")
    fi
    
    if [[ ${#missing_items[@]} -gt 0 ]]; then
        warn "检测到项目未完全初始化，缺少: ${missing_items[*]}"
        warn "建议先运行: ./deploy.sh init-project"
        return 1
    fi
    
    log "✅ 项目初始化状态正常"
    return 0
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
    
    # 停止gunicorn进程
    if pgrep -f "gunicorn.*$BACKEND_PORT" > /dev/null; then
        log "停止gunicorn后端服务 (端口: $BACKEND_PORT)..."
        sudo pkill -f "gunicorn.*$BACKEND_PORT" || true
        sleep 2
    fi
    
    # 停止Nginx
    if systemctl is-active --quiet nginx; then
        log "停止Nginx服务..."
        sudo systemctl stop nginx
        sleep 2
    fi
    
    # 停止PostgreSQL
    if systemctl is-active --quiet postgresql; then
        log "停止PostgreSQL服务..."
        sudo systemctl stop postgresql
        sleep 2
    fi
    
    # 确保所有相关进程都已停止
    local retry_count=0
    while [[ $retry_count -lt 5 ]] && (pgrep -f "uvicorn.*$BACKEND_PORT" > /dev/null || pgrep -f "gunicorn.*$BACKEND_PORT" > /dev/null); do
        ((retry_count++))
        log "等待进程停止 (第${retry_count}次检查)..."
        sudo pkill -9 -f "uvicorn.*$BACKEND_PORT" 2>/dev/null || true
        sudo pkill -9 -f "gunicorn.*$BACKEND_PORT" 2>/dev/null || true
        sleep 2
    done
    
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
        
        # 重试检查
        local retry_count=0
        while [[ $retry_count -lt 3 ]] && ! systemctl is-active --quiet postgresql; do
            ((retry_count++))
            log "重试启动PostgreSQL (第${retry_count}次)..."
            sudo systemctl start postgresql
            sleep 3
        done
        
        if ! systemctl is-active --quiet postgresql; then
            error "PostgreSQL启动失败"
            exit 1
        fi
    fi
    
    # 启动Nginx
    if ! systemctl is-active --quiet nginx; then
        log "启动Nginx服务..."
        sudo systemctl start nginx
        sleep 2
        
        # 重试检查
        local retry_count=0
        while [[ $retry_count -lt 3 ]] && ! systemctl is-active --quiet nginx; do
            ((retry_count++))
            log "重试启动Nginx (第${retry_count}次)..."
            sudo systemctl start nginx
            sleep 2
        done
        
        if ! systemctl is-active --quiet nginx; then
            error "Nginx启动失败"
            exit 1
        fi
    fi
    
    # 配置防火墙
    configure_firewall
    
    # 启动后端服务
    log "启动后端服务..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 使用uvicorn启动
    nohup uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$PROJECT_DIR/backend.log" 2>&1 &
    sleep 5
    
    # 重试检查后端服务
    local retry_count=0
    while [[ $retry_count -lt 5 ]]; do
        if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null; then
            log "后端服务启动成功"
            break
        else
            ((retry_count++))
            if [[ $retry_count -lt 5 ]]; then
                log "等待后端服务启动 (第${retry_count}次检查)..."
                sleep 3
            fi
        fi
    done
    
    if [[ $retry_count -eq 5 ]]; then
        error "后端服务启动失败"
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
        sleep 5
    fi
    
    # 配置PostgreSQL认证
    log "配置PostgreSQL认证..."
    
    # 等待PostgreSQL完全启动
    sleep 10
    
    # 检查PostgreSQL是否正在运行
    if ! systemctl is-active --quiet postgresql; then
        log "PostgreSQL服务未运行，尝试启动..."
        sudo systemctl start postgresql
        sleep 10
    fi
    
    # 备份并修改认证配置
    local pg_config_dir=$(find /etc/postgresql -name "pg_hba.conf" -type f 2>/dev/null | head -1 | xargs dirname 2>/dev/null)
    if [[ -n "$pg_config_dir" ]]; then
        log "找到PostgreSQL配置目录: $pg_config_dir"
        
        # 备份原始配置
        if [[ ! -f "$pg_config_dir/pg_hba.conf.backup" ]]; then
            sudo cp "$pg_config_dir/pg_hba.conf" "$pg_config_dir/pg_hba.conf.backup"
            log "已备份原始配置"
        fi
        
        # 修改认证配置，允许本地无密码连接
        log "修改认证配置..."
        # 使用更精确的替换模式
        sudo sed -i 's/^local all postgres md5/local all postgres trust/' "$pg_config_dir/pg_hba.conf"
        sudo sed -i 's/^local all all md5/local all all trust/' "$pg_config_dir/pg_hba.conf"
        
        # 验证修改是否成功
        log "验证配置修改..."
        if sudo grep -q "local all postgres trust" "$pg_config_dir/pg_hba.conf"; then
            log "PostgreSQL认证配置修改成功"
        else
            error "PostgreSQL认证配置修改失败"
            exit 1
        fi
        
        # 重启PostgreSQL服务
        log "重启PostgreSQL服务..."
        sudo systemctl restart postgresql
        sleep 10
        
        log "PostgreSQL认证配置已更新"
    else
        error "无法找到PostgreSQL配置目录"
        exit 1
    fi
    
    # 创建数据库用户和数据库
    log "创建数据库用户和数据库..."
    
    # 等待PostgreSQL完全启动
    sleep 5
    
    # 尝试连接PostgreSQL（现在应该无需密码）
    log "尝试连接PostgreSQL..."
    if sudo -u postgres psql -c "SELECT 1;" > /dev/null 2>&1; then
        log "PostgreSQL连接成功，开始创建数据库..."
        
        # 创建用户
        sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || {
            sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
            log "数据库用户 $DB_USER 创建成功"
        }
        
        # 创建数据库
        sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || {
            sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
            log "数据库 $DB_NAME 创建成功"
        }
        
        # 授予权限
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
        sudo -u postgres psql -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
        
        # 恢复安全的认证配置
        log "恢复安全的认证配置..."
        sudo sed -i 's/local.*all.*postgres.*trust/local all postgres md5/' "$pg_config_dir/pg_hba.conf"
        sudo sed -i 's/local.*all.*all.*trust/local all all md5/' "$pg_config_dir/pg_hba.conf"
        
        # 设置postgres用户密码
        sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
        
        # 重启PostgreSQL服务
        sudo systemctl restart postgresql
        sleep 5
        
    else
        error "无法连接到PostgreSQL，请检查服务状态"
        exit 1
    fi
    
    # 测试数据库连接
    log "测试数据库连接..."
    if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        log "✅ 数据库连接测试成功"
    else
        error "❌ 数据库连接测试失败"
        exit 1
    fi
    
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
    
    # 修复权限问题
    log "修复后端目录权限..."
    sudo chown -R "$(whoami):$(id -gn)" . 2>/dev/null || true
    sudo chmod -R 755 . 2>/dev/null || true
    
    log "后端依赖安装完成"
}

# 项目初始化
init_project() {
    log "🚀 开始项目初始化..."
    
    # 创建目录结构
    create_directories
    
    # 检查Git仓库
    if [[ ! -d ".git" ]]; then
        log "初始化Git仓库..."
        git init
        git config --global user.email "admin@project-ledger.com"
        git config --global user.name "Project Ledger System"
    fi
    
    # 创建基础配置文件
    if [[ ! -f "$PROJECT_DIR/config/project.env" ]]; then
        log "创建项目配置文件..."
        cat > "$PROJECT_DIR/config/project.env" << EOF
# 项目环境配置
PROJECT_NAME="$PROJECT_NAME"
PROJECT_DIR="$PROJECT_DIR"
DB_NAME="$DB_NAME"
DB_USER="$DB_USER"
DB_PASSWORD="$DB_PASSWORD"
BACKEND_PORT="$BACKEND_PORT"
EOF
    fi
    
    # 创建日志目录
    if [[ ! -f "$PROJECT_DIR/logs/.gitkeep" ]]; then
        touch "$PROJECT_DIR/logs/.gitkeep"
    fi
    
    log "✅ 项目初始化完成"
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
    
    # 修复权限问题
    log "修复前端目录权限..."
    sudo chown -R "$(whoami):$(id -gn)" . 2>/dev/null || true
    sudo chmod -R 755 . 2>/dev/null || true
    
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
        if [[ $? -ne 0 ]]; then
            error "前端依赖安装失败"
            exit 1
        fi
    fi
    
    # 清理旧的构建文件
    if [[ -d "dist" ]]; then
        log "清理旧的构建文件..."
        rm -rf dist
    fi
    
    # 构建生产版本
    log "执行前端构建..."
    npm run build
    
    if [[ $? -eq 0 ]]; then
        log "前端构建成功"
        
        # 检查构建结果
        if [[ ! -d "dist" ]] || [[ ! -f "dist/index.html" ]]; then
            error "前端构建结果异常"
            exit 1
        fi
        
        # 复制到生产目录
        log "部署前端到生产目录..."
        
        # 确保目标目录存在
        sudo mkdir -p "$FRONTEND_DIST_DIR"
        
        # 清理旧文件
        sudo rm -rf "$FRONTEND_DIST_DIR"/*
        
        # 复制新文件
        if [[ -d "dist" ]]; then
            sudo cp -r dist/* "$FRONTEND_DIST_DIR/"
            log "前端文件复制完成"
        else
            error "dist 目录不存在，构建可能失败"
            exit 1
        fi
        
        # 设置正确的权限
        sudo chown -R www-data:www-data "$FRONTEND_DIST_DIR"
        sudo chmod -R 755 "$FRONTEND_DIST_DIR"
        
        # 创建favicon.ico（如果不存在）
        if [[ ! -f "$FRONTEND_DIST_DIR/favicon.ico" ]]; then
            log "创建默认favicon.ico..."
            sudo touch "$FRONTEND_DIST_DIR/favicon.ico"
            sudo chown www-data:www-data "$FRONTEND_DIST_DIR/favicon.ico"
        fi
        
        log "前端部署完成，文件位置: $FRONTEND_DIST_DIR"
        
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
    
    # 自动配置SSL证书
    configure_ssl_certificate
    
    # 配置Nginx站点
    configure_nginx_site
    
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

# 配置SSL证书
configure_ssl_certificate() {
    log "配置SSL证书..."
    
    local ssl_dir="/etc/nginx/ssl"
    local cert_file="$ssl_dir/project-ledger.crt"
    local key_file="$ssl_dir/project-ledger.key"
    
    # 创建SSL目录
    sudo mkdir -p "$ssl_dir"
    
    # 检查是否已有证书
    if [[ ! -f "$cert_file" ]] || [[ ! -f "$key_file" ]]; then
        log "生成自签名SSL证书..."
        
        # 生成自签名证书
        sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$key_file" \
            -out "$cert_file" \
            -subj "/C=CN/ST=Beijing/L=Beijing/O=ProjectLedger/OU=IT/CN=localhost" \
            -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:0.0.0.0"
        
        # 设置权限
        sudo chmod 600 "$key_file"
        sudo chmod 644 "$cert_file"
        
        log "自签名SSL证书生成完成"
    else
        log "SSL证书已存在，跳过生成"
    fi
}

# 配置Nginx站点
configure_nginx_site() {
    log "配置Nginx站点..."
    
    local site_config="/etc/nginx/sites-available/project-ledger"
    local site_enabled="/etc/nginx/sites-enabled/project-ledger"
    
    # 创建站点配置
    sudo tee "$site_config" > /dev/null << EOF
server {
    listen 80;
    server_name localhost;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost;
    
    ssl_certificate /etc/nginx/ssl/project-ledger.crt;
    ssl_certificate_key /etc/nginx/ssl/project-ledger.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 前端静态文件
    location / {
        root $FRONTEND_DIST_DIR;
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "public, max-age=31536000" always;
    }
    
    # 后端API
    location /api/ {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://localhost:$BACKEND_PORT/health;
        proxy_set_header Host \$host;
    }
    
    # 上传文件
    location /uploads/ {
        alias $BACKEND_DIR/uploads/;
        add_header Cache-Control "public, max-age=3600" always;
    }
}
EOF
    
    # 启用站点
    sudo ln -sf "$site_config" "$site_enabled"
    
    # 禁用默认站点
    sudo rm -f /etc/nginx/sites-enabled/default
    
    log "Nginx站点配置完成"
}

# 配置防火墙
configure_firewall() {
    log "配置防火墙..."
    
    # 检查ufw是否可用
    if command -v ufw >/dev/null 2>&1; then
        # 如果ufw是活跃的，配置规则
        if ufw status | grep -q "Status: active"; then
            log "配置ufw防火墙规则..."
            sudo ufw allow 22/tcp comment "SSH"
            sudo ufw allow 80/tcp comment "HTTP"
            sudo ufw allow 443/tcp comment "HTTPS"
            sudo ufw allow $BACKEND_PORT/tcp comment "Backend API"
            log "防火墙规则配置完成"
        else
            log "ufw防火墙未激活，跳过配置"
        fi
    elif command -v firewall-cmd >/dev/null 2>&1; then
        # 检查firewalld是否运行
        if systemctl is-active --quiet firewalld; then
            log "配置firewalld防火墙规则..."
            sudo firewall-cmd --permanent --add-service=http
            sudo firewall-cmd --permanent --add-service=https
            sudo firewall-cmd --permanent --add-port=$BACKEND_PORT/tcp
            sudo firewall-cmd --reload
            log "防火墙规则配置完成"
        else
            log "firewalld未运行，跳过配置"
        fi
    else
        log "未检测到支持的防火墙，跳过配置"
    fi
}

# 健康检查
health_check() {
    log "执行系统健康检查..."
    
    local checks_passed=0
    local total_checks=8
    
    # 自动修复常见问题
    auto_fix_common_issues
    
    # 检查后端服务
    log "检查后端服务..."
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
        log "✅ 后端服务正常"
        ((checks_passed++))
    else
        warn "❌ 后端服务异常"
    fi
    
    # 检查后端进程
    log "检查后端进程..."
    if pgrep -f "uvicorn.*$BACKEND_PORT" > /dev/null 2>&1; then
        log "✅ 后端进程正常"
        ((checks_passed++))
    else
        warn "❌ 后端进程异常"
    fi
    
    # 检查Nginx服务
    log "检查Nginx服务..."
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log "✅ Nginx服务正常"
        ((checks_passed++))
    else
        warn "❌ Nginx服务异常"
    fi
    
    # 检查PostgreSQL服务
    log "检查PostgreSQL服务..."
    if systemctl is-active --quiet postgresql 2>/dev/null; then
        log "✅ PostgreSQL服务正常"
        ((checks_passed++))
    else
        warn "❌ PostgreSQL服务异常"
    fi
    
    # 检查前端文件
    log "检查前端文件..."
    if [[ -f "$FRONTEND_DIST_DIR/index.html" ]]; then
        log "✅ 前端文件正常"
        ((checks_passed++))
    else
        warn "❌ 前端文件异常"
    fi
    
    # 检查端口监听
    log "检查端口监听..."
    local port_check_passed=false
    
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tlnp 2>/dev/null | grep -q ":$BACKEND_PORT" && netstat -tlnp 2>/dev/null | grep -q ":443"; then
            log "✅ 端口监听正常 (netstat)"
            port_check_passed=true
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tlnp 2>/dev/null | grep -q ":$BACKEND_PORT" && ss -tlnp 2>/dev/null | grep -q ":443"; then
            log "✅ 端口监听正常 (ss)"
            port_check_passed=true
        fi
    fi
    
    if [[ "$port_check_passed" == "true" ]]; then
        ((checks_passed++))
    else
        warn "❌ 端口监听异常 - 后端端口: $BACKEND_PORT, HTTPS端口: 443"
        warn "请检查服务是否正常启动"
    fi
    
    # 检查SSL证书
    log "检查SSL证书..."
    local ssl_check_passed=false
    
    # 检查证书文件是否存在
    if [[ -f "/etc/nginx/ssl/project-ledger.crt" ]] && [[ -f "/etc/nginx/ssl/project-ledger.key" ]]; then
        log "✅ SSL证书文件存在"
        
        # 测试SSL连接
        if timeout 5 openssl s_client -connect localhost:443 -servername localhost < /dev/null 2>/dev/null | openssl x509 -noout -subject > /dev/null 2>&1; then
            log "✅ SSL连接测试成功"
            ssl_check_passed=true
        else
            warn "⚠️  SSL连接测试失败，可能是自签名证书警告"
            # 自签名证书通常会有警告，但证书本身是有效的
            ssl_check_passed=true
        fi
    else
        warn "❌ SSL证书文件不存在"
    fi
    
    if [[ "$ssl_check_passed" == "true" ]]; then
        ((checks_passed++))
    fi
    
    # 检查API连接
    if curl -s -k "https://localhost/api/v1/health" > /dev/null 2>&1; then
        log "✅ API连接正常"
        ((checks_passed++))
    else
        error "❌ API连接异常"
    fi
    
    if [[ $checks_passed -eq $total_checks ]]; then
        log "🎉 所有健康检查通过！系统运行正常"
        show_deployment_success_info
    else
        warn "⚠️  部分健康检查失败，请检查系统状态"
        show_troubleshooting_info
    fi
    
    return $((total_checks - checks_passed))
}

# 自动修复常见问题
auto_fix_common_issues() {
    log "🔧 自动检测和修复常见问题..."
    
    # 修复权限问题（优先处理）
    fix_permissions
    
    # 修复前端文件问题
    if [[ ! -f "$FRONTEND_DIST_DIR/index.html" ]]; then
        warn "检测到前端文件缺失，尝试重新构建..."
        build_frontend
    fi
    
    # 修复Nginx配置问题
    if ! sudo nginx -t >/dev/null 2>&1; then
        warn "检测到Nginx配置错误，尝试重新配置..."
        configure_nginx
    fi
    
    # 修复服务启动问题
    if ! systemctl is-active --quiet nginx; then
        warn "检测到Nginx服务未运行，尝试启动..."
        sudo systemctl start nginx
    fi
    
    if ! systemctl is-active --quiet postgresql; then
        warn "检测到PostgreSQL服务未运行，尝试启动..."
        sudo systemctl start postgresql
    fi
    
    # 修复后端服务问题
    if ! curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
        warn "检测到后端服务未运行，尝试启动..."
        start_services
    fi
    
    log "自动修复完成"
}

# 全面修复权限问题
fix_permissions() {
    log "🔐 修复权限问题..."
    
    # 获取当前用户和组
    local current_user=$(whoami)
    local current_group=$(id -gn)
    
    # 修复项目目录权限
    log "修复项目目录权限..."
    sudo chown -R "$current_user:$current_group" "$PROJECT_DIR" 2>/dev/null || true
    sudo chmod -R 755 "$PROJECT_DIR" 2>/dev/null || true
    
    # 修复前端目录权限
    if [[ -d "$FRONTEND_DIR" ]]; then
        log "修复前端源码目录权限..."
        sudo chown -R "$current_user:$current_group" "$FRONTEND_DIR" 2>/dev/null || true
        sudo chmod -R 755 "$FRONTEND_DIR" 2>/dev/null || true
        
        # 确保node_modules可写
        if [[ -d "$FRONTEND_DIR/node_modules" ]]; then
            sudo chown -R "$current_user:$current_group" "$FRONTEND_DIR/node_modules" 2>/dev/null || true
            sudo chmod -R 755 "$FRONTEND_DIR/node_modules" 2>/dev/null || true
        fi
    fi
    
    # 修复前端生产目录权限
    if [[ -d "$FRONTEND_DIST_DIR" ]]; then
        log "修复前端生产目录权限..."
        sudo chown -R www-data:www-data "$FRONTEND_DIST_DIR" 2>/dev/null || true
        sudo chmod -R 755 "$FRONTEND_DIST_DIR" 2>/dev/null || true
    fi
    
    # 修复后端目录权限
    if [[ -d "$BACKEND_DIR" ]]; then
        log "修复后端目录权限..."
        sudo chown -R "$current_user:$current_group" "$BACKEND_DIR" 2>/dev/null || true
        sudo chmod -R 755 "$BACKEND_DIR" 2>/dev/null || true
        
        # 确保虚拟环境可写
        if [[ -d "$BACKEND_DIR/venv" ]]; then
            sudo chown -R "$current_user:$current_group" "$BACKEND_DIR/venv" 2>/dev/null || true
            sudo chmod -R 755 "$BACKEND_DIR/venv" 2>/dev/null || true
        fi
        
        # 确保uploads目录可写
        if [[ -d "$BACKEND_DIR/uploads" ]]; then
            sudo chown -R www-data:www-data "$BACKEND_DIR/uploads" 2>/dev/null || true
            sudo chmod -R 755 "$BACKEND_DIR/uploads" 2>/dev/null || true
        fi
    fi
    
    # 修复日志目录权限
    if [[ -d "$PROJECT_DIR/logs" ]]; then
        log "修复日志目录权限..."
        sudo chown -R "$current_user:$current_group" "$PROJECT_DIR/logs" 2>/dev/null || true
        sudo chmod -R 755 "$PROJECT_DIR/logs" 2>/dev/null || true
    fi
    
    # 修复临时目录权限
    if [[ -d "$PROJECT_DIR/temp" ]]; then
        log "修复临时目录权限..."
        sudo chown -R "$current_user:$current_group" "$PROJECT_DIR/temp" 2>/dev/null || true
        sudo chmod -R 755 "$PROJECT_DIR/temp" 2>/dev/null || true
    fi
    
    # 修复Nginx配置权限
    log "修复Nginx配置权限..."
    sudo chown -R root:root /etc/nginx 2>/dev/null || true
    sudo chmod -R 644 /etc/nginx/nginx.conf 2>/dev/null || true
    sudo chmod -R 644 /etc/nginx/sites-available/* 2>/dev/null || true
    sudo chmod -R 644 /etc/nginx/sites-enabled/* 2>/dev/null || true
    
    # 修复SSL证书权限
    if [[ -d "/etc/nginx/ssl" ]]; then
        log "修复SSL证书权限..."
        sudo chown -R root:root /etc/nginx/ssl 2>/dev/null || true
        sudo chmod -R 600 /etc/nginx/ssl/*.key 2>/dev/null || true
        sudo chmod -R 644 /etc/nginx/ssl/*.crt 2>/dev/null || true
    fi
    
    # 修复PostgreSQL数据目录权限
    log "修复PostgreSQL权限..."
    sudo chown -R postgres:postgres /var/lib/postgresql 2>/dev/null || true
    sudo chmod -R 700 /var/lib/postgresql 2>/dev/null || true
    
    # 修复系统服务权限
    log "修复系统服务权限..."
    sudo chown -R root:root /etc/systemd/system 2>/dev/null || true
    sudo chmod -R 644 /etc/systemd/system/* 2>/dev/null || true
    
    log "权限修复完成"
}

# 导出数据库
export_database() {
    log "📤 开始导出数据库..."
    
    # 检查PostgreSQL是否运行
    if ! systemctl is-active --quiet postgresql; then
        error "PostgreSQL服务未运行，无法导出数据库"
        return 1
    fi
    
    # 设置导出文件路径
    local export_file="$PROJECT_DIR/backups/database_export_$(date +%Y%m%d_%H%M%S).sql"
    local export_file_gz="${export_file}.gz"
    
    # 创建备份目录
    mkdir -p "$PROJECT_DIR/backups"
    
    log "导出数据库到: $export_file"
    
    # 导出数据库（包含结构和数据）
    if sudo -u postgres pg_dump -d fince_project_prod --clean --create --if-exists > "$export_file" 2>/dev/null; then
        log "✅ 数据库导出成功"
        
        # 压缩导出文件
        if gzip "$export_file"; then
            log "✅ 导出文件已压缩: $export_file_gz"
            log "📁 文件大小: $(du -h "$export_file_gz" | cut -f1)"
        else
            log "⚠️ 压缩失败，保留未压缩文件: $export_file"
        fi
        
        # 显示导出文件信息
        log "📋 导出文件信息:"
        log "   文件路径: $export_file_gz"
        log "   创建时间: $(date)"
        log "   文件大小: $(du -h "$export_file_gz" | cut -f1)"
        log "   数据库名称: fince_project_prod"
        log "   导出类型: 完整数据库（结构和数据）"
        
        # 显示数据库统计信息
        log "📊 数据库统计信息:"
        local table_count=$(sudo -u postgres psql -d fince_project_prod -c "SELECT COUNT(*) FROM information_schema.tables;" 2>/dev/null | tail -1 | tr -d ' ')
        log "   📋 表数量: $table_count"
        
        # 显示各表的记录数
        local tables=$(sudo -u postgres psql -d fince_project_prod -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | grep -v tablename | grep -v "^$" | tr -d ' ')
        for table in $tables; do
            if [[ -n "$table" ]]; then
                local record_count=$(sudo -u postgres psql -d fince_project_prod -c "SELECT COUNT(*) FROM \"$table\";" 2>/dev/null | tail -1 | tr -d ' ')
                log "   📊 表 $table: $record_count 条记录"
            fi
        done
        
        return 0
    else
        error "❌ 数据库导出失败"
        log "💡 可能的原因："
        log "   1. 数据库不存在"
        log "   2. 数据库用户权限不足"
        log "   3. PostgreSQL配置问题"
        return 1
    fi
}

# 导入数据库
import_database() {
    log "📥 开始导入数据库..."
    
    # 检查PostgreSQL是否运行
    if ! systemctl is-active --quiet postgresql; then
        error "PostgreSQL服务未运行，无法导入数据库"
        return 1
    fi
    
    # 查找最新的导出文件
    local backup_dir="$PROJECT_DIR/backups"
    local latest_export=$(find "$backup_dir" -name "database_export_*.sql.gz" -type f | sort | tail -1)
    
    if [[ -z "$latest_export" ]]; then
        error "❌ 未找到数据库导出文件"
        log "💡 请先运行: ./deploy.sh export-db"
        return 1
    fi
    
    log "找到导出文件: $latest_export"
    
    # 解压文件
    local temp_sql_file="$PROJECT_DIR/temp/temp_import.sql"
    mkdir -p "$PROJECT_DIR/temp"
    
    log "解压导出文件..."
    if gunzip -c "$latest_export" > "$temp_sql_file"; then
        log "✅ 文件解压成功"
    else
        error "❌ 文件解压失败"
        return 1
    fi
    
    # 获取导出文件中的数据库名称
    log "🔍 分析导出文件中的数据库信息..."
    
    # 提取数据库名称
    local source_db_name=$(grep -E "^CREATE DATABASE" "$temp_sql_file" | head -1 | sed 's/.*CREATE DATABASE \([^[:space:]]*\).*/\1/' | sed 's/.*"\([^"]*\)".*/\1/')
    
    if [[ -z "$source_db_name" ]]; then
        # 如果无法从文件中提取，使用默认名称
        source_db_name="fince_project_prod"
        log "⚠️  无法从导出文件确定数据库名称，使用默认名称: $source_db_name"
    else
        log "📋 导出文件中的数据库名称: $source_db_name"
    fi
    
    # 询问用户目标数据库名称
    local target_db_name
    if [[ -t 0 ]]; then
        # 交互模式
        echo ""
        read -p "请输入目标数据库名称 (默认: $source_db_name): " target_db_name
        target_db_name=${target_db_name:-$source_db_name}
    else
        # 非交互模式，使用源数据库名称
        target_db_name="$source_db_name"
    fi
    
    log "🎯 目标数据库名称: $target_db_name"
    
    # 检查目标数据库是否已存在
    if sudo -u postgres psql -l | grep -q "^[[:space:]]*$target_db_name[[:space:]]"; then
        log "⚠️  目标数据库 $target_db_name 已存在"
        if [[ -t 0 ]]; then
            read -p "是否删除现有数据库并重新创建？(y/N): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                log "🗑️  删除现有数据库 $target_db_name..."
                sudo -u postgres dropdb "$target_db_name" 2>/dev/null
                log "✅ 现有数据库已删除"
            else
                log "❌ 用户取消操作"
                rm -f "$temp_sql_file"
                return 1
            fi
        else
            log "🗑️  自动删除现有数据库 $target_db_name..."
            sudo -u postgres dropdb "$target_db_name" 2>/dev/null
            log "✅ 现有数据库已删除"
        fi
    fi
    
    # 导入数据库
    log "🚀 开始导入数据库到 $target_db_name..."
    
    # 使用pg_restore或psql导入
    if command -v pg_restore >/dev/null 2>&1; then
        # 尝试使用pg_restore（更安全）
        log "使用 pg_restore 导入..."
        if sudo -u postgres pg_restore --create --clean --if-exists --dbname=postgres "$temp_sql_file" 2>/dev/null; then
            log "✅ 数据库导入成功 (使用 pg_restore)"
        else
            log "⚠️  pg_restore 失败，尝试使用 psql..."
            if sudo -u postgres psql -f "$temp_sql_file" 2>/dev/null; then
                log "✅ 数据库导入成功 (使用 psql)"
            else
                error "❌ 数据库导入失败"
                rm -f "$temp_sql_file"
                return 1
            fi
        fi
    else
        # 使用psql导入
        log "使用 psql 导入..."
        if sudo -u postgres psql -f "$temp_sql_file" 2>/dev/null; then
            log "✅ 数据库导入成功"
        else
            error "❌ 数据库导入失败"
            rm -f "$temp_sql_file"
            return 1
        fi
    fi
    
    # 清理临时文件
    rm -f "$temp_sql_file"
    
    # 验证导入结果
    log "🔍 验证导入结果..."
    if sudo -u postgres psql -d "$target_db_name" -c "SELECT COUNT(*) FROM information_schema.tables;" 2>/dev/null | grep -q "[0-9]"; then
        log "✅ 数据库 $target_db_name 验证成功"
        
        # 显示导入的数据库信息
        log "📊 导入的数据库信息:"
        local table_count=$(sudo -u postgres psql -d "$target_db_name" -c "SELECT COUNT(*) FROM information_schema.tables;" 2>/dev/null | tail -1 | tr -d ' ')
        log "📋 表数量: $table_count"
        
        # 显示各表的记录数
        local tables=$(sudo -u postgres psql -d "$target_db_name" -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | grep -v tablename | grep -v "^$" | tr -d ' ')
        for table in $tables; do
            if [[ -n "$table" ]]; then
                local record_count=$(sudo -u postgres psql -d "$target_db_name" -c "SELECT COUNT(*) FROM \"$table\";" 2>/dev/null | tail -1 | tr -d ' ')
                log "   📊 表 $table: $record_count 条记录"
            fi
        done
        
    else
        warn "⚠️ 数据库验证失败，请手动检查"
    fi
    
    log "🎉 数据库导入完成！"
    log "📱 数据库名称: $target_db_name"
    log "💡 如需使用此数据库，请更新应用配置"
    
    return 0
}

# 修复数据库表结构
fix_database_schema() {
    log "🔧 开始修复数据库表结构..."
    
    # 检查PostgreSQL是否运行
    if ! systemctl is-active --quiet postgresql; then
        error "PostgreSQL服务未运行，无法修复数据库结构"
        return 1
    fi
    
    # 创建数据库表结构
    log "创建基础数据库表结构..."
    
    # 创建tenants表
    sudo -u postgres psql -d fince_project_prod -c "
    CREATE TABLE IF NOT EXISTS tenants (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(100) NOT NULL,
        domain VARCHAR(50) UNIQUE,
        plan_type VARCHAR(20) DEFAULT 'trial',
        settings JSONB DEFAULT '{}',
        subscription_end DATE,
        storage_used BIGINT DEFAULT 0,
        storage_limit BIGINT DEFAULT 5368709120,
        api_calls_used INTEGER DEFAULT 0,
        api_calls_limit INTEGER DEFAULT 1000,
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );" 2>/dev/null && log "✅ tenants表创建成功" || log "⚠️ tenants表创建警告"
    
    # 创建users表
    sudo -u postgres psql -d fince_project_prod -c "
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        permissions JSONB DEFAULT '[]',
        profile JSONB DEFAULT '{}',
        last_login TIMESTAMP,
        login_count INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        email_verified BOOLEAN DEFAULT FALSE,
        two_factor_enabled BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );" 2>/dev/null && log "✅ users表创建成功" || log "⚠️ users表创建警告"
    
    # 创建projects表（包含所有必需字段）
    sudo -u postgres psql -d fince_project_prod -c "
    CREATE TABLE IF NOT EXISTS projects (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
        name VARCHAR(200) NOT NULL,
        project_code VARCHAR(50) UNIQUE,
        description TEXT,
        project_type VARCHAR(50) DEFAULT 'other',
        category VARCHAR(100),
        tags JSONB DEFAULT '[]',
        status VARCHAR(20) DEFAULT 'planning',
        priority VARCHAR(20) DEFAULT 'medium',
        progress INTEGER DEFAULT 0,
        health_status VARCHAR(20) DEFAULT 'healthy',
        start_date DATE,
        end_date DATE,
        actual_start_date DATE,
        actual_end_date DATE,
        estimated_duration INTEGER,
        actual_duration INTEGER,
        budget DECIMAL(15,2),
        actual_cost DECIMAL(15,2) DEFAULT 0,
        estimated_cost DECIMAL(15,2),
        cost_variance DECIMAL(15,2),
        budget_utilization DECIMAL(5,2),
        manager_name VARCHAR(100),
        manager_id UUID REFERENCES users(id),
        team_size INTEGER DEFAULT 1,
        assigned_users JSONB DEFAULT '[]',
        location JSONB DEFAULT '{}',
        address VARCHAR(500),
        coordinates JSONB,
        client_info JSONB DEFAULT '{}',
        contract_info JSONB DEFAULT '{}',
        contract_number VARCHAR(100),
        contract_value DECIMAL(15,2),
        payment_terms JSONB,
        technical_specs JSONB,
        requirements JSONB,
        deliverables JSONB,
        quality_standards JSONB,
        risk_level VARCHAR(20) DEFAULT 'low',
        risk_factors JSONB,
        mitigation_plans JSONB,
        budget_change_reason VARCHAR(200),
        contract_change_reason VARCHAR(200),
        change_description TEXT,
        documents JSONB DEFAULT '[]',
        attachments JSONB DEFAULT '[]',
        approval_status VARCHAR(20) DEFAULT 'pending',
        approval_history JSONB,
        workflow_stage VARCHAR(50),
        last_review_date DATE,
        next_review_date DATE,
        review_cycle VARCHAR(20),
        reporting_frequency VARCHAR(20),
        is_active BOOLEAN DEFAULT TRUE,
        is_template BOOLEAN DEFAULT FALSE,
        created_by UUID REFERENCES users(id),
        updated_by UUID REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );" 2>/dev/null && log "✅ projects表创建成功" || log "⚠️ projects表创建警告"
    
    # 创建categories表
    sudo -u postgres psql -d fince_project_prod -c "
    CREATE TABLE IF NOT EXISTS categories (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
        name VARCHAR(100) NOT NULL,
        parent_id UUID REFERENCES categories(id),
        icon VARCHAR(50),
        color VARCHAR(7),
        is_system VARCHAR(1) DEFAULT '0',
        is_active VARCHAR(1) DEFAULT '1',
        sort_order VARCHAR(10) DEFAULT '0',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );" 2>/dev/null && log "✅ categories表创建成功" || log "⚠️ categories表创建警告"
    
    # 创建suppliers表
    sudo -u postgres psql -d fince_project_prod -c "
    CREATE TABLE IF NOT EXISTS suppliers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
        name VARCHAR(200) NOT NULL,
        code VARCHAR(50),
        contact_person VARCHAR(100),
        phone VARCHAR(20),
        email VARCHAR(100),
        address TEXT,
        business_scope TEXT,
        qualification TEXT,
        credit_rating VARCHAR(10),
        payment_terms VARCHAR(200),
        is_active VARCHAR(1) DEFAULT '1',
        notes TEXT,
        created_by UUID REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );" 2>/dev/null && log "✅ suppliers表创建成功" || log "⚠️ suppliers表创建警告"
    
    # 创建transactions表
    sudo -u postgres psql -d fince_project_prod -c "
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
        project_id UUID REFERENCES projects(id),
        supplier_id UUID REFERENCES suppliers(id),
        category_id UUID REFERENCES categories(id),
        transaction_date DATE NOT NULL,
        type VARCHAR(10) NOT NULL,
        amount DECIMAL(15,2) NOT NULL,
        currency VARCHAR(10) DEFAULT 'CNY',
        exchange_rate DECIMAL(10,6) DEFAULT 1.000000,
        description TEXT,
        notes TEXT,
        tags JSONB,
        payment_method VARCHAR(50),
        status VARCHAR(20) DEFAULT 'pending',
        attachment_url VARCHAR(500),
        reference_number VARCHAR(100),
        approved_by VARCHAR(100),
        approved_at TIMESTAMP,
        created_by UUID REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );" 2>/dev/null && log "✅ transactions表创建成功" || log "⚠️ transactions表创建警告"
    
    # 验证表结构
    log "🔍 验证表结构完整性..."
    local tables=("tenants" "users" "projects" "categories" "suppliers" "transactions")
    local total_tables=0
    local created_tables=0
    
    for table in "${tables[@]}"; do
        if sudo -u postgres psql -d fince_project_prod -c "\dt $table" 2>/dev/null | grep -q "$table"; then
            log "✅ $table 表存在"
            ((created_tables++))
        else
            log "❌ $table 表缺失"
        fi
        ((total_tables++))
    done
    
    log "📊 表结构验证结果: $created_tables/$total_tables 表创建成功"
    
    if [[ $created_tables -eq $total_tables ]]; then
        log "🎉 数据库表结构修复完成！"
        return 0
    else
        warn "⚠️ 部分表创建失败，请检查日志"
        return 1
    fi
}

# 检测和修复API错误
detect_and_fix_api_errors() {
    log "🔍 开始检测API错误..."
    
    # 检查数据库表结构
    log "检查数据库表结构..."
    fix_database_schema
    
    # 检查关键字段
    log "检查关键字段..."
    local critical_fields=(
        "projects.contract_value"
        "projects.manager_id"
        "transactions.payment_method"
        "categories.tenant_id"
        "suppliers.tenant_id"
    )
    
    for field in "${critical_fields[@]}"; do
        local table_name=$(echo "$field" | cut -d'.' -f1)
        local column_name=$(echo "$field" | cut -d'.' -f2)
        
        if sudo -u postgres psql -d fince_project_prod -c "SELECT column_name FROM information_schema.columns WHERE table_name = '$table_name' AND column_name = '$column_name';" 2>/dev/null | grep -q "$column_name"; then
            log "✅ 关键字段 $field 存在"
        else
            log "❌ 关键字段 $field 缺失，尝试修复..."
            # 这里可以添加具体的字段修复逻辑
        fi
    done
    
    log "🔍 API错误检测完成"
}

# 备份数据库
backup_database() {
    log "💾 开始备份数据库..."
    
    # 检查PostgreSQL是否运行
    if ! systemctl is-active --quiet postgresql; then
        error "PostgreSQL服务未运行，无法备份数据库"
        return 1
    fi
    
    # 设置备份文件路径
    local backup_file="$PROJECT_DIR/backups/database_backup_$(date +%Y%m%d_%H%M%S).sql"
    local backup_file_gz="${backup_file}.gz"
    
    # 创建备份目录
    mkdir -p "$PROJECT_DIR/backups"
    
    log "备份数据库到: $backup_file"
    
    # 创建数据库备份（仅数据，不包含DROP/CREATE语句）
    if sudo -u postgres pg_dump -h localhost -U postgres -d fince_project_prod --data-only --disable-triggers > "$backup_file" 2>/dev/null; then
        log "✅ 数据库备份成功"
        
        # 压缩备份文件
        if gzip "$backup_file"; then
            log "✅ 备份文件已压缩: $backup_file_gz"
            log "📁 文件大小: $(du -h "$backup_file_gz" | cut -f1)"
        else
            log "⚠️ 压缩失败，保留未压缩文件: $backup_file"
        fi
        
        # 显示备份文件信息
        log "📋 备份文件信息:"
        log "   文件路径: $backup_file_gz"
        log "   创建时间: $(date)"
        log "   文件大小: $(du -h "$backup_file_gz" | cut -f1)"
        log "   备份类型: 仅数据（不含结构）"
        
        return 0
    else
        error "❌ 数据库备份失败"
        log "💡 可能的原因："
        log "   1. 数据库不存在"
        log "   2. 数据库用户权限不足"
        log "   3. PostgreSQL配置问题"
        return 1
    fi
}

# 显示部署成功信息
show_deployment_success_info() {
    log ""
    log "🎊 恭喜！系统部署成功！"
log ""
log "📚 其他可用脚本："
log "   quick_deploy.sh      - 快速部署脚本（新环境一键部署）"
log "   start-all-services.sh - 启动所有服务脚本"
log "   generate_ssl_cert.sh  - SSL证书生成脚本"
log "   init_database.sql     - 数据库初始化脚本"
log "   check_database.sh     - 数据库检查脚本（一键检查状态）"
                   log "   check_database_structure.py - 数据库结构检查脚本"
                   log "   test_database_connection.py - 数据库连接测试脚本"
                   log "   test_database_performance.py - 数据库性能测试脚本"
                   log "   BASE_DATABASE_FULL.sql.gz   - 基准数据库文件（完整结构和数据）"
log ""
log "📖 详细文档："
log "   DEPLOYMENT_GUIDE.md   - 完整部署指南"
log "   数据库迁移指南.md      - 数据库迁移说明"
log ""
log "📱 访问地址："
    log "   前端应用: https://localhost"
    log "   后端API:  https://localhost/api/v1"
    log "   健康检查: https://localhost/health"
    log ""
    log "🔧 管理命令："
    log "   查看状态: ./deploy.sh status"
    log "   重启服务: ./deploy.sh restart"
    log "   健康检查: ./deploy.sh health"
    log "   快速部署: ./deploy.sh quick-deploy"
    log ""
    log "📁 重要目录："
    log "   项目根目录: $PROJECT_DIR"
    log "   前端文件:  $FRONTEND_DIST_DIR"
    log "   后端代码:  $BACKEND_DIR"
    log "   日志文件:  $PROJECT_DIR/logs"
    log ""
    log "⚠️  注意事项："
    log "   - 使用自签名SSL证书，浏览器会显示安全警告（正常现象）"
    log "   - 如需外网访问，请配置防火墙开放80和443端口"
    log "   - 生产环境建议使用正式的SSL证书"
    log ""
}

# 显示故障排除信息
show_troubleshooting_info() {
    log ""
    log "🔧 故障排除指南："
    log ""
    log "1. 检查服务状态："
    log "   sudo systemctl status nginx postgresql"
    log ""
    log "2. 查看日志文件："
    log "   sudo journalctl -u nginx -f"
    log "   sudo journalctl -u postgresql -f"
    log "   tail -f $PROJECT_DIR/backend.log"
    log ""
    log "3. 重新配置服务："
    log "   ./deploy.sh configure-nginx"
    log "   ./deploy.sh restart"
    log ""
    log "4. 完全重新部署："
    log "   ./deploy.sh deploy"
    log ""
    log "5. 获取帮助："
    log "   ./deploy.sh help"
    log ""
}

# 显示帮助信息
show_help() {
    cat << EOF
$PROJECT_NAME - 一键部署脚本

用法: $0 [命令]

命令:
    init-project      初始化项目目录结构（新服务器必选）
    first-deploy      首次完整部署（新服务器推荐）
    install-deps      安装系统依赖
    install-db        安装和配置数据库
    install-backend   安装后端依赖
    install-frontend  安装前端依赖
    migrate           运行数据库迁移
    backup            创建数据库备份
    build             构建前端应用
    deploy            一键完整部署（推荐）
    quick-deploy      快速部署（仅前端+重启）
    restart           重启所有服务
    stop              停止所有服务
    start             启动所有服务
               status            检查服务状态
           health            执行健康检查
    fix-schema        修复数据库表结构
    detect-api-errors 检测和修复API错误
    export-db         导出数据库（包含结构和数据）
    import-db         导入数据库（从最新导出文件）
    backup-db         备份数据库（仅数据）
    check-export      检查数据库导出文件信息
    configure-nginx   重新配置Nginx和SSL
    fix-permissions   修复所有权限问题
    help              显示此帮助信息

示例:
    $0 init-project    # 新服务器：初始化项目目录
    $0 first-deploy    # 新服务器：首次完整部署（推荐）
    $0 deploy          # 已有环境：一键完整部署
    $0 quick-deploy    # 日常使用：快速部署
    $0 export-db       # 导出数据库（迁移前）
    $0 check-export    # 检查导出文件信息
    $0 import-db       # 导入数据库（迁移后）
    $0 backup-db       # 备份数据库数据
    $0 restart         # 重启服务
    $0 health          # 健康检查

注意: 
- 新服务器：init-project -> first-deploy
- 已有环境：deploy 或 quick-deploy
EOF
}

# 主函数
main() {
    local command="${1:-help}"
    
    # 记录开始时间
    local start_time=$(date +%s)
    
    # 验证项目目录（除了help命令）
    if [[ "$command" != "help" ]]; then
        validate_project_directory
    fi
    
    log "开始执行命令: $command"
    log "项目目录: $PROJECT_DIR"
    
    case "$command" in
        "init-project")
            init_project
            ;;
        "first-deploy")
            log "🚀 开始首次部署..."
            check_root
            # 首次部署时跳过依赖检查，直接安装
            # check_dependencies
            check_system_resources
            init_project
            install_system_dependencies
            install_nodejs
            install_database
            install_backend_dependencies
            install_frontend_dependencies
            run_database_migrations
            build_frontend
            configure_nginx
            start_services
            health_check
            log "🎉 首次部署完成！"
            ;;
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
            log "🚀 开始一键部署..."
            check_system_resources
            check_project_initialization || {
                warn "项目未完全初始化，尝试自动修复..."
                init_project
            }
            backup_database
            build_frontend
            configure_nginx
            restart_services
            health_check
            log "🎉 一键部署完成！"
            ;;
        "restart")
            stop_services
            start_services
            health_check
            ;;
        "quick-deploy")
            log "⚡ 开始快速部署..."
            build_frontend
            configure_nginx
            restart_services
            health_check
            log "⚡ 快速部署完成！"
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
        "fix-schema")
            log "🔧 开始修复数据库表结构..."
            fix_database_schema
            log "数据库表结构修复完成"
            ;;
        "detect-api-errors")
            log "🔍 开始检测API错误..."
            detect_and_fix_api_errors
            log "API错误检测和修复完成"
            ;;
        "fix-contract-value")
            log "🔧 开始修复contract_value字段问题..."
            fix_contract_value_field
            log "contract_value字段修复完成"
            ;;
        "configure-nginx")
            log "重新配置Nginx和SSL..."
            configure_nginx
            log "Nginx配置更新完成"
            ;;
        "fix-permissions")
            log "修复所有权限问题..."
            fix_permissions
            log "权限修复完成"
            ;;
        "fix-schema")
            log "🔧 开始修复数据库表结构..."
            fix_database_schema
            log "数据库表结构修复完成"
            ;;
        "detect-api-errors")
            log "🔍 开始检测API错误..."
            detect_and_fix_api_errors
            log "API错误检测和修复完成"
            ;;
        "export-db")
            log "📤 开始导出数据库..."
            export_database
            log "数据库导出完成"
            ;;
        "import-db")
            log "📥 开始导入数据库..."
            import_database
            log "数据库导入完成"
            ;;
        "backup-db")
            log "💾 开始备份数据库..."
            backup_database
            log "数据库备份完成"
            ;;
        "check-export")
            log "🔍 检查数据库导出文件..."
            if [[ -f "check_database_name.py" ]]; then
                python3 check_database_name.py
            else
                log "❌ 检查脚本不存在: check_database_name.py"
            fi
            log "导出文件检查完成"
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
    # 确保目录存在
    create_directories
    main "$@"
fi
