# 健康检查 API

健康检查API提供了全面的服务健康状态监控功能，支持Kubernetes的存活检查、就绪检查和启动检查。

## 📋 API 端点概览

| 方法 | 端点 | 描述 | 用途 |
|------|------|------|------|
| GET | `/health/` | 基础健康检查 | 通用健康状态 |
| GET | `/health/live` | 存活检查 | Kubernetes livenessProbe |
| GET | `/health/ready` | 就绪检查 | Kubernetes readinessProbe |
| GET | `/health/startup` | 启动检查 | Kubernetes startupProbe |
| GET | `/health/detailed` | 详细健康检查 | 运维监控 |

## 🏥 基础健康检查

### 端点
```
GET /api/v1/health/
```

### 描述
提供服务的基本健康状态信息，包括服务状态、运行时间和基本系统信息。

### 响应
```json
{
  "status": "healthy | unhealthy | degraded",
  "timestamp": "number",
  "service": "ai-model-service",
  "version": "string",
  "uptime": "number",
  "checks": {
    "database": "healthy | unhealthy",
    "kubernetes": "healthy | unhealthy",
    "models": "healthy | unhealthy"
  }
}
```

### 示例
```bash
curl -X GET http://localhost:8080/api/v1/health/ \
  -H "Accept: application/json"
```

### 响应示例
```json
{
  "status": "healthy",
  "timestamp": 1704067200.123,
  "service": "ai-model-service",
  "version": "1.0.0",
  "uptime": 3600.5,
  "checks": {
    "database": "healthy",
    "kubernetes": "healthy",
    "models": "healthy"
  }
}
```

## 💓 存活检查 (Liveness Probe)

### 端点
```
GET /api/v1/health/live
```

### 描述
用于Kubernetes存活检查，确定容器是否正在运行。如果此检查失败，Kubernetes将重启容器。

### 检查项目
- 服务进程状态
- 关键线程状态
- 内存使用情况
- 基本响应能力

### 响应
```json
{
  "status": "healthy | unhealthy",
  "timestamp": "number",
  "service": "ai-model-service",
  "version": "string",
  "uptime": "number",
  "checks": {
    "process": "healthy | unhealthy",
    "memory": "healthy | unhealthy",
    "threads": "healthy | unhealthy"
  }
}
```

### Kubernetes 配置示例
```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### 示例
```bash
curl -X GET http://localhost:8080/api/v1/health/live
```

## ✅ 就绪检查 (Readiness Probe)

### 端点
```
GET /api/v1/health/ready
```

### 描述
用于Kubernetes就绪检查，确定容器是否准备好接收流量。如果此检查失败，Kubernetes将从Service的端点中移除该Pod。

### 检查项目
- 数据库连接
- Kubernetes API连接
- 依赖服务状态
- 模型加载状态
- 配置文件有效性

### 响应
```json
{
  "status": "ready | not_ready",
  "timestamp": "number",
  "service": "ai-model-service",
  "version": "string",
  "uptime": "number",
  "checks": {
    "database": "ready | not_ready",
    "kubernetes": "ready | not_ready",
    "dependencies": "ready | not_ready",
    "models": "ready | not_ready",
    "configuration": "ready | not_ready"
  }
}
```

### Kubernetes 配置示例
```yaml
readinessProbe:
  httpGet:
    path: /api/v1/health/ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### 示例
```bash
curl -X GET http://localhost:8080/api/v1/health/ready
```

## 🚀 启动检查 (Startup Probe)

### 端点
```
GET /api/v1/health/startup
```

### 描述
用于Kubernetes启动检查，确定容器内的应用程序是否已启动。在启动检查成功之前，存活检查和就绪检查将被禁用。

### 检查项目
- 应用程序初始化
- 配置加载
- 数据库迁移
- 模型预加载
- 依赖服务连接

### 响应
```json
{
  "status": "started | starting | failed",
  "timestamp": "number",
  "service": "ai-model-service",
  "version": "string",
  "uptime": "number",
  "checks": {
    "initialization": "completed | in_progress | failed",
    "configuration": "loaded | loading | failed",
    "database": "connected | connecting | failed",
    "models": "loaded | loading | failed",
    "dependencies": "connected | connecting | failed"
  }
}
```

### Kubernetes 配置示例
```yaml
startupProbe:
  httpGet:
    path: /api/v1/health/startup
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 30  # 允许最多5分钟启动时间
```

### 示例
```bash
curl -X GET http://localhost:8080/api/v1/health/startup
```

## 🔍 详细健康检查

### 端点
```
GET /api/v1/health/detailed
```

### 描述
提供详细的系统健康信息，包括系统资源使用情况、性能指标和详细的组件状态。主要用于运维监控和故障排除。

