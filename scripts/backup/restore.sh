#!/bin/bash
# 索克生活数据恢复脚本

set -e

if [ $# -eq 0 ]; then
    echo "用法: $0 <backup_date>"
    echo "示例: $0 20231201_120000"
    exit 1
fi

BACKUP_DATE=$1
BACKUP_DIR="/backups"
DB_NAME="suokelife_prod"

# 恢复数据库
echo "恢复数据库..."
gunzip -c $BACKUP_DIR/db_backup_$BACKUP_DATE.sql.gz | psql $DB_NAME

# 恢复文件
echo "恢复文件..."
tar -xzf $BACKUP_DIR/files_backup_$BACKUP_DATE.tar.gz -C /

echo "恢复完成: $BACKUP_DATE"
