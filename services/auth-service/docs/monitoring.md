# 授权服务监控指南

本文档提供关于授权服务(Auth Service)监控和可观测性设置的详细指南，方便运维人员进行有效监控和快速故障排除。

## 监控架构概述

Auth Service实现了全面的可观测性架构，包括三个关键方面：

1. **指标（Metrics）**：使用Prometheus收集系统和业务指标
2. **日志（Logging）**：采用结构化日志格式，通过OpenTelemetry整合
3. **追踪（Tracing）**：分布式请求追踪，使用OpenTelemetry标准

![监控架构](../docs/images/monitoring-architecture.png)

## 关键指标

### 系统指标

| 指标名称 | 类型 | 描述 | 警报阈值 |
|---------|------|------|----------|
| `auth_process_cpu_seconds_total` | Counter | CPU使用时间总计 | N/A |
| `auth_process_resident_memory_bytes` | Gauge | 驻留内存使用量 | >500MB |
| `auth_process_open_fds` | Gauge | 打开的文件描述符数量 | >1000 |
| `auth_process_max_fds` | Gauge | 最大文件描述符限制 | N/A |
| `auth_go_goroutines` | Gauge | 活跃协程数量 | >5000 |
| `auth_go_threads` | Gauge | 系统线程数量 | >100 |

### HTTP指标

| 指标名称 | 类型 | 描述 | 警报阈值 |
|---------|------|------|----------|
| `auth_request_total` | Counter | 请求总数 | N/A |
| `auth_request_latency_seconds` | Histogram | 请求延迟分布 | p99 > 1s |
| `auth_request_size_bytes` | Histogram | 请求大小分布 | N/A |
| `auth_response_size_bytes` | Histogram | 响应大小分布 | N/A |
| `auth_http_active_requests` | Gauge | 当前活跃请求数 | >500 |

### 业务指标

| 指标名称 | 类型 | 描述 | 警报阈值 |
|---------|------|------|----------|
| `auth_attempt_total` | Counter | 认证尝试总数（按结果标签区分） | N/A |
| `auth_login_failures_total` | Counter | 登录失败总数（按原因标签区分） | >10/分钟 |
| `auth_token_operation_total` | Counter | 令牌操作总数（创建/验证/刷新/撤销） | N/A |
| `auth_user_operation_total` | Counter | 用户操作总数（创建/更新/删除） | N/A |
| `auth_active_tokens` | Gauge | 当前活跃的访问令牌数 | N/A |
| `auth_token_validation_latency_seconds` | Histogram | 令牌验证延迟 | p95 > 50ms |
| `auth_mfa_operations_total` | Counter | 多因素认证操作数（按类型标签区分） | N/A |
| `auth_throttled_requests_total` | Counter | 被限流的请求数 | >20/分钟 |

### 数据库指标

| 指标名称 | 类型 | 描述 | 警报阈值 |
|---------|------|------|----------|
| `auth_db_connections_total` | Gauge | 数据库连接池大小 | >80% 配置最大值 |
| `auth_db_connections_active` | Gauge | 活跃数据库连接数 | >90% 配置最大值 |
| `auth_db_query_latency_seconds` | Histogram | 数据库查询延迟 | p95 > 100ms |
| `auth_db_errors_total` | Counter | 数据库错误总数 | >5/分钟 |

### Redis指标

| 指标名称 | 类型 | 描述 | 警报阈值 |
|---------|------|------|----------|
| `auth_redis_operations_total` | Counter | Redis操作总数 | N/A |
| `auth_redis_errors_total` | Counter | Redis错误总数 | >5/分钟 |
| `auth_redis_latency_seconds` | Histogram | Redis操作延迟 | p95 > 10ms |
| `auth_redis_connections` | Gauge | Redis连接数 | >80% 配置最大值 |

### 弹性指标

| 指标名称 | 类型 | 描述 | 警报阈值 |
|---------|------|------|----------|
| `auth_circuit_breaker_state` | Gauge | 断路器状态（关闭=0,半开=0.5,开路=1） | 1（开路） |
| `auth_circuit_breaker_failures_total` | Counter | 断路器记录的失败总数 | >10/分钟 |
| `auth_retries_total` | Counter | 重试操作总数 | >20/分钟 |
| `auth_rate_limited_total` | Counter | 被速率限制的请求总数 | >30/分钟 |

## 日志收集与查询

授权服务使用结构化日志格式，便于统一收集和查询。日志包含以下标准字段：

