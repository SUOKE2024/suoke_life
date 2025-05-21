#!/bin/bash
# 数据库备份定时任务脚本
# 用于cron计划任务，定期执行备份

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${SCRIPT_DIR}/../backup.py"
LOG_FILE="/var/log/suoke/auth-service/backup-cron.log"

# 配置参数
BACKUP_DIR="/var/backups/auth-service"
RETENTION_DAYS=30
DB_HOST="postgres-service"
DB_PORT="5432" 
DB_NAME="auth_db"
DB_USER="postgres"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 判断今天是否是星期天（每周完整备份）
if [ "$(date +%u)" -eq 7 ]; then
  log "执行完整备份..."
  python3 "$BACKUP_SCRIPT" --full \
    --backup-dir "$BACKUP_DIR" \
    --retention-days "$RETENTION_DAYS" \
    --db-host "$DB_HOST" \
    --db-port "$DB_PORT" \
    --db-name "$DB_NAME" \
    --db-user "$DB_USER" >> "$LOG_FILE" 2>&1
else
  # 其他日子执行增量备份
  log "执行增量备份..."
  python3 "$BACKUP_SCRIPT" --incremental \
    --backup-dir "$BACKUP_DIR" \
    --retention-days "$RETENTION_DAYS" \
    --db-host "$DB_HOST" \
    --db-port "$DB_PORT" \
    --db-name "$DB_NAME" \
    --db-user "$DB_USER" >> "$LOG_FILE" 2>&1
fi

# 定期清理旧备份
if [ "$(date +%d)" -eq 1 ]; then
  # 每月1号执行清理
  log "清理旧备份..."
  python3 "$BACKUP_SCRIPT" --cleanup \
    --backup-dir "$BACKUP_DIR" \
    --retention-days "$RETENTION_DAYS" >> "$LOG_FILE" 2>&1
fi

exit 0