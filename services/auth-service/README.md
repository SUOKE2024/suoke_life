# 授权服务 (Auth Service)

索克生命平台的用户认证和授权服务，提供安全可靠的身份验证、用户管理和访问控制功能。

## 功能特性

- **用户认证**：用户名/密码、JWT、OAuth2、第三方认证
- **多因素认证**：支持 TOTP、SMS、邮件验证码等多因素认证方式
- **用户管理**：用户注册、配置文件管理、账户恢复
- **权限控制**：基于角色的访问控制(RBAC)、细粒度权限管理
- **令牌管理**：访问令牌颁发、刷新和撤销
- **安全机制**：密码策略、失败限制、会话管理
- **审计日志**：用户活动和安全事件的详细日志记录

## 技术栈

- **语言**：Python 3.11+
- **Web框架**：FastAPI + gRPC
- **数据库**：PostgreSQL (主数据库)、Redis (缓存和会话)
- **容器化**：Docker + Kubernetes
- **CI/CD**：GitHub Actions
- **监控**：Prometheus + Grafana
- **日志**：结构化日志 + OpenTelemetry

## 目录结构

```
services/auth-service/
├── api/                   # API定义
│   ├── grpc/              # gRPC API定义文件
│   └── rest/              # REST API文档和模式
├── cmd/                   # 入口点命令
│   └── server/            # 服务器启动命令
├── config/                # 配置文件和模板
├── deploy/                # 部署配置
│   ├── docker/            # Docker配置
│   ├── kubernetes/        # Kubernetes配置
│   └── grafana/           # Grafana仪表板配置
├── docs/                  # 服务文档
├── internal/              # 内部实现代码
│   ├── delivery/          # API处理器和路由
│   │   ├── grpc/          # gRPC实现
│   │   └── rest/          # REST API实现
│   ├── model/             # 领域模型和数据结构
│   ├── observability/     # 可观测性工具
│   ├── repository/        # 数据存储和访问层
│   ├── resilience/        # 弹性和容错机制
│   ├── security/          # 安全工具和实用函数
│   └── service/           # 业务逻辑
├── pkg/                   # 公共包
│   ├── middleware/        # 中间件组件
│   └── utils/             # 通用工具函数
├── scripts/               # 脚本工具
│   ├── backup.py          # 数据库备份工具
│   ├── cron/              # 定时任务脚本
│   └── security_check.py  # 安全检查脚本
└── test/                  # 测试代码
    ├── integration/       # 集成测试
    └── unit/              # 单元测试
```

## 快速开始

### 本地开发环境

1. **克隆仓库**

   ```bash
   git clone https://github.com/suoke/life.git
   cd life/services/auth-service
   ```

2. **创建虚拟环境**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或者
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **设置环境变量**

   ```bash
   # Linux/macOS
   cp .env.example .env
   # 编辑.env文件配置

   # 或者直接设置
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=auth_db
   export DB_USER=postgres
   export DB_PASSWORD=your_password
   export REDIS_HOST=localhost
   export REDIS_PORT=6379
   export JWT_SECRET_KEY=your_secret_key
   export JWT_ALGORITHM=HS256
   ```

5. **启动本地服务**

   ```bash
   python -m cmd.server.main
   ```

6. **访问API文档**

   打开浏览器访问: http://localhost:8000/docs

### Docker部署

使用Docker Compose快速部署:

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### Kubernetes部署

1. **创建配置和密钥**

   ```bash
   # 创建命名空间
   kubectl create namespace suoke

   # 创建配置映射
   kubectl apply -f deploy/kubernetes/auth-service.yaml

   # 创建密钥
   kubectl create secret generic auth-service-secrets \
     --namespace=suoke \
     --from-literal=jwt-secret=your_jwt_secret \
     --from-literal=db-password=your_db_password
   ```

2. **部署服务**

   ```bash
   kubectl apply -f deploy/kubernetes/auth-service.yaml
   ```

3. **检查部署状态**

   ```bash
   kubectl get pods -n suoke
   kubectl get services -n suoke
   ```

## 配置指南

### 主要配置选项

