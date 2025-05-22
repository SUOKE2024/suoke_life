# 索克生活APP数据库配置指南

本文档提供索克生活APP微服务数据库配置和使用的标准指南，确保所有微服务遵循相同的数据库最佳实践。

## 目录结构

```
services/common/database/
├── README.md                # 本文档
├── db_config.yaml           # 通用数据库配置模板
├── db_engine.py             # 数据库引擎，提供读写分离和连接池管理
├── db_monitor.py            # 数据库健康监控和性能指标收集
├── sqlite_manager.py        # SQLite数据库管理器（用于移动端本地存储）
└── migrations/              # 数据库迁移脚本目录
```

## 数据库选型标准

索克生活APP微服务采用以下数据库类型：

1. **PostgreSQL**：主要关系型数据库，用于存储结构化数据和支持复杂查询
2. **SQLite**：移动端本地存储，用于离线数据缓存和同步
3. **Redis**：缓存和会话存储
4. **Milvus/Chroma**：向量数据库，用于存储和检索大模型嵌入向量
5. **MongoDB**：用于非结构化文档存储（如医疗知识库）

## 使用指南

### 标准化配置

所有微服务应使用通用配置模板（`db_config.yaml`）进行配置，确保统一的数据库连接参数和优化设置。

配置文件示例：

```yaml
database:
  primary:
    type: postgresql
    host: ${DB_HOST:-localhost}
    port: ${DB_PORT:-5432}
    username: ${DB_USER:-postgres}
    password: ${DB_PASS:-postgres}
    database: ${DB_NAME:-service_db}
    
    # 连接池配置
    pool:
      min_size: 5
      max_size: ${DB_POOL_SIZE:-20}
      max_overflow: 10
      timeout: 30
```

### 数据库引擎使用

使用标准化的数据库引擎类来管理数据库连接和操作：

```python
from services.common.database.db_engine import DatabaseEngine

# 初始化数据库引擎
db_engine = DatabaseEngine("path/to/config.yaml")

# 使用写操作连接
async with db_engine.get_async_session() as session:
    # 执行写操作
    
# 使用读操作连接（自动路由到只读副本）
async with db_engine.get_read_session() as session:
    # 执行读操作
```

### 读写分离

当配置了数据库只读副本时，数据库引擎会自动实现读写分离：

1. 写操作和事务使用主数据库
2. 只读查询使用只读副本
3. 支持多种负载均衡策略

配置示例：

```yaml
database:
  # ... 主数据库配置 ...
  
  # 只读副本配置
  replicas:
    enabled: true
    strategy: "round_robin"  # 轮询策略
    nodes:
      - host: replica1.host
        port: 5432
        # ... 其他配置 ...
```

### 数据库监控

使用标准化的数据库监控工具收集性能指标和健康状态：

```python
from services.common.database.db_monitor import DatabaseMonitor

# 初始化监控器
db_monitor = DatabaseMonitor(
    service_name="my-service",
    config=app_config.get("database", {}).get("monitoring", {}),
    prometheus_port=9090
)

# 启动监控
await db_monitor.start_monitoring(db_engine)

# 查询监控信息
health_status = db_monitor.get_health_status()
slow_queries = db_monitor.get_slow_queries(limit=10)
```

### SQLite本地存储

移动端可使用优化的SQLite管理器进行本地数据存储和同步：

```python
from services.common.database.sqlite_manager import SQLiteManager

# 初始化SQLite管理器
sqlite_manager = SQLiteManager(
    db_path="path/to/local.db",
    config={
        "journal_mode": "WAL",
        "synchronous": "NORMAL",
        "backup": {"enabled": True}
    }
)

# 执行查询
result = sqlite_manager.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# 异步执行查询
result = await sqlite_manager.execute_async("SELECT * FROM health_data LIMIT 100")
```

## 最佳实践

### 连接池管理

1. 合理设置连接池大小，避免过大或过小
2. 主数据库和只读副本使用独立的连接池
3. 定期回收长时间空闲的连接
4. 监控连接池使用情况

### 查询优化

1. 使用参数化查询，避免SQL注入
2. 建立必要的索引，避免全表扫描
3. 编写高效的SQL查询，避免N+1查询问题
4. 使用适当的索引和查询优化技术

### 数据库监控

1. 设置慢查询监控，及时发现性能问题
2. 监控连接池使用情况
3. 配置适当的告警，及时发现和处理异常
4. 定期查看和分析性能指标

### 数据库迁移

1. 所有数据库结构变更通过迁移脚本执行
2. 迁移脚本应该是幂等的，可以重复执行
3. 测试环境验证迁移脚本后再应用到生产环境
4. 保留所有历史迁移脚本，确保可重现

## 数据库安全

1. 使用环境变量存储敏感配置（如密码、连接字符串）
2. 数据库用户应使用最小权限原则
3. 启用数据库审计日志
4. 定期更新数据库和驱动程序版本，修复安全漏洞
5. 考虑使用数据加密技术保护敏感数据

## 故障恢复

1. 配置自动备份
2. 定期测试数据恢复流程
3. 记录故障恢复步骤和操作手册
4. 实施高可用方案，如主备切换 

## 配置优化历史

### 2025-05-23: 数据库标准化配置优化

本次更新完成了以下微服务的数据库配置标准化：

1. **智能体服务**
   - xiaoai-service: 医疗健康助手智能体
   - xiaoke-service: 诊断智能体
   - laoke-service: 社区健康知识智能体
   - soer-service: 生活方式智能体

2. **核心服务**
   - user-service: 用户管理服务（增强配置，更大连接池）
   - med-knowledge: 医疗知识库服务（增加MongoDB和向量数据库配置）
   - rag-service: 检索增强生成服务（增强向量数据库配置）
   - message-bus: 消息总线服务（优化消息持久化配置）
   - accessibility-service: 无障碍服务（定制SQLite配置）

主要改进内容：

- 标准化数据库配置格式和参数
- 实现读写分离机制，支持数据库副本
- 优化连接池管理，提高数据库连接效率
- 增加监控和健康检查功能
- 为SQLite添加优化配置，提升移动端性能
- 为向量数据库配置合理的索引策略
- 将配置与代码分离，使用环境变量注入
- 为不同服务类型定制化数据库配置（如消息总线服务的高并发配置）

后续优化计划：

1. 完成剩余微服务的数据库配置标准化
2. 实现分布式追踪与数据库操作集成
3. 优化数据库迁移流程
4. 实现自动化备份与恢复机制 