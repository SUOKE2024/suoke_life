# Agent Coordinator Service 环境变量配置指南

## 概述

本文档详细介绍了Agent Coordinator Service支持的环境变量配置，包括核心配置、服务连接配置、安全配置和监控配置等。

## 核心配置

| 环境变量 | 描述 | 默认值 | 是否必需 | 示例 |
|---------|------|--------|---------|-----|
| `NODE_ENV` | 运行环境 | `production` | 是 | `production`, `development`, `testing` |
| `PORT` | 服务监听端口 | `3000` | 是 | `3000` |
| `LOG_LEVEL` | 日志级别 | `info` | 否 | `debug`, `info`, `warn`, `error` |
| `LOG_FORMAT` | 日志格式 | `json` | 否 | `json`, `pretty` |
| `COORDINATOR_MODE` | 协调器运行模式 | `standalone` | 否 | `standalone`, `distributed` |
| `CONFIG_PATH` | 配置文件路径 | `/app/config` | 否 | `/app/config` |
| `MAX_CONCURRENT_TASKS` | 最大并发任务数 | `50` | 否 | `100` |
| `REQUEST_TIMEOUT_MS` | 请求超时(毫秒) | `30000` | 否 | `60000` |

## 服务连接配置

| 环境变量 | 描述 | 默认值 | 是否必需 | 示例 |
|---------|------|--------|---------|-----|
| `RAG_SERVICE_URL` | RAG服务URL | `http://rag-service:8080` | 是 | `http://rag-service.suoke.svc:8080` |
| `LLM_SERVICE_URL` | LLM服务URL | `http://llm-service:9000` | 是 | `http://llm-service.suoke.svc:9000` |
| `RAG_SERVICE_TIMEOUT_MS` | RAG服务超时(毫秒) | `5000` | 否 | `10000` |
| `LLM_SERVICE_TIMEOUT_MS` | LLM服务超时(毫秒) | `10000` | 否 | `20000` |
| `RETRY_ATTEMPTS` | 服务调用重试次数 | `3` | 否 | `5` |
| `RETRY_DELAY_MS` | 重试延迟(毫秒) | `1000` | 否 | `2000` |

## 状态持久化配置

| 环境变量 | 描述 | 默认值 | 是否必需 | 示例 |
|---------|------|--------|---------|-----|
| `AGENT_STATE_PERSISTENCE` | 状态持久化类型 | `memory` | 否 | `memory`, `redis`, `postgres` |
| `REDIS_HOST` | Redis主机 | `redis` | 条件必需* | `redis.suoke.svc` |
| `REDIS_PORT` | Redis端口 | `6379` | 条件必需* | `6379` |
| `REDIS_PASSWORD` | Redis密码 | `""` | 否 | `password123` |
| `REDIS_DB` | Redis数据库编号 | `0` | 否 | `1` |
| `REDIS_KEYPREFIX` | Redis键前缀 | `agent:` | 否 | `agent:prod:` |

*注: 当`AGENT_STATE_PERSISTENCE=redis`时必需

## 监控与可观测性配置

| 环境变量 | 描述 | 默认值 | 是否必需 | 示例 |
|---------|------|--------|---------|-----|
| `METRICS_PORT` | 指标端口 | `9090` | 否 | `9091` |
| `OTEL_ENABLED` | 是否启用OpenTelemetry | `true` | 否 | `true`, `false` |
| `OTEL_SERVICE_NAME` | 服务名称 | `agent-coordinator-service` | 条件必需* | `agent-coordinator-service-prod` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP端点 | `http://otel-collector:4317` | 条件必需* | `http://otel-collector.monitoring:4317` |
| `HEALTH_CHECK_INTERVAL_MS` | 健康检查间隔(毫秒) | `30000` | 否 | `60000` |

*注: 当`OTEL_ENABLED=true`时必需

## 安全配置

| 环境变量 | 描述 | 默认值 | 是否必需 | 示例 |
|---------|------|--------|---------|-----|
| `JWT_SECRET` | JWT密钥 | - | 是 | `your-jwt-secret-key` |
| `JWT_EXPIRATION` | JWT过期时间(秒) | `3600` | 否 | `7200` |
| `API_KEY_HEADER` | API密钥请求头 | `X-API-Key` | 否 | `X-Suoke-API-Key` |
| `ALLOWED_ORIGINS` | 允许的跨域源 | `*` | 否 | `https://suoke.life,https://admin.suoke.life` |
| `RATE_LIMIT_WINDOW_MS` | 速率限制窗口(毫秒) | `60000` | 否 | `120000` |
| `RATE_LIMIT_MAX` | 速率限制最大请求数 | `100` | 否 | `200` |

## 容器环境配置

| 环境变量 | 描述 | 默认值 | 是否必需 | 示例 |
|---------|------|--------|---------|-----|
| `KUBERNETES_NAMESPACE` | K8s命名空间 | - | 否 | `suoke` |
| `KUBERNETES_POD_NAME` | Pod名称 | - | 否 | `agent-coordinator-859d64b4b7-2xzn5` |
| `NODE_OPTIONS` | Node.js选项 | - | 否 | `--max-old-space-size=2048` |
| `TZ` | 时区 | `Asia/Shanghai` | 否 | `Asia/Shanghai` |

## 环境变量使用示例

### 开发环境示例

```
NODE_ENV=development
PORT=3000
LOG_LEVEL=debug
LOG_FORMAT=pretty
COORDINATOR_MODE=standalone
MAX_CONCURRENT_TASKS=10
RAG_SERVICE_URL=http://localhost:8080
LLM_SERVICE_URL=http://localhost:9000
AGENT_STATE_PERSISTENCE=memory
METRICS_PORT=9090
OTEL_ENABLED=false
JWT_SECRET=dev-secret-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 生产环境示例

```
NODE_ENV=production
PORT=3000
LOG_LEVEL=info
LOG_FORMAT=json
COORDINATOR_MODE=distributed
MAX_CONCURRENT_TASKS=100
RAG_SERVICE_URL=http://rag-service.suoke.svc:8080
LLM_SERVICE_URL=http://llm-service.suoke.svc:9000
AGENT_STATE_PERSISTENCE=redis
REDIS_HOST=redis-master.suoke.svc
REDIS_PORT=6379
REDIS_PASSWORD=SecureP@ssw0rd
REDIS_DB=0
REDIS_KEYPREFIX=agent:prod:
METRICS_PORT=9090
OTEL_ENABLED=true
OTEL_SERVICE_NAME=agent-coordinator-service
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector.monitoring.svc:4317
JWT_SECRET=production-secret-from-vault
JWT_EXPIRATION=3600
API_KEY_HEADER=X-Suoke-API-Key
ALLOWED_ORIGINS=https://suoke.life,https://admin.suoke.life
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=100
TZ=Asia/Shanghai
```

## 环境变量管理最佳实践

1. **敏感配置**
   - 不要在代码或配置文件中硬编码敏感信息
   - 使用HashiCorp Vault管理密钥
   - 使用Kubernetes Secrets存储敏感环境变量

2. **配置优先级**
   - 环境变量覆盖配置文件
   - 配置文件覆盖默认值
   - 使用ConfigMap存储非敏感配置

3. **环境隔离**
   - 为不同环境(开发、测试、生产)维护不同的环境变量集
   - 使用环境特定的服务连接信息

4. **文档与验证**
   - 保持环境变量文档的更新
   - 在应用启动时验证必要的环境变量
   - 在CI/CD流程中包含配置验证步骤