| 环境变量 | 描述 | 默认值 | 必须 |
|----------|------|--------|------|
| `SERVICE_NAME` | 服务名称 | `auth-service` | 否 |
| `ENV` | 环境(development,staging,production) | `development` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `DB_HOST` | 数据库主机 | `localhost` | 是 |
| `DB_PORT` | 数据库端口 | `5432` | 否 |
| `DB_NAME` | 数据库名称 | `auth_db` | 是 |
| `DB_USER` | 数据库用户 | `postgres` | 是 |
| `DB_PASSWORD` | 数据库密码 | - | 是 |
| `REDIS_HOST` | Redis主机 | `localhost` | 是 |
| `REDIS_PORT` | Redis端口 | `6379` | 否 |
| `JWT_SECRET_KEY` | JWT签名密钥 | - | 是 |
| `JWT_ALGORITHM` | JWT算法 | `HS256` | 否 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 访问令牌过期时间(分钟) | `30` | 否 |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 刷新令牌过期时间(天) | `7` | 否 |
| `HTTP_PORT` | HTTP服务器端口 | `8000` | 否 |
| `GRPC_PORT` | gRPC服务器端口 | `50051` | 否 |
| `CORS_ORIGINS` | 允许的CORS源(逗号分隔) | `*` | 否 |
| `METRICS_ENABLED` | 是否启用指标收集 | `true` | 否 |
| `OTLP_ENDPOINT` | OpenTelemetry导出器端点 | - | 否 |
| `ENABLE_CONSOLE_EXPORT` | 是否启用控制台导出 | `true` | 否 |

### 高可用配置

通过以下环境变量启用高可用特性:

```bash
# 区域感知路由
export ZONE_AWARE_ROUTING=true
export PRIMARY_REGION=cn-north
export BACKUP_REGIONS=cn-east,cn-south

# 读写分离
export READ_REPLICAS_ENABLED=true
export PRIMARY_DB_HOST=postgres-primary
export REPLICA_DB_HOST=postgres-replica

# Redis哨兵
export REDIS_SENTINEL_ADDRS=redis-sentinel-0:26379,redis-sentinel-1:26379
export REDIS_MASTER_NAME=auth-redis-master

# 弹性配置
export CIRCUIT_BREAKER_ENABLED=true
export CONNECTION_TIMEOUT_MS=3000
export REQUEST_TIMEOUT_MS=5000
export RETRY_COUNT=3
```

## 健康监控

服务提供以下健康检查端点:

- **完整健康状态**: `GET /health`
- **存活探针**: `GET /health/live` (用于Kubernetes livenessProbe)
- **就绪探针**: `GET /health/ready` (用于Kubernetes readinessProbe)

## API文档

- **OpenAPI文档**: 访问 `/docs` 或 `/redoc`
- **gRPC反射**: 服务启用了gRPC反射，可使用grpcurl等工具探索API

## 备份与恢复

服务提供数据库备份与恢复工具:

```bash
# 完整备份
python scripts/backup.py --full

# 增量备份
python scripts/backup.py --incremental

# 从备份文件恢复
python scripts/backup.py --restore /path/to/backup.sql

# 自动化备份(每周日完整备份，其他日子增量备份)
# 添加到crontab:
# 0 1 * * * /path/to/scripts/cron/backup-cron.sh
```

## 安全检查

运行安全检查工具:

```bash
# 安装安全工具
python scripts/security_check.py --install-tools

# 运行安全检查
python scripts/security_check.py --code-path .

# 查看详细报告
python scripts/security_check.py --detailed
```

## 性能优化

服务内置多项性能优化:

- **连接池**: 数据库和Redis连接池管理
- **缓存策略**: 多级缓存(内存、Redis)
- **异步处理**: 基于asyncio的非阻塞IO
- **水平扩展**: 支持无状态部署多个实例

## 监控与告警

使用Prometheus和Grafana监控服务:

1. 服务暴露`/metrics`端点，提供标准和自定义指标
2. 部署目录包含Grafana仪表板配置
3. 关键指标:
   - 请求率和延迟
   - 认证成功/失败率
   - 用户操作计数
   - 系统资源使用率

## 故障排除

常见问题:

- **数据库连接失败**: 检查`DB_*`环境变量和网络设置
- **Redis连接失败**: 验证`REDIS_*`配置和连接性
- **JWT验证失败**: 确保使用正确的`JWT_SECRET_KEY`和`JWT_ALGORITHM`
- **性能问题**: 启用详细日志并检查数据库查询性能

## 贡献指南

欢迎贡献代码，请遵循以下步骤:

1. Fork仓库并创建功能分支
2. 添加测试并确保现有测试通过
3. 遵循代码风格指南(使用black和flake8)
4. 提交Pull Request并详细描述更改

## 许可证

© 2023 索克生命科技有限公司。保留所有权利。 