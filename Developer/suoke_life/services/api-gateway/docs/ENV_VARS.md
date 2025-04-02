# API网关环境变量文档

本文档详细说明API网关服务使用的环境变量配置。这些环境变量可以在`.env`文件中设置，也可以通过Docker容器运行时或Kubernetes配置映射提供。

## 核心配置

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `NODE_ENV` | 运行环境 | `production` | 是 | `development`, `test`, `production` |
| `PORT` | HTTP服务端口 | `3000` | 是 | `3000` |
| `HOST` | 服务器监听地址 | `0.0.0.0` | 是 | `0.0.0.0`, `127.0.0.1` |
| `LOG_LEVEL` | 日志级别 | `info` | 否 | `debug`, `info`, `warn`, `error` |
| `LOG_FORMAT` | 日志格式 | `json` | 否 | `json`, `pretty` |
| `LOG_DIR` | 日志存储目录 | `logs` | 否 | `/app/logs` |

## 安全配置

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `CORS_ORIGIN` | CORS允许的源 | `*` | 否 | `*`, `https://app.suoke.life` |
| `CORS_METHODS` | CORS允许的方法 | `GET,POST,PUT,DELETE,OPTIONS` | 否 | `GET,POST` |
| `JWT_SECRET` | JWT令牌密钥 | - | 是 | `your-secret-key` |
| `JWT_EXPIRES_IN` | JWT令牌过期时间 | `86400` (1天) | 否 | `3600` (1小时) |
| `RATE_LIMIT_WINDOW_MS` | 速率限制窗口(毫秒) | `60000` (1分钟) | 否 | `300000` (5分钟) |
| `RATE_LIMIT_MAX` | 窗口内最大请求数 | `100` | 否 | `500` |
| `TLS_KEY_PATH` | TLS私钥路径 | - | 否 | `/app/secrets/tls.key` |
| `TLS_CERT_PATH` | TLS证书路径 | - | 否 | `/app/secrets/tls.crt` |

## 监控和可观测性

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `METRICS_ENABLED` | 是否启用指标 | `true` | 否 | `true`, `false` |
| `METRICS_PORT` | 指标服务端口 | `9090` | 否 | `9090` |
| `METRICS_PATH` | 指标端点路径 | `/metrics` | 否 | `/prometheus` |
| `OTEL_ENABLED` | 是否启用OpenTelemetry | `false` | 否 | `true`, `false` |
| `OTEL_SERVICE_NAME` | 服务名称 | `api-gateway` | 否 | `api-gateway-prod` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP导出器端点 | - | 否 | `http://otel-collector:4317` |
| `HEALTH_CHECK_PATH` | 健康检查路径 | `/health` | 否 | `/healthz` |

## 缓存配置

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `CACHE_ENABLED` | 是否启用缓存 | `true` | 否 | `true`, `false` |
| `CACHE_TTL` | 缓存过期时间(秒) | `300` (5分钟) | 否 | `600` (10分钟) |
| `CACHE_MAX_SIZE` | 缓存最大条目数 | `1000` | 否 | `5000` |
| `REDIS_HOST` | Redis主机地址 | - | 否 | `redis.suoke.internal` |
| `REDIS_PORT` | Redis端口 | `6379` | 否 | `6379` |
| `REDIS_PASSWORD` | Redis密码 | - | 否 | `your-redis-password` |
| `REDIS_DB` | Redis数据库编号 | `0` | 否 | `1` |

## 断路器配置

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `CIRCUIT_BREAKER_ENABLED` | 是否启用断路器 | `true` | 否 | `true`, `false` |
| `CIRCUIT_BREAKER_TIMEOUT` | 请求超时时间(毫秒) | `5000` | 否 | `10000` |
| `CIRCUIT_BREAKER_RESET_TIMEOUT` | 断路器重置时间(毫秒) | `30000` | 否 | `60000` |
| `CIRCUIT_BREAKER_FAILURE_THRESHOLD` | 故障阈值 | `5` | 否 | `10` |

