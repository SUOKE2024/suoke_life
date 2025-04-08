# 索克生活API网关服务

API网关是索克生活微服务架构的核心组件，负责路由客户端请求到适当的后端服务，并提供多种横切关注点的功能，如认证、限流、缓存等。

## 主要功能

### 请求路由
- 基于路径和请求方法的路由
- 服务发现集成
- 健康检查和负载均衡

### 横切关注点
- JWT认证与授权
- 请求限流保护
- 响应缓存
- API监控与指标收集
- 跨域(CORS)支持
- 请求/响应日志记录
- 熔断器支持

## 技术栈
- Go 1.20+
- Gin Web框架
- JWT认证
- Prometheus指标
- Zap日志

## 配置指南

API网关通过`config.yaml`文件进行配置。配置文件示例位于`internal/configs/config-example.yaml`。

### 运行参数
```yaml
server:
  port: 8080
  host: 0.0.0.0
  read_timeout: 30
  write_timeout: 30
  shutdown_timeout: 10
```

### 缓存配置
```yaml
cache:
  enabled: true
  default_ttl: 300  # 秒
  max_cache_size: 1000
  exclude_paths:
    - "/api/v1/auth.*"
    - "/api/v1/users/profile"
```

### 限流配置
```yaml
rate_limit:
  enabled: true
  requests_per_minute: 100
  burst_size: 20
  time_window: 60  # 秒
```

### 服务发现
```yaml
service_discovery:
  enabled: false
  url: "http://consul:8500"
  refresh_interval: 30
  timeout: 5
  fallback_to_static: true
```

### 熔断器
```yaml
circuit_breaker:
  enabled: true
  max_failures: 5
  timeout: 10  # 秒
  reset_timeout: 30  # 秒
```

### 后端服务
```yaml
services:
  auth_service:
    url: "http://auth-service:8081"
    timeout: 5
    retry_count: 3
    retry_interval: 1
```

## 启动方式

### 直接运行
```bash
# 设置配置文件路径
export API_GATEWAY_CONFIG=/path/to/config.yaml

# 启动服务
go run cmd/api-gateway/main.go
```

### Docker运行
```bash
docker build -t suoke-life/api-gateway .
docker run -p 8080:8080 -v /path/to/config.yaml:/etc/api-gateway/config.yaml suoke-life/api-gateway
```

### Kubernetes部署
```bash
kubectl apply -f k8s/api-gateway.yaml
```

## 性能优化

API网关经过多项性能优化，包括：

1. 请求缓存：降低后端服务负载，提升响应速度
2. 连接池：复用后端服务连接，减少建立连接的开销
3. 请求合并：合并同类请求，减少后端服务负载
4. 异步日志：使用非阻塞日志减少请求延迟
5. 压缩响应：支持gzip和deflate压缩
6. 高效JSON序列化：使用高性能的JSON库

## 监控指标

API网关暴露Prometheus指标，可通过`/metrics`路径访问。主要指标包括：

- 请求延迟
- 请求数量
- 错误率
- 缓存命中率
- 限流统计
- 熔断器状态

## 开发指南

### 构建
```bash
make build
```

### 测试
```bash
make test
```

### 代码质量
```bash
make lint
```

### 生成API文档
```bash
make docs
```

## 路由规则

API网关按照以下模式路由请求：

- `/api/v1/auth/*` → 认证服务
- `/api/v1/users/*` → 用户服务
- `/api/v1/rag/*` → RAG检索增强服务
- `/api/v1/kg/*` → 知识图谱服务
- `/api/v1/inquiry/*` → 问诊服务
- `/api/v1/xiaoke/*` → 小柯服务
- `/api/v1/agents/*` → 智能体协调服务

## 贡献指南

1. Fork仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 提交Pull Request

## 许可证

本项目采用MIT许可证 - 详情参见[LICENSE](LICENSE)文件