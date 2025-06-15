#!/bin/bash

# 索克生活 - 全量备份脚本

BACKUP_DIR="/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "🗄️ 开始数据备份..."

# 备份数据库
echo "备份PostgreSQL数据库..."
pg_dump -h localhost -U postgres suoke_life > $BACKUP_DIR/database.sql

# 备份Redis数据
echo "备份Redis数据..."
redis-cli --rdb $BACKUP_DIR/redis.rdb

# 备份配置文件
echo "备份配置文件..."
tar -czf $BACKUP_DIR/configs.tar.gz config/

# 备份日志文件
echo "备份日志文件..."
tar -czf $BACKUP_DIR/logs.tar.gz logs/

echo "✅ 备份完成: $BACKUP_DIR"
