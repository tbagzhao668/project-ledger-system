#!/bin/bash

# 🗄️ 数据库备份脚本
# 备份时间: 2025-08-28

# 配置
DB_NAME="project_ledger"
DB_USER="postgres"
DB_PASSWORD="123456"
BACKUP_DIR="./database_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/project_ledger_${TIMESTAMP}.sql"

echo "🗄️ 开始数据库备份..."

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

# 执行备份
echo "📦 备份数据库: ${DB_NAME}"
PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h localhost \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --clean \
    --if-exists \
    --create \
    --verbose \
    --file="${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "✅ 数据库备份成功！"
    echo "📁 备份文件: ${BACKUP_FILE}"
    
    # 显示备份文件信息
    echo "📊 备份文件大小:"
    ls -lh "${BACKUP_FILE}"
    
    # 创建备份信息文件
    INFO_FILE="${BACKUP_DIR}/backup_info_${TIMESTAMP}.txt"
    cat > "${INFO_FILE}" << EOF
数据库备份信息
================
备份时间: $(date)
数据库名: ${DB_NAME}
备份文件: ${BACKUP_FILE}
系统状态: 完全修复状态
Git提交: 9ac38d4
备份说明: 系统完全修复后的数据库状态

恢复命令:
pg_restore -h localhost -U postgres -d project_ledger ${BACKUP_FILE}

或者使用SQL文件:
psql -h localhost -U postgres -d project_ledger -f ${BACKUP_FILE}
EOF
    
    echo "📝 备份信息已保存到: ${INFO_FILE}"
    
else
    echo "❌ 数据库备份失败！"
    exit 1
fi

echo -e "\n🎯 备份完成！"
echo "📁 备份目录: ${BACKUP_DIR}"
echo "🔑 恢复命令: 查看备份信息文件"