## 服务发现配置

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `SERVICE_DISCOVERY_ENABLED` | 是否启用服务发现 | `false` | 否 | `true`, `false` |
| `SERVICE_DISCOVERY_TYPE` | 服务发现类型 | `kubernetes` | 否 | `kubernetes`, `consul`, `etcd` |
| `SERVICE_DISCOVERY_HOST` | 服务发现主机 | `service-discovery` | 否 | `consul.suoke.internal` |
| `SERVICE_DISCOVERY_PORT` | 服务发现端口 | `8080` | 否 | `8500` |
| `SERVICE_REGISTRY_TTL` | 服务注册生存时间(秒) | `30` | 否 | `60` |
| `SERVICE_HEARTBEAT_INTERVAL` | 心跳间隔(秒) | `10` | 否 | `20` |

## Vault集成配置

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `VAULT_ENABLED` | 是否启用Vault | `false` | 否 | `true`, `false` |
| `VAULT_HOST` | Vault主机 | `vault` | 否 | `vault.suoke.internal` |
| `VAULT_PORT` | Vault端口 | `8200` | 否 | `8200` |
| `VAULT_TOKEN` | Vault令牌 | - | 否 | `hvs.CAESIJVfxr...` |
| `VAULT_PATH_PREFIX` | Vault路径前缀 | `secret/data/api-gateway` | 否 | `secret/data/prod` |

## 微服务连接配置

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `AUTH_SERVICE_URL` | 认证服务URL | - | 是 | `http://auth-service:3000` |
| `USER_SERVICE_URL` | 用户服务URL | - | 是 | `http://user-service:3000` |
| `KNOWLEDGE_SERVICE_URL` | 知识服务URL | - | 是 | `http://knowledge-service:3000` |
| `RAG_SERVICE_URL` | RAG服务URL | - | 是 | `http://rag-service:3000` |
| `HEALTH_SERVICE_URL` | 健康服务URL | - | 是 | `http://health-service:3000` |
| `AGENT_SERVICE_URL` | 代理服务URL | - | 是 | `http://agent-service:3000` |
| `MULTIMODAL_SERVICE_URL` | 多模态服务URL | - | 是 | `http://multimodal-service:3000` |

## 高级配置

| 环境变量 | 描述 | 默认值 | 必填 | 示例 |
|---------|------|-------|------|------|
| `BODY_PARSER_LIMIT` | 请求体大小限制 | `1mb` | 否 | `5mb` |
| `COMPRESSION_LEVEL` | 压缩级别 | `6` | 否 | `9` |
| `REQUEST_TIMEOUT` | 请求超时时间(毫秒) | `30000` | 否 | `60000` |
| `NODE_OPTIONS` | Node.js选项 | - | 否 | `--max-old-space-size=2048` |
| `KEEP_ALIVE_TIMEOUT` | Keep-Alive超时(毫秒) | `5000` | 否 | `10000` |
| `HEADERS_TIMEOUT` | 头部超时(毫秒) | `6000` | 否 | `11000` |
| `PROXY_TIMEOUT` | 代理超时(毫秒) | `30000` | 否 | `60000` |

## 使用示例

### 开发环境示例

```dotenv
NODE_ENV=development
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=debug
LOG_FORMAT=pretty
CORS_ORIGIN=*
METRICS_ENABLED=true
CACHE_ENABLED=true
CIRCUIT_BREAKER_ENABLED=true
AUTH_SERVICE_URL=http://localhost:3001
USER_SERVICE_URL=http://localhost:3002
```

### 生产环境示例

```dotenv
NODE_ENV=production
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=info
LOG_FORMAT=json
CORS_ORIGIN=https://app.suoke.life,https://admin.suoke.life
JWT_SECRET=${VAULT_SECRET}
METRICS_ENABLED=true
OTEL_ENABLED=true
OTEL_SERVICE_NAME=api-gateway-prod
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
CACHE_ENABLED=true
REDIS_HOST=redis.suoke.internal
REDIS_PASSWORD=${REDIS_SECRET}
SERVICE_DISCOVERY_ENABLED=true
SERVICE_DISCOVERY_TYPE=kubernetes
```

## 使用Vault集成

当配置使用Vault时，可以通过Vault模板获取密钥:

```yaml
vault.hashicorp.com/agent-inject: "true"
vault.hashicorp.com/role: "api-gateway"
vault.hashicorp.com/agent-inject-secret-config: "secret/data/api-gateway"
vault.hashicorp.com/agent-inject-template-config: |
  {{- with secret "secret/data/api-gateway" -}}
  {
    "JWT_SECRET": "{{ .Data.data.jwt_secret }}",
    "REDIS_PASSWORD": "{{ .Data.data.redis_password }}"
  }
  {{- end -}}
``` 