### 响应
```json
{
  "status": "healthy | unhealthy | degraded",
  "timestamp": "number",
  "service": "ai-model-service",
  "version": "string",
  "uptime": "number",
  "checks": {
    "system": {
      "platform": "string",
      "python_version": "string",
      "cpu_count": "string",
      "cpu_percent": "number",
      "memory_percent": "number",
      "disk_percent": "number"
    },
    "database": {
      "status": "healthy | unhealthy",
      "connection_pool": {
        "active": "number",
        "idle": "number",
        "total": "number"
      },
      "response_time": "number"
    },
    "kubernetes": {
      "status": "healthy | unhealthy",
      "api_server": "reachable | unreachable",
      "namespace": "string",
      "node_count": "number"
    },
    "models": {
      "total": "number",
      "running": "number",
      "failed": "number",
      "pending": "number"
    },
    "performance": {
      "avg_response_time": "number",
      "requests_per_second": "number",
      "error_rate": "number"
    }
  }
}
```

### 示例
```bash
curl -X GET http://localhost:8080/api/v1/health/detailed \
  -H "Accept: application/json"
```

### 响应示例
```json
{
  "status": "healthy",
  "timestamp": 1704067200.123,
  "service": "ai-model-service",
  "version": "1.0.0",
  "uptime": 3600.5,
  "checks": {
    "system": {
      "platform": "Linux-5.4.0-74-generic-x86_64-with-glibc2.31",
      "python_version": "3.13.0",
      "cpu_count": "8",
      "cpu_percent": 25.5,
      "memory_percent": 45.2,
      "disk_percent": 60.1
    },
    "database": {
      "status": "healthy",
      "connection_pool": {
        "active": 5,
        "idle": 10,
        "total": 15
      },
      "response_time": 12.5
    },
    "kubernetes": {
      "status": "healthy",
      "api_server": "reachable",
      "namespace": "suoke-life",
      "node_count": 3
    },
    "models": {
      "total": 5,
      "running": 4,
      "failed": 0,
      "pending": 1
    },
    "performance": {
      "avg_response_time": 150.5,
      "requests_per_second": 25.3,
      "error_rate": 0.01
    }
  }
}
```

## 📊 健康状态说明

### 状态值定义

| 状态 | 描述 | HTTP状态码 |
|------|------|------------|
| `healthy` | 所有检查通过，服务正常 | 200 |
| `unhealthy` | 关键检查失败，服务不可用 | 503 |
| `degraded` | 部分检查失败，服务降级运行 | 200 |
| `ready` | 服务准备就绪 | 200 |
| `not_ready` | 服务未准备就绪 | 503 |
| `started` | 服务已启动 | 200 |
| `starting` | 服务正在启动 | 503 |
| `failed` | 服务启动失败 | 503 |

### 检查项目说明

| 检查项 | 描述 | 失败影响 |
|--------|------|----------|
| `process` | 主进程状态 | 服务不可用 |
| `memory` | 内存使用情况 | 性能降级 |
| `threads` | 线程池状态 | 功能受限 |
| `database` | 数据库连接 | 数据操作失败 |
| `kubernetes` | K8s API连接 | 部署操作失败 |
| `models` | 模型状态 | 推理功能受限 |
| `configuration` | 配置有效性 | 功能异常 |
| `dependencies` | 依赖服务 | 相关功能不可用 |

## 🔧 监控集成

### Prometheus 监控
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ai-model-service-health'
    static_configs:
      - targets: ['ai-model-service:8080']
    metrics_path: '/api/v1/health/detailed'
    scrape_interval: 30s
```

### Grafana 仪表板
```json
{
  "dashboard": {
    "title": "AI Model Service Health",
    "panels": [
      {
        "title": "Service Status",
        "type": "stat",
        "targets": [
          {
            "expr": "ai_model_service_health_status"
          }
        ]
      }
    ]
  }
}
```

### 告警规则
```yaml
# alerts.yml
groups:
  - name: ai-model-service
    rules:
      - alert: ServiceUnhealthy
        expr: ai_model_service_health_status != 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AI Model Service is unhealthy"
          description: "Service has been unhealthy for more than 1 minute"
```

## 🚨 故障排除

### 常见问题

1. **健康检查超时**
   - 检查网络连接
   - 验证服务端口
   - 查看服务日志

2. **就绪检查失败**
   - 检查数据库连接
   - 验证Kubernetes配置
   - 确认依赖服务状态

3. **启动检查失败**
   - 检查配置文件
   - 验证环境变量
   - 查看初始化日志

### 调试命令
```bash
# 检查服务状态
kubectl get pods -l app=ai-model-service

# 查看健康检查日志
kubectl logs -l app=ai-model-service | grep health

# 手动测试健康检查
curl -v http://localhost:8080/api/v1/health/detailed
```

## 📚 相关文档

- [API概览](overview.md)
- [模型管理API](models.md)
- [运维指南](../operations/troubleshooting.md)