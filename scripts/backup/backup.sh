#!/bin/bash
# 索克生活数据备份脚本

set -e

# 配置
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="suokelife_prod"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 数据库备份
echo "开始数据库备份..."
pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 文件备份
echo "开始文件备份..."
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /app/uploads

# 清理旧备份
echo "清理旧备份..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "备份完成: $DATE"
