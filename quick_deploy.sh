#!/bin/bash

# 工程项目流水账系统 - 快速部署脚本
# 版本: 1.0.1
# 用于日常快速部署

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目配置
PROJECT_DIR="/home/dev/工程项目流水账"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend-new"
FRONTEND_DIST_DIR="$PROJECT_DIR/frontend/dist"
BACKEND_PORT="8000"

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] 错误: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] 警告: $1${NC}"
}

# 快速部署函数
quick_deploy() {
    log "🚀 开始快速部署..."
    
    # 1. 备份数据库
    log "📦 创建数据库备份..."
    ./deploy.sh backup
    
    # 2. 构建前端
    log "🏗️  构建前端应用..."
    ./deploy.sh build
    
    # 3. 重启服务
    log "🔄 重启所有服务..."
    ./deploy.sh restart
    
    # 4. 健康检查
    log "🏥 执行健康检查..."
    ./deploy.sh health
    
    log "✅ 快速部署完成！"
}

# 仅构建前端
build_only() {
    log "🏗️  仅构建前端..."
    ./deploy.sh build
    log "✅ 前端构建完成！"
}

# 仅重启服务
restart_only() {
    log "🔄 仅重启服务..."
    ./deploy.sh restart
    log "✅ 服务重启完成！"
}

# 显示帮助
show_help() {
    cat << EOF
工程项目流水账系统 - 快速部署脚本

用法: $0 [选项]

选项:
    deploy      完整快速部署（推荐）
    build       仅构建前端
    restart     仅重启服务
    help        显示此帮助信息

示例:
    $0 deploy    # 完整快速部署
    $0 build     # 仅构建前端
    $0 restart   # 仅重启服务

注意: 此脚本是deploy.sh的简化版本，用于日常快速部署
EOF
}

# 主函数
main() {
    local option="${1:-deploy}"
    
    case "$option" in
        "deploy")
            quick_deploy
            ;;
        "build")
            build_only
            ;;
        "restart")
            restart_only
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