- `timestamp`: ISO 8601格式的时间戳
- `level`: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `service`: 服务名称 ("auth-service")
- `instance_id`: 实例标识符（容器ID或主机名）
- `trace_id`: 关联的追踪ID（与分布式追踪集成）
- `span_id`: 关联的跨度ID
- `req_id`: 请求唯一标识符
- `user_id`: 用户ID（如果已验证）
- `path`: 请求路径
- `method`: HTTP方法
- `status_code`: HTTP状态码
- `duration_ms`: 请求处理时间（毫秒）
- `message`: 日志消息
- `error`: 错误详情（如果有）

### 常用日志查询示例（Elasticsearch）

```
# 查询特定用户的认证失败
service: "auth-service" AND level: "ERROR" AND user_id: "123456" AND message: "*authentication failed*"

# 查询JWT验证延迟过高的问题
service: "auth-service" AND path: "/api/v1/auth/verify" AND duration_ms: >50

# 查询数据库连接问题
service: "auth-service" AND message: "*database connection*" AND level: "ERROR"
```

## 分布式追踪

授权服务支持通过OpenTelemetry进行分布式追踪，以下是主要配置和使用方法：

1. **导出端点**：通过`OTLP_ENDPOINT`环境变量配置，例如`http://jaeger:4317`
2. **采样率**：通过`OTEL_TRACE_SAMPLER_ARG`环境变量控制，默认为0.1（10%）
3. **主要跟踪点**：
   - API请求处理
   - 数据库操作
   - Redis操作
   - 外部服务调用
   - 令牌验证
   - 安全操作

### 常见追踪场景

1. **跨服务认证流程**：
   - API Gateway → Auth Service → User Service → Database 
2. **令牌验证链**：
   - API Gateway → Auth Service → Redis → Token Blacklist Check
3. **OAuth认证流程**：
   - Auth Service → OAuth Provider → Callback → User Creation

## Grafana仪表板

提供预配置的Grafana仪表板，包括：

1. **Auth Service Overview**：总体服务状态和性能指标
2. **Authentication Metrics**：认证相关指标和趋势
3. **Security Dashboard**：安全事件和异常检测
4. **Performance Insights**：性能瓶颈和优化建议
5. **Error Tracking**：错误率和分类

仪表板JSON配置位于 `deploy/grafana/dashboards/` 目录。

## 告警规则

Prometheus告警规则配置位于 `deploy/prometheus/alerts.yaml`。主要告警包括：

1. **AuthServiceDown**：服务实例不可用
2. **AuthServiceHighLatency**：服务响应延迟过高
3. **AuthDatabaseConnectionIssues**：数据库连接问题
4. **AuthRedisConnectionIssues**：Redis连接问题
5. **AuthHighErrorRate**：错误率异常升高
6. **AuthHighLoginFailures**：登录失败率异常升高
7. **AuthCircuitBreakerOpen**：断路器开路
8. **AuthServiceHighMemory**：内存使用过高
9. **AuthServiceRestartFrequent**：服务频繁重启

## 健康检查端点

服务提供以下健康检查端点：

- **GET /health**：完整健康状态，包含所有依赖服务状态
- **GET /health/live**：存活检查（Kubernetes liveness probe）
- **GET /health/ready**：就绪检查（Kubernetes readiness probe）
- **GET /metrics**：Prometheus指标端点

## 常见问题排查

### 1. 认证延迟过高

检查点：
- 数据库查询性能（`auth_db_query_latency_seconds`指标）
- Redis操作延迟（`auth_redis_latency_seconds`指标）
- 服务CPU使用率（`auth_process_cpu_seconds_total`指标）
- 追踪中的慢操作（通过Jaeger UI查看）

解决方案：
- 优化数据库索引
- 调整数据库连接池大小
- 调整缓存策略
- 考虑水平扩展服务实例

### 2. 高失败率

检查点：
- 登录失败分布（`auth_login_failures_total`按原因划分）
- 服务错误日志（查看ERROR级别日志）
- 数据库或Redis连接问题

解决方案：
- 检查数据库连接配置
- 验证Redis可用性
- 检查外部服务依赖
- 查看密码策略是否过于严格

### 3. 令牌验证问题

检查点：
- 令牌验证失败率（`auth_token_operation_total`指标）
- JWT密钥配置是否一致
- 时钟漂移问题

解决方案：
- 确保所有服务使用相同的JWT密钥
- 同步服务器时间
- 检查令牌黑名单功能

## 监控最佳实践

1. **建立基线**：在正常负载下记录性能指标基线
2. **警报分级**：设置不同严重度的警报阈值
3. **关联分析**：结合指标、日志和追踪进行问题分析
4. **容量规划**：基于历史指标趋势进行容量规划
5. **异常检测**：实施基于机器学习的异常检测
6. **定期审计**：定期审查安全事件和访问模式
7. **定期演练**：进行故障注入演练，测试恢复能力 