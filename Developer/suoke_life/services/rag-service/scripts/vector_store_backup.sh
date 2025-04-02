#!/bin/bash
#
# 向量存储跨区域备份脚本
# 将本地向量存储备份到OSS，实现跨可用区备份
#

set -e

# 配置
DATA_DIR="/app/data/vector_store"
BACKUP_DIR="/app/data/backups"
OSS_BUCKET="suoke-rag-backups"
OSS_PATH="vector_store"
RETENTION_DAYS=30
FULL_BACKUP_DAY="7"  # 星期日做全量备份
REGIONS=("cn-beijing" "cn-shanghai")  # 多区域备份
ALERT_EMAIL="admin@suoke.life"

# 日志函数
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/www/suoke.life/logs/vector_backup.log
}

# 发送警报
send_alert() {
  local subject="$1"
  local message="$2"
  
  echo "$message" | mail -s "[向量存储] $subject" $ALERT_EMAIL
  log "已发送警报: $subject"
}

# 确保目录存在
mkdir -p $BACKUP_DIR

# 备份文件名（使用日期）
DATESTAMP=$(date +%Y%m%d-%H%M%S)
DAY_OF_WEEK=$(date +%u)
BACKUP_TYPE="incremental"

# 星期日做全量备份
if [ "$DAY_OF_WEEK" = "$FULL_BACKUP_DAY" ]; then
  BACKUP_TYPE="full"
fi

BACKUP_FILE="${BACKUP_TYPE}-${DATESTAMP}.tar.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

# 执行备份
log "开始 $BACKUP_TYPE 备份..."

if [ "$BACKUP_TYPE" = "full" ]; then
  # 全量备份
  log "执行全量备份..."
  tar -czf $BACKUP_PATH -C $(dirname $DATA_DIR) $(basename $DATA_DIR)
else
  # 增量备份 - 只备份24小时内修改的文件
  log "执行增量备份..."
  find $DATA_DIR -type f -mtime -1 -print0 | tar -czf $BACKUP_PATH --null -T -
fi

# 检查备份文件大小
BACKUP_SIZE=$(du -h $BACKUP_PATH | cut -f1)
log "备份文件大小: $BACKUP_SIZE"

# 验证备份
log "验证备份文件完整性..."
if tar -tzf $BACKUP_PATH >/dev/null 2>&1; then
  log "备份文件验证成功"
else
  log "错误: 备份文件验证失败"
  send_alert "备份验证失败" "向量存储备份验证失败，请检查: $BACKUP_PATH"
  exit 1
fi

# 多区域备份 - 使用阿里云OSS
log "开始跨区域备份..."

for region in "${REGIONS[@]}"; do
  log "备份到区域: $region"
  OSS_ENDPOINT="oss-${region}.aliyuncs.com"
  OSS_DEST="oss://${OSS_BUCKET}-${region}/${OSS_PATH}/${BACKUP_FILE}"
  
  # 上传到OSS
  if ! ossutil cp $BACKUP_PATH $OSS_DEST --endpoint $OSS_ENDPOINT; then
    log "错误: 无法备份到区域 $region"
    send_alert "OSS备份失败" "向量存储备份到区域 $region 失败"
  else
    log "成功备份到区域: $region"
  fi
done

# 检查和维护本地备份保留策略
log "清理过期备份..."
find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

# 检查所有区域是否都有最新备份
for region in "${REGIONS[@]}"; do
  OSS_ENDPOINT="oss-${region}.aliyuncs.com"
  
  if ! ossutil ls "oss://${OSS_BUCKET}-${region}/${OSS_PATH}/" --endpoint $OSS_ENDPOINT | grep -q "${BACKUP_FILE}"; then
    log "警告: 区域 $region 可能没有最新备份"
    send_alert "备份不完整" "区域 $region 可能没有最新的向量存储备份"
  fi
done

# 生成备份报告
TOTAL_BACKUPS=$(find $BACKUP_DIR -name "*.tar.gz" | wc -l)
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)

log "备份报告:"
log "- 备份类型: $BACKUP_TYPE"
log "- 备份文件: $BACKUP_FILE"
log "- 文件大小: $BACKUP_SIZE"
log "- 本地备份总数: $TOTAL_BACKUPS"
log "- 本地备份总大小: $TOTAL_SIZE"
log "- 备份区域: ${REGIONS[*]}"

log "备份完成" 