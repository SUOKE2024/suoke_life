# PostgreSQL 迁移指南

## 概述

本指南详细说明如何将索克生活健康数据服务从SQLite迁移到PostgreSQL数据库。PostgreSQL提供了更好的性能、并发性和扩展性，适合生产环境使用。

## 迁移前准备

### 1. 系统要求

- **操作系统**: Linux (Ubuntu/CentOS) 或 macOS
- **PostgreSQL版本**: 12.0 或更高版本
- **Python版本**: 3.8 或更高版本
- **内存**: 建议至少 4GB RAM
- **存储**: 确保有足够空间存储数据

### 2. 备份现有数据

在开始迁移前，请务必备份现有的SQLite数据库：

```bash
# 备份SQLite数据库
cp data/health_data.db data/health_data_backup_$(date +%Y%m%d_%H%M%S).db

# 导出数据（可选）
sqlite3 data/health_data.db .dump > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 安装和配置PostgreSQL

### 方法一：使用自动安装脚本（推荐）

我们提供了一个自动安装和配置脚本：

```bash
# 进入健康数据服务目录
cd services/health-data-service

# 运行安装脚本
chmod +x scripts/setup_postgresql.sh
./scripts/setup_postgresql.sh

# 自定义数据库配置
./scripts/setup_postgresql.sh \
  --db-name "suoke_health_data" \
  --db-user "suoke_user" \
  --db-password "your_secure_password"
```

### 方法二：手动安装

#### Ubuntu/Debian

```bash
# 更新包列表
sudo apt-get update

# 安装PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib postgresql-client

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### CentOS/RHEL

```bash
# 安装PostgreSQL
sudo yum install -y postgresql-server postgresql-contrib

# 初始化数据库
sudo postgresql-setup initdb

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS

```bash
# 使用Homebrew安装
brew install postgresql

# 启动服务
brew services start postgresql
```

## 配置PostgreSQL

### 1. 创建数据库和用户

```sql
-- 连接到PostgreSQL
sudo -u postgres psql

-- 创建用户
CREATE USER suoke_user WITH PASSWORD 'your_secure_password';

-- 创建数据库
CREATE DATABASE suoke_health_data OWNER suoke_user;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE suoke_health_data TO suoke_user;

-- 连接到新数据库
\c suoke_health_data

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 授予schema权限
GRANT ALL ON SCHEMA public TO suoke_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO suoke_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO suoke_user;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO suoke_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO suoke_user;

\q
```

### 2. 优化PostgreSQL配置

编辑 `/etc/postgresql/[version]/main/postgresql.conf`：

```ini
# 内存配置
shared_buffers = 256MB          # 25% of total memory
effective_cache_size = 1GB      # 75% of total memory
work_mem = 16MB
maintenance_work_mem = 256MB

# 连接配置
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

# WAL配置
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# 查询优化
random_page_cost = 1.1
effective_io_concurrency = 200

# 日志配置
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
```

## 更新应用配置

### 1. 更新依赖

确保 `requirements.txt` 包含PostgreSQL相关依赖：

```txt
asyncpg>=0.29.0
psycopg2-binary>=2.9.9
sqlalchemy-utils>=0.41.1
```

安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 更新配置文件

修改 `config/default.yaml`：

```yaml
# 数据库配置 - 使用PostgreSQL
database:
  dialect: "postgresql"
  driver: "asyncpg"
  host: "${DB_HOST:localhost}"
  port: "${DB_PORT:5432}"
  database: "${DB_NAME:suoke_health_data}"
  username: "${DB_USER:suoke_user}"
  password: "${DB_PASSWORD:your_password}"
  
  # PostgreSQL优化配置
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600
  pool_pre_ping: true
  echo: false
  
  # 连接参数
  connect_args:
    server_settings:
      application_name: "suoke_health_data_service"
      
  # 引擎选项
  engine_options:
    isolation_level: "READ_COMMITTED"
```

### 3. 设置环境变量

创建或更新 `.env` 文件：

```bash
# PostgreSQL数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=suoke_health_data
DB_USER=suoke_user
DB_PASSWORD=your_secure_password

# 连接池配置
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# 其他配置
DB_ECHO=false
DB_POOL_PRE_PING=true
```

## 数据迁移

### 1. 检查迁移前提条件

```bash
# 检查迁移前提条件
python scripts/migrate_to_postgresql.py --dry-run
```

### 2. 执行数据迁移

```bash
# 执行完整迁移
python scripts/migrate_to_postgresql.py

# 指定自定义SQLite路径
python scripts/migrate_to_postgresql.py --sqlite-path /path/to/your/sqlite.db

# 使用自定义配置文件
python scripts/migrate_to_postgresql.py --config config/production.yaml
```

### 3. 验证迁移结果

迁移脚本会自动验证数据完整性，但您也可以手动检查：

```sql
-- 连接到PostgreSQL
psql -h localhost -U suoke_user -d suoke_health_data

-- 检查表和数据
\dt                                    -- 列出所有表
SELECT COUNT(*) FROM health_data_records;  -- 检查记录数
SELECT COUNT(*) FROM users;               -- 检查用户数

-- 检查最新数据
SELECT * FROM health_data_records ORDER BY created_at DESC LIMIT 5;
```

## 更新应用代码

### 1. 数据库连接

应用代码已经更新为支持PostgreSQL，主要变化包括：

- 移除SQLite特定的配置
- 添加PostgreSQL连接池优化
- 更新数据库初始化逻辑

### 2. 测试更新

运行测试确保一切正常：

```bash
# 运行单元测试
python -m pytest test/unit/ -v

