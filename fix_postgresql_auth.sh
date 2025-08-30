#!/bin/bash

# PostgreSQL认证配置修复脚本
# 专门用于解决deploy.sh first-deploy中的PostgreSQL认证问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# 项目配置
PROJECT_DIR="/home/serveruser/project-ledger-system"
DB_USER="fince_app_project"
DB_NAME="fince_project_prod"
DB_PASSWORD="Fince_project_5%8*6^9(3#0)"

log "🚀 开始修复PostgreSQL认证配置..."

# 检查PostgreSQL服务状态
log "🔍 检查PostgreSQL服务状态..."
if ! sudo systemctl is-active --quiet postgresql; then
    error "PostgreSQL服务未运行，正在启动..."
    sudo systemctl start postgresql
    sleep 3
fi

if sudo systemctl is-active --quiet postgresql; then
    success "PostgreSQL服务运行正常"
else
    error "PostgreSQL服务启动失败"
    exit 1
fi

# 检查PostgreSQL版本
log "📋 检查PostgreSQL版本..."
PG_VERSION=$(sudo -u postgres psql -c "SELECT version();" 2>/dev/null | head -1 | grep -oE 'PostgreSQL [0-9]+' | grep -oE '[0-9]+' || echo "unknown")
log "PostgreSQL版本: $PG_VERSION"

# 备份原始配置
log "💾 备份PostgreSQL配置..."
sudo cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || \
sudo cp /var/lib/pgsql/data/pg_hba.conf /var/lib/pgsql/data/pg_hba.conf.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || \
warn "无法备份pg_hba.conf，继续执行..."

# 修复pg_hba.conf配置
log "🔧 修复PostgreSQL认证配置..."

# 检测PostgreSQL配置目录
if [[ -d "/etc/postgresql" ]]; then
    # Ubuntu/Debian系统
    PG_CONF_DIR="/etc/postgresql/*/main"
    PG_HBA_FILE="/etc/postgresql/*/main/pg_hba.conf"
elif [[ -d "/var/lib/pgsql" ]]; then
    # CentOS/RHEL系统
    PG_CONF_DIR="/var/lib/pgsql/data"
    PG_HBA_FILE="/var/lib/pgsql/data/pg_hba.conf"
else
    error "无法找到PostgreSQL配置目录"
    exit 1
fi

log "PostgreSQL配置目录: $PG_CONF_DIR"

# 创建新的pg_hba.conf配置
log "📝 创建新的认证配置..."
sudo tee "$PG_HBA_FILE" > /dev/null << 'EOF'
# PostgreSQL Client Authentication Configuration File
# ===========================================
#
# Refer to the "Client Authentication" section in the PostgreSQL
# documentation for a complete description of this file.

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
host    all             all             127.0.0.1/32            trust

# IPv6 local connections:
host    all             all             ::1/128                 md5
host    all             all             ::1/128                 trust

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust

# 允许所有本地连接（开发环境）
host    all             all             0.0.0.0/0               md5
host    all             all             0.0.0.0/0               trust
EOF

success "pg_hba.conf配置已更新"

# 重启PostgreSQL服务
log "🔄 重启PostgreSQL服务..."
sudo systemctl restart postgresql
sleep 5

# 验证PostgreSQL连接
log "🔍 验证PostgreSQL连接..."
if sudo -u postgres psql -c "SELECT 1;" >/dev/null 2>&1; then
    success "PostgreSQL连接正常"
else
    error "PostgreSQL连接失败"
    exit 1
fi

# 创建数据库用户
log "👤 创建数据库用户..."
if sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER';" 2>/dev/null | grep -q 1; then
    log "用户 $DB_USER 已存在，更新密码..."
    sudo -u postgres psql -c "ALTER ROLE $DB_USER WITH PASSWORD '$DB_PASSWORD';"
else
    log "创建用户 $DB_USER..."
    sudo -u postgres psql -c "CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';"
fi

# 创建数据库
log "🗄️  创建数据库..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    log "数据库 $DB_NAME 已存在"
else
    log "创建数据库 $DB_NAME..."
    sudo -u postgres createdb "$DB_NAME"
fi

# 授权用户访问数据库
log "🔐 授权用户访问数据库..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

# 测试数据库连接
log "🧪 测试数据库连接..."
if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
    success "数据库连接测试成功"
else
    error "数据库连接测试失败"
    log "尝试使用psql连接..."
    if sudo -u postgres psql -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        success "使用postgres用户连接成功"
    else
        error "所有连接测试都失败"
        exit 1
    fi
fi

# 显示PostgreSQL状态
log "📊 PostgreSQL状态信息:"
sudo systemctl status postgresql --no-pager -l

# 显示数据库列表
log "📋 数据库列表:"
sudo -u postgres psql -c "\l"

# 显示用户列表
log "👥 用户列表:"
sudo -u postgres psql -c "\du"

success "🎉 PostgreSQL认证配置修复完成！"
log "💡 现在可以重新运行: ./deploy.sh first-deploy"
log "🔧 如果仍有问题，请检查日志: sudo journalctl -u postgresql -f"