# 运行集成测试
python -m pytest test/integration/ -v

# 运行性能测试
python -m pytest test/performance/ -v
```

## 性能优化

### 1. 索引优化

PostgreSQL迁移后，确保关键索引已创建：

```sql
-- 检查现有索引
\di

-- 创建复合索引（如果需要）
CREATE INDEX CONCURRENTLY idx_health_data_user_type_time 
ON health_data_records(user_id, data_type, recorded_at);

-- 创建部分索引
CREATE INDEX CONCURRENTLY idx_health_data_recent 
ON health_data_records(recorded_at) 
WHERE recorded_at > NOW() - INTERVAL '30 days';
```

### 2. 查询优化

```sql
-- 分析表统计信息
ANALYZE health_data_records;
ANALYZE users;

-- 检查查询计划
EXPLAIN ANALYZE SELECT * FROM health_data_records 
WHERE user_id = 'some-uuid' AND recorded_at > NOW() - INTERVAL '7 days';
```

### 3. 连接池调优

根据应用负载调整连接池参数：

```yaml
database:
  pool_size: 20        # 基础连接数
  max_overflow: 10     # 额外连接数
  pool_timeout: 30     # 获取连接超时
  pool_recycle: 3600   # 连接回收时间
```

## 监控和维护

### 1. 性能监控

```sql
-- 启用pg_stat_statements扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查看慢查询
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- 查看数据库大小
SELECT pg_size_pretty(pg_database_size('suoke_health_data'));
```

### 2. 定期维护

```bash
# 创建维护脚本
cat << 'EOF' > scripts/postgresql_maintenance.sh
#!/bin/bash

# 数据库维护脚本
DB_NAME="suoke_health_data"
DB_USER="suoke_user"

# 更新统计信息
psql -h localhost -U $DB_USER -d $DB_NAME -c "ANALYZE;"

# 清理死元组
psql -h localhost -U $DB_USER -d $DB_NAME -c "VACUUM ANALYZE;"

# 重建索引（如果需要）
# psql -h localhost -U $DB_USER -d $DB_NAME -c "REINDEX DATABASE $DB_NAME;"

echo "数据库维护完成: $(date)"
EOF

chmod +x scripts/postgresql_maintenance.sh
```

### 3. 备份策略

```bash
# 创建备份脚本
cat << 'EOF' > scripts/postgresql_backup.sh
#!/bin/bash

DB_NAME="suoke_health_data"
DB_USER="suoke_user"
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
pg_dump -h localhost -U $DB_USER -d $DB_NAME \
  --format=custom \
  --compress=9 \
  --file="$BACKUP_DIR/suoke_health_data_$DATE.backup"

# 保留最近30天的备份
find $BACKUP_DIR -name "*.backup" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR/suoke_health_data_$DATE.backup"
EOF

chmod +x scripts/postgresql_backup.sh
```

## 故障排除

### 1. 常见问题

#### 连接问题

```bash
# 检查PostgreSQL服务状态
sudo systemctl status postgresql

# 检查端口监听
sudo netstat -tlnp | grep 5432

# 测试连接
psql -h localhost -U suoke_user -d suoke_health_data -c "SELECT version();"
```

#### 权限问题

```sql
-- 检查用户权限
\du suoke_user

-- 检查数据库权限
\l suoke_health_data

-- 重新授权（如果需要）
GRANT ALL PRIVILEGES ON DATABASE suoke_health_data TO suoke_user;
```

#### 性能问题

```sql
-- 检查活动连接
SELECT * FROM pg_stat_activity WHERE datname = 'suoke_health_data';

-- 检查锁等待
SELECT * FROM pg_locks WHERE NOT granted;

-- 检查表大小
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2. 日志分析

```bash
# 查看PostgreSQL日志
sudo tail -f /var/log/postgresql/postgresql-*.log

# 查看应用日志
tail -f logs/health_data_service.log
```

## 回滚计划

如果迁移出现问题，可以回滚到SQLite：

### 1. 恢复SQLite配置

```yaml
# 恢复config/default.yaml中的SQLite配置
database:
  dialect: "sqlite"
  driver: "aiosqlite"
  path: "${DB_PATH:data/health_data.db}"
  # ... 其他SQLite配置
```

### 2. 恢复数据

```bash
# 恢复备份的SQLite文件
cp data/health_data_backup_*.db data/health_data.db

# 重启服务
python cmd/server/main.py
```

## 迁移检查清单

- [ ] 备份现有SQLite数据库
- [ ] 安装和配置PostgreSQL
- [ ] 更新应用依赖
- [ ] 修改配置文件
- [ ] 设置环境变量
- [ ] 运行迁移脚本
- [ ] 验证数据完整性
- [ ] 运行测试套件
- [ ] 性能测试
- [ ] 设置监控
- [ ] 配置备份策略
- [ ] 文档更新

## 总结

PostgreSQL迁移完成后，您将获得：

1. **更好的性能**: 支持更高的并发和更复杂的查询
2. **更强的扩展性**: 支持水平和垂直扩展
3. **更丰富的功能**: JSON支持、全文搜索、地理信息等
4. **更好的可靠性**: ACID事务、WAL日志、热备份等
5. **更完善的监控**: 详细的统计信息和性能指标

如果在迁移过程中遇到问题，请参考故障排除部分或联系技术支持团队